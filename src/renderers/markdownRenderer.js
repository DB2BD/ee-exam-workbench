// src/renderers/markdownRenderer.js
/**
 * Solution Markdown Parser & Image Path Resolver.
 * Resolves Markdown images from IMAGE_MAP / NATIONAL_IMAGE_MAP.
 */

function resolveSolutionMarkdown(targetPath, qid) {
  const cleanPath = targetPath ? targetPath.replace(/^\.\//, '') : '';
  const isGK = (qid && qid.startsWith('GK-')) || (cleanPath && cleanPath.includes('國考同級')) || (currentExamCategory === 'GK');

  let rawMd = '';

  if (isGK) {
    if (typeof NATIONAL_BUNDLED_MD !== 'undefined' && NATIONAL_BUNDLED_MD[cleanPath]) {
      rawMd = NATIONAL_BUNDLED_MD[cleanPath];
    } else if (typeof BUNDLED_MD !== 'undefined' && BUNDLED_MD[cleanPath]) {
      rawMd = BUNDLED_MD[cleanPath];
    }
  } else {
    if (typeof BUNDLED_MD !== 'undefined' && BUNDLED_MD[cleanPath]) {
      rawMd = BUNDLED_MD[cleanPath];
    } else if (typeof NATIONAL_BUNDLED_MD !== 'undefined' && NATIONAL_BUNDLED_MD[cleanPath]) {
      rawMd = NATIONAL_BUNDLED_MD[cleanPath];
    }
  }

  return rawMd;
}

function resolveImageMapUrl(src, isGK, qid) {
  if (!src || /^(?:data:|blob:|https?:|\/\/)/i.test(src)) return src;

  // Keep query/hash fragments for browsers, but exclude them while looking
  // up the repository asset. This also supports URL-encoded Chinese names.
  const rawSrc = String(src).trim();
  const split = rawSrc.match(/^([^?#]*)([?#].*)?$/);
  const rawPath = (split ? split[1] : rawSrc).replace(/^\.\//, '');
  const path = rawPath.split('/').reduce((parts, part) => {
    if (!part || part === '.') return parts;
    if (part === '..') { parts.pop(); return parts; }
    parts.push(part);
    return parts;
  }, []).join('/');
  const suffix = split && split[2] ? split[2] : '';
  const decodedPath = (() => {
    try { return decodeURIComponent(path); } catch (_) { return path; }
  })();
  const basename = decodedPath.split('/').pop() || decodedPath;

  // Legacy PE notes commonly embed a whole page (…_p1.png) at the start of
  // every question.  Prefer the attested question-level crop for the active
  // QID when the crop compiler has supplied one.  Dedicated circuit SVG/PNG
  // assets are intentionally left untouched.
  if (!isGK && qid && typeof QUESTION_CROP_MAP !== 'undefined'
      && QUESTION_CROP_MAP[qid]
      && /_p\d+\.(?:png|jpe?g|webp)$/i.test(basename)
      && !/\/questions\//i.test(decodedPath)) {
    return `${QUESTION_CROP_MAP[qid]}${suffix}`;
  }

  const lookup = (map) => {
    if (!map) return '';
    const candidates = [
      path,
      decodedPath,
      `./${path}`,
      `./${decodedPath}`,
      basename,
      encodeURIComponent(decodedPath),
      encodeURIComponent(basename),
    ];
    for (const candidate of candidates) {
      if (map[candidate]) return map[candidate];
    }
    return '';
  };

  const preferred = isGK && typeof NATIONAL_IMAGE_MAP !== 'undefined'
    ? lookup(NATIONAL_IMAGE_MAP) : '';
  const fallback = typeof IMAGE_MAP !== 'undefined' ? lookup(IMAGE_MAP) : '';
  const nationalFallback = typeof NATIONAL_IMAGE_MAP !== 'undefined'
    ? lookup(NATIONAL_IMAGE_MAP) : '';
  return `${preferred || fallback || nationalFallback || path}${suffix}`;
}

/** Resolve every image emitted by marked.js, including images in card topics. */
function resolveRenderedImageSources(html, isGK, qid) {
  if (!html || typeof html !== 'string') return html;
  return html.replace(/(\bsrc\s*=\s*["'])([^"']+)(["'])/gi, (match, prefix, src, suffix) => {
    return `${prefix}${resolveImageMapUrl(src, isGK, qid)}${suffix}`;
  });
}

/** Render question stems so Markdown emphasis and inline/display math are not shown literally. */
function renderQuestionTopic(rawText) {
  if (!rawText) return '';
  const html = typeof processMarkdownWithMath === 'function'
    ? processMarkdownWithMath(rawText)
    : rawText;
  const isGK = typeof currentExamCategory !== 'undefined' && currentExamCategory === 'GK';
  return resolveRenderedImageSources(html, isGK);
}
