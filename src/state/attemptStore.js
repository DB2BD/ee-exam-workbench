// One reliable boundary for accepting a learner's self-assessment.
// localStorage cannot provide an atomic multi-key transaction; the journal
// below enables best-effort rollback and blocks new writes if recovery fails.

const ATTEMPT_RECOVERY_KEY = 'EE_EXAM_ATTEMPT_RECOVERY_V1';
const successfulLearningAttempts = new Map();
const learningAttemptFingerprints = new Map();

function learningAttemptFingerprint(payload) {
  return JSON.stringify({
    attemptId: payload.attemptId,
    qid: payload.question && payload.question.id,
    examFamily: payload.question && payload.question.examFamily,
    sourceMode: payload.sourceMode,
    rating: Number(payload.rating),
    revealStep: Number(payload.revealStep),
    recallEntry: Boolean(payload.recallEntry),
    errorType: payload.errorType || null,
  });
}

function learningAttemptFailure(code, message) {
  return { ok: false, duplicate: false, code, message, nextReviewDate: null, nextAction: null };
}

function restoreLearningAttemptJournal(journal, storage) {
  const failures = [];
  [...(journal.writtenKeys || [])].reverse().forEach(key => {
    try {
      const before = journal.beforeByKey[key];
      if (before === null) storage.removeItem(key);
      else storage.setItem(key, before);
    } catch (_) { failures.push(key); }
  });
  if (failures.length) {
    journal.phase = 'recovery_required';
    try { storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal)); } catch (_) { /* remain blocked by the existing journal */ }
    return false;
  }
  try { storage.removeItem(ATTEMPT_RECOVERY_KEY); } catch (_) { return false; }
  return true;
}

function recoverPendingLearningAttempt(storage) {
  let raw;
  try { raw = storage.getItem(ATTEMPT_RECOVERY_KEY); } catch (_) { return false; }
  if (!raw) return true;
  let journal;
  try { journal = JSON.parse(raw); } catch (_) { return false; }
  if (journal.phase === 'committed') {
    try { storage.removeItem(ATTEMPT_RECOVERY_KEY); return true; } catch (_) { return false; }
  }
  return restoreLearningAttemptJournal(journal, storage);
}

