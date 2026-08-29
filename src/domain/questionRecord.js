// src/domain/questionRecord.js
/**
 * Stable named-field boundary for legacy PE/GK question tuples.
 *
 * The generated bundles remain positional for backwards compatibility, while
 * UI and future domain code can consume one explicit QuestionRecord shape.
 */

const QUESTION_SCHEMA_VERSION = '1.0.0';
const QUESTION_STATUSES = ['verified', 'in_progress', 'pending', 'ambiguous', 'unavailable'];

function toQuestionRecord(record, examFamily) {
  const family = examFamily || (String(record && record[0] || '').startsWith('GK-') ? 'GK' : 'PE');
  if (record && !Array.isArray(record)) {
    return Object.assign({
      schemaVersion: QUESTION_SCHEMA_VERSION,
      examFamily: family,
    }, record);
  }
  if (!Array.isArray(record) || record.length < 12) throw new Error('Invalid question tuple');
  const view = {
    schemaVersion: QUESTION_SCHEMA_VERSION,
    id: record[0],
    examFamily: family,
    subjectId: record[1],
    year: record[2],
    number: record[3],
    stem: record[4],
    tags: Array.isArray(record[5]) ? record[5] : [],
    solutionLink: record[6] || '',
    sourceLink: record[7] || '',
    difficulty: record[8],
    solutionStatus: record[9] || 'pending',
    formulaTags: Array.isArray(record[10]) ? record[10] : [],
    hasDedicatedSolution: !!record[11],
    taxonomy: {
      primaryChapter: record.primaryChapter || null,
      secondaryTopics: Array.isArray(record.secondaryTopics) ? record.secondaryTopics : [],
      confidence: typeof record.confidence === 'number' ? record.confidence : null,
    },
    provenance: {
      questionCrop: '',
      figureCrops: [],
      sourcePages: [],
      sourcePdfSha256: '',
    },
  };
  if (family === 'GK' || record.length >= 18) {
    view.categoryId = record[12] || family;
    view.relatedPEId = record[13] || '';
    view.provenance.questionCrop = record[14] || '';
    view.provenance.figureCrops = Array.isArray(record[15]) ? record[15] : [];
    view.provenance.sourcePages = Array.isArray(record[16]) ? record[16] : [];
    view.provenance.sourcePdfSha256 = record[17] || '';
  }
  return view;
}

function questionField(record, field, examFamily) {
  return toQuestionRecord(record, examFamily)[field];
}

function isValidQuestionStatus(status) {
  return QUESTION_STATUSES.includes(status);
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    QUESTION_SCHEMA_VERSION,
    QUESTION_STATUSES,
    toQuestionRecord,
    questionField,
    isValidQuestionStatus,
  };
}
