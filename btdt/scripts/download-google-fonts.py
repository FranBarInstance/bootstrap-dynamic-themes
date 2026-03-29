#!/usr/bin/env python3
"""Download Google Fonts for local hosting with licenses.

Supports variable font ranges (e.g., 100..900) and both WOFF2/TrueType formats.
"""

import argparse
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


def slugify(name: str) -> str:
    """Convert font name to slug (lowercase, hyphens)."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_css(url: str) -> str:
    """Fetch CSS from Google Fonts API."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def download_font_file(url: str, dest: Path) -> None:
    """Download a font file to destination."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        dest.write_bytes(resp.read())


def parse_font_faces(css: str) -> list[dict]:
    """Parse @font-face rules from Google Fonts CSS."""
    faces = []
    pattern = r"@font-face\s*\{([^}]+)\}"
    for match in re.finditer(pattern, css, re.DOTALL):
        block = match.group(1)
        font_face = {}

        family_match = re.search(r"font-family:\s*['\"]?([^;'\"]+)['\"]?", block)
        if family_match:
            font_face["family"] = family_match.group(1).strip()

        weight_match = re.search(r"font-weight:\s*(\d+)", block)
        font_face["weight"] = weight_match.group(1) if weight_match else "400"

        style_match = re.search(r"font-style:\s*(\w+)", block)
        font_face["style"] = style_match.group(1) if style_match else "normal"

        url_match = re.search(r"url\(([^)]+)\)\s*format\(['\"]?woff2['\"]?\)", block)
        if url_match:
            font_face["url"] = url_match.group(1).strip("'\"")
            font_face["format"] = "woff2"
        else:
            url_match = re.search(r"url\(([^)]+)\)\s*format\(['\"]?truetype['\"]?\)", block)
            if url_match:
                font_face["url"] = url_match.group(1).strip("'\"")
                font_face["format"] = "truetype"

        if "url" in font_face:
            faces.append(font_face)

    return faces


def download_license(slug: str, dest: Path, original_name: str = "") -> bool:
    """Download OFL license from Google Fonts GitHub repository."""
    # Try different variations of the font name
    slugs_to_try = [slug]
    if original_name:
        slugs_to_try.insert(0, slugify(original_name).lower())
    # Also try the original slug with hyphens as-is
    slugs_to_try.append(slug.lower())

    for try_slug in slugs_to_try:
        # Try to download the actual OFL.txt from Google Fonts GitHub repo
        github_urls = [
            f"https://raw.githubusercontent.com/google/fonts/main/ofl/{try_slug}/OFL.txt",
            f"https://raw.githubusercontent.com/google/fonts/main/apache/{try_slug}/LICENSE.txt",
            f"https://raw.githubusercontent.com/google/fonts/main/ufl/{try_slug}/UFL.txt",
        ]

        for url in github_urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read().decode("utf-8")
                    dest.write_text(content, encoding="utf-8")
                    return True
            except urllib.error.HTTPError:
                continue
            except urllib.error.URLError:
                continue

    # If all failed, create a reference file
    print("  Warning: Could not download license from GitHub, creating reference file")
    ref_text = f"""Font: {slug}
Source: https://fonts.google.com/specimen/{slug.replace('-', '+')}

This font is available on Google Fonts. Please visit the specimen page above
to view the license information (typically SIL Open Font License 1.1).

For license details, see:
- https://github.com/google/fonts/tree/main/ofl/{slug}/
- https://scripts.sil.org/OFL
"""
    dest.write_text(ref_text, encoding="utf-8")
    return False


def download_font(font_name: str, base_dir: Path) -> Path:
    """Download a Google Font and generate local CSS with license."""
    slug = slugify(font_name)
    fonts_dir = base_dir / "btdt" / "fonts" / slug
    css_path = fonts_dir / f"{slug}.css"
    license_path = fonts_dir / "LICENSE.txt"

    print(f"Downloading font: {font_name} ({slug})")

    encoded_name = font_name.replace(" ", "+")
    google_url = f"https://fonts.googleapis.com/css2?family={encoded_name}:wght@100..900&display=swap"

    print(f"Fetching: {google_url}")

    try:
        css = fetch_css(google_url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Error: Font '{font_name}' not found on Google Fonts")
        else:
            print(f"Error fetching font: {e}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error fetching font: {e}")
        sys.exit(1)

    font_faces = parse_font_faces(css)

    if not font_faces:
        print("ERROR: Could not find any font files to download")
        sys.exit(1)

    fonts_dir.mkdir(parents=True, exist_ok=True)

    local_font_faces = []
    for face in font_faces:
        url = face["url"]
        if url.startswith("//"):
            url = "https:" + url
        elif url.startswith("/"):
            url = urljoin(google_url, url)

        fmt = face.get("format", "woff2")
        ext = ".woff2" if fmt == "woff2" else ".ttf"
        filename = f"{slug}-{face['weight']}-{face['style']}{ext}"
        file_path = fonts_dir / filename

        print(f"  Downloading: {face['weight']} {face['style']} -> {filename}")
        try:
            download_font_file(url, file_path)
        except urllib.error.URLError as e:
            print(f"  Error downloading: {e}")
            continue

        local_font_faces.append({
            "family": face["family"],
            "weight": face["weight"],
            "style": face["style"],
            "filename": filename,
            "format": fmt,
        })

    # Generate local CSS
    css_lines = [f"/* {font_name} - Downloaded from Google Fonts */", ""]

    for face in local_font_faces:
        fmt = face.get("format", "woff2")
        css_lines.extend([
            "@font-face {",
            f"  font-family: '{face['family']}';",
            f"  font-style: {face['style']};",
            f"  font-weight: {face['weight']};",
            "  font-display: swap;",
            f"  src: url({face['filename']}) format('{fmt}');",
            "}",
            "",
        ])

    css_path.write_text("\n".join(css_lines), encoding="utf-8")
    print(f"\nGenerated CSS: {css_path}")

    # Download license
    download_license(font_name, license_path)
    print(f"License: {license_path}")

    return fonts_dir


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download Google Fonts for local hosting with licenses"
    )
    parser.add_argument(
        "font_name",
        help='Font name (e.g., "Inter", "Roboto Slab")',
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Base directory of the project",
    )

    args = parser.parse_args()

    fonts_dir = download_font(args.font_name, args.base_dir)

    print(f"\nSuccess! Font downloaded to: {fonts_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
