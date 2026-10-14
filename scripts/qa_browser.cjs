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
    // v1.3.7 作答時間帽: a closed-book phase 6 minutes in shows the notice, the 起手式 toggle survives the tick, 16 minutes turns it firm.
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.addInitScript(() => {
          if (!localStorage.getItem('EE_EXAM_TODAY_TASK_V1')) {
            localStorage.setItem('EE_EXAM_TODAY_TASK_V1', JSON.stringify({ completed: {}, active: { code: 'CORE-01', phaseIndex: 0, phaseStartedAt: Date.now() - 6 * 60000 } }));
          }
        });
        await page.goto(url);
        const cap = page.locator('#today-task-timecap');
        await cap.waitFor();
        assert(/已經 5 分鐘還沒下第一筆/.test(await cap.innerText()), 'Stage 1 notice text');
        const starter = cap.locator('[data-today-starter]').first();
        await starter.click();
        await page.locator('#today-task-timecap [data-today-starter-panel]').waitFor();
        await page.waitForTimeout(2300); // survive at least two 1-second ticks
        assert.equal(await page.locator('#today-task-timecap [data-today-starter-panel]').count(), 1, 'Revealed starter must survive the tick');
        assert.equal(await page.locator('#today-task-overlay [data-today-check]').count(), 0, 'Closed book must not offer the solution');
        await page.evaluate(() => { todayTaskState.active.phaseStartedAt -= 10 * 60000; });
        await page.waitForFunction(() => document.getElementById('today-task-timecap')?.classList.contains('today-task-timecap--stop'));
        assert(/卡超過 15 分鐘了/.test(await cap.innerText()), 'Stage 2 notice text');
        assert.equal(await page.locator('#today-task-timecap [data-today-starter-panel]').count(), 1, 'Panel stays open at stage 2');
        await starter.click();
        assert.equal(await page.locator('#today-task-timecap [data-today-starter-panel]').count(), 0, 'Second click hides the panel');
        const stop = page.locator('#today-task-overlay [data-today-act="next"]').first();
        await stop.click(); // more than 5 minutes remain: first tap arms the confirm
        await page.locator('#today-task-overlay [data-confirming="1"]').waitFor();
        await stop.click();
        assert.equal(await page.locator('#today-task-timecap').count(), 0, 'No notice once the phase moved on');
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'today-task-timecap', passed: true });
        console.log('PASS today-task time cap 390px: stage 1 notice, 起手式 toggle survives tick, stage 2, cleared after stop');
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, 'failure-timecap.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'today-task-timecap', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.3.8 動態 FOCUS: with result-card records in the 配電 anchor chapters, starting FOCUS-01 picks 例題＋新題 by
    // src/domain/anchorSelection.js; the overlay shows exactly those two and the 核對 phase result card lists only the 新題.
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.goto(url);
        const chapters = ['dist-short-circuit-capacity', 'dist-load-characteristics'];
        // Seed 2 non-legacy records per anchor chapter (一個 × 觀念錯、一個 △ 計算錯), 3–6 days old (past the 2-day cooldown).
        const seeded = await page.evaluate(chapters => {
          const day = 86400000;
          const now = Date.now();
          const chapterOf = qid => {
            const evidence = QUESTION_TAXONOMY_MAP[qid];
            return typeof evidence === 'string' ? evidence : (evidence && evidence.primaryChapter) || '';
          };
          const out = [];
          chapters.forEach((chapter, c) => {
            const qids = DB_DATA.questions.map(q => q[0])
              .filter(q => /^EE-\d{3}-06-\d+$/.test(q) && !/^EE-(114|108)-/.test(q) && chapterOf(q) === chapter).slice(0, 2);
            qids.forEach((qid, i) => {
              const mark = i === 0 ? 'x' : 'tri';
              const parts = buildResultModel(qid).parts.map(p => Object.assign({}, p, { mark }));
              const saved = saveResultRecord({ qid, at: now - (3 + c * 2 + i) * day, source: 'today', parts, errors: [i === 0 ? 'K' : 'C'] }, { skipSM2: true });
              if (saved.ok) out.push(qid);
            });
          });
          return out;
        }, chapters);
        assert(seeded.length >= 3, 'Seeding must leave at least three result-card records in the anchor chapters');
        assert.equal(await page.evaluate(() => todayTaskStartCodeNow('FOCUS-01')), true, 'FOCUS-01 must start');
        const readActive = () => page.evaluate(() => JSON.parse(localStorage.getItem('EE_EXAM_TODAY_TASK_V1')).active);
        const active = await readActive();
        assert.equal(active.code, 'FOCUS-01');
        assert.equal(active.phaseIndex, 0);
        assert(Array.isArray(active.qids) && active.qids.length === 2 && active.qids[0] !== active.qids[1], 'Dynamic pick must store two distinct qids');
        assert(active.qids.every(q => /^EE-\d{3}-06-\d+$/.test(q)), '配電 round must pick 配電 questions');
        assert.deepEqual(active.scoredQids, [active.qids[1]], 'Only the 新題 is scored');
        assert(chapters.includes(active.chapter), `Picked chapter ${active.chapter} must be one of the seeded anchor chapters`);
        const meta = await page.evaluate(({ qids, chapter }) => {
          const chapterOf = qid => { const e = QUESTION_TAXONOMY_MAP[qid]; return typeof e === 'string' ? e : (e && e.primaryChapter) || ''; };
          return { chapters: qids.map(chapterOf), name: KNOWLEDGE_DAG[chapter].name };
        }, active);
        assert.deepEqual(meta.chapters, [active.chapter, active.chapter], '例題 and 新題 belong to the picked chapter');
        const [example, fresh] = active.qids;
        await page.locator('#today-task-overlay').waitFor();
        assert((await page.locator('#today-task-overlay .today-task-eyebrow').first().innerText()).includes(`弱章專攻｜工業配電／${meta.name}`), 'Overlay title names the picked chapter');
        const checks = page.locator('#today-task-overlay [data-today-check]');
        assert.equal(await checks.count(), 1, 'Phase 1 opens only the example solution');
        assert.equal(await checks.first().getAttribute('data-today-check'), example);
        // A reload keeps the same two questions.
        await page.reload();
        await page.locator('#today-task-overlay [data-today-check]').first().waitFor();
        assert.deepEqual((await readActive()).qids, active.qids, 'Reload keeps the dynamic pick');
        assert.equal(await page.locator('#today-task-overlay [data-today-check]').first().getAttribute('data-today-check'), example);
        const nextPhase = async toIndex => {
          const button = page.locator('#today-task-overlay [data-today-act="next"]').first();
          await button.click();
          if (await page.locator('#today-task-overlay [data-confirming="1"]').count()) await page.locator('#today-task-overlay [data-today-act="next"]').first().click();
          await page.waitForFunction(i => JSON.parse(localStorage.getItem('EE_EXAM_TODAY_TASK_V1')).active.phaseIndex === i, toIndex);
        };
        await nextPhase(1);
        await nextPhase(2);
        assert.equal(await page.locator('#today-task-overlay [data-today-check]').count(), 0, 'Closed-book phases offer no solution');
        assert.deepEqual((await readActive()).qids, active.qids, 'The pick survives phase changes');
        await nextPhase(3);
        const chips = page.locator('#today-task-result-chips button');
        await chips.first().waitFor();
        assert.equal(await chips.count(), 1, '核對 phase result card lists only the 新題');
        assert((await chips.first().innerText()).includes(fresh), 'The listed result card is the 新題');
        assert(!(await page.locator('#today-task-overlay').innerText()).includes(`還有 2 題未處理`), 'Example is not asked for a result card');
        assert((await page.locator('#today-task-result-title').innerText()).includes(fresh), 'Result card title names the 新題');
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'focus-dynamic-pick', passed: true, pick: active });
        console.log('PASS dynamic FOCUS-01 390px: two picked questions, chapter title, reload keeps pick, result card lists only the new question');
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, 'failure-focus-dynamic.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'focus-dynamic-pick', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.3.9 日程進度: completed up to CORE-20 on 10/14 -> the 成績 tab lists CORE-21～23 and FOCUS-01 as behind, plus the next milestone.
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.clock.setFixedTime(new Date(2026, 9, 14, 9, 0, 0));
        await page.addInitScript(() => {
          const completed = {};
          for (let n = 1; n <= 20; n++) completed['CORE-' + String(n).padStart(2, '0')] = new Date(2026, 9, 12, 20, n).toISOString();
          localStorage.setItem('EE_EXAM_TODAY_TASK_V1', JSON.stringify({ completed, active: null }));
        });
        await page.goto(url);
        await page.locator('#tab-btn-scoreboard').click();
        const pace = page.locator('#scoreboard-container .sb-pace');
        await pace.waitFor();
        assert.equal((await pace.getAttribute('aria-label')), '日程進度');
        const rows = pace.locator(':scope > .sb-pace-table tbody tr');
        assert.equal(await rows.count(), 4, '落後項目 lists exactly four rows');
        const codes = await rows.locator('.sb-pace-code').allInnerTexts();
        assert.deepEqual(codes, ['CORE-21', 'CORE-22', 'CORE-23', 'FOCUS-01']);
        assert.deepEqual(await rows.locator('td.sb-pace-num:nth-child(3)').allInnerTexts(), ['10/12', '10/12', '10/13', '10/13']);
        assert(/^落後約 \d+(\.\d+)? 小時（4 項未按日程完成）$/.test((await pace.locator('.sb-pace-line').innerText()).trim()), 'Status line');
        assert(/^下一關卡 10\/17 核心收尾關卡：剩 \d+ 項，需 [\d.]+ 小時／可用 [\d.]+ 小時$/.test((await pace.locator('.sb-pace-next').innerText()).trim()), 'Next milestone line');
        assert.equal(await pace.locator('details.sb-pace-cut').getAttribute('open'), null, '已自動刪減 starts collapsed');
        const overflow = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
        assert(overflow.scroll <= overflow.client, `No horizontal scroll at 390px (${overflow.scroll} > ${overflow.client})`);
        await pace.screenshot({ path: path.join(artifacts, 'scoreboard-pace-390.png') });
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'scoreboard-pace', passed: true, codes });
        console.log('PASS scoreboard 日程進度 390px: four behind rows, next milestone, no horizontal scroll');
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, 'failure-scoreboard-pace.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'scoreboard-pace', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.3.10 自動快照: seeded data -> one 每日 snapshot -> import (scoreboard redraws, 匯入前 snapshot) -> two-tap 還原 brings the data back.
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        const openModal = async () => {
          await page.evaluate(() => openBackupModal());
          await page.locator('#snapshot-list').waitFor();
        };
        const rowCount = () => page.locator('#snapshot-list .snapshot-row').count();
        const closeModal = () => page.evaluate(() => closeBackupModal());
        const snapshotTotal = () => page.evaluate(() => snapshotListMeta().then(list => list.length));
        const waitForSnapshots = async count => {
          const deadline = Date.now() + 15000;
          while (Date.now() < deadline) {
            if (await snapshotTotal() === count) return;
            await page.waitForTimeout(150);
          }
          throw new Error(`Expected ${count} snapshots, found ${await snapshotTotal()}`);
        };
        const resultCardCount = () => page.evaluate(() => JSON.parse(localStorage.getItem('EE_EXAM_RESULT_CARD_V1')).records.length);
        // 1. Brand-new browser: empty data takes no snapshot.
        await page.goto(url);
        await page.waitForTimeout(1200);
        await openModal();
        assert.equal((await page.locator('#snapshot-list').innerText()).trim(), '尚無快照', 'Empty data must not create a snapshot');
        await closeModal();
        // 2. Seed result cards and two scheduled completions, reload: exactly one 每日 snapshot appears.
        const seeded = await page.evaluate(() => {
          const qids = DB_DATA.questions.map(q => q[0]).filter(q => /^EE-\d{3}-01-\d+$/.test(q)).slice(0, 4);
          qids.forEach(qid => {
            const parts = buildResultModel(qid).parts.map(p => Object.assign({}, p, { mark: 'o' }));
            saveResultRecord({ qid, at: Date.now() - 86400000, source: 'today', parts, errors: [] }, { skipSM2: true });
          });
          const completed = {};
          ['CORE-01', 'CORE-02'].forEach(code => { completed[code] = new Date().toISOString(); });
          localStorage.setItem('EE_EXAM_TODAY_TASK_V1', JSON.stringify({ completed, active: null }));
          return qids.length;
        });
        assert.equal(seeded, 4);
        await page.reload();
        await waitForSnapshots(1);
        await openModal();
        await page.locator('#snapshot-list .snapshot-row').first().waitFor();
        assert.equal(await rowCount(), 1, 'One snapshot after the reload');
        const first = (await page.locator('#snapshot-list .snapshot-row').first().innerText()).replace(/\s+/g, ' ');
        assert(first.includes('每日') && first.includes('結果卡 4 筆・已完成 2 項') && first.includes('還原'), `Row text: ${first}`);
        await closeModal();
        // Opening the app again the same day does not add another 每日 snapshot.
        await page.reload();
        await page.waitForTimeout(1200);
        await openModal();
        assert.equal(await rowCount(), 1, 'Only one daily snapshot per day');
        await closeModal();
        // 3. Import a backup with no result cards while the 成績 tab is open: the scoreboard redraws and a 匯入前 snapshot appears.
        await page.locator('#tab-btn-scoreboard').click();
        const emptyText = await page.evaluate(() => SCOREBOARD_EMPTY_TEXT);
        assert(!(await page.locator('#scoreboard-container').innerText()).includes(emptyText), 'Scoreboard shows data before the import');
        await openModal();
        await page.evaluate(() => {
          const backup = JSON.parse(exportAllUserDataJSON());
          backup.resultCard = { version: 1, records: [] };
          document.getElementById('backup-json-textarea').value = JSON.stringify(backup);
        });
        await page.evaluate(() => applyImportedBackupJSON('replace'));
        await page.waitForFunction(text => document.getElementById('scoreboard-container').innerText.includes(text), emptyText);
        await waitForSnapshots(2);
        // 4. The 還原 button is two-tap and disarms by itself after 3 seconds.
        await openModal();
        await page.waitForFunction(() => document.querySelectorAll('#snapshot-list .snapshot-row').length === 2);
        const dailyRow = page.locator('#snapshot-list .snapshot-row', { hasText: '每日' });
        const importRow = page.locator('#snapshot-list .snapshot-row', { hasText: '匯入前' });
        assert((await importRow.innerText()).includes('結果卡 4 筆・已完成 2 項'), '匯入前 snapshot holds the pre-import data');
        assert((await dailyRow.innerText()).includes('結果卡 4 筆'), 'Daily snapshot keeps its counts');
        assert.equal(await resultCardCount(), 0, 'Result cards are gone after the import');
        const restoreBtn = dailyRow.locator('.snapshot-restore');
        await restoreBtn.click();
        assert.equal((await restoreBtn.innerText()).trim(), '再按一次確認還原');
        await page.waitForTimeout(3300);
        assert.equal((await restoreBtn.innerText()).trim(), '還原', 'Auto-disarmed after 3 seconds');
        assert.equal(await resultCardCount(), 0, 'One tap alone restores nothing');
        await page.screenshot({ path: path.join(artifacts, 'snapshot-390.png') });
        // 5. Two taps restore, then the page reloads with the result cards back and a 還原前 snapshot kept.
        await restoreBtn.click();
        await Promise.all([page.waitForNavigation({ waitUntil: 'load' }), restoreBtn.click()]);
        assert.equal(await resultCardCount(), 4, 'Result cards restored');
        assert.deepEqual(await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('EE_EXAM_TODAY_TASK_V1')).completed).sort()), ['CORE-01', 'CORE-02']);
        await page.waitForTimeout(800);
        await openModal();
        await page.waitForFunction(() => document.querySelectorAll('#snapshot-list .snapshot-row').length === 3);
        const kinds = (await page.locator('#snapshot-list .snapshot-kind').allInnerTexts()).sort();
        assert.deepEqual(kinds, ['每日', '匯入前', '還原前'].sort());
        const overflow = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
        assert(overflow.scroll <= overflow.client, `No horizontal scroll at 390px (${overflow.scroll} > ${overflow.client})`);
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'auto-snapshot', passed: true, kinds });
        console.log('PASS auto snapshot 390px: empty data skipped, one daily snapshot, import redraws scoreboard, two-tap restore brings data back');
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, 'failure-auto-snapshot.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'auto-snapshot', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.3.10 多分頁同步: a change saved in tab A reaches tab B through the storage event (today task card, SM-2, recall).
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 900 } });
      const pageA = await context.newPage();
      const pageB = await context.newPage();
      const errors = [];
      [pageA, pageB].forEach(p => p.on('pageerror', error => errors.push(String(error))));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      [pageA, pageB].forEach(p => p.setDefaultTimeout(15000));
      try {
        await pageA.goto(url);
        await pageB.goto(url);
        await pageA.locator('#today-task-card .today-task-card').waitFor();
        await pageB.locator('#today-task-card .today-task-card').waitFor();
        const cardText = p => p.locator('#today-task-card').innerText();
        const before = await cardText(pageB);
        // Tab A finishes the current task through the app's own state functions (saved to storage + card redrawn).
        await pageA.evaluate(() => {
          const next = todayTaskStart(todayTaskState, Date.now());
          const done = Object.assign({}, next.completed);
          done[next.active.code] = new Date().toISOString();
          todayTaskCommit({ completed: done, active: null });
          renderTodayTaskCard();
        });
        const expected = await cardText(pageA);
        assert.notEqual(expected, before, 'Tab A card changes after completing the task');
        await pageB.waitForFunction(text => document.getElementById('today-task-card').innerText === text, expected);
        assert.equal(await pageB.evaluate(() => Object.keys(todayTaskState.completed).length), 1, 'Tab B holds the completion in memory too');
        // SM-2 and recall: written by tab A, reloaded into tab B's memory.
        const qid = await pageA.evaluate(() => DB_DATA.questions[0][0]);
        await pageA.evaluate(qid => {
          localStorage.setItem('EE_EXAM_SM2_SCHEDULE_V1', JSON.stringify({ [qid]: { repetitions: 1, interval: 4, easeFactor: 2.5, lastReviewed: '2026-10-12', nextReviewDate: '2026-10-16' } }));
          localStorage.setItem('EE_EXAM_RECALL_V1', JSON.stringify({ [qid]: { level: 2, streak: 1, attempts: 2, lastAchieved: 2, lastErrorType: null, lastReviewed: '2026-10-12T00:00:00.000Z' } }));
        }, qid);
        await pageB.waitForFunction(q => !!sm2Schedule[q] && !!recallState[q], qid);
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'cross-tab-sync', passed: true });
        console.log('PASS cross-tab sync: today task card, SM-2 and recall follow the other tab');
      } catch (error) {
        await pageB.screenshot({ path: path.join(artifacts, 'failure-cross-tab.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'cross-tab-sync', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.4.0 首頁像素風狀態視窗: seeded stores -> window numbers match the stores, collapsible, never covers 今日任務, no horizontal scroll,
    // light and dark readable, reduced motion shows the final state; screenshots at 1440 and 390 (QA_HOME_STATUS_SHOT_DIR overrides the folder).
    for (const width of [1440, 390]) {
      const context = await browser.newContext({ viewport: { width, height: width > 600 ? 900 : 844 } });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.clock.setFixedTime(new Date(2026, 9, 14, 9, 0, 0));
        await page.addInitScript(() => {
          if (localStorage.getItem('EE_EXAM_TODAY_TASK_V1')) return;
          const completed = {};
          for (let n = 1; n <= 21; n++) completed['CORE-' + String(n).padStart(2, '0')] = new Date(2026, 9, 14 - Math.floor((21 - n) / 4), 20, n).toISOString();
          localStorage.setItem('EE_EXAM_TODAY_TASK_V1', JSON.stringify({ completed, active: null }));
        });
        await page.goto(url);
        const seeded = await page.evaluate(() => {
          const qids = DB_DATA.questions.map(q => q[0]);
          let count = 0;
          ['01', '02', '04', '05', '06'].forEach((sub, si) => {
            qids.filter(q => q.split('-')[2] === sub).slice(0, 14).forEach((qid, i) => {
              const mark = (i + si) % 4 === 0 ? 'x' : ((i + si) % 3 === 0 ? 'tri' : 'o');
              const parts = buildResultModel(qid).parts.map(p => Object.assign({}, p, { mark }));
              if (saveResultRecord({ qid, at: Date.now() - (i % 9) * 86400000 - 3600000, source: 'today', parts, errors: [] }, { skipSM2: true }).ok) count += 1;
            });
          });
          return count;
        });
        assert.equal(seeded, 70, 'Seeded result cards');
        await page.reload();
        const host = page.locator('#home-status');
        await host.locator('.hs-frame').waitFor();
        assert(await host.evaluate(el => el.classList.contains('hs--intro')), 'The first draw plays the typing intro');
        await page.waitForFunction(() => !document.getElementById('home-status').classList.contains('hs--intro'), null, { timeout: 12000 });
        const label = sel => host.locator(sel + ' .hs-num').first().getAttribute('aria-label');
        // numbers come from the stores
        const expected = await page.evaluate(() => {
          const m = homeStatusModel(homeStatusInputs(Date.now()));
          const cardExp = getResultRecords().reduce((n, r) => n + homeStatusCardExp(r), 0);
          return { level: m.level, title: m.title, exp: m.exp, cardExp, streak: m.streak.days, cards: JSON.parse(localStorage.getItem('EE_EXAM_RESULT_CARD_V1')).records.length, score: m.score };
        });
        assert.equal(expected.cards, 70);
        assert.equal(await label('[data-hs="level"]'), String(expected.level));
        assert.equal(await label('[data-hs="exam"]'), '31', '2026-10-14 -> 2026-11-14 is 31 days');
        assert.equal(await label('[data-hs="tasks"]'), '21／67');
        assert.equal(await label('[data-hs="cards"]'), '70');
        assert.equal(await label('[data-hs="streak"]'), String(expected.streak));
        assert(expected.streak >= 1, 'Streak counts today');
        assert.equal(expected.exp.total, 21 * 100 + expected.cardExp, 'EXP = 100 per task + card EXP');
        assert.equal((await host.locator('[data-hs="title"]').innerText()).trim(), expected.title);
        assert(expected.score.hasData, 'Seeded result cards give a score estimate');
        assert.equal(await label('[data-hs="score"]'), `${expected.score.total}／${expected.score.target}`);
        assert.equal(await host.locator('.hs-attr').count(), 6, 'Six subject attributes');
        assert.deepEqual(await host.locator('.hs-attr-k').allInnerTexts(), ['電路', '電子', '工數', '電機', '電力', '配電']);
        // the header one-liner and the window agree
        assert((await page.locator('#header-summary-line').innerText()).includes(`估計總分 ${expected.score.total}／${expected.score.target}`));
        // collapsible: phones start collapsed, desktop expanded; the toggle flips it and keeps aria in sync
        const toggle = page.locator('#hs-toggle');
        const startsCollapsed = width < 641;
        assert.equal(await toggle.getAttribute('aria-expanded'), startsCollapsed ? 'false' : 'true');
        const bodyVisible = () => page.locator('#hs-body').isVisible();
        assert.equal(await bodyVisible(), !startsCollapsed);
        const noOverflow = async what => {
          const o = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth }));
          assert(o.scroll <= o.client, `No horizontal scroll ${what} at ${width}px (${o.scroll} > ${o.client})`);
        };
        await noOverflow('(initial)');
        await toggle.click();
        assert.equal(await toggle.getAttribute('aria-expanded'), startsCollapsed ? 'true' : 'false');
        assert.equal(await bodyVisible(), startsCollapsed);
        await noOverflow('(toggled)');
        if (!startsCollapsed) await toggle.click(); // desktop: back to expanded
        assert.equal(await bodyVisible(), true);
        // 今日任務 card and the three tabs are outside the window and stay visible, below the header
        const header = await page.locator('header.hs-header').boundingBox();
        const taskCard = page.locator('#today-task-card .today-task-card');
        await taskCard.waitFor();
        const taskBox = await taskCard.boundingBox();
        assert(taskBox.y >= header.y + header.height - 1, '今日任務 card sits below the header, not under the window');
        assert(taskBox.y < (width > 600 ? 900 : 844), '今日任務 card is on the first screen');
        for (const id of ['practice', 'mock', 'scoreboard']) assert(await page.locator('#tab-btn-' + id).isVisible(), `Tab ${id} stays visible`);
        assert.equal(await page.locator('#home-action-start').count(), 1, 'Random-practice entry stays');
        // the window follows new data: one more result card raises the count
        const before = await label('[data-hs="cards"]');
        await page.evaluate(() => {
          const qid = DB_DATA.questions.map(q => q[0]).filter(q => /^EE-\d{3}-03-\d+$/.test(q))[0];
          const parts = buildResultModel(qid).parts.map(p => Object.assign({}, p, { mark: 'o' }));
          saveResultRecord({ qid, at: Date.now(), source: 'today', parts, errors: [] }, { skipSM2: true });
        });
        await page.waitForFunction(n => document.querySelector('#home-status [data-hs="cards"] .hs-num').getAttribute('aria-label') === String(Number(n) + 1), before);
        // light and dark: the label text keeps >= 4.5:1 against the panel
        const contrast = () => page.evaluate(() => {
          const parse = c => { const m = c.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1 }; };
          const lum = ({ r, g, b }) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
          const panel = parse(getComputedStyle(document.querySelector('.hs-inner')).backgroundColor);
          const base = { r: 20, g: 28, b: 52 }; // worst-case scene colour under the 0.9 panel
          const bg = { r: panel.r * panel.a + base.r * (1 - panel.a), g: panel.g * panel.a + base.g * (1 - panel.a), b: panel.b * panel.a + base.b * (1 - panel.a) };
          const out = {};
          ['.hs-k', '.hs-attr-k', '.hs-title', '.hs-exp-num', '.hs-toggle', '.hs-v small'].forEach(sel => {
            const el = document.querySelector('#home-status ' + sel);
            const fg = parse(getComputedStyle(el).color);
            const [hi, lo] = [lum(fg), lum(bg)].sort((a, b) => b - a);
            out[sel] = (hi + 0.05) / (lo + 0.05);
          });
          return out;
        });
        for (const theme of ['dark', 'light']) {
          await page.evaluate(t => document.documentElement.setAttribute('data-theme', t), theme);
          const ratios = await contrast();
          Object.keys(ratios).forEach(sel => assert(ratios[sel] >= 4.5, `${sel} contrast ${ratios[sel].toFixed(2)} in ${theme}`));
          await noOverflow(`(${theme})`);
        }
        await page.evaluate(() => document.documentElement.setAttribute('data-theme', 'dark'));
        // screenshots: the window expanded under the scene (390 shows the strip above it)
        if ((await toggle.getAttribute('aria-expanded')) === 'false') await toggle.click();
        await page.waitForFunction(() => document.querySelector('#home-status .hs-body') && !document.querySelector('#home-status .hs-body').hidden);
        await page.locator('#hs-scene.hs-scene--ready').waitFor();
        await page.waitForTimeout(600);
        const shotDir = process.env.QA_HOME_STATUS_SHOT_DIR || artifacts;
        fs.mkdirSync(shotDir, { recursive: true });
        await page.screenshot({ path: path.join(shotDir, `home-status-${width}.png`) });
        if (shotDir !== artifacts) await page.screenshot({ path: path.join(artifacts, `home-status-${width}.png`) });
        assert.deepEqual(errors, []);
        results.push({ width, scenario: 'home-status', passed: true, level: expected.level, exp: expected.exp.total });
        console.log(`PASS home status window ${width}px: store-derived numbers, collapsible, 今日任務 stays visible, no horizontal scroll, contrast in both themes`);
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, `failure-home-status-${width}.png`), fullPage: true }).catch(() => {});
        results.push({ width, scenario: 'home-status', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
        await context.close();
      }
    }
    // v1.4.0 reduced motion: no animation on the window or the scene, everything already in its final state.
    {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
      const page = await context.newPage();
      const errors = [];
      page.on('pageerror', error => errors.push(String(error)));
      await context.route('**/*', route => route.request().url().startsWith(url) ? route.continue() : route.abort());
      page.setDefaultTimeout(15000);
      try {
        await page.goto(url);
        await page.locator('#home-status .hs-frame').waitFor();
        await page.locator('#hs-scene.hs-scene--ready').waitFor();
        const state = await page.evaluate(() => {
          const names = sel => Array.from(document.querySelectorAll(sel)).map(el => getComputedStyle(el).animationName);
          const rows = Array.from(document.querySelectorAll('#home-status .hs-row'));
          return {
            window: names('#home-status .hs-row, #home-status .hs-bar i, #home-status .hs-lv'),
            scene: names('.hs-hero-body, .hs-stars, .hs-lamp, .hs-beacon, .hs-screen'),
            rowOpacity: rows.map(el => getComputedStyle(el).opacity),
            sparkDisplay: getComputedStyle(document.querySelector('.hs-spark')).display
          };
        });
        assert(state.window.length > 0 && state.window.every(n => n === 'none'), 'No window animation: ' + state.window.join());
        assert(state.scene.length > 0 && state.scene.every(n => n === 'none'), 'No scene animation: ' + state.scene.join());
        assert(state.rowOpacity.every(o => o === '1'), 'Rows are fully shown immediately');
        assert.equal(state.sparkDisplay, 'none');
        assert.deepEqual(errors, []);
        results.push({ width: 390, scenario: 'home-status-reduced-motion', passed: true });
        console.log('PASS home status reduced motion 390px: no animation, final state shown');
      } catch (error) {
        await page.screenshot({ path: path.join(artifacts, 'failure-home-status-reduced.png'), fullPage: true }).catch(() => {});
        results.push({ scenario: 'home-status-reduced-motion', passed: false, error: String(error), browserErrors: errors });
        throw error;
      } finally {
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
