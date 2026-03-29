/*! See license: https://github.com/FranBarInstance/bootstrap-dynamic-themes */
(function () {
  function createImportRegex() {
    return /@import\s+(?:url\(\s*(?:(\"[^\"]+\")|(\'[^\']+\')|([^)\s]+))\s*\)|(\"[^\"]+\")|(\'[^\']+\'))(\s+[^;]+)?\s*;/g;
  }

  function getImportTarget(match) {
    return [match[1], match[2], match[3], match[4], match[5]]
      .find((value) => value != null);
  }

  function stripQuotes(value) {
    return value.trim().replace(/^['"]|['"]$/g, '');
  }

  function isExternalImport(specifier) {
    return /^(?:https?:)?\/\//i.test(specifier);
  }

  async function fetchText(url) {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
    }
    return await response.text();
  }

  function rewriteFontURLs(css, currentUrl, rootUrl) {
    const currentBase = new URL('./', currentUrl).href;
    const rootBase = new URL('./', rootUrl).href;
    if (currentBase === rootBase) return css;

    // Only rewrite if it's a font-face or contains font indicators
    if (!css.includes('@font-face') || !css.includes('src:')) return css;

    return css.replace(/url\(\s*(['"]?)([^)'\"]+)\1\s*\)/gi, (match, quote, url) => {
      if (url.startsWith('data:') || url.startsWith('/') || /^(?:https?:)?\/\//i.test(url)) {
        return match;
      }

      // Match .ttf and .woff2 specifically to align with Python script behavior
      if (!url.toLowerCase().endsWith('.woff2') && !url.toLowerCase().endsWith('.ttf')) {
        return match;
      }

      try {
        const targetUrl = new URL(url, currentBase).href;
        const root = new URL(rootBase);
        const target = new URL(targetUrl);

        if (root.origin !== target.origin) return match;

        const rootParts = root.pathname.split('/').filter(Boolean);
        const targetParts = target.pathname.split('/').filter(Boolean);

        while (rootParts.length > 0 && targetParts.length > 0 && rootParts[0] === targetParts[0]) {
          rootParts.shift();
          targetParts.shift();
        }

        const relPath = '../'.repeat(rootParts.length) + targetParts.join('/');
        return `url(${quote}${relPath}${quote})`;
      } catch (e) {
        return match;
      }
    });
  }

  async function resolveCSSImports(css, baseUrl, rootUrl, stack = []) {
    let cursor = 0;
    let output = '';
    let match;
    const importRe = createImportRegex();

    while ((match = importRe.exec(css)) !== null) {
      output += css.slice(cursor, match.index);
      cursor = importRe.lastIndex;

      const rawTarget = getImportTarget(match);
      if (!rawTarget) {
        throw new Error('Could not parse @import rule');
      }

      const specifier = stripQuotes(rawTarget);
      const tail = (match[6] || '').trim();

      if (isExternalImport(specifier) || tail) {
        output += match[0];
        continue;
      }

      const resolvedUrl = new URL(specifier, baseUrl).href;
      if (stack.includes(resolvedUrl)) {
        throw new Error(`Circular @import detected: ${[...stack, resolvedUrl].join(' -> ')}`);
      }

      const importedCSS = await fetchText(resolvedUrl);
      const processedCSS = await resolveCSSImports(importedCSS, resolvedUrl, rootUrl, [...stack, resolvedUrl]);
      output += rewriteFontURLs(processedCSS, resolvedUrl, rootUrl);
    }

    output += css.slice(cursor);
    return output;
  }

  function hoistImportsToTop(css) {
    const imports = [];
    const importRe = createImportRegex();
    const body = css.replace(importRe, (fullMatch) => {
      imports.push(fullMatch.trim());
      return '';
    }).trim();

    if (!imports.length) return body;
    if (!body) return `${imports.join('\n')}\n`;
    return `${imports.join('\n')}\n\n${body}`;
  }

  function minifyCSS(css) {
    return css
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\s+/g, ' ')
      .replace(/\s*([{}:;,>])\s*/g, '$1')
      .replace(/;}/g, '}')
      .trim();
  }

  async function bundleAndMinifyPresetCSS(css, options = {}) {
    const presetUrl = options.presetUrl || new URL('../themes/preset/custom.css', window.location.href).href;
    const bundled = await resolveCSSImports(css, presetUrl, presetUrl);
    const hoisted = hoistImportsToTop(bundled);
    const minified = minifyCSS(hoisted);
    return minified || '/* empty */';
  }

  window.BTDTMinifier = {
    isAvailable() {
      return window.location.protocol !== 'file:';
    },
    async bundleAndMinifyPresetCSS(css, options) {
      return bundleAndMinifyPresetCSS(css, options);
    }
  };
})();
