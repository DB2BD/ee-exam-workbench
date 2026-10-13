#!/usr/bin/env node
// Permanent gate: every learner-facing text field must render through the
// app's own Markdown+KaTeX pipeline with
//   * zero KaTeX parse errors (`katex-error`), and
//   * zero leaked LaTeX source in the visible text (a `\frac`, `\quad`, a bare
//     `$` ...).  Rendered KaTeX, <code> and <pre> are removed by walking the
//     HTML tags (not by regex guessing) before the leak scan; an escaped
//     currency sign (`\$`) in the source is allowed to appear as `$`.
//
// Covered: RECALL_HINTS (activationMd, trapsMd), KNOWLEDGE_DAG and the
// canonical knowledge graph (coreFormula, keyTrap), CHEATSHEET_DATA, and every
// file of BUNDLED_MD / NATIONAL_BUNDLED_MD (solutions, questions, knowledge
// base).  Bundled Markdown is first reduced to what the solution pane shows
// (frontmatter, 官方題目 headings and 獨立校驗紀錄 blocks are dropped; see
// extractQuestionMarkdown in src/components/solutionModal.js).
//
// Usage: node scripts/audit_math_render.cjs [--repo <dir>] [--out <file.json>] [--quiet]
// Exit code: 0 when clean, 1 when any error/leak is found.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

function parseArgs(argv) {
  const args = { repo: path.resolve(__dirname, '..'), out: null, quiet: false };
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === '--repo') args.repo = path.resolve(argv[++i]);
    else if (argv[i] === '--out') args.out = argv[++i];
    else if (argv[i] === '--quiet') args.quiet = true;
  }
  return args;
}

function loadContext(repo) {
  const ctx = { console: { log() {}, error() {}, warn() {} }, window: {}, document: undefined };
  ctx.self = ctx;
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  const load = (file, optional) => {
    const full = path.join(repo, file);
    if (!fs.existsSync(full)) {
      if (optional) return false;
      throw new Error(`missing ${file}`);
    }
    vm.runInContext(fs.readFileSync(full, 'utf8'), ctx, { filename: file });
    return true;
  };
  load('libs/katex.min.js');
  load('libs/marked.min.js');
  if (!ctx.katex && ctx.window.katex) ctx.katex = ctx.window.katex;
  if (!ctx.marked && ctx.window.marked) ctx.marked = ctx.window.marked;
  load('src/renderers/katexRenderer.js');
  ['src/data/knowledge-dag.js', 'src/data/knowledge-dag.generated.js', 'src/data/recallHints.generated.js',
    'src/data/cheatsheet.generated.js', 'solutions-bundle.js', 'national-solutions-bundle.js']
    .forEach(file => load(file, true));
  vm.runInContext(`this.__data = {
    dag: typeof KNOWLEDGE_DAG !== 'undefined' ? KNOWLEDGE_DAG : {},
    graph: typeof CANONICAL_KNOWLEDGE_GRAPH !== 'undefined' ? CANONICAL_KNOWLEDGE_GRAPH : null,
    hints: typeof RECALL_HINTS !== 'undefined' ? RECALL_HINTS : {},
    cheat: typeof CHEATSHEET_DATA !== 'undefined' ? CHEATSHEET_DATA : null,
    md: typeof BUNDLED_MD !== 'undefined' ? BUNDLED_MD : {},
    nmd: typeof NATIONAL_BUNDLED_MD !== 'undefined' ? NATIONAL_BUNDLED_MD : {}
  };`, ctx);
  return ctx;
}

