// src/domain/passingProbability.js
/**
 * Passing Probability Index (PPI) & Readiness Prediction Engine
 * ==============================================================
 * Scientifically estimates examinee's performance in Taiwan Professional Electrical
 * Engineer (PE) Examination (6 core subjects, 100 pts each, passing line: avg >= 60).
 *
 * Factors:
 * 1. Historical chapter frequency & difficulty weighting
 * 2. Active recall layer achievement (L1 ~ L4)
 * 3. SM-2 memory retention & overdue decay
 * 4. Dangerous single-subject bottleneck penalty (< 40 pts)
 * 5. High-ROI chapter improvement recommendations
 */

const PASSING_SCORE_THRESHOLD = 60.0;
const DANGER_SCORE_THRESHOLD = 40.0;

const SUBJECT_CONFIG_PE = {
  '01': { id: '01', name: '電路學', icon: '⚡', targetScore: 70 },
  '02': { id: '02', name: '電子學（含電力電子）', icon: '🔬', targetScore: 65 },
  '03': { id: '03', name: '工程數學', icon: '📐', targetScore: 60 },
  '04': { id: '04', name: '電機機械', icon: '⚙️', targetScore: 65 },
  '05': { id: '05', name: '電力系統', icon: '🏭', targetScore: 70 },
  '06': { id: '06', name: '工業配電', icon: '🔌', targetScore: 65 }
};

/**
 * Calculate effective mastery multiplier for a single question.
 */
function evaluateQuestionReadiness(qid, progressVal, sm2Item, recallItem, now = new Date()) {
  const p = Number(progressVal) || 0;
  let baseMastery = 0.08; // Base unstarted familiarity
  if (p === 1) baseMastery = 1.0;       // Mastered
  else if (p === 2) baseMastery = 0.35; // In review / wrong

  // Recall layer multiplier (Level 1 ~ 4)
  let recallMult = 0.75;
  if (recallItem && typeof recallItem.achievedLevel === 'number') {
    const lvl = recallItem.achievedLevel;
    if (lvl >= 4) recallMult = 1.0;
    else if (lvl === 3) recallMult = 0.85;
    else if (lvl === 2) recallMult = 0.65;
    else if (lvl === 1) recallMult = 0.45;
  }

  // SM-2 retention decay if overdue
  let retentionMult = 1.0;
  if (sm2Item && sm2Item.nextReviewDate) {
    const dueDate = new Date(sm2Item.nextReviewDate);
    const nowDate = new Date(now);
    const diffDays = Math.floor((nowDate - dueDate) / (1000 * 60 * 60 * 24));
    if (diffDays > 0) {
      // Memory decay over time: 5% per day overdue, minimum 0.4
      retentionMult = Math.max(0.4, 1.0 - diffDays * 0.05);
    }
  }

  return Math.min(1.0, Math.max(0.05, baseMastery * recallMult * retentionMult));
}

/**
 * Calculates projected score and metrics for a specific subject.
 */
function calculateSubjectReadiness(subjectId, questions, progressState = {}, sm2Store = {}, recallStore = {}, options = {}) {
  const now = options.now ? new Date(options.now) : new Date();
  const subjQuestions = (questions || []).filter(q => {
    const sid = Array.isArray(q) ? q[1] : (q && q.subjectId);
    return String(sid) === String(subjectId);
  });

  const totalQuestions = subjQuestions.length;
  if (totalQuestions === 0) {
    return {
      subjectId,
      totalQuestions: 0,
      masteredCount: 0,
      reviewCount: 0,
      estimatedScore: 25,
      effectiveMasteryRate: 0.1,
      isDanger: true,
      weakChapters: []
    };
  }

  let totalWeight = 0;
  let earnedScoreWeight = 0;
  let masteredCount = 0;
  let reviewCount = 0;
  const chapterBreakdown = {};

  subjQuestions.forEach(q => {
    const qid = Array.isArray(q) ? q[0] : q.id;
    const year = Number(Array.isArray(q) ? q[2] : q.year) || 104;
    const diff = Number(Array.isArray(q) ? q[8] : q.difficulty) || 3;
    const chapter = (q.taxonomy && q.taxonomy.primaryChapter) || (Array.isArray(q) ? (q[4] || '未分類') : '未分類');

    // Recency weight: recent 5 years (>= 110) have 1.3x weight
    const recencyWeight = year >= 110 ? 1.3 : 1.0;
    // Difficulty weight: Level 3 ~ 5 have higher discriminator in exam
    const diffWeight = 0.8 + (diff * 0.1);
    const qWeight = recencyWeight * diffWeight;

    const pVal = progressState[qid] || 0;
    if (pVal === 1) masteredCount++;
    else if (pVal === 2) reviewCount++;

    const sm2Item = sm2Store[qid] || null;
    const recallItem = recallStore[qid] || null;
    const readiness = evaluateQuestionReadiness(qid, pVal, sm2Item, recallItem, now);

    totalWeight += qWeight;
    earnedScoreWeight += qWeight * readiness;

    // Track chapter weaknesses
    if (!chapterBreakdown[chapter]) {
      chapterBreakdown[chapter] = { total: 0, mastered: 0, unmasteredQids: [] };
    }
    chapterBreakdown[chapter].total++;
    if (pVal === 1) {
      chapterBreakdown[chapter].mastered++;
    } else {
      chapterBreakdown[chapter].unmasteredQids.push(qid);
    }
  });

  const effectiveMastery = totalWeight > 0 ? (earnedScoreWeight / totalWeight) : 0;
  // Scaled score formula:
  // Base 20 pts (formula setup / basic recognition) + 78 pts scaled by effective mastery
  const rawScore = 20.0 + (78.0 * effectiveMastery);
  const estimatedScore = Math.min(96, Math.max(20, Math.round(rawScore * 10) / 10));
  const isDanger = estimatedScore < DANGER_SCORE_THRESHOLD;

  // Identify weak chapters
  const weakChapters = Object.entries(chapterBreakdown)
    .map(([chap, data]) => ({
      chapter: chap,
      total: data.total,
      mastered: data.mastered,
      masteryRate: data.total > 0 ? data.mastered / data.total : 0,
      gapCount: data.total - data.mastered,
      unmasteredQids: data.unmasteredQids
    }))
    .filter(c => c.gapCount > 0)
    .sort((a, b) => b.gapCount - a.gapCount);

  return {
    subjectId,
    totalQuestions,
    masteredCount,
    reviewCount,
    estimatedScore,
    effectiveMasteryRate: Math.round(effectiveMastery * 100) / 100,
    isDanger,
    weakChapters
  };
}

