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

  async function resolveCSSImports(css, baseUrl, stack = []) {
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
      output += await resolveCSSImports(importedCSS, resolvedUrl, [...stack, resolvedUrl]);
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
    const bundled = await resolveCSSImports(css, presetUrl);
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
