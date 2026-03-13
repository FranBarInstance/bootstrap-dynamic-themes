// js/theme-manager.js

class ThemeManager {
  constructor(options = {}) {
    // Base path for theme files (e.g., 'btdt/' or '../')
    this.basePath = options.basePath || '';
    // Ensure basePath ends with a slash if not empty
    if (this.basePath && !this.basePath.endsWith('/')) {
      this.basePath += '/';
    }

    // Available theme categories
    this.categories = {
      colors: [
        'ocean', 'sunset', 'forest',
        'lavender', 'corporate', 'candy',
        'white', 'gray-light', 'black', 'teal', 'rose', 'amber', 'mint', 'peach', 'sky',
        'nord', 'desert', 'plum',
        'midnight', 'volcano', 'olive', 'orchid',
        'arctic', 'citrus', 'coffee', 'gold',
        'slate', 'ink', 'neon', 'tropical'
      ],
      fonts: [
        'inter', 'merriweather', 'nunito', 'jetbrains-mono',
        'playfair-display', 'roboto-slab', 'quicksand', 'oswald',
        'montserrat', 'poppins', 'roboto', 'lora', 'raleway', 'fira-sans',
        'dm-sans', 'pt-serif', 'neucha', 'cabin-sketch', 'alfa-slab-one', 'bebas-neue'
      ],
      borders: ['normal', 'extra', 'none'],
      rounding: ['normal', 'extra', 'none'],
      shadows: ['normal', 'extra', 'none'],
      spacing: ['normal', 'large', 'small'],
      gradients: ['on', 'off'],
      accent: ['none', 'left', 'right', 'top', 'bottom']
    };

    // Available modes
    this.modes = ['light', 'dark'];

    // Current mode ('light' | 'dark')
    this._mode = 'light';

    // Current active theme
    this.activeTheme = {
      colors: null,
      fonts: null,
      borders: null,
      rounding: null,
      shadows: null,
      spacing: null,
      gradients: null,
      accent: null
    };

    // Predefined presets
    // List of available presets (filenames in themes/preset/)
    this.presets = [
      'studio', 'aurora', 'paper', 'retro',
      'noir', 'citrus', 'calm', 'wild',
      'sunset', 'neon', 'candy', 'forest', 'default'
    ];

    // Cache buster for theme CSS. Helps when iterating on theme files.
    this._cacheBust = String(Date.now());

    this._initContainer();
    this._initModeLink();
    this.loadFromStorage();
  }

  _withCacheBust(path) {
    if (!path) return path;
    const sep = path.includes('?') ? '&' : '?';
    return `${path}${sep}v=${this._cacheBust}`;
  }

  // Creates a container for theme CSS
  _initContainer() {
    // Use <head> directly so <link rel="stylesheet"> is always applied.
    // (Some browsers may ignore <link> nested inside a <div> in <head>.)
    const legacy = document.getElementById('theme-styles');
    if (legacy) legacy.remove();
    this.container = document.head;
  }

  // Creates the <link> placeholder for the dark mode CSS
  _initModeLink() {
    let link = document.getElementById('theme-mode');
    if (!link) {
      link = document.createElement('link');
      link.rel = 'stylesheet';
      link.id = 'theme-mode';
      link.setAttribute('data-theme-category', 'mode');
      // Disabled by default (light mode)
      link.disabled = true;
      link.href = this._withCacheBust(`${this.basePath}themes/modes/dark.css`);
      // Always last in <head> so it overrides
      document.head.appendChild(link);
    }
    this._modeLink = link;
  }

  // Helper to ensure path uses the correct base
  _resolvePath(relativePath) {
    return `${this.basePath}${relativePath}`;
  }

  // Category to file path mapping
  _getPath(category, value) {
    if (!value) return null;

    const pathMap = {
      colors:   `themes/colors/${value}.css`,
      fonts:    `themes/fonts/${value}.css`,
      borders:  `themes/styles/borders-${value}.css`,
      rounding: `themes/styles/rounding-${value}.css`,
      shadows:  `themes/styles/shadows-${value}.css`,
      spacing:  `themes/styles/spacing-${value}.css`,
      gradients:`themes/styles/gradients-${value}.css`,
      accent:   `themes/styles/accent-${value}.css`
    };

    return pathMap[category] ? this._resolvePath(pathMap[category]) : null;
  }