/**
 * Calculates overall Exam Readiness and Passing Probability Index (PPI).
 */
function calculateExamReadiness(questions, progressState = {}, sm2Store = {}, recallStore = {}, options = {}) {
  const family = options.examFamily || 'PE';
  const subjectsMap = SUBJECT_CONFIG_PE;
  const subjectIds = Object.keys(subjectsMap);

  const subjectResults = {};
  let totalScoreSum = 0;
  let minScore = 100;
  let dangerCount = 0;

  subjectIds.forEach(sid => {
    const res = calculateSubjectReadiness(sid, questions, progressState, sm2Store, recallStore, options);
    subjectResults[sid] = Object.assign({}, res, {
      name: subjectsMap[sid].name,
      icon: subjectsMap[sid].icon,
      targetScore: subjectsMap[sid].targetScore
    });
    totalScoreSum += res.estimatedScore;
    if (res.estimatedScore < minScore) minScore = res.estimatedScore;
    if (res.isDanger) dangerCount++;
  });

  const subjectCount = subjectIds.length;
  const projectedAverage = Math.round((totalScoreSum / subjectCount) * 10) / 10;

  // Logistic Passing Probability Model
  // Sigmoid center at 60.0 points
  const delta = projectedAverage - PASSING_SCORE_THRESHOLD;
  let baseProb = 1.0 / (1.0 + Math.exp(-0.22 * delta));

  // Single-subject fatal flaw penalty (if any subject < 40 pts, passing probability plummets)
  if (minScore < DANGER_SCORE_THRESHOLD) {
    const penaltyFactor = Math.max(0.2, (minScore - 15) / 25);
    baseProb *= penaltyFactor;
  }

  const passingProbability = Math.min(99, Math.max(3, Math.round(baseProb * 100)));

  // Tier classification
  let tier = 'danger';
  let tierLabel = '死穴待搶救';
  let tierColor = '#b85d58';
  if (passingProbability >= 80) {
    tier = 'top';
    tierLabel = '高機率金榜';
    tierColor = '#5f8d64';
  } else if (passingProbability >= 62) {
    tier = 'competitive';
    tierLabel = '穩健衝刺中';
    tierColor = '#4a7c8f';
  } else if (passingProbability >= 45) {
    tier = 'borderline';
    tierLabel = '拔河及格邊緣';
    tierColor = '#d49e35';
  }

  // Derive Top ROI Actionable Boosters
  const topRoiBoosters = deriveTopRoiBoosters(subjectResults);

  return {
    examFamily: family,
    projectedAverage,
    passingThreshold: PASSING_SCORE_THRESHOLD,
    passingProbability,
    tier,
    tierLabel,
    tierColor,
    minSubjectScore: minScore,
    dangerCount,
    subjectResults,
    topRoiBoosters
  };
}

/**
 * Derives the Top 3 High-ROI chapters that give the biggest jump in projected score.
 */
function deriveTopRoiBoosters(subjectResults, limit = 3) {
  const candidates = [];

  Object.values(subjectResults).forEach(subj => {
    (subj.weakChapters || []).forEach(chap => {
      if (chap.gapCount >= 2) {
        // Impact score: gap questions * subject weakness factor
        const subjUrgency = Math.max(1.0, (70.0 - subj.estimatedScore) / 10.0);
        const scoreGainPotential = Math.min(6.5, Math.round(chap.gapCount * 0.8 * subjUrgency * 10) / 10);
        candidates.push({
          subjectId: subj.subjectId,
          subjectName: subj.name,
          subjectIcon: subj.icon,
          chapter: chap.chapter,
          unmasteredCount: chap.gapCount,
          sampleQids: chap.unmasteredQids.slice(0, 3),
          projectedScoreGain: scoreGainPotential,
          recommendation: `攻克【${subj.name} · ${chap.chapter}】${chap.gapCount} 道核心題，預估拉升本科 +${scoreGainPotential} 分`
        });
      }
    });
  });

  candidates.sort((a, b) => b.projectedScoreGain - a.projectedScoreGain);
  return candidates.slice(0, limit);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    PASSING_SCORE_THRESHOLD,
    DANGER_SCORE_THRESHOLD,
    SUBJECT_CONFIG_PE,
    evaluateQuestionReadiness,
    calculateSubjectReadiness,
    calculateExamReadiness,
    deriveTopRoiBoosters
  };
}
