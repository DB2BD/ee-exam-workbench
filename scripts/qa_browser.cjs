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
    for (const [width, mode] of [[1440, 'weighted'], [390, 'weighted'], [1440, 'all'], [390, 'all']]) {
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
        // GK is no longer selectable in the daily-practice UI (PE only since v1.2); vary the 選題方式 mode instead.
        await page.locator('#daily-practice-mode').selectOption(mode);
        await page.locator('#home-action-start').click();
        const seen = new Set();
        const readJson = key => page.evaluate(k => JSON.parse(localStorage.getItem(k)), key);
        for (let index = 0; index < 3; index++) {
          await page.locator('.daily-practice-progress').waitFor();
          assert.equal((await page.locator('.daily-practice-progress').innerText()).trim(), `${index + 1} / 3`);
          const qid = await page.locator('.daily-practice-question .qid').innerText();
          assert(!seen.has(qid), 'The round must contain three distinct questions');
          seen.add(qid);
          assert(await page.evaluate(({ qid }) => {
            const state = JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1'));
            return state.activeSession.category === 'PE' && state.activeSession.questionIds[state.activeSession.currentIndex] === qid
              && DB_DATA.questions.some(q => q[0] === qid);
          }, { qid }), 'The question and stored session must belong to PE');
          await page.waitForFunction(() => { const img = document.querySelector('.daily-practice-source-image'); return img && img.complete && img.naturalWidth > 0; });
          // Starting a round / moving on opens the recall window by itself; after a reload it may be restored or closed.
          const modalOpen = () => page.evaluate(() => document.getElementById('solution-modal').classList.contains('show'));
          if (!(await modalOpen())) await page.locator('[data-daily-open-solution="recall"]').click();
          await page.locator('#recall-step-box').waitFor();
          assert.equal(await page.locator('#recall-full-section').isVisible(), false);
          for (const layer of [1, 2, 3]) {
            const hint = page.locator(`#recall-layer-${layer}`);
            if (!(await hint.isVisible())) await page.locator(`[onclick="revealRecallLayer(${layer})"]`).click();
            await hint.waitFor({ state: 'visible' });
            assert((await hint.innerText()).trim().length > 8, 'The revealed hint must contain content');
            assert.equal(await page.evaluate(qid => JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).activeSession.revealLevelByQuestion[qid], qid), layer);
          }
          if (index === 0) {
            // Reload mid-question (after hint 3): the session must resume on the same question.
            await page.reload();
            await page.locator('.daily-practice-progress').waitFor();
            assert.equal((await page.locator('.daily-practice-progress').innerText()).trim(), '1 / 3');
            assert.equal(await page.locator('.daily-practice-question .qid').innerText(), qid);
            if (!(await modalOpen())) await page.locator('[data-daily-open-solution="recall"]').click();
            await page.locator('#recall-step-box').waitFor();
            for (const layer of [1, 2, 3]) if (!(await page.locator(`#recall-layer-${layer}`).isVisible())) await page.locator(`[onclick="revealRecallLayer(${layer})"]`).click();
          }
          await page.locator('[onclick="revealRecallFull()"]').click();
          await page.locator('#recall-full-section').waitFor();
          assert((await page.locator('#recall-full-section').innerText()).trim().length > 20, 'The full solution must contain substantive text');
          await page.evaluate(() => document.fonts.ready);
          assert.equal(await page.locator('.katex-error').count(), 0);
          const card = page.locator('.result-card--docked');
          await card.waitFor();
          const expand = card.locator('.result-card-expand');
          if (await expand.isVisible()) await expand.click();
          const rows = await card.locator('.result-card-row').count();
          assert(rows > 0, 'The result card must list at least one part');
          for (let row = 0; row < rows; row++) await card.locator(`.result-card-mark[data-row="${row}"][data-mark="o"]`).click();
          await card.locator('.result-card-save').click();
          // Saving closes the window and, mid-round, immediately opens the next question's recall window.
          await page.waitForFunction(q => q in (JSON.parse(localStorage.getItem('EE_EXAM_DAILY_PRACTICE_V1')).completionByQuestion || {}), qid);
          const state = await readJson('EE_EXAM_DAILY_PRACTICE_V1');
          assert(qid in state.completionByQuestion, 'Result card save must persist completion');
          const cardStore = await readJson('EE_EXAM_RESULT_CARD_V1');
          assert(cardStore.records.some(r => r.qid === qid && r.parts.every(p => p.mark === 'o')), 'Result card record must persist');
          if (index < 2) {
            assert.equal(state.activeSession.currentIndex, index + 1);
            if (index === 1) await page.reload(); // reload between questions: resume at 3 / 3
          }
        }
        await page.locator('.daily-practice-summary').waitFor();
        assert.deepEqual(errors, []);
        await page.screenshot({ path: path.join(artifacts, `summary-${mode}-${width}.png`), fullPage: true });
        assert.equal(seen.size, 3);
        results.push({ width, mode, questionIds: [...seen], passed: true });
        console.log(`PASS PE/${mode} ${width}px: three questions, four stages, result card, completion, resume and summary`);
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, `failure-${mode}-${width}.png`), fullPage: true }).catch(() => {});
        results.push({ width, mode, passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.tracing.stop({ path: path.join(artifacts, `trace-${mode}-${width}.zip`) });
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
