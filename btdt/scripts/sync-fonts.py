#!/usr/bin/env python3
"""Synchronize all fonts from themes with local font files.

Scans btdt/themes/fonts/ for font CSS files, checks if corresponding
font files exist in btdt/fonts/, and downloads missing fonts.
"""

import argparse
import re
import sys
import urllib.error
from pathlib import Path


def slugify(name: str) -> str:
    """Convert font name to slug (lowercase, hyphens)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def extract_fonts_from_css(css_path: Path) -> set[str]:
    """Extract all font names used in a CSS file.

    Includes fonts from:
    - @import url (local or Google Fonts)
    - font-family declarations in CSS rules

    Returns set of font names (e.g., 'PT Sans', 'Inter')
    """
    content = css_path.read_text(encoding="utf-8")
    fonts = set()

    # Try local format first: @import url('../../fonts/slug/slug.css')
    local_match = re.search(
        r"@import\s+url\(['\"]?[^'\"]*/fonts/([^/'\"]+)/[^'\"]+\.css['\"]?\)",
        content
    )
    if local_match:
        slug = local_match.group(1)
        fonts.add(slug.replace("-", " ").title())

    # Try old Google Fonts format
    google_match = re.search(
        r"@import\s+url\(['\"]?https://fonts\.googleapis\.com/css2\?family=([^:&'\"]+)",
        content
    )
    if google_match:
        name = google_match.group(1).replace("+", " ").strip()
        fonts.add(name)

    # Extract all font-family declarations
    # Match font-family: 'Font Name', ... or font-family: "Font Name", ...
    for match in re.finditer(r"font-family:\s*['\"]?([^;'\"]+)['\"]?", content):
        font_list = match.group(1)
        # Split by comma and extract first font (the primary one)
        primary_font = font_list.split(',')[0].strip().strip("'\"")
        # Skip generic font families
        if primary_font.lower() not in {'sans-serif', 'serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'inherit', 'initial', 'unset'}:
            # Skip system fonts
            system_fonts = {'-apple-system', 'blinkmacsystemfont', 'segoe ui', 'roboto', 'helvetica neue', 'arial', 'noto sans', 'apple color emoji', 'segoe ui emoji', 'segoe ui symbol', 'noto color emoji'}
            if primary_font.lower() not in system_fonts:
                fonts.add(primary_font)

    return fonts


def get_required_fonts(themes_fonts_dir: Path) -> dict[str, str]:
    """Get all fonts required by theme CSS files.

    Returns dict mapping slug -> font_name
    """
    fonts = {}

    for css_file in themes_fonts_dir.glob("*.css"):
        # Skip minified files
        if css_file.name.endswith(".min.css"):
            continue
        # Skip default.css which doesn't import a font
        if css_file.name == "default.css":
            continue

        font_names = extract_fonts_from_css(css_file)
        for font_name in font_names:
            slug = slugify(font_name)
            fonts[slug] = font_name

    return fonts


def is_font_downloaded(fonts_dir: Path, slug: str) -> bool:
    """Check if a font is already downloaded."""
    font_dir = fonts_dir / slug
    if not font_dir.exists():
        return False

    # Check if there's at least one font file and CSS
    has_css = (font_dir / f"{slug}.css").exists()
    has_font_files = any(font_dir.glob("*.woff2")) or any(font_dir.glob("*.ttf"))

    return has_css and has_font_files


def sync_fonts(base_dir: Path, dry_run: bool = False) -> int:
    """Synchronize fonts - download missing ones."""
    themes_fonts_dir = base_dir / "btdt" / "themes" / "fonts"
    fonts_dir = base_dir / "btdt" / "fonts"

    if not themes_fonts_dir.exists():
        print(f"Error: Themes fonts directory not found: {themes_fonts_dir}")
        return 1

    # Get required fonts from themes
    required = get_required_fonts(themes_fonts_dir)
    print(f"Found {len(required)} fonts in themes")

    # Check which are missing
    missing = []
    for slug, name in sorted(required.items()):
        if is_font_downloaded(fonts_dir, slug):
            print(f"  ✓ {name} ({slug}) - already downloaded")
        else:
            print(f"  ✗ {name} ({slug}) - MISSING")
            missing.append((slug, name))

    if not missing:
        print("\nAll fonts are already synchronized!")
        return 0

    print(f"\n{len(missing)} font(s) need to be downloaded")

    if dry_run:
        print("\nDry run - not downloading. Use without --dry-run to download.")
        return 0

    # Import download function from download-google-fonts
    # pylint: disable=import-error,import-outside-toplevel
    sys.path.insert(0, str(base_dir / "btdt" / "scripts"))
    from download_google_fonts import download_font

    # Download missing fonts
    success = 0
    failed = 0

    for slug, name in missing:
        print(f"\nDownloading: {name}")
        try:
            download_font(name, base_dir)
            success += 1
        except (OSError, urllib.error.URLError) as e:
            print(f"  Error: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Downloaded: {success}")
    print(f"Failed: {failed}")
    print(f"Total: {len(missing)}")

    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize fonts from themes with local font files"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Base directory of the project",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be downloaded without actually downloading",
    )

    args = parser.parse_args()

    return sync_fonts(args.base_dir, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
