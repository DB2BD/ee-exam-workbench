// One reliable boundary for accepting a learner's self-assessment.
// localStorage cannot provide an atomic multi-key transaction; the journal
// below enables best-effort rollback and blocks new writes if recovery fails.

const ATTEMPT_RECOVERY_KEY = 'EE_EXAM_ATTEMPT_RECOVERY_V1';
const ATTEMPT_ENVELOPES_KEY = 'EE_EXAM_ATTEMPT_ENVELOPES_V1';
const ATTEMPT_ENVELOPE_SCHEMA = 'learning-attempts.v1';
const ATTEMPT_LIFECYCLE_STATES = ['active', 'committed', 'acknowledged'];
const successfulLearningAttempts = new Map();
const learningAttemptFingerprints = new Map();

function attemptLifecycleFailure(code, message) {
  return { ok: false, duplicate: false, code, message, status: null, sessionId: null, envelope: null };
}

function attemptNow(dependencies) {
  const candidate = dependencies && dependencies.now ? new Date(dependencies.now) : new Date();
  return Number.isNaN(candidate.getTime()) ? new Date() : candidate;
}

function attemptQidFamily(qid) {
  if (typeof qid !== 'string') return null;
  if (qid.startsWith('EE-')) return 'PE';
  if (qid.startsWith('GK-')) return 'GK';
  return null;
}

function readAttemptEnvelopeStore(storage) {
  let raw;
  try { raw = storage.getItem(ATTEMPT_ENVELOPES_KEY); }
  catch (_) { return { ok: false, code: 'attempt_store_read_failed', message: '無法讀取作答紀錄。', store: null }; }
  if (!raw) return { ok: true, store: { schemaVersion: ATTEMPT_ENVELOPE_SCHEMA, attempts: {} } };
  let store;
  try { store = JSON.parse(raw); } catch (_) {
    return { ok: false, code: 'attempt_store_invalid', message: '作答紀錄格式損壞，未寫入。', store: null };
  }
  if (!store || typeof store !== 'object' || Array.isArray(store)
      || store.schemaVersion !== ATTEMPT_ENVELOPE_SCHEMA
      || !store.attempts || typeof store.attempts !== 'object' || Array.isArray(store.attempts)) {
    return { ok: false, code: 'attempt_store_invalid', message: '作答紀錄版本或格式無效，未寫入。', store: null };
  }
  for (const [sessionId, envelope] of Object.entries(store.attempts)) {
    if (!envelope || typeof envelope !== 'object'
        || envelope.sessionId !== sessionId
        || !ATTEMPT_LIFECYCLE_STATES.includes(envelope.status)
        || !envelope.qid || !['PE', 'GK'].includes(envelope.examFamily)) {
      return { ok: false, code: 'attempt_store_invalid', message: `作答紀錄 ${sessionId} 無效，未寫入。`, store: null };
    }
  }
  return { ok: true, store };
}

function writeAttemptEnvelopeStore(storage, store) {
  try {
    storage.setItem(ATTEMPT_ENVELOPES_KEY, JSON.stringify(store));
    return { ok: true };
  } catch (_) {
    return { ok: false, code: 'attempt_store_write_failed', message: '作答紀錄無法保存。' };
  }
}

function attemptChecksum(value) {
  // A small deterministic integrity marker is sufficient for the local
  // recovery journal; it is not used as an authentication primitive.
  let hash = 2166136261;
  for (let index = 0; index < String(value).length; index += 1) {
    hash ^= String(value).charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }
  return (hash >>> 0).toString(16).padStart(8, '0');
}

function attemptJournalIsValid(journal) {
  if (journal.version !== 2) return true;
  if (!journal.operationId || !journal.payloadVersion || !journal.checksums) return false;
  return Object.entries(journal.afterByKey || {}).every(([key, value]) => journal.checksums[key] === attemptChecksum(value));
}

