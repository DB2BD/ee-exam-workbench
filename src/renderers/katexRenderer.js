// src/renderers/katexRenderer.js
/**
 * Direct KaTeX & Math Formula Protection Engine.
 * Extracts LaTeX delimiters before Markdown parsing and renders them safely.
 */

/**
 * Normalize a small set of legacy, unbraced LaTeX unit macros before KaTeX
 * sees them. Imported notes historically contain forms such as ``\mathrm A``;
 * braces are the standard LaTeX spelling and avoid parser differences between
 * KaTeX versions while preserving the visible result.
 */
function normalizeLatexSyntax(latex) {
  return String(latex || '')
    .replace(/\\mathrm\s+([A-Za-zΩμ%])/g, '\\mathrm{$1}')
    .replace(/\\operatorname\s+([A-Za-zΩμ%])/g, '\\operatorname{$1}');
}

function renderLatexDirect(latex, displayMode) {
  latex = normalizeLatexSyntax(latex);
  if (typeof katex === 'undefined') {
    return `<code class="math-fallback">${latex}</code>`;
  }
  try {
    return katex.renderToString(latex, {
      displayMode: displayMode,
      throwOnError: false,
      // Chinese explanatory text and punctuation occasionally appears inside
      // imported math blocks. KaTeX can render it correctly; ignore only this
      // compatibility warning while keeping all other strict-mode warnings.
      strict: (errorCode) => errorCode === 'unicodeTextInMathMode' ? 'ignore' : 'warn'
    });
  } catch (err) {
    console.error('KaTeX rendering error:', err);
    return `<span class="katex-error">${latex}</span>`;
  }
}

/**
 * Convert Obsidian's image embed syntax to HTML before marked.js sees it.
 *
 * `marked` intentionally does not parse `![[file.png|750]]`, so without this
 * pass the wiki embed is displayed literally in the solution pane.  Keep the
 * source path untouched here; the later IMAGE_MAP/NATIONAL_IMAGE_MAP pass is
 * responsible for mapping the basename to the published asset path.
 */
function normalizeObsidianImageEmbeds(markdown) {
  if (!markdown || !markdown.includes('![[')) return markdown;

  const escapeAttribute = (value) => String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  return markdown.replace(/!\[\[([^|\]]+?)(?:\|([^\]]+?))?\]\]/g, (match, rawTarget, rawSize) => {
    const target = rawTarget.trim();
    if (!target) return match;

    const size = (rawSize || '').trim();
    // Obsidian accepts a numeric width and a WxH size. Only emit dimensions
    // for strict numeric values so arbitrary pipe text cannot become HTML.
    const dimensions = size.match(/^(\d{1,4})(?:x(\d{1,4}))?$/i);
    const attrs = dimensions
      ? ` width="${dimensions[1]}"${dimensions[2] ? ` height="${dimensions[2]}"` : ''}`
      : '';
    const alt = target.split(/[\\/]/).pop().replace(/\.[^.]+$/, '') || '題目圖片';
    return `<img src="${escapeAttribute(target)}" alt="${escapeAttribute(alt)}"${attrs}>`;
  });
}

function isEscapedCharacter(text, index) {
  let slashCount = 0;
  for (let i = index - 1; i >= 0 && text[i] === '\\'; i -= 1) slashCount += 1;
  return slashCount % 2 === 1;
}

/**
 * Legacy notes occasionally put LaTeX units inside ordinary parentheses,
 * e.g. ``(2500\,\mathrm{MVA})`` without an opening ``\(``.  Markdown leaves
 * those commands as visible backslashes.  Wrap only same-line parenthetical
 * fragments that actually contain a LaTeX command; existing math blocks and
 * inline-code spans are copied untouched.
 */
