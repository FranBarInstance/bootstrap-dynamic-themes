# BTDT Scripts

This directory contains maintenance and build utilities for the `btdt/` module.

Available scripts:

- `minify/`
- `sync-configs.py`

## `minify/`

Utility to generate minified assets from source files.

> [!IMPORTANT]
> This tool is designed specifically for the BTDT project structure and preset format. It is not intended to be a generic CSS/JS minification or bundling utility.

Files:

- [`minify.py`](minify/minify.py)
- [`requirements.txt`](minify/requirements.txt)

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