function beginOrResume(input, dependencies) {
  const payload = input || {};
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage || !recoverPendingLearningAttempt(storage)) return attemptLifecycleFailure('recovery_required', '先前寫入尚未恢復，已暫停新的作答。');
  const sessionId = payload.sessionId || payload.attemptId;
  const qid = payload.qid || (payload.question && payload.question.id);
  const examFamily = payload.examFamily || (payload.question && payload.question.examFamily);
  const sourceMode = payload.sourceMode || 'browse';
  const fingerprint = payload.fingerprint || null;
  if (!sessionId || !qid || !['PE', 'GK'].includes(examFamily)) return attemptLifecycleFailure('invalid_attempt', '作答 session、QID 或考試類別無效。');
  const qidFamily = attemptQidFamily(qid);
  if (qidFamily && qidFamily !== examFamily) return attemptLifecycleFailure('family_mismatch', 'QID 與考試類別不一致。');
  const loaded = readAttemptEnvelopeStore(storage);
  if (!loaded.ok) return attemptLifecycleFailure(loaded.code, loaded.message);
  const store = loaded.store;
  const existing = store.attempts[sessionId];
  if (existing) {
    if (existing.qid !== qid || existing.examFamily !== examFamily || existing.sourceMode !== sourceMode
        || (fingerprint && existing.fingerprint && existing.fingerprint !== fingerprint)) {
      return attemptLifecycleFailure('attempt_conflict', '同一 session 的作答識別或內容不一致。');
    }
    let resumed = existing;
    if (fingerprint && !existing.fingerprint) {
      resumed = Object.assign({}, existing, { fingerprint, updatedAt: attemptNow(dependencies).toISOString() });
      const saved = writeAttemptEnvelopeStore(storage, {
        schemaVersion: ATTEMPT_ENVELOPE_SCHEMA,
        attempts: Object.assign({}, store.attempts, { [sessionId]: resumed }),
      });
      if (!saved.ok) return attemptLifecycleFailure(saved.code, saved.message);
    }
    learningAttemptFingerprints.set(sessionId, resumed.fingerprint || fingerprint || null);
    return {
      ok: true,
      duplicate: true,
      code: 'ok',
      message: existing.status === 'active' ? '已恢復進行中的作答。' : '已恢復已提交的作答。',
      status: existing.status,
      sessionId,
      attemptId: sessionId,
      envelope: resumed,
    };
  }
  const now = attemptNow(dependencies).toISOString();
  const envelope = {
    schemaVersion: ATTEMPT_ENVELOPE_SCHEMA,
    sessionId,
    attemptId: sessionId,
    qid,
    examFamily,
    sourceMode,
    status: 'active',
    fingerprint,
    createdAt: now,
    updatedAt: now,
    committedAt: null,
    acknowledgedAt: null,
    result: null,
  };
  const nextStore = { schemaVersion: ATTEMPT_ENVELOPE_SCHEMA, attempts: Object.assign({}, store.attempts, { [sessionId]: envelope }) };
  const saved = writeAttemptEnvelopeStore(storage, nextStore);
  if (!saved.ok) return attemptLifecycleFailure(saved.code, saved.message);
  learningAttemptFingerprints.set(sessionId, fingerprint);
  return { ok: true, duplicate: false, code: 'ok', message: '已建立作答 session。', status: 'active', sessionId, attemptId: sessionId, envelope };
}

function findActiveAttempt(qid, examFamily, sourceMode, dependencies) {
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage || !qid || !['PE', 'GK'].includes(examFamily)) return null;
  if (!recoverPendingLearningAttempt(storage)) return null;
  const loaded = readAttemptEnvelopeStore(storage);
  if (!loaded.ok) return null;
  return Object.values(loaded.store.attempts)
    .filter(envelope => envelope.status === 'active' && envelope.qid === qid
      && envelope.examFamily === examFamily && envelope.sourceMode === sourceMode)
    .sort((left, right) => String(right.updatedAt).localeCompare(String(left.updatedAt)))[0] || null;
}

