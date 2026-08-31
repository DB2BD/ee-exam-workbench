// src/data/manualTopicLabels.js
//
// User-confirmed chapter labels for the questions that were deliberately
// kept in the manual-review queue.  These are topic decisions only: the
// solution audit status remains ``needs_manual_review`` until the numerical
// derivation is independently verified.

const MANUAL_TOPIC_LABEL_SEED = {
  'EE-113-02-2': { chapterId: 'el-bjt-bias-small-signal', source: 'user-confirmed' },
  'EE-113-04-4': { chapterId: 'emach-induction-motor-equiv', source: 'user-confirmed' },
  'EE-112-02-1': { chapterId: 'el-bjt-bias-small-signal', source: 'user-confirmed' },
  'EE-111-02-3': { chapterId: 'el-mosfet-bias-small-signal', source: 'user-confirmed' },
  'EE-111-02-4': { chapterId: 'el-feedback-stability', source: 'user-confirmed' },
  'EE-111-04-4': { chapterId: 'emach-synchronous-generator-round', source: 'user-confirmed' },
  'EE-111-06-1': { chapterId: 'dist-protection-coordination', source: 'user-confirmed' },
  'EE-111-06-2': { chapterId: 'dist-motor-installation', source: 'user-confirmed' },
  'EE-111-06-3': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed' },
  'EE-111-06-4': { chapterId: 'dist-motor-installation', source: 'user-confirmed' },
  'EE-110-06-5': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed' },
  'EE-109-02-3': { chapterId: 'el-pe-buck-boost', source: 'user-confirmed' },
  'EE-108-06-2': { chapterId: 'dist-voltage-drop', source: 'user-confirmed' },
  'EE-107-06-2': { chapterId: 'dist-voltage-drop', source: 'user-confirmed' },
  'EE-106-02-2': { chapterId: 'el-feedback-stability', source: 'user-confirmed' },
  'EE-106-06-2': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed' },
  'EE-105-04-5': { chapterId: 'emach-dc-motor-generator', source: 'user-confirmed' },
  'EE-104-05-3': { chapterId: 'ps-three-phase-fault', source: 'user-confirmed' },
  'EE-104-06-5': { chapterId: 'dist-harmonics-mitigation', source: 'user-confirmed' },
};
