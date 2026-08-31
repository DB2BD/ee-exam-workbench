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

  // Protect inline math $ ... $
  protectedMd = protectedMd.replace(/\$([^\$\n]+?)\$/g, (match, math) => {
    const idx = mathPlaceholders.length;
    mathPlaceholders.push({ type: 'inline', math: math.trim() });
    return `@@KATEX_INLINE_${idx}@@`;
  });

  // Standard LaTeX inline delimiters \( ... \).
  protectedMd = protectedMd.replace(/\\\(([^\n]+?)\\\)/g, (match, math) => {
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
