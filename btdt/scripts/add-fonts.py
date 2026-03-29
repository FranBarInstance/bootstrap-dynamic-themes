#!/usr/bin/env python3
"""Add a new font to BTDT system.

Downloads the font files and creates the theme CSS file if they don't exist.
Usage: python3 add-fonts.py "Font Name"
"""

import argparse
import re
import sys
import urllib.error
from pathlib import Path


def slugify(name: str) -> str:
    """Convert font name to slug (lowercase, hyphens)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def font_exists(fonts_dir: Path, slug: str) -> bool:
    """Check if font is already downloaded."""
    font_dir = fonts_dir / slug
    if not font_dir.exists():
        return False
    has_css = (font_dir / f"{slug}.css").exists()
    has_fonts = any(font_dir.glob("*.woff2")) or any(font_dir.glob("*.ttf"))
    return has_css and has_fonts


def theme_css_exists(themes_fonts_dir: Path, slug: str) -> bool:
    """Check if theme CSS file already exists."""
    return (themes_fonts_dir / f"{slug}.css").exists()


def create_theme_css(themes_fonts_dir: Path, slug: str, font_name: str) -> Path:
    """Create the theme CSS file that imports local font."""
    css_path = themes_fonts_dir / f"{slug}.css"

    css_content = f'''/*! See license: https://github.com/FranBarInstance/bootstrap-dynamic-themes */
/* themes/fonts/{slug}.css */
@import url('../../fonts/{slug}/{slug}.css');

:root {{
  --bs-body-font-family: '{font_name}', -apple-system, BlinkMacSystemFont, sans-serif;
  --bs-body-font-weight: 400;
  --bs-body-line-height: 1.6;
}}

h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6 {{
  font-family: '{font_name}', sans-serif;
  font-weight: 700;
  letter-spacing: -0.02em;
}}

.display-1, .display-2, .display-3,
.display-4, .display-5, .display-6 {{
  font-weight: 300;
  letter-spacing: -0.03em;
}}

.btn {{
  font-family: '{font_name}', sans-serif;
  font-weight: 500;
  letter-spacing: 0.01em;
}}

.navbar-brand {{
  font-weight: 700;
  letter-spacing: -0.02em;
}}

.form-label {{
  font-weight: 500;
}}
'''

    css_path.write_text(css_content, encoding="utf-8")
    return css_path


def add_font(font_name: str, base_dir: Path) -> int:
    """Add a font to BTDT system."""
    slug = slugify(font_name)
    fonts_dir = base_dir / "btdt" / "fonts"
    themes_fonts_dir = base_dir / "btdt" / "themes" / "fonts"

    print(f"Adding font: {font_name} ({slug})")
    print()

    # Check if font files exist
    if font_exists(fonts_dir, slug):
        print(f"✓ Font files already exist: {fonts_dir / slug}")
    else:
        print("✗ Font files missing - downloading...")
        # Import and use download function
        # pylint: disable=import-error,import-outside-toplevel
        sys.path.insert(0, str(base_dir / "btdt" / "scripts"))
        from download_google_fonts import download_font
        try:
            download_font(font_name, base_dir)
            print("✓ Font downloaded successfully")
        except (OSError, urllib.error.URLError) as e:
            print(f"✗ Error downloading font: {e}")
            return 1

    print()

    # Check if theme CSS exists
    if theme_css_exists(themes_fonts_dir, slug):
        print(f"✓ Theme CSS already exists: {themes_fonts_dir / f'{slug}.css'}")
    else:
        print("✗ Theme CSS missing - creating...")
        css_path = create_theme_css(themes_fonts_dir, slug, font_name)
        print(f"✓ Theme CSS created: {css_path}")

    print()
    print("=" * 50)
    print("Font added successfully!")
    print()
    print("Next steps:")
    print("1. Run: python3 btdt/scripts/sync-configs.py")
    print("2. Run: python3 btdt/scripts/minify-all.py")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add a new font to BTDT system"
    )
    parser.add_argument(
        "font_name",
        help='Font name from Google Fonts (e.g., "Inter", "Roboto Slab")',
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Base directory of the project",
    )

    args = parser.parse_args()

    return add_font(args.font_name, args.base_dir)


if __name__ == "__main__":
    raise SystemExit(main())
