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

function resolveImageMapUrl(src, isGK) {
  const cleanSrc = src.replace(/^\.\//, '');

  if (isGK && typeof NATIONAL_IMAGE_MAP !== 'undefined' && NATIONAL_IMAGE_MAP[cleanSrc]) {
    return NATIONAL_IMAGE_MAP[cleanSrc];
  }
  if (typeof IMAGE_MAP !== 'undefined' && IMAGE_MAP[cleanSrc]) {
    return IMAGE_MAP[cleanSrc];
  }
  if (typeof NATIONAL_IMAGE_MAP !== 'undefined' && NATIONAL_IMAGE_MAP[cleanSrc]) {
    return NATIONAL_IMAGE_MAP[cleanSrc];
  }
  return src;
}

/** Render question stems so Markdown emphasis and inline/display math are not shown literally. */
function renderQuestionTopic(rawText) {
  if (!rawText) return '';
  return typeof processMarkdownWithMath === 'function'
    ? processMarkdownWithMath(rawText)
    : rawText;
}
