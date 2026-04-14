# BTDT Scripts

This directory contains maintenance and build utilities for the `btdt/` module.

## Installation

Most utilities in `btdt/scripts/` use only Python's standard library and can be
run directly with `python3`.

The only utility that currently requires a virtual environment is
`btdt/scripts/minify.py`. Its dependencies are installed in the shared
`btdt/scripts/.venv` environment so future Python utilities can reuse the same
setup if needed.

Install it with:

```bash
python3 -m venv btdt/scripts/.venv
source btdt/scripts/.venv/bin/activate
pip install -r btdt/scripts/requirements.txt
```

Available scripts:

- `add-fonts.py`
- `download_google_fonts.py`
- `export-runtime.py`
- `minify.py`
- `minify-all`
- `minify-all.py`
- `sync-configs.py`
- `sync-fonts.py`

## `export-runtime.py`

Utility to export the minimal BTDT runtime asset subset into another directory.

File:

- [`export-runtime.py`](export-runtime.py)

### Purpose

`export-runtime.py` creates or updates `DESTINATION/btdt/` and copies only:

- the project root `README.md` as `DESTINATION/btdt/README.md`
- `btdt/css/bootstrap.min.css`
- `btdt/js/bootstrap.bundle.min.js`
- `btdt/js/btdt.min.js`
- `btdt/themes/modes/dark.min.css`
- `btdt/themes/preset/*.min.css`
- `btdt/fonts/*/*` (only fonts used by the selected presets)

It preserves the relative directory structure inside the exported `btdt/` folder.

Examples:

```bash
# Export all presets and all fonts (full export)
python3 btdt/scripts/export-runtime.py tmp/runtime-export

# Export only specific presets with their required fonts only
python3 btdt/scripts/export-runtime.py tmp/runtime-export --presets nordic-elegance,amber-roar
python3 btdt/scripts/export-runtime.py tmp/runtime-export --presets amber-roar --force

# Dry run to preview what would be copied
python3 btdt/scripts/export-runtime.py tmp/runtime-export --dry-run
python3 btdt/scripts/export-runtime.py tmp/runtime-export --presets amber-roar --dry-run
```

### Notes

- This script uses only Python's standard library
- `tmp/` is a good default destination for local preview exports because the repo ignores its contents
- The destination argument is the parent directory; the script creates `DESTINATION/btdt/`
- If `DESTINATION/btdt/` already exists, the script does nothing unless `--force` is passed
- With `--force`, existing files in the destination are overwritten only for the exported subset
- With `--presets`, only the specified presets are exported, and only the fonts they use are included

## `download_google_fonts.py`

Utility to download Google Fonts for local hosting with licenses.

File:

- [`download_google_fonts.py`](download_google_fonts.py)

### Purpose

`download_google_fonts.py` downloads individual Google Fonts with all their weights and variants for local hosting. It:

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
python3 btdt/scripts/download_google_fonts.py "Font Name"
```

Example:

```bash
python3 btdt/scripts/download_google_fonts.py "Inter"
python3 btdt/scripts/download_google_fonts.py "Roboto Slab"
python3 btdt/scripts/download_google_fonts.py "Playfair Display"
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

## `sync-fonts.py`

Utility to synchronize fonts from themes with local font files.

File:

- [`sync-fonts.py`](sync-fonts.py)

### Purpose

`sync-fonts.py` scans `btdt/themes/fonts/` for font CSS files, checks if corresponding font files exist in `btdt/fonts/`, and downloads missing fonts using `download_google_fonts.py`.

This is typically used when:
- Setting up a new development environment
- Synchronizing after adding new fonts to themes
- Updating font files after theme changes

### Usage

```bash
python3 btdt/scripts/sync-fonts.py
python3 btdt/scripts/sync-fonts.py --dry-run
```

### What it does

1. Scans `btdt/themes/fonts/*.css` for font imports
2. Supports both old format (Google Fonts CDN) and new format (local files)
3. Checks if each font exists in `btdt/fonts/[slug]/`
4. Downloads missing fonts automatically
5. Reports which fonts are already present vs missing

### Notes

- This script uses only Python's standard library
- Uses `--dry-run` to preview what would be downloaded without actually downloading
- Automatically imports and uses `download_google_fonts.py` for downloads
- Handles both WOFF2 and TrueType font formats

## `add-fonts.py`

Utility to add a new font to BTDT system in one step.

File:

- [`add-fonts.py`](add-fonts.py)

### Purpose

`add-fonts.py` combines downloading font files and creating theme CSS into a single command. It:

- Downloads font files if not already present
- Creates theme CSS file if not already present
- Reports status of each step

This is the recommended way to add new fonts to BTDT.

### Usage

```bash
python3 btdt/scripts/add-fonts.py "Font Name"
```

Example:

```bash
python3 btdt/scripts/add-fonts.py "Inter"
python3 btdt/scripts/add-fonts.py "Playfair Display"
```

### What it does

1. Checks if font files exist in `btdt/fonts/[slug]/`
2. If missing, downloads using `download_google_fonts.py`
3. Checks if theme CSS exists in `btdt/themes/fonts/[slug].css`
4. If missing, creates CSS that imports local font with Bootstrap variable mappings
5. Shows next steps (sync-configs.py and minify-all.py)

### Output

```
Adding font: Inter (inter)

✓ Font files already exist: btdt/fonts/inter

✓ Theme CSS already exists: btdt/themes/fonts/inter.css

==================================================
Font added successfully!

Next steps:
1. Run: python3 btdt/scripts/sync-configs.py
2. Run: python3 btdt/scripts/minify-all.py
```

### Notes

- This script uses only Python's standard library
- Safe to run multiple times - won't overwrite existing files
- Font name is case-sensitive (use exact name from Google Fonts)
- Automatically imports and uses `download_google_fonts.py`

## `minify.py`

Utility to generate minified assets from source files.

> [!IMPORTANT]
> This tool is designed specifically for the BTDT project structure and preset format. It is not intended to be a generic CSS/JS minification or bundling utility.

Files:

- [`minify.py`](minify.py)
- [`requirements.txt`](requirements.txt)
- [`minify-all`](minify-all)
- [`minify-all.py`](minify-all.py)

### Purpose

`minify.py` supports two modes:

- `normal`: minifies source `.js` and `.css` files into `.min.js` and `.min.css`
- `preset`: compiles preset CSS files by resolving and embedding their `@import` dependencies first, then minifies the final bundled result

### Requirements

From the project root:

```bash
source btdt/scripts/.venv/bin/activate
pip install -r btdt/scripts/requirements.txt
```

Dependencies:

- `rjsmin`
- `rcssmin`

### Usage

Run from `btdt/scripts/`:

```bash
source .venv/bin/activate
python minify.py normal <file-or-directory>
python minify.py preset <file-or-directory>
```

Examples:

```bash
python btdt/scripts/minify.py normal btdt/js/btdt.js
python btdt/scripts/minify.py normal btdt/themes/styles
python btdt/scripts/minify.py preset btdt/themes/preset/amber-roar.css
python btdt/scripts/minify.py preset btdt/themes/preset
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

It also emits warnings when it finds mismatches or modules that do not follow the conventions documented in `.agents/skills/`.

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
