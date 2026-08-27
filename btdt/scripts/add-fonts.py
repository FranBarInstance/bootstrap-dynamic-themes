#!/usr/bin/env python3
"""Add a new font to BTDT system."""

import argparse
import re
import sys
import urllib.error
from pathlib import Path


def slugify(name: str) -> str:
    """Convert font name to slug (lowercase, hyphens)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def font_exists(fonts_dir: Path, slug: str) -> bool:
    """Check if font files are already downloaded."""
    font_dir = fonts_dir / slug
    return font_dir.exists() and (font_dir / f"{slug}.css").exists() and bool(
        any(font_dir.glob("*.woff2")) or any(font_dir.glob("*.ttf"))
    )


def theme_css_exists(themes_fonts_dir: Path, slug: str) -> bool:
    """Check if theme CSS file already exists."""
    return (themes_fonts_dir / f"{slug}.css").exists()


def create_theme_css(themes_fonts_dir: Path, slug: str, font_name: str) -> Path:
    """Create the theme CSS file that imports the local font."""
    css_path = themes_fonts_dir / f"{slug}.css"
    css_content = f"""/*! See license: https://github.com/FranBarInstance/bootstrap-dynamic-themes */
/* themes/fonts/{slug}.css */
@import url('../../fonts/{slug}/{slug}.css');

:root {{
  --bs-body-font-family: '{font_name}', -apple-system, BlinkMacSystemFont, sans-serif;
  --bs-body-font-weight: 400;
  --bs-body-line-height: 1.6;
  font-synthesis: none;
}}

/* Keep the source font's available weights; do not synthesize bold/light. */
body,
.btn,
.form-label {{
  font-family: '{font_name}', sans-serif;
  font-weight: 400;
}}

h1, h2, h3, h4, h5, h6,
.h1, .h2, .h3, .h4, .h5, .h6,
.display-1, .display-2, .display-3,
.display-4, .display-5, .display-6,
.navbar-brand {{
  font-family: '{font_name}', sans-serif;
  font-weight: 400;
  letter-spacing: -0.02em;
}}

.btn {{
  letter-spacing: 0.01em;
}}
"""
    css_path.write_text(css_content, encoding="utf-8")
    return css_path


def add_font(font_name: str, base_dir: Path) -> int:
    """Add a new font to BTDT."""
    slug = slugify(font_name)
    fonts_dir = base_dir / "btdt" / "fonts"
    themes_fonts_dir = base_dir / "btdt" / "themes" / "fonts"
    print(f"Adding font: {font_name} ({slug})")

    if not font_exists(fonts_dir, slug):
        sys.path.insert(0, str(base_dir / "btdt" / "scripts"))
        from download_google_fonts import DownloadFontError, download_font
        try:
            download_font(font_name, base_dir)
        except (DownloadFontError, OSError, urllib.error.URLError) as exc:
            print(f"Error downloading font: {exc}")
            return 1

    if not theme_css_exists(themes_fonts_dir, slug):
        create_theme_css(themes_fonts_dir, slug, font_name)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a new font to BTDT system")
    parser.add_argument("font_name", help='Font name from Google Fonts')
    parser.add_argument("--base-dir", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    return add_font(args.font_name, args.base_dir)


if __name__ == "__main__":
    raise SystemExit(main())