function normalizeBareLatexFragments(markdown) {
  let result = '';
  let cursor = 0;
  let inFence = false;

  while (cursor < markdown.length) {
    if (markdown.startsWith('```', cursor)) {
      const end = markdown.indexOf('```', cursor + 3);
      if (end < 0) return result + markdown.slice(cursor);
      result += markdown.slice(cursor, end + 3);
      cursor = end + 3;
      inFence = !inFence;
      continue;
    }
    if (inFence) {
      result += markdown[cursor++];
      continue;
    }
    if (markdown[cursor] === '`') {
      const end = markdown.indexOf('`', cursor + 1);
      if (end < 0) return result + markdown.slice(cursor);
      result += markdown.slice(cursor, end + 1);
      cursor = end + 1;
      continue;
    }

    // Do not rewrite text that is already inside a supported math delimiter.
    const mathStart = markdown.startsWith('$$', cursor)
      || markdown.startsWith('\\[', cursor)
      || markdown.startsWith('\\(', cursor)
      || (markdown[cursor] === '$' && markdown[cursor + 1] !== '$');
    if (mathStart) {
      const isDouble = markdown.startsWith('$$', cursor);
      const left = isDouble ? '$$' : markdown.startsWith('\\[', cursor) ? '\\[' : markdown.startsWith('\\(', cursor) ? '\\(' : '$';
      const right = isDouble ? '$$' : left === '\\[' ? '\\]' : left === '\\(' ? '\\)' : '$';
      const end = markdown.indexOf(right, cursor + left.length);
      if (end < 0) {
        result += markdown[cursor++];
      } else {
        result += markdown.slice(cursor, end + right.length);
        cursor = end + right.length;
      }
      continue;
    }

    if (markdown[cursor] === '(') {
      // Find the matching close rather than the first close; equations often
      // contain nested calls such as ``i_p(t_{on})`` or ``\arctan(...)``.
      let end = -1;
      let depth = 0;
      for (let probe = cursor; probe < markdown.length; probe += 1) {
        if (markdown[probe] === '(' && !isEscapedCharacter(markdown, probe)) depth += 1;
        if (markdown[probe] === ')' && !isEscapedCharacter(markdown, probe)) {
          depth -= 1;
          if (depth === 0) { end = probe; break; }
        }
        if (markdown[probe] === '\n') break;
      }
      if (end >= 0 && !markdown.slice(cursor + 1, end).includes('\n')) {
        const fragment = markdown.slice(cursor, end + 1);
        // Parentheses which merely surround an existing delimiter, e.g.
        // ``(\\(-\\pi,0]\\)`` must remain untouched.
        const containsDelimiter = /(?:\\\\?\(|\\\\?\[|\$)/.test(fragment);
        if (!containsDelimiter && /\\(?:[A-Za-z]+|[,;%])/.test(fragment)) {
          // A few legacy notes used ``(\\frac{...}\\right)`` without the
          // matching ``\\left``.  Reconstruct the intended paired fence so
          // KaTeX receives valid syntax while preserving the visual grouping.
          const rightFence = fragment.match(/\\right\s*([)\]}])\s*$/);
          if (rightFence && !/\\left/.test(fragment)) {
            const inner = fragment.slice(1, -1).replace(/\\right\s*$/, '');
            const leftFence = { ')': '(', ']': '[', '}': '{' }[rightFence[1]];
            result += `\\(\\left${leftFence}${inner}\\right${rightFence[1]}\\)`;
          } else {
            result += `\\(${fragment}\\)`;
          }
          cursor = end + 1;
          continue;
        }
      }
    }

    result += markdown[cursor++];
  }
  return result;
}

