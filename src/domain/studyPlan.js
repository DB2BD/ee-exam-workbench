// src/domain/studyPlan.js
/**
 * Study-plan tiers (主攻 / 基本分), practice weights and scoring factors.
 * Pure functions over the generated TARGET_ALLOCATION global
 * (src/data/targetAllocation.generated.js must load first).
 */

const TOTAL_TARGET = 375;
const PASS_LINE = 360;

function studyAllocation_() {
  return typeof TARGET_ALLOCATION !== 'undefined' ? TARGET_ALLOCATION : null;
}

function studyEntryFor_(qid) {
  const alloc = studyAllocation_();
  if (!alloc || typeof qid !== 'string' || qid.indexOf('EE-') !== 0) return null;
  return alloc.questionTiers[qid] || null;
}

function studyTierFor(qid) {
  const entry = studyEntryFor_(qid);
  return entry ? entry.tier : null;
}

function studyRoleFor(subjectId) {
  const alloc = studyAllocation_();
  const subject = alloc && alloc.subjects[String(subjectId)];
  return subject ? subject.role : null;
}

function targetFor(subjectId) {
  const alloc = studyAllocation_();
  const subject = alloc && alloc.subjects[String(subjectId)];
  return subject ? subject.target : null;
}

function practiceWeightFor(qid) {
  const entry = studyEntryFor_(qid);
  if (!entry) return 0;
  const role = studyRoleFor(entry.subject);
  if (entry.tier === 'main') {
    if (role === 'basic') return 2;
    return 3; // high-subject main, shared / combined main
  }
  if (role === 'high') return 1;
  if (role === 'combined') return 1;
  return 0.5; // basic subject, basic chapter
}

function scoreFactorFor(tier, mark) {
  const table = {
    main: { o: 1, tri: 0.5, x: 0 },
    basic: { o: 0.5, tri: 0.25, x: 0 }
  };
  const row = table[tier];
  if (!row || !(mark in row)) return 0;
  return row[mark];
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    TOTAL_TARGET, PASS_LINE, studyTierFor, studyRoleFor, targetFor,
    practiceWeightFor, scoreFactorFor
  };
}