function ack(input, dependencies) {
  const payload = input || {};
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage || !recoverPendingLearningAttempt(storage)) return attemptLifecycleFailure('recovery_required', '先前寫入尚未恢復，無法確認作答。');
  const sessionId = payload.sessionId || payload.attemptId;
  if (!sessionId) return attemptLifecycleFailure('invalid_attempt', '缺少作答 session。');
  const loaded = readAttemptEnvelopeStore(storage);
  if (!loaded.ok) return attemptLifecycleFailure(loaded.code, loaded.message);
  const envelope = loaded.store.attempts[sessionId];
  if (!envelope) return attemptLifecycleFailure('attempt_not_found', '找不到作答 session。');
  if (payload.qid && payload.qid !== envelope.qid) return attemptLifecycleFailure('attempt_conflict', '確認的 QID 不一致。');
  if (payload.examFamily && payload.examFamily !== envelope.examFamily) return attemptLifecycleFailure('family_mismatch', '確認的考試類別不一致。');
  if (envelope.status === 'active') return attemptLifecycleFailure('not_committed', '作答結果尚未完成提交。');
  if (envelope.status === 'acknowledged') {
    return { ok: true, duplicate: true, code: 'ok', message: '作答確認已完成。', status: 'acknowledged', sessionId, envelope };
  }
  const now = attemptNow(dependencies).toISOString();
  const acknowledged = Object.assign({}, envelope, { status: 'acknowledged', acknowledgedAt: now, updatedAt: now });
  const nextStore = { schemaVersion: ATTEMPT_ENVELOPE_SCHEMA, attempts: Object.assign({}, loaded.store.attempts, { [sessionId]: acknowledged }) };
  const saved = writeAttemptEnvelopeStore(storage, nextStore);
  if (!saved.ok) return attemptLifecycleFailure(saved.code, saved.message);
  return { ok: true, duplicate: false, code: 'ok', message: '作答確認已完成。', status: 'acknowledged', sessionId, envelope: acknowledged };
}

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
  if (!journal || typeof journal !== 'object' || !journal.phase || !journal.beforeByKey || !journal.afterByKey
      || !attemptJournalIsValid(journal)) return false;
  if (journal.phase === 'committed') {
    try { storage.removeItem(ATTEMPT_RECOVERY_KEY); return true; } catch (_) { return false; }
  }
  // The envelope is written last.  Its committed marker is the durable
  // commit point, so a crash in the small window before the journal phase is
  // updated must keep the completed attempt rather than roll it back.
  if (journal.phase === 'pending' && journal.attemptId) {
    const loaded = readAttemptEnvelopeStore(storage);
    const envelope = loaded.ok && loaded.store.attempts[journal.attemptId];
    if (envelope && ['committed', 'acknowledged'].includes(envelope.status)) {
      try { storage.removeItem(ATTEMPT_RECOVERY_KEY); return true; } catch (_) { return false; }
    }
  }
  if (!['pending', 'recovery_required'].includes(journal.phase)) return false;
  return restoreLearningAttemptJournal(journal, storage);
}

