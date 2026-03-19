# BTDT Scripts

This directory contains maintenance and build utilities for the `btdt/` module.

For now, the available script is:

- `minify/`

## `minify/`

Utility to generate minified assets from source files.

> [!IMPORTANT]
> This tool is designed specifically for the BTDT project structure and preset format. It is not intended to be a generic CSS/JS minification or bundling utility.

Files:

- [`minify.py`](/home/enrique/trabajos/proyectos/bootstrap-dynamic-themes/btdt/scripts/minify/minify.py)
- [`requirements.txt`](/home/enrique/trabajos/proyectos/bootstrap-dynamic-themes/btdt/scripts/minify/requirements.txt)

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
