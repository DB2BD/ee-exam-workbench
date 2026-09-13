// Real browser QA against staged assets; isolated storage, loopback only.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const root = path.resolve(__dirname, '..');
fs.mkdirSync(path.join(root, '.qa-artifacts'), { recursive: true });
const artifacts = fs.mkdtempSync(path.join(root, '.qa-artifacts', 'browser-'));

async function main() {
  assert(fs.existsSync(path.join(root, '_site/index.html')), 'Run python3 scripts/stage_pages_artifact.py first');
  const server = spawn(process.env.PYTHON || 'python3', ['-u', '-m', 'http.server', '0', '--bind', '127.0.0.1', '--directory', path.join(root, '_site')]);
  let browser;
  const results = [];
  try {
    const url = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('Local server startup timed out')), 10000);
      let output = '';
      let stderr = '';
      server.once('error', error => { clearTimeout(timer); reject(error); });
      server.once('exit', code => { clearTimeout(timer); reject(new Error(`Server exited: ${code}\n${stderr}`)); });
      server.stdout.on('data', chunk => {
        output += chunk;
        const match = output.match(/port (\d+)/);
        if (match) { clearTimeout(timer); resolve(`http://127.0.0.1:${match[1]}/`); }
      });
      server.stderr.on('data', chunk => { stderr = (stderr + chunk).slice(-4000); });
    });
    browser = await chromium.launch({ headless: !process.env.QA_HEADED });
    for (const [width, category] of [[1440, 'PE'], [390, 'PE'], [1440, 'GK'], [390, 'GK']]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      await context.addInitScript(() => { let seed = 42; Math.random = () => ((seed = (1664525 * seed + 1013904223) >>> 0) / 4294967296); });
      await context.tracing.start({ screenshots: true, snapshots: true });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      page.on('response', response => { if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`); });
      page.on('requestfailed', request => {
        const failure = request.failure()?.errorText || 'unknown network failure';
        // Navigation can cancel the preceding embedded PDF; it is not a missing asset.
        if (request.url().startsWith(url) && failure !== 'net::ERR_ABORTED') errors.push(`${failure} ${request.url()}`);
      });
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.goto(url);
        await page.locator('#daily-practice-category').selectOption(category);
        await page.locator('[onclick="dailyPracticeStart()"]').click();
        const seen = new Set();
        for (let index = 0; index < 3; index++) {
          assert.equal((await page.locator('.daily-practice-progress').innerText()).trim(), `${index + 1} / 3`);
          const qid = await page.locator('.daily-practice-question .qid').innerText();
          assert(!seen.has(qid), 'The round must contain three distinct questions');
          seen.add(qid);
          assert(await page.evaluate(({ category, qid }) => {
            const data = category === 'GK' ? NATIONAL_EXAMS_DATA : DB_DATA;
            const state = JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1'));
            return state.activeSession.category === category && data.questions.some(q => q[0] === qid);
          }, { category, qid }), 'The question and stored session must belong to the selected category');
          const crop = page.locator('.daily-practice-source-image');
          await crop.waitFor();
          await page.waitForFunction(() => { const img = document.querySelector('.daily-practice-source-image'); return img && img.complete && img.naturalWidth > 0; });
          assert.equal(await page.locator('[data-daily-open-solution="recall"]').count(), 1);
          await page.locator('[data-daily-open-solution="recall"]').click();
          await page.locator('#recall-step-box').waitFor();
          assert.equal(await page.locator('#recall-full-section').isVisible(), false);
          for (const layer of [1, 2, 3]) {
            await page.locator(`[onclick="revealRecallLayer(${layer})"]`).click();
            const hint = page.locator(`#recall-layer-${layer}`);
            await hint.waitFor({ state: 'visible' });
            assert((await hint.innerText()).trim().length > 8, 'The revealed hint must contain content');
            assert.equal(await page.evaluate(qid => JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).activeSession.revealLevelByQuestion[qid], qid), layer);
          }
          await page.locator('[onclick="revealRecallFull()"]').click();
          await page.locator('#recall-full-section').waitFor();
          assert((await page.locator('#recall-full-section').innerText()).trim().length > 20, 'The full solution must contain substantive text');
          await page.evaluate(() => document.fonts.ready);
          assert.equal(await page.locator('.katex-error').count(), 0);
          await page.locator('#recall-rating-bar .btn-sm2-5').click();
          await page.waitForFunction(() => !document.getElementById('solution-modal').classList.contains('show'));
          const state = await page.evaluate(() => JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')));
          assert(qid in state.completionByQuestion, 'Self-assessment must persist completion');
          if (index < 2) {
            assert.equal(state.activeSession.currentIndex, index + 1);
            await page.reload();
          }
        }
        await page.locator('.daily-practice-summary').waitFor();
        assert.deepEqual(errors, []);
        await page.screenshot({ path: path.join(artifacts, `summary-${category}-${width}.png`), fullPage: true });
        assert.equal(seen.size, 3);
        results.push({ width, category, questionIds: [...seen], passed: true });
        console.log(`PASS ${category} ${width}px: three questions, four layers, completion and reload`);
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, `failure-${category}-${width}.png`), fullPage: true }).catch(() => {});
        results.push({ width, category, passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.tracing.stop({ path: path.join(artifacts, `trace-${category}-${width}.zip`) });
        await context.close();
      }
    }
  } finally {
    if (browser) await browser.close();
    if (server.exitCode === null && server.pid) {
      const exited = once(server, 'exit');
      server.kill();
      const deadline = setTimeout(() => server.kill('SIGKILL'), 5000);
      try { await exited; } finally { clearTimeout(deadline); }
    }
    fs.writeFileSync(path.join(artifacts, 'result.json'), JSON.stringify(results, null, 2));
    console.log(`QA artifacts: ${artifacts}`);
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
