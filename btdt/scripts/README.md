# BTDT Scripts

This directory contains maintenance and build utilities for the `btdt/` module.

Available scripts:

- `download-google-fonts.py`
- `export-runtime.py`
- `minify/`
- `minify-all`
- `minify-all.py`
- `sync-configs.py`

## `export-runtime.py`

Utility to export the minimal BTDT runtime asset subset into another directory.

File:

- [`export-runtime.py`](export-runtime.py)

### Purpose

`export-runtime.py` creates or updates `DESTINATION/btdt/` and copies only:

- `README.md` de la raíz del proyecto como `DESTINATION/btdt/README.md`
- `btdt/css/bootstrap.min.css`
- `btdt/js/bootstrap.bundle.min.js`
- `btdt/js/btdt.min.js`
- `btdt/themes/modes/dark.min.css`
- `btdt/themes/preset/*.min.css`

It preserves the relative directory structure inside the exported `btdt/` folder.

Examples:

```bash
python3 btdt/scripts/export-runtime.py /tmp/runtime-export
python3 btdt/scripts/export-runtime.py /tmp/runtime-export --force
python3 btdt/scripts/export-runtime.py /tmp/runtime-export --dry-run
```

### Notes

- This script uses only Python's standard library
- The destination argument is the parent directory; the script creates `DESTINATION/btdt/`
- If `DESTINATION/btdt/` already exists, the script does nothing unless `--force` is passed
- With `--force`, existing files in the destination are overwritten only for the exported subset

## `download-google-fonts.py`

Utility to download Google Fonts for local hosting with licenses.

File:

- [`download-google-fonts.py`](download-google-fonts.py)

### Purpose

`download-google-fonts.py` downloads individual Google Fonts with all their weights and variants for local hosting. It:

- Fetches font metadata from Google Fonts API
- Downloads all variants (supports variable font ranges like 100..900)
- Saves WOFF2 or TrueType files to `btdt/fonts/[font-slug]/`
- Downloads the original OFL license from Google Fonts GitHub repository
- Generates local CSS with @font-face rules

This is typically used when:
- Adding a new font to BTDT for offline/air-gapped environments
- Preparing fonts for production with local file hosting
- Reducing external CDN dependencies

### Usage

```bash
python3 btdt/scripts/download-google-fonts.py "Font Name"
```

Example:

```bash
python3 btdt/scripts/download-google-fonts.py "Inter"
python3 btdt/scripts/download-google-fonts.py "Roboto Slab"
python3 btdt/scripts/download-google-fonts.py "Playfair Display"
```

### What it does

1. Fetches CSS from Google Fonts API using variable weight range (100..900)
2. Parses @font-face rules for each weight and style
3. Downloads font files (WOFF2 or TrueType) from Google Fonts servers
4. Saves to `btdt/fonts/[slug]/` directory
5. Downloads OFL license from `github.com/google/fonts` repository
6. Generates `[slug].css` with local @font-face rules pointing to downloaded files

### Output structure

```
btdt/fonts/
└── inter/
    ├── inter-100-normal.woff2
    ├── inter-400-normal.woff2
    ├── inter-700-normal.woff2
    ├── inter.css
    └── LICENSE.txt
```

### Notes

- This script uses only Python's standard library
- The font name is case-sensitive (use the exact name from Google Fonts)
- Supports both WOFF2 and TrueType formats (detected automatically from CSS)
- Variable font ranges (e.g., 100..900) are expanded to individual weights
- License is downloaded from the official Google Fonts GitHub repository
- If license download fails, a reference file with links is created instead

## `minify/`

Utility to generate minified assets from source files.

> [!IMPORTANT]
> This tool is designed specifically for the BTDT project structure and preset format. It is not intended to be a generic CSS/JS minification or bundling utility.

Files:

- [`minify.py`](minify/minify.py)
- [`requirements.txt`](minify/requirements.txt)
- [`minify-all`](minify-all)
- [`minify-all.py`](minify-all.py)

### Purpose

`minify.py` supports two modes:

- `normal`: minifies source `.js` and `.css` files into `.min.js` and `.min.css`
- `preset`: compiles preset CSS files by resolving and embedding their `@import` dependencies first, then minifies the final bundled result

### Requirements

From `btdt/scripts/minify/`:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencies:

- `rjsmin`
- `rcssmin`

### Usage

Run from `btdt/scripts/minify/`:

```bash
source .venv/bin/activate
python minify.py normal <file-or-directory>
python minify.py preset <file-or-directory>
```

Examples:

```bash
python minify.py normal ../../js/btdt.js
python minify.py normal ../../themes/styles
python minify.py preset ../../themes/preset/amber-roar.css
python minify.py preset ../../themes/preset
```

### Modes

#### `normal`

- Accepts a single file or a directory
- Processes `.js` and `.css`
- Skips files already ending in `.min.js` or `.min.css`
- Writes minified output next to the source file

#### `preset`

- Accepts a single preset CSS file or a directory of preset CSS files
- Only processes `.css`
- Resolves recursive `@import "..."` statements
- Embeds imported CSS into one final stylesheet
- Moves any remaining `@import` rules to the top of the final stylesheet before minifying
- Minifies the bundled result into a `.min.css` file next to the source preset

### Notes

- The script skips common non-source directories such as `.git`, `node_modules`, `__pycache__`, and `.venv`
- In `preset` mode, circular imports are detected and reported as an error
- `--help` works even if dependencies are not installed yet
- `minify-all` is the Bash wrapper for running the full BTDT minification pass
- `minify-all.py` is the Python wrapper equivalent for running the full BTDT minification pass

## `sync-configs.py`

Utility to regenerate the BTDT catalog files in `btdt/js/` from the actual contents of `btdt/themes/`.

File:

- [`sync-configs.py`](sync-configs.py)

### Purpose

`sync-configs.py` rebuilds:

- `btdt/js/config-colors.js`
- `btdt/js/config-fonts.js`
- `btdt/js/config-presets.js`
- `btdt/js/config-ui.js`

It does **not** rewrite the corresponding `.min.js` files. Those remain under the minification workflow.

It also emits warnings when it finds mismatches or modules that do not follow the conventions documented in `.agent/skills/`.

Examples:

```bash
python3 btdt/scripts/sync-configs.py
python3 btdt/scripts/sync-configs.py --check
```

### What it validates

- Color modules expose the expected primary, secondary, and accent variables
- Font modules define the required body typography variables
- Presets declare the expected 11 imports and metadata keys
- Style modules follow recognized naming conventions
- Existing config catalogs do not drift away from the files actually present on disk

### Notes

- This script uses only Python's standard library
- `--check` validates and reports warnings without writing any file
- Only the source `config-*.js` files are regenerated