  // Load individual CSS by category
  _loadCSS(category, value) {
    // Remove previous of this category
    const existingLink = document.getElementById(`theme-${category}`);
    if (existingLink) {
      existingLink.remove();
    }

    if (!value) {
      this.activeTheme[category] = null;
      return;
    }

    const path = this._getPath(category, value);
    if (!path) return;

    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = this._withCacheBust(path);
    link.id = `theme-${category}`;
    link.setAttribute('data-theme-category', category);
    link.setAttribute('data-theme-value', value);

    this.container.appendChild(link);
    // Keep mode CSS last so it can override any theme CSS.
    if (this._modeLink) {
      document.head.appendChild(this._modeLink);
    }
    this.activeTheme[category] = value;
  }

  // ===== MODE API =====

  /**
   * Set the display mode.
   * @param {'light'|'dark'} mode
   */
  setMode(mode) {
    if (!this.modes.includes(mode)) {
      console.warn(`Mode "${mode}" is not valid. Use 'light' or 'dark'.`);
      return this;
    }
    this._mode = mode;

    if (mode === 'dark') {
      document.documentElement.setAttribute('data-mode', 'dark');
      this._modeLink.disabled = false;
    } else {
      document.documentElement.removeAttribute('data-mode');
      this._modeLink.disabled = true;
    }
    // Ensure mode CSS stays last in the cascade.
    if (this._modeLink) {
      document.head.appendChild(this._modeLink);
    }

    this._saveModeToStorage();
    this._dispatchEvent('mode', mode);
    return this;
  }

  /** Toggle between light and dark. */
  toggleMode() {
    return this.setMode(this._mode === 'dark' ? 'light' : 'dark');
  }

  /** Returns current mode string ('light' | 'dark'). */
  getMode() {
    return this._mode;
  }

  /** Load saved mode from localStorage. */
  loadModeFromStorage() {
    try {
      const saved = localStorage.getItem('bs-theme-mode');
      if (saved && this.modes.includes(saved)) {
        this.setMode(saved);
      }
    } catch (e) { /* silent */ }
    return this;
  }

  _saveModeToStorage() {
    try {
      localStorage.setItem('bs-theme-mode', this._mode);
    } catch (e) { /* silent */ }
  }

  // ===== PUBLIC API =====

  // Change single category
  set(category, value) {
    if (!this.categories[category]) {
      console.warn(`Category "${category}" does not exist`);
      return this;
    }
    if (value && !this.categories[category].includes(value)) {
      console.warn(`Value "${value}" is not valid for "${category}"`);
      return this;
    }

    // If a preset is active, "materialize" its values by loading individual
    // modules for everything EXCEPT the category we are changing.
    if (this.activeTheme._preset) {
      const currentValues = { ...this.activeTheme };
      this._removeActivePreset();
      
      Object.entries(currentValues).forEach(([cat, val]) => {
        if (cat !== '_preset' && cat !== category && val) {
          this._loadCSS(cat, val);
        }
      });
    }

    this._loadCSS(category, value);
    this._saveToStorage();
    this._dispatchEvent(category, value);
    return this; // Allows chaining
  }

  _removeActivePreset() {
    const link = document.getElementById('theme-preset');
    if (link) link.remove();
    this.activeTheme._preset = null;
  }

  /**
   * Apply complete preset via CSS file
   * High compatibility: uses computed styles to recover metadata (no CORS issues)
   */
  async applyPreset(presetName) {
    if (!this.presets.includes(presetName)) {
      console.warn(`Preset "${presetName}" does not exist`);
      return this;
    }

    const path = this._resolvePath(`themes/preset/${presetName}.css`);
    
    // 1. Clear individual styles
    Object.keys(this.activeTheme).forEach(cat => {
      if (cat !== '_preset') {
        const link = document.getElementById(`theme-${cat}`);
        if (link) link.remove();
        this.activeTheme[cat] = null;
      }
    });

    // 2. Load the preset CSS file
    let link = document.getElementById('theme-preset');
    if (!link) {
      link = document.createElement('link');
      link.id = 'theme-preset';
      link.rel = 'stylesheet';
      this.container.appendChild(link);
    }
    
    // Set href and wait for it to be applied
    link.href = this._withCacheBust(path);
    this.activeTheme._preset = presetName;

    // 3. Sync metadata from Computed Styles (Works in file://)
    return new Promise((resolve) => {
      // Give the browser enough time to load the CSS and apply imports
      setTimeout(() => {
        this._syncFromComputedStyles();
        this._saveToStorage();
        
        // Dispatch event so UI can update everything
        this._dispatchEvent('preset', presetName);
        resolve(this);
      }, 300); 
    }).then(() => {
      if (this._modeLink) {
        document.head.appendChild(this._modeLink);
      }
      return this;
    });
  }