function submitLearningAttempt(input, dependencies) {
  const payload = input || {};
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage || !recoverPendingLearningAttempt(storage)) return learningAttemptFailure('recovery_required', '先前寫入尚未恢復，已暫停新的自評。');
  const question = payload.question;
  if (!payload.attemptId || !question || !question.id || !['PE', 'GK'].includes(question.examFamily)) return learningAttemptFailure('invalid_question', '題目或作答識別無效。');
  if (!['daily-practice', 'due-review', 'browse'].includes(payload.sourceMode)) return learningAttemptFailure('invalid_mode', '自評入口無效。');
  if (![1, 3, 5].includes(Number(payload.rating))) return learningAttemptFailure('invalid_rating', '自評分數無效。');
  if (!payload.recallEntry || Number(payload.revealStep) < 4) return learningAttemptFailure('not_revealed', '請先完成第④段再自評。');
  if ((typeof recallStoreLoadError !== 'undefined' && recallStoreLoadError)
      || (payload.sourceMode !== 'daily-practice' && typeof sm2StoreLoadError !== 'undefined' && sm2StoreLoadError)) {
    return learningAttemptFailure('store_load_failed', '既有學習紀錄無法讀取，已保留原始資料並停止寫入。');
  }
  const fingerprint = learningAttemptFingerprint(payload);
  const lockedFingerprint = learningAttemptFingerprints.get(payload.attemptId);
  if (lockedFingerprint && lockedFingerprint !== fingerprint) return learningAttemptFailure('attempt_conflict', '同一次作答的內容不一致。');
  if (!lockedFingerprint) learningAttemptFingerprints.set(payload.attemptId, fingerprint);
  const prior = successfulLearningAttempts.get(payload.attemptId);
  if (prior) {
    if (prior.fingerprint !== fingerprint) return learningAttemptFailure('attempt_conflict', '同一次作答的內容不一致。');
    return Object.assign({}, prior.result, { duplicate: true });
  }

  const qid = question.id;
  const rating = Number(payload.rating);
  const achieved = rating === 5 ? 4 : rating === 3 ? 2 : 0;
  const now = dependencies && dependencies.now ? new Date(dependencies.now) : new Date();
  const writes = [];
  const nextRecallAll = Object.assign({}, recallState || {});
  nextRecallAll[qid] = calculateRecallAttemptState(getRecallState(qid), achieved, payload.errorType, now.toISOString());
  let dailyMeta = null;
  if (payload.sourceMode === 'daily-practice') {
    const loaded = loadDailyPracticeStore({ storage });
    if (loaded.error || !loaded.state.activeSession || loaded.state.activeSession.category !== question.examFamily) {
      return learningAttemptFailure('question_mismatch', '目前題目不屬於這次每日練習。');
    }
    const nextPractice = !loaded.error && calculateCompletedPracticeState(loaded.state, qid, now.getTime(), {
      rating, errorType: payload.errorType,
    });
    if (!nextPractice) return learningAttemptFailure('question_mismatch', '目前題目不屬於這次每日練習。');
    dailyMeta = {
      category: loaded.state.activeSession.category,
      subjectId: loaded.state.activeSession.subjectId,
      total: loaded.state.activeSession.questionIds.length,
      finished: nextPractice.activeSession === null,
      results: loaded.state.activeSession.questionIds.map(id => {
        const value = nextPractice.completionByQuestion[id];
        return value && typeof value === 'object'
          ? { qid: id, rating: value.rating, errorType: value.errorType || null } : null;
      }).filter(Boolean),
    };
    writes.push([DAILY_PRACTICE_STORAGE_KEY, JSON.stringify(nextPractice)]);
  }
  writes.push([RECALL_STORAGE_KEY, JSON.stringify(nextRecallAll)]);

  let nextSM2All = null;
  let nextProgressAll = null;
  let progressKey = null;
  if (payload.sourceMode !== 'daily-practice') {
    nextSM2All = Object.assign({}, sm2Schedule || {});
    nextSM2All[qid] = calculateSM2ReviewItem(nextSM2All[qid], rating, now);
    progressKey = progressStorageKeyForExamFamily(question.examFamily);
    let storedProgress = {};
    try { storedProgress = JSON.parse(storage.getItem(progressKey) || '{}') || {}; } catch (_) { return learningAttemptFailure('invalid_progress', '學習進度資料損壞，未寫入。'); }
    if (typeof progressStateIsValid !== 'function' || !progressStateIsValid(storedProgress, question.examFamily)) {
      return learningAttemptFailure('invalid_progress', '學習進度資料格式無效，未寫入。');
    }
    nextProgressAll = Object.assign({}, storedProgress);
    if (rating === 5) nextProgressAll[qid] = 1;
    else if (rating === 1) nextProgressAll[qid] = 2;
    writes.push([SM2_STORAGE_KEY, JSON.stringify(nextSM2All)]);
    writes.push([progressKey, JSON.stringify(nextProgressAll)]);
  }

  const beforeByKey = {};
  try { writes.forEach(([key]) => { beforeByKey[key] = storage.getItem(key); }); }
  catch (_) { return learningAttemptFailure('storage_read_failed', '無法讀取原始進度，未開始寫入。'); }
  const journal = { version: 1, attemptId: payload.attemptId, fingerprint, phase: 'pending', beforeByKey, afterByKey: Object.fromEntries(writes), writtenKeys: [], createdAt: now.toISOString() };
  try { storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal)); }
  catch (_) { return learningAttemptFailure('journal_failed', '無法建立恢復紀錄，未開始寫入。'); }
  try {
    writes.forEach(([key, value]) => {
      journal.writtenKeys.push(key);
      storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal));
      storage.setItem(key, value);
    });
  } catch (_) {
    const recovered = restoreLearningAttemptJournal(journal, storage);
    return learningAttemptFailure(recovered ? 'storage_write_failed' : 'recovery_required', recovered ? '進度寫入失敗，已回復，可重試。' : '進度回復失敗，已暫停新的自評。');
  }

  journal.phase = 'committed';
  try { storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal)); }
  catch (_) {
    const recovered = restoreLearningAttemptJournal(journal, storage);
    return learningAttemptFailure(recovered ? 'journal_commit_failed' : 'recovery_required', recovered ? '無法確認完整提交，已回復，可重試。' : '提交確認與回復失敗，已暫停新的自評。');
  }

  recallState = nextRecallAll;
  if (payload.sourceMode === 'daily-practice') {
    if (typeof dailyPracticeState !== 'undefined') dailyPracticeState = JSON.parse(writes[0][1]);
  } else {
    sm2Schedule = nextSM2All;
    if (typeof currentExamCategory !== 'undefined' && currentExamCategory === question.examFamily) progressState = nextProgressAll;
  }
  try { storage.removeItem(ATTEMPT_RECOVERY_KEY); }
  catch (_) { /* committed marker remains; the next submission may safely clear it */ }
  const result = {
    ok: true, duplicate: false, code: 'ok', message: '自評已儲存。',
    nextReviewDate: nextSM2All ? nextSM2All[qid].nextReviewDate : null,
    nextAction: payload.sourceMode === 'daily-practice'
      ? { type: 'advance-daily', category: dailyMeta.category, subjectId: dailyMeta.subjectId, total: dailyMeta.total, finished: dailyMeta.finished, results: dailyMeta.results }
      : { type: 'refresh-review' },
  };
  successfulLearningAttempts.set(payload.attemptId, { fingerprint, result });
  return result;
}

