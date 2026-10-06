// scripts/qa_guards.cjs - browser QA for the v1.3.5 guards: mock session restore, two-step 交卷／停筆／放棄, Esc, backup nudge.
// Needs a staged _site (npm run stage) and playwright (npm ci).
const path = require('node:path');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const { chromium } = require('playwright');

async function main() {
  const server = spawn('python3', ['-u', '-m', 'http.server', '0', '--bind', '127.0.0.1', '--directory', path.join(root, '_site')]);
  const url = await new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error('server timeout')), 10000);
    const onData = d => { const m = /port (\d+)/.exec(String(d)); if (m) { clearTimeout(t); resolve(`http://127.0.0.1:${m[1]}/`); } };
    server.stdout.on('data', onData); server.stderr.on('data', onData);
  });
  const browser = await chromium.launch({ headless: true });
  const results = [];
  const step = async (name, fn) => { try { await fn(); results.push('PASS ' + name); } catch (e) { results.push('FAIL ' + name + ' :: ' + (e && e.message)); } };
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(String(e)));
    await page.goto(url);
    await page.waitForSelector('#today-task-card');
    const ls = (k) => page.evaluate(k => localStorage.getItem(k), k);

    // --- today overlay: Esc, 停筆 confirm, 放棄 confirm ---------------------------------
    await step('overlay: start MOCK114-01 closed phase, primary focused', async () => {
      await page.evaluate(() => { todayTaskCommit(todayTaskStart(todayTaskRefresh(), Date.now(), 'MOCK114-01')); openTodayTaskOverlay(); });
      await page.waitForSelector('#today-task-overlay[style*="flex"]');
      const focused = await page.evaluate(() => document.activeElement && document.activeElement.className);
      assert.match(String(focused), /today-task-start/);
      assert.equal(await page.textContent('[data-today-act="next"]'), '停筆，開始核對');
    });
    await step('overlay: Escape closes without changing state', async () => {
      await page.keyboard.press('Escape');
      await page.waitForSelector('#today-task-overlay', { state: 'hidden' });
      const st = JSON.parse(await ls('EE_EXAM_TODAY_TASK_V1'));
      assert.equal(st.active.code, 'MOCK114-01');
    });
    await step('overlay: 停筆 needs two taps, 取消 reverts', async () => {
      await page.evaluate(() => openTodayTaskOverlay());
      await page.click('[data-today-act="next"]');
      assert.match(await page.textContent('[data-today-act="next"]'), /還有 \d+ 分鐘，確定停筆並開始核對/);
      await page.click('[data-today-act="cancel-confirm"]');
      assert.equal(await page.textContent('[data-today-act="next"]'), '停筆，開始核對');
      assert.equal(JSON.parse(await ls('EE_EXAM_TODAY_TASK_V1')).active.phaseIndex, 0);
    });
    await step('overlay: 放棄本次 needs two taps and auto-reverts after 3 s', async () => {
      await page.click('[data-today-act="abandon"]');
      assert.equal(await page.textContent('[data-today-act="abandon"]'), '確定放棄？會清掉這次進度');
      await page.waitForTimeout(3300);
      assert.equal(await page.textContent('[data-today-act="abandon"]'), '放棄本次');
      await page.click('[data-today-act="abandon"]');
      await page.click('[data-today-act="abandon"]');
      await page.waitForSelector('#today-task-overlay', { state: 'hidden' });
      assert.equal(JSON.parse(await ls('EE_EXAM_TODAY_TASK_V1')).active, null);
    });
    await step('overlay: 停筆 second tap advances to review phase', async () => {
      await page.evaluate(() => { todayTaskCommit(todayTaskStart(todayTaskRefresh(), Date.now(), 'MOCK114-01')); openTodayTaskOverlay(); });
      await page.click('[data-today-act="next"]');
      await page.click('[data-today-act="next"]');
      assert.equal(JSON.parse(await ls('EE_EXAM_TODAY_TASK_V1')).active.phaseIndex, 1);
      await page.evaluate(() => { todayTaskCommit(todayTaskAbandon(todayTaskRefresh())); closeTodayTaskOverlay(); });
    });

    // --- solution modal Esc protects a dirty docked card ---------------------------------
    await step('modal: Esc collapses dirty docked card, second Esc closes', async () => {
      await page.evaluate(() => {
        const r = findQuestionRecord('EE-114-01-1');
        openSolutionModal(null, r[6], 'EE-114-01-1', r[3], { mode: 'browse' });
        openResultCard({ qid: 'EE-114-01-1', source: 'today' });
      });
      await page.waitForSelector('#solution-modal.show');
      await page.click('[data-result-card-docked] .result-card-expand');
      await page.click('[data-result-card-docked] .result-card-mark');
      await page.keyboard.press('Escape');
      assert.ok(await page.$('#solution-modal.show'), 'modal should stay open');
      assert.ok(await page.$('[data-result-card-docked].is-collapsed'), 'card should be collapsed');
      await page.keyboard.press('Escape');
      await page.waitForSelector('#solution-modal.show', { state: 'detached' }).catch(() => {});
      assert.equal(await page.$('#solution-modal.show'), null);
    });
    await step('modal: Esc inside textarea is ignored', async () => {
      await page.evaluate(() => {
        const r = findQuestionRecord('EE-114-01-1');
        openSolutionModal(null, r[6], 'EE-114-01-1', r[3], { mode: 'browse' });
        openResultCard({ qid: 'EE-114-01-1', source: 'today' });
      });
      await page.click('[data-result-card-docked] .result-card-expand');
      await page.click('[data-result-card-docked] .result-card-note-toggle');
      await page.focus('[data-result-card-docked] .result-card-note-input');
      await page.keyboard.press('Escape');
      assert.ok(await page.$('#solution-modal.show'), 'modal should stay open');
      await page.evaluate(() => closeModal());
    });

    // --- mock exam: two-step submit, session restore, summary ----------------------------
    await step('mock: 交卷 two-step with 取消 and session persisted', async () => {
      await page.evaluate(() => switchTab('mock'));
      await page.click('[data-mock-pick="114:01"]');
      await page.waitForSelector('[data-mock-submit]');
      assert.ok(await page.$('.mock-q-cap'), 'time cap visible before submit');
      await page.click('[data-mock-submit]');
      assert.equal(await page.textContent('[data-mock-submit]'), '確定交卷？會顯示全部答案');
      await page.click('[data-mock-submit-cancel]');
      assert.equal(await page.textContent('[data-mock-submit]'), '交卷');
      assert.equal(JSON.parse(await ls('EE_EXAM_MOCK_SESSION_V1')).phase, 'paper');
      await page.click('[data-mock-submit]');
      await page.click('[data-mock-submit]');
      await page.waitForSelector('#mock-running-total');
      assert.equal(await page.$('.mock-q-cap'), null, 'time cap hidden in grading');
      const s = JSON.parse(await ls('EE_EXAM_MOCK_SESSION_V1'));
      assert.equal(s.phase, 'grading'); assert.match(s.mockId, /^114-01-\d+$/);
    });
    await step('mock: grade one question, reload, grading resumes with same mockId', async () => {
      const before = JSON.parse(await ls('EE_EXAM_MOCK_SESSION_V1')).mockId;
      const card = await page.$('[data-mock-card] .result-card');
      assert.ok(card, 'inline card mounted');
      const rows = await card.$$('.result-card-row');
      for (const row of rows) await (await row.$('.result-card-mark')).click();
      await (await card.$('.result-card-save')).click();
      await page.waitForTimeout(300);
      await page.reload();
      await page.waitForSelector('#today-task-card');
      await page.evaluate(() => switchTab('mock'));
      await page.waitForSelector('#mock-running-total');
      assert.equal(JSON.parse(await ls('EE_EXAM_MOCK_SESSION_V1')).mockId, before);
      const total = await page.textContent('#mock-running-total');
      assert.match(total, /已評 1／\d 題/);
      const cards = await page.$$('[data-mock-card] .result-card');
      assert.ok(cards.length >= 1, 'remaining cards mounted');
    });
    await step('mock: finish paper -> summary shows 下一份 + 下載備份', async () => {
      for (let i = 0; i < 10; i++) {
        const card = await page.$('[data-mock-card] .result-card');
        if (!card) break;
        for (const row of await card.$$('.result-card-row')) await (await row.$('.result-card-mark')).click();
        await (await card.$('.result-card-save')).click();
        await page.waitForTimeout(200);
      }
      await page.waitForSelector('.mock-summary');
      const next = await page.textContent('.mock-summary .mock-btn-primary');
      assert.match(next, /^下一份：(MOCK114|BLIND108)-\d+/);
      assert.ok(await page.$('.mock-summary button[onclick="backupDownloadNow()"]'), '下載備份 button');
      assert.match(await page.textContent('.mock-sync-notice'), /MOCK114-01/);
    });

    // --- backup nudge ----------------------------------------------------------------------
    await step('nudge: shows 還沒備份過 with data, 明天再說 hides it', async () => {
      await page.evaluate(() => switchTab('practice'));
      await page.evaluate(() => renderBackupNudge());
      assert.match(await page.textContent('#backup-nudge'), /還沒備份過/);
      await page.click('#backup-nudge .backup-nudge-later');
      assert.equal((await page.textContent('#backup-nudge')).trim(), '');
    });
    await step('nudge: 4 days since last backup -> 已 4 天沒備份; download clears it', async () => {
      await page.evaluate(() => {
        localStorage.removeItem('EE_EXAM_BACKUP_NUDGE_V1');
        const meta = JSON.parse(localStorage.getItem('EE_EXAM_BACKUP_META_V1') || '{}');
        meta.lastBackupAt = new Date(Date.now() - 4 * 86400000).toISOString();
        localStorage.setItem('EE_EXAM_BACKUP_META_V1', JSON.stringify(meta));
      });
      await page.reload();
      await page.waitForSelector('#today-task-card');
      assert.match(await page.textContent('#backup-nudge'), /已 4 天沒備份/);
      const dl = page.waitForEvent('download');
      await page.click('#backup-nudge .backup-nudge-btn:not(.backup-nudge-later)');
      await dl;
      assert.equal((await page.textContent('#backup-nudge')).trim(), '');
    });
    results.push(errors.length ? 'FAIL page errors: ' + errors.join(' | ') : 'PASS no page errors');
  } finally {
    await browser.close();
    server.kill();
  }
  console.log(results.join('\n'));
  if (results.some(r => r.startsWith('FAIL'))) process.exit(1);
}
main().catch(e => { console.error(e); process.exit(1); });