// ---- HTML walking -------------------------------------------------------
const VOID_TAGS = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);
const SKIP_TAGS = new Set(['pre', 'code', 'script', 'style']);
const TOKEN_RE = /<!--[\s\S]*?-->|<(\/?)([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^'">])*)>|[^<]+|</g;
const ENTITIES = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ' };

function decodeEntities(text) {
  return text.replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, (match, body) => {
    if (body[0] === '#') {
      const code = body[1].toLowerCase() === 'x' ? parseInt(body.slice(2), 16) : parseInt(body.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : match;
    }
    return Object.prototype.hasOwnProperty.call(ENTITIES, body.toLowerCase()) ? ENTITIES[body.toLowerCase()] : match;
  });
}

function hasClass(attrs, name) {
  const found = attrs.match(/\bclass\s*=\s*("([^"]*)"|'([^']*)')/);
  return !!found && (found[2] || found[3] || '').split(/\s+/).includes(name);
}

// Returns the learner-visible text: everything outside rendered KaTeX
// (`.katex`, `.katex-display`, `.katex-error`), <code> and <pre>.
// `errors` is the list of KaTeX error messages (spans with class katex-error).
function inspectHtml(html) {
  let visible = '';
  const errors = [];
  let skipName = null;
  let depth = 0;
  TOKEN_RE.lastIndex = 0;
  let token;
  while ((token = TOKEN_RE.exec(html)) !== null) {
    const [raw, closing, name, attrs] = token;
    if (name === undefined) {
      if (skipName === null && !raw.startsWith('<!--')) visible += raw;
      continue;
    }
    const tag = name.toLowerCase();
    const selfClosing = /\/\s*$/.test(attrs || '') || VOID_TAGS.has(tag);
    if (skipName !== null) {
      if (tag === skipName && !selfClosing) depth += closing ? -1 : 1;
      if (depth === 0) skipName = null;
      continue;
    }
    if (closing || selfClosing) continue;
    const isKatex = tag === 'span' && (hasClass(attrs, 'katex') || hasClass(attrs, 'katex-display') || hasClass(attrs, 'katex-error'));
    if (isKatex || SKIP_TAGS.has(tag)) {
      if (hasClass(attrs, 'katex-error')) {
        const title = attrs.match(/\btitle\s*=\s*"([^"]*)"/);
        errors.push(title ? decodeEntities(title[1]) : 'katex-error');
      }
      skipName = tag;
      depth = 1;
    }
  }
  return { visible: decodeEntities(visible), errors };
}

// ---- checks ------------------------------------------------------------
function createChecker(ctx) {
  const problems = [];
  const stats = {};
  const run = (fn, arg) => {
    ctx.__arg = arg;
    return vm.runInContext(`${fn}(__arg)`, ctx);
  };
  const check = (group, id, source, html) => {
    stats[group] = stats[group] || { checked: 0, errors: 0, leaks: 0 };
    stats[group].checked += 1;
    const { visible, errors } = inspectHtml(html);
    const leaks = [];
    (visible.match(/\\[A-Za-z]+|\\[()[\]]/g) || []).forEach(m => leaks.push(m));
    if (/@@KATEX_/.test(visible)) leaks.push('@@KATEX_');
    // Escaped currency (`\$`) in the source legitimately shows as `$`.
    const allowedDollars = (String(source).match(/\\\$/g) || []).length;
    const dollars = (visible.match(/\$/g) || []).length;
    if (dollars > allowedDollars) leaks.push('$');
    if (errors.length) stats[group].errors += errors.length;
    if (leaks.length) stats[group].leaks += 1;
    if (errors.length || leaks.length) {
      problems.push({
        group, id, errors: errors.slice(0, 4), leaks: [...new Set(leaks)].slice(0, 8),
        sample: String(source).slice(0, 160)
      });
    }
  };
  return {
    problems,
    stats,
    markdown: (group, id, md) => { if (md) check(group, id, md, run('processMarkdownWithMath', md)); },
    formula: (group, id, text) => { if (text) check(group, id, text, run('renderCoreFormulaHtml', text)); },
    inline: (group, id, md) => { if (md) check(group, id, md, run('renderInlineMarkdownWithMath', md)); }
  };
}

// What the solution pane actually renders from a bundled Markdown file.
function learnerFacingMarkdown(raw) {
  return String(raw)
    .replace(/^﻿?---\s*\r?\n[\s\S]*?\r?\n---\s*(?:\r?\n|$)/, '')
    .replace(/^[ \t]*#{2,6}[ \t]+官方題目[^\r\n]*(?:\r?\n|$)/gmi, '')
    .replace(/(?:^|\r?\n)#{2,6}[ \t]+獨立校驗紀錄[^\r\n]*(?:\r?\n|$)[\s\S]*?(?=\r?\n#{2,6}[ \t]+|$)/gi, '');
}

function walkCheatsheet(cheat, markdown) {
  if (!cheat) return;
  (cheat.subjects || []).forEach(subject => {
    (subject.categories || []).forEach(category => {
      (category.items || []).forEach((item, index) => {
        markdown('cheatsheet', `${subject.id}/${category.id}#${index}`, item.text);
      });
    });
  });
  (cheat.assumption_templates || []).forEach((tpl, index) => {
    markdown('cheatsheet', `assumption#${index}`, `${tpl.situation || ''}。${tpl.how_to_write || ''}`);
  });
}

function audit(repo) {
  const ctx = loadContext(repo);
  const data = ctx.__data;
  const checker = createChecker(ctx);

  // Fallback copy shown when a chapter has no core formula (recallStore.js):
  // must render as ordinary text, never as a math span.
  ['先寫出本章節的核心公式，再代入題目條件。', '寫出本章節核心公式。'].forEach((text, index) => {
    const html = vm.runInContext(`renderCoreFormulaHtml(${JSON.stringify(text)})`, ctx);
    if (/class="katex/.test(html)) {
      checker.problems.push({ group: 'formulaFallback', id: `fallback#${index}`, errors: [], leaks: ['wrapped in math'], sample: text });
    }
  });

  const seen = new Set();
  const nodes = [];
  Object.entries(data.dag || {}).forEach(([id, node]) => nodes.push([id, node]));
  if (data.graph && data.graph.nodes) Object.entries(data.graph.nodes).forEach(([id, node]) => nodes.push([id, node]));
  nodes.forEach(([id, node]) => {
    if (!node) return;
    if (node.coreFormula && !seen.has(`f|${node.coreFormula}`)) {
      seen.add(`f|${node.coreFormula}`);
      checker.formula('coreFormula', id, node.coreFormula);
    }
    if (node.keyTrap && !seen.has(`t|${node.keyTrap}`)) {
      seen.add(`t|${node.keyTrap}`);
      checker.inline('keyTrap', id, node.keyTrap);
    }
  });

  Object.entries(data.hints || {}).forEach(([qid, hint]) => {
    checker.markdown('activationMd', qid, hint.activationMd);
    checker.markdown('trapsMd', qid, hint.trapsMd);
  });

  walkCheatsheet(data.cheat, checker.markdown);

  Object.entries(data.md || {}).forEach(([file, md]) => {
    checker.markdown('bundledMd', file, learnerFacingMarkdown(md));
  });
  Object.entries(data.nmd || {}).forEach(([file, md]) => {
    checker.markdown('nationalBundledMd', file, learnerFacingMarkdown(md));
  });

  const totals = { errors: 0, leakFields: 0, checked: 0 };
  Object.values(checker.stats).forEach(stat => {
    totals.errors += stat.errors;
    totals.leakFields += stat.leaks;
    totals.checked += stat.checked;
  });
  return { totals, stats: checker.stats, problems: checker.problems };
}

if (require.main === module) {
  const args = parseArgs(process.argv.slice(2));
  const started = Date.now();
  const result = audit(args.repo);
  if (args.out) fs.writeFileSync(args.out, JSON.stringify(result, null, 1));
  if (!args.quiet) {
    result.problems.forEach(p => {
      console.error(`${p.group}\t${p.id}\terrors=${p.errors.length}${p.errors.length ? ` (${p.errors[0].slice(0, 80)})` : ''}\tleaks=${p.leaks.join(' ')}`);
    });
  }
  const { totals } = result;
  console.log(`math render audit: checked=${totals.checked} katex-errors=${totals.errors} leak-fields=${totals.leakFields} problems=${result.problems.length} (${Date.now() - started} ms)`);
  process.exit(result.problems.length ? 1 : 0);
}

module.exports = { audit, inspectHtml, learnerFacingMarkdown };