  /**
   * Reads metadata from CSS variables defined in :root by the preset
   * Example: --preset-colors: "ocean";
   */
  _syncFromComputedStyles() {
    console.log("Syncing config from computed styles...");
    const styles = getComputedStyle(document.documentElement);
    
    Object.keys(this.activeTheme).forEach(cat => {
      if (cat === '_preset') return;
      
      const varName = `--preset-${cat}`;
      const value = styles.getPropertyValue(varName).trim().replace(/"/g, '').replace(/'/g, '');
      
      if (value && value !== 'initial' && value !== '') {
        this.activeTheme[cat] = value;
        console.log(`-> Recovered ${cat}: ${value}`);
      }
    });
  }

  // Apply complete custom config
  async applyConfig(config) {
    if (config._preset) {
      return await this.applyPreset(config._preset);
    }

    Object.entries(config).forEach(([category, value]) => {
      if (this.categories[category]) {
        this._loadCSS(category, value);
      }
    });

    this._saveToStorage();
    this._dispatchEvent('config', config);
    return this;
  }

  // Reset to Bootstrap default
  reset() {
    this._removeActivePreset();
    Object.keys(this.activeTheme).forEach(category => {
      if (category !== '_preset') {
        const link = document.getElementById(`theme-${category}`);
        if (link) link.remove();
        this.activeTheme[category] = null;
      }
    });

    this._saveToStorage();
    this._dispatchEvent('reset', null);
    return this;
  }

  // Get current configuration
  getConfig() {
    return { ...this.activeTheme };
  }

  // Generates CSS @import statements for a preset file
  generatePresetCSS() {
    const config = this.getConfig();
    let css = "/* Theme Preset - Save as themes/preset/custom.css */\n";
    
    Object.entries(config).forEach(([cat, val]) => {
      if (!val || cat === '_preset') return;
      
      let path = "";
      if (cat === 'colors') path = `../colors/${val}.css`;
      else if (cat === 'fonts') path = `../fonts/${val}.css`;
      else path = `../styles/${cat}-${val}.css`;
      
      css += `@import "${path}";\n`;
    });

    // Invisible metadata block for file:// compatibility
    css += `\n/* Metadata for the editor */\n`;
    css += `:root {\n`;
    Object.entries(config).forEach(([cat, val]) => {
      if (!val || cat === '_preset') return;
      css += `  --preset-${cat}: "${val}";\n`;
    });
    css += `}\n`;
    
    return css;
  }

  // Get list of presets
  getPresets() {
    return this.presets;
  }

  // Add custom preset
  addPreset(name) {
    if (!this.presets.includes(name)) {
      this.presets.push(name);
    }
    return this;
  }

  // Save to localStorage
  _saveToStorage() {
    try {
      localStorage.setItem(
        'bs-theme-config',
        JSON.stringify(this.activeTheme)
      );
    } catch (e) { /* silent */ }
  }

  // Load from localStorage
  loadFromStorage() {
    try {
      const saved = localStorage.getItem('bs-theme-config');
      if (saved) {
        const config = JSON.parse(saved);
        this.applyConfig(config);
      }
    } catch (e) { /* silent */ }
    this.loadModeFromStorage();
    return this;
  }

  // Custom event
  _dispatchEvent(category, value) {
    window.dispatchEvent(new CustomEvent('themechange', {
      detail: {
        category,
        value,
        fullConfig: this.getConfig()
      }
    }));
  }
}

// Export for module systems or use as a global class
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ThemeManager;
} else {
  window.ThemeManager = ThemeManager;
}
