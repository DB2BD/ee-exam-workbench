// src/renderers/katexRenderer.js
/**
 * Direct KaTeX & Math Formula Protection Engine.
 * Extracts LaTeX delimiters before Markdown parsing and renders them safely.
 */

function renderLatexDirect(latex, displayMode) {
  if (typeof katex === 'undefined') {
    return `<code class="math-fallback">${latex}</code>`;
  }
  try {
    return katex.renderToString(latex, {
      displayMode: displayMode,
      throwOnError: false
    });
  } catch (err) {
    console.error('KaTeX rendering error:', err);
    return `<span class="katex-error">${latex}</span>`;
  }
}

function processMarkdownWithMath(rawMarkdown) {
  if (!rawMarkdown) return '';

  const mathPlaceholders = [];

  // Protect display math $$ ... $$
  let protectedMd = rawMarkdown.replace(/\$\$([\s\S]+?)\$\$/g, (match, math) => {
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
