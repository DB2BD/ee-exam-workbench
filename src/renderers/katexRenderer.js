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
      const end = markdown.indexOf(')', cursor + 1);
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
  protectedMd = protectInlineDollarMath(protectedMd, mathPlaceholders);

  // Normalize legacy parenthetical fragments before the standard inline
  // delimiter pass, so the generated \(...\) wrapper is captured as a
  // placeholder rather than emitted as literal Markdown text.
  protectedMd = normalizeBareLatexFragments(protectedMd);

  // Standard LaTeX inline delimiters \( ... \).
  protectedMd = protectedMd.replace(/\\\(([\s\S]+?)\\\)/g, (match, math) => {
    const idx = mathPlaceholders.length;
    mathPlaceholders.push({ type: 'inline', math: math.trim() });
    return `@@KATEX_INLINE_${idx}@@`;
  });

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