// A small number of legacy notes have a standalone equation line such as
// ``|Y_p| = \\sqrt{...}`` with no `$`/`\\(` fence.  Wrap only equation-shaped
// lines (leading ASCII symbol and an equality/LaTeX command) so prose that
// merely mentions a unit is never swallowed into a math span.
function normalizeUndelimitedEquationLines(markdown) {
  const command = /\\(?:frac|sqrt|mathrm|operatorname|text|cdot|times|pi|theta|angle|left|right|boxed|sum|int|cos|sin|tan|log|ln|pm|leq|geq|approx|infty|mathcal|mathbb|mathbf|widetilde|overline|Delta|Omega|Phi|eta|omega|lambda|mu|sigma|delta|alpha|beta|gamma|partial|nabla|Im|Re)\b/;
  return String(markdown || '').split(/(\n)/).map((line) => {
    if (line === '\n' || !line.trim()) return line;
    if (/@@KATEX_(?:INLINE|DISPLAY)_\d+@@/.test(line)) return line;
    if (/\$\$|\\\(|\\\[|(^|[^\\])\$(?!\$)/.test(line)) return line;
    const body = line.trim();
    const equationLike = /^(?:[|A-Za-z\\]|[-+]?\d+(?:\.\d+)?\s*[A-Za-z_])/.test(body)
      && (body.includes('=') || command.test(body)) && command.test(body);
    if (!equationLike || /^<!--|^-->|^```|^\s*(?:https?:|!\[\[)/.test(body)) return line;
    const lead = line.match(/^\s*/)[0];
    return `${lead}\\(${body}\\)`;
  }).join('');
}

// Legacy annual notes occasionally leave a Greek/operator command in prose,
// e.g. "開 \\Delta 接" or "\\mathcal R". Once fenced equations have become
// placeholders, normalize only the remaining prose commands so raw
// backslashes cannot leak into the rendered answer. Unknown commands remain
// untouched for manual review.
function normalizeBareLatexCommands(markdown) {
  const replacements = [
    [/\\text\{([^{}\n]*)\}/g, '$1'],
    [/\\mathrm\{([^{}\n]*)\}/g, '$1'],
    [/\\operatorname\{([^{}\n]*)\}/g, '$1'],
    [/\\mathcal\s*([A-Za-z])/g, '$1'],
    [/\\Delta\b/g, 'Δ'],
    [/\\Omega\b/g, 'Ω'],
    [/\\Phi\b/g, 'Φ'],
    [/\\theta\b/g, 'θ'],
    [/\\omega\b/g, 'ω'],
    [/\\lambda\b/g, 'λ'],
    [/\\mu\b/g, 'μ'],
    [/\\sigma\b/g, 'σ'],
    [/\\alpha\b/g, 'α'],
    [/\\beta\b/g, 'β'],
    [/\\gamma\b/g, 'γ']
  ];
  let result = '';
  let cursor = 0;
  let inFence = false;
  while (cursor < markdown.length) {
    if (markdown.startsWith('```', cursor)) {
      const end = markdown.indexOf('```', cursor + 3);
      if (end < 0) return result + markdown.slice(cursor);
      result += markdown.slice(cursor, end + 3);
      cursor = end + 3;
      inFence = !inFence;
      continue;
    }
    if (inFence) {
      result += markdown[cursor++];
      continue;
    }
    if (markdown[cursor] === '`') {
      const end = markdown.indexOf('`', cursor + 1);
      if (end < 0) return result + markdown.slice(cursor);
      result += markdown.slice(cursor, end + 1);
      cursor = end + 1;
      continue;
    }
    const placeholder = markdown.slice(cursor).match(/^@@KATEX_(?:INLINE|DISPLAY)_\d+@@/);
    if (placeholder) {
      result += placeholder[0];
      cursor += placeholder[0].length;
      continue;
    }
    let next = cursor + 1;
    while (next < markdown.length
      && markdown[next] !== '`'
      && !markdown.startsWith('```', next)
      && !markdown.slice(next).match(/^@@KATEX_(?:INLINE|DISPLAY)_\d+@@/)) next += 1;
    let segment = markdown.slice(cursor, next);
    replacements.forEach(([pattern, replacement]) => {
      segment = segment.replace(pattern, replacement);
    });
    result += segment;
    cursor = next;
  }
  return result;
}

/**
 * Protect inline `$...$` blocks without treating an escaped currency marker
 * (`\$`) inside a unit such as `\text{\$/h}` as the closing delimiter.
 * A scanner is used instead of a single regex so escaped backslashes and
 * same-line Markdown text remain distinguishable.
 */
function protectInlineDollarMath(markdown, mathPlaceholders) {
  let result = '';
  let cursor = 0;

  while (cursor < markdown.length) {
    const isOpening = markdown[cursor] === '$'
      && markdown[cursor + 1] !== '$'
      && !isEscapedCharacter(markdown, cursor);
    if (!isOpening) {
      result += markdown[cursor];
      cursor += 1;
      continue;
    }

    let closing = cursor + 1;
    while (closing < markdown.length && markdown[closing] !== '\n') {
      if (markdown[closing] === '$'
          && markdown[closing + 1] !== '$'
          && !isEscapedCharacter(markdown, closing)) break;
      closing += 1;
    }

    if (closing < markdown.length && markdown[closing] === '$') {
      const math = markdown.slice(cursor + 1, closing).trim();
      if (math) {
        const idx = mathPlaceholders.length;
        mathPlaceholders.push({ type: 'inline', math });
        result += `@@KATEX_INLINE_${idx}@@`;
        cursor = closing + 1;
        continue;
      }
    }

    // No valid closing delimiter on this line: preserve the source literally.
    result += markdown[cursor];
    cursor += 1;
  }

  return result;
}

function processMarkdownWithMath(rawMarkdown) {
  if (!rawMarkdown) return '';

  const mathPlaceholders = [];

  // Some legacy exports converted the backslash in ``\text`` to a tab (for
  // example ``$\text{deg}$`` became ``$\text{deg}$`` with a literal tab).
  // Restore that exact corruption before delimiter scanning so the unit label
  // remains a normal inline formula instead of leaking as plain text.
  rawMarkdown = String(rawMarkdown).replace(/\$(?:\t| )ext\{/g, '$\\text{');

  // Convert wiki image embeds before math protection/Markdown parsing. This
  // covers all existing `![[...|750]]` and `![[...|850]]` solution embeds.
  let protectedMd = normalizeObsidianImageEmbeds(rawMarkdown);

  // Protect display math $$ ... $$
  protectedMd = protectedMd.replace(/\$\$([\s\S]+?)\$\$/g, (match, math) => {
    const idx = mathPlaceholders.length;
    mathPlaceholders.push({ type: 'display', math: math.trim() });
    return `@@KATEX_DISPLAY_${idx}@@`;
  });

  // Also accept the standard LaTeX display delimiters \[ ... \].  Several
  // imported solutions use this form; leaving it to marked.js would expose
  // the delimiters as literal text instead of rendering the equation.
  protectedMd = protectedMd.replace(/\\\[([\s\S]+?)\\\]/g, (match, math) => {
    const idx = mathPlaceholders.length;
    mathPlaceholders.push({ type: 'display', math: math.trim() });
    return `@@KATEX_DISPLAY_${idx}@@`;
  });

  // Protect inline math $ ... $.  The scanner deliberately skips escaped
  // currency markers inside a formula (for example `\text{\$/MWh}`).
  // Keep this after the legacy normalizers so existing dollar-delimited
  // formulas remain visible to their delimiter guard.
  protectedMd = protectInlineDollarMath(protectedMd, mathPlaceholders);

  // Normalize legacy parenthetical fragments after dollar protection; this
  // prevents a parenthesis inside an existing `$...$` expression from being
  // wrapped a second time.
  protectedMd = normalizeBareLatexFragments(protectedMd);

  protectedMd = normalizeUndelimitedEquationLines(protectedMd);


  // Standard LaTeX inline delimiters \( ... \).
  protectedMd = protectedMd.replace(/\\\(([\s\S]+?)\\\)/g, (match, math) => {
    const idx = mathPlaceholders.length;
    mathPlaceholders.push({ type: 'inline', math: math.trim() });
    return `@@KATEX_INLINE_${idx}@@`;
  });

  // Any remaining LaTeX commands are in ordinary prose; convert the small
  // legacy compatibility set to readable Unicode/text before Markdown parse.
  protectedMd = normalizeBareLatexCommands(protectedMd);

  // Parse Markdown via marked.js
  let html = (typeof marked !== 'undefined') ? marked.parse(protectedMd) : protectedMd;

  // Restore and render KaTeX
  html = html.replace(/@@KATEX_DISPLAY_(\d+)@@/g, (match, idx) => {
    const item = mathPlaceholders[parseInt(idx, 10)];
    return item ? renderLatexDirect(item.math, true) : match;
  });

  html = html.replace(/@@KATEX_INLINE_(\d+)@@/g, (match, idx) => {
    const item = mathPlaceholders[parseInt(idx, 10)];
    return item ? renderLatexDirect(item.math, false) : match;
  });

  return html;
}