function recover(dependencies) {
  const storage = dependencies && dependencies.storage ? dependencies.storage : (typeof localStorage !== 'undefined' ? localStorage : null);
  if (!storage) return { ok: false, code: 'storage_unavailable', message: '無法讀取作答恢復紀錄。', recovered: false };
  let raw;
  try { raw = storage.getItem(ATTEMPT_RECOVERY_KEY); } catch (_) {
    return { ok: false, code: 'recovery_read_failed', message: '無法讀取作答恢復紀錄。', recovered: false };
  }
  if (!raw) return { ok: true, code: 'clean', message: '沒有待恢復的作答。', recovered: false };
  let journal = null;
  try { journal = JSON.parse(raw); } catch (_) {
    return { ok: false, code: 'recovery_corrupt', message: '作答恢復紀錄損壞，請保留資料後人工處理。', recovered: false };
  }
  const ok = recoverPendingLearningAttempt(storage);
  return {
    ok,
    code: ok ? 'recovered' : 'recovery_required',
    message: ok ? '作答恢復完成。' : '作答恢復失敗，已暫停新的提交。',
    recovered: ok,
    attemptId: journal && journal.attemptId ? journal.attemptId : null,
    phase: journal && journal.phase ? journal.phase : null,
  };
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
  const fingerprint = learningAttemptFingerprint(payload);
  const lockedFingerprint = learningAttemptFingerprints.get(payload.attemptId);
  if (lockedFingerprint && lockedFingerprint !== fingerprint) return learningAttemptFailure('attempt_conflict', '同一次作答的內容不一致。');
  const now = attemptNow(dependencies);
  const lifecycle = beginOrResume({
    sessionId: payload.attemptId,
    qid: question.id,
    examFamily: question.examFamily,
    sourceMode: payload.sourceMode,
    fingerprint,
  }, { storage, now });
  if (!lifecycle.ok) return learningAttemptFailure(lifecycle.code, lifecycle.message);
  if (lifecycle.status !== 'active') {
    if (!lifecycle.envelope || !lifecycle.envelope.result) return learningAttemptFailure('attempt_store_invalid', '已提交作答缺少結果，未重複寫入。');
    return Object.assign({}, lifecycle.envelope.result, { duplicate: true, status: lifecycle.status });
  }
  if ((typeof recallStoreLoadError !== 'undefined' && recallStoreLoadError)
      || (payload.sourceMode !== 'daily-practice' && typeof sm2StoreLoadError !== 'undefined' && sm2StoreLoadError)) {
    return learningAttemptFailure('store_load_failed', '既有學習紀錄無法讀取，已保留原始資料並停止寫入。');
  }
  const prior = successfulLearningAttempts.get(payload.attemptId);
  if (prior) {
    if (prior.fingerprint !== fingerprint) return learningAttemptFailure('attempt_conflict', '同一次作答的內容不一致。');
    return Object.assign({}, prior.result, { duplicate: true });
  }

  const qid = question.id;
  const rating = Number(payload.rating);
  const achieved = rating === 5 ? 4 : rating === 3 ? 2 : 0;
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

  const result = {
    ok: true, duplicate: false, status: 'committed', attemptId: payload.attemptId,
    code: 'ok', message: '自評已儲存。',
    nextReviewDate: nextSM2All ? nextSM2All[qid].nextReviewDate : null,
    nextAction: payload.sourceMode === 'daily-practice'
      ? { type: 'advance-daily', category: dailyMeta.category, subjectId: dailyMeta.subjectId, total: dailyMeta.total, finished: dailyMeta.finished, results: dailyMeta.results }
      : { type: 'refresh-review' },
  };
  const storedEnvelopes = readAttemptEnvelopeStore(storage);
  if (!storedEnvelopes.ok || !storedEnvelopes.store.attempts[payload.attemptId]) {
    return learningAttemptFailure(storedEnvelopes.ok ? 'attempt_store_invalid' : storedEnvelopes.code, storedEnvelopes.ok ? '作答 session 已遺失，未寫入。' : storedEnvelopes.message);
  }
  const activeEnvelope = storedEnvelopes.store.attempts[payload.attemptId];
  const committedEnvelope = Object.assign({}, activeEnvelope, {
    status: 'committed',
    result,
    committedAt: now.toISOString(),
    updatedAt: now.toISOString(),
  });
  const nextEnvelopeStore = {
    schemaVersion: ATTEMPT_ENVELOPE_SCHEMA,
    attempts: Object.assign({}, storedEnvelopes.store.attempts, { [payload.attemptId]: committedEnvelope }),
  };
  // The envelope is written last in this journal.  Its committed state is the
  // durable boundary used by recovery to distinguish a redo from a replay.
  writes.push([ATTEMPT_ENVELOPES_KEY, JSON.stringify(nextEnvelopeStore)]);

  const beforeByKey = {};
  try { writes.forEach(([key]) => { beforeByKey[key] = storage.getItem(key); }); }
  catch (_) { return learningAttemptFailure('storage_read_failed', '無法讀取原始進度，未開始寫入。'); }
  const afterByKey = Object.fromEntries(writes);
  const journal = {
    version: 2,
    operationId: `attempt-commit-${payload.attemptId}-${now.getTime()}`,
    attemptId: payload.attemptId,
    fingerprint,
    phase: 'pending',
    payloadVersion: ATTEMPT_ENVELOPE_SCHEMA,
    beforeByKey,
    afterByKey,
    checksums: Object.fromEntries(Object.entries(afterByKey).map(([key, value]) => [key, attemptChecksum(value)])),
    writtenKeys: [],
    createdAt: now.toISOString(),
  };
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
  successfulLearningAttempts.set(payload.attemptId, { fingerprint, result });
  return result;
}

// Public lifecycle spelling used by the durable attempt contract.  The
// existing submitLearningAttempt name remains the UI compatibility entry.
function submit(input, dependencies) {
  return submitLearningAttempt(input, dependencies);
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
