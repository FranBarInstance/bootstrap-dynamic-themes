# BTDT Scripts

This directory contains maintenance and build utilities for the `btdt/` module.

Available scripts:

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
