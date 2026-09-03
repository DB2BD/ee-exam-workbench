// src/data/manualTopicLabels.js
//
// User-confirmed chapter labels recorded from the website review workflow.
// These are topic decisions only and are independent of the solution audit
// status: a question may retain its confirmed chapter after its derivation is
// promoted to ``verified``.

const MANUAL_TOPIC_LABEL_SEED = {
  'EE-113-02-2': { chapterId: 'el-bjt-bias-small-signal', source: 'user-confirmed' },
  'EE-113-04-4': { chapterId: 'emach-induction-motor-equiv', source: 'user-confirmed' },
  'EE-112-02-1': { chapterId: 'el-bjt-bias-small-signal', source: 'user-confirmed', secondaryTopicIds: ['el-active-filter'] },
  'EE-111-02-3': { chapterId: 'el-mosfet-bias-small-signal', source: 'user-confirmed' },
  'EE-111-02-4': { chapterId: 'el-feedback-stability', source: 'user-confirmed' },
  'EE-111-04-4': { chapterId: 'emach-synchronous-generator-round', source: 'user-confirmed' },
  'EE-111-06-1': { chapterId: 'dist-protection-coordination', source: 'user-confirmed' },
  'EE-111-06-2': { chapterId: 'dist-motor-installation', source: 'user-confirmed' },
  'EE-111-06-3': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed' },
  'EE-111-06-4': { chapterId: 'dist-motor-installation', source: 'user-confirmed' },
  'EE-110-06-5': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed', secondaryTopicIds: ['dist-motor-installation'] },
  'EE-108-06-2': { chapterId: 'dist-voltage-drop', source: 'user-confirmed' },
  'EE-109-02-3': { chapterId: 'el-pe-buck-boost', source: 'user-confirmed' },
  'EE-107-06-2': { chapterId: 'dist-voltage-drop', source: 'user-confirmed' },
  'EE-106-02-2': { chapterId: 'el-feedback-stability', source: 'user-confirmed', secondaryTopicIds: ['el-mosfet-bias-small-signal'] },
  'EE-106-06-2': { chapterId: 'dist-short-circuit-capacity', source: 'user-confirmed' },
  'EE-105-04-5': { chapterId: 'emach-dc-motor-generator', source: 'user-confirmed' },
  'EE-104-06-5': { chapterId: 'dist-harmonics-mitigation', source: 'user-confirmed', secondaryTopicIds: ['dist-power-factor-correction'] },
};