function scheduleDailyPracticeFollowUp(qid, dependencies) {
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  const now = dependencies && dependencies.now ? new Date(dependencies.now) : new Date();
  if (!storage || !qid || !recoverPendingLearningAttempt(storage)) return learningAttemptFailure('recovery_required', '先前寫入尚未恢復，無法加入到期複習。');
  let stored;
  try { stored = JSON.parse(storage.getItem(SM2_STORAGE_KEY) || '{}'); } catch (_) { return learningAttemptFailure('invalid_sm2', '到期排程資料損壞，未寫入。'); }
  if (!stored || typeof stored !== 'object' || Array.isArray(stored)) return learningAttemptFailure('invalid_sm2', '到期排程格式無效，未寫入。');
  if (typeof backupValidateSM2 === 'function' && Object.values(stored).some(item => !backupValidateSM2(item))) {
    return learningAttemptFailure('invalid_sm2', '到期排程內容無效，未寫入。');
  }
  const tomorrow = calculateSM2ReviewItem(null, 1, now).nextReviewDate;
  const existing = stored[qid];
  if (existing && existing.nextReviewDate && existing.nextReviewDate <= tomorrow) {
    return { ok: true, duplicate: true, code: 'already_scheduled', message: '已保留較早的到期日。', nextReviewDate: existing.nextReviewDate, nextAction: { type: 'refresh-review' } };
  }
  const nextItem = existing ? Object.assign({}, existing, { interval: 1, nextReviewDate: tomorrow })
    : { repetitions: 0, interval: 1, easeFactor: 2.5, lastReviewed: null, nextReviewDate: tomorrow };
  const next = Object.assign({}, stored, { [qid]: nextItem });
  let before;
  try { before = storage.getItem(SM2_STORAGE_KEY); } catch (_) { return learningAttemptFailure('storage_read_failed', '無法讀取原始排程，未開始寫入。'); }
  const journal = { version: 1, attemptId: `daily-followup-${qid}`, phase: 'pending', beforeByKey: { [SM2_STORAGE_KEY]: before }, afterByKey: { [SM2_STORAGE_KEY]: JSON.stringify(next) }, writtenKeys: [], createdAt: now.toISOString() };
  try {
    storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal));
    journal.writtenKeys.push(SM2_STORAGE_KEY);
    storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal));
    storage.setItem(SM2_STORAGE_KEY, JSON.stringify(next));
    journal.phase = 'committed';
    storage.setItem(ATTEMPT_RECOVERY_KEY, JSON.stringify(journal));
  } catch (_) {
    const recovered = restoreLearningAttemptJournal(journal, storage);
    return learningAttemptFailure(recovered ? 'storage_write_failed' : 'recovery_required', recovered ? '排程寫入失敗，已回復。' : '排程回復失敗，已暫停寫入。');
  }
  sm2Schedule = next;
  try { storage.removeItem(ATTEMPT_RECOVERY_KEY); } catch (_) { /* committed marker is safe */ }
  return { ok: true, duplicate: false, code: 'ok', message: '已加入到期複習。', nextReviewDate: tomorrow, nextAction: { type: 'refresh-review' } };
}
