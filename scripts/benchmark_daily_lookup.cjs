// Compare every real PE/GK result and repeated lookup cost against a Git ref.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const { performance } = require('node:perf_hooks');
const root = path.resolve(__dirname, '..');
const ref = process.argv[2] || 'HEAD';
const file = 'src/components/dailyPractice.js';
const oldSource = execFileSync('git', ['show', `${ref}:${file}`], { cwd: root, encoding: 'utf8' });
const shared = ['dashboard-data.js', 'national-exams-data.js', 'src/domain/questionRecord.js']
  .map(name => fs.readFileSync(path.join(root, name), 'utf8')).join('\n');
function measure(source) {
  const context = vm.createContext({});
  vm.runInContext(shared + '\n' + source + `
    const cases = [...DB_DATA.questions.map(q => ['PE', q[0]]), ...NATIONAL_EXAMS_DATA.questions.map(q => ['GK', q[0]])];
    let conversions = 0;
    const originalConverter = toQuestionRecord;
    toQuestionRecord = (...args) => { conversions++; return originalConverter(...args); };
    function lookupAll() {
      return cases.map(([category, id]) => {
        dailyPracticeState = {activeSession: {category, currentIndex: 0, questionIds: [id]}};
        return dailyPracticeCurrentQuestion();
      });
    }
  `, context);
  const values = JSON.parse(vm.runInContext('JSON.stringify(lookupAll())', context));
  const conversions = vm.runInContext('conversions', context);
  for (let i = 0; i < 3; i++) vm.runInContext('lookupAll()', context);
  const timings = [];
  for (let i = 0; i < 7; i++) {
    const start = performance.now();
    vm.runInContext('for(let i=0;i<10;i++) lookupAll()', context);
    timings.push(performance.now() - start);
  }
  timings.sort((a, b) => a - b);
  return { values, conversions, medianMs: timings[3] };
}
const before = measure(oldSource);
const after = measure(fs.readFileSync(path.join(root, file), 'utf8'));
assert.deepEqual(after.values, before.values);
console.log(JSON.stringify({ ref, questions: after.values.length, equivalent: true,
  before: { conversions: before.conversions, medianMs: before.medianMs },
  after: { conversions: after.conversions, medianMs: after.medianMs },
  note: 'Median of seven batches of ten full-library lookups; microbenchmark, not page-load latency.'
}, null, 2));
