#!/usr/bin/env python3
"""Export the minimal BTDT runtime asset subset into a destination directory."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BTDT_DIR = ROOT / "btdt"

STATIC_FILES = [
    Path("css/bootstrap.min.css"),
    Path("js/bootstrap.bundle.min.js"),
    Path("js/btdt.min.js"),
    Path("themes/modes/dark.min.css"),
]
PRESET_GLOB = "themes/preset/*.min.css"
FONTS_GLOB = "fonts/*/*"
ROOT_README = ROOT / "README.md"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Copy the minimal BTDT runtime asset subset into DESTINATION/btdt, "
            "preserving the internal directory structure."
        )
    )
    parser.add_argument(
        "destination",
        help="Directory where the script will create or update the nested btdt/ folder.",
    )
    parser.add_argument(
        "--presets",
        metavar="PRESET1,PRESET2,...",
        help="Comma-separated list of preset names to export (e.g., 'nordic-elegance,default'). If omitted, all presets are exported.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the files that would be copied without writing anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing DESTINATION/btdt export.",
    )
    return parser.parse_args()


def extract_fonts_from_preset(preset_path: Path) -> set[str]:
    """Extract font names used in a preset CSS file.

    Analyzes both @import statements and @font-face rules to detect fonts.
    """
    fonts: set[str] = set()
    content = preset_path.read_text(encoding="utf-8")

    # Look for @import "../fonts/fontname.css" patterns
    import_pattern = re.compile(
        r'@import\s+["\']\.\.?/fonts/([^"\']+)\.css["\']',
        re.IGNORECASE
    )
    for match in import_pattern.finditer(content):
        fonts.add(match.group(1))

    # Look for font files referenced in @font-face src:url() paths
    # Matches patterns like: url(../fonts/../../fonts/nunito/nunito-400.ttf)
    # or url(nunito-400.ttf) - extracting the folder name if present
    font_path_pattern = re.compile(
        r'src:\s*url\([^)]*fonts/([^/)]+)/[^)]+\.\w+\)',
        re.IGNORECASE
    )
    for match in font_path_pattern.finditer(content):
        fonts.add(match.group(1))

    # Also detect fonts referenced directly in font-family declarations
    # like: --bs-body-font-family:'Work Sans',... or font-family:'Montserrat',...
    font_family_pattern = re.compile(
        r"(?:font-family|var\(--bs-body-font-family\))\s*:\s*['\"]?([^,'\"]{2,})['\"]?",
        re.IGNORECASE
    )
    for match in font_family_pattern.finditer(content):
        family = match.group(1).lower().replace(' ', '-')
        # Only add if there's a matching font directory
        font_dir = BTDT_DIR / "fonts" / family
        if font_dir.exists():
            fonts.add(family)

    return fonts


def collect_source_files(preset_names: list[str] | None = None) -> tuple[list[Path], set[str]]:
    """Return the full list of source files that must be exported.

    Args:
        preset_names: List of preset names to include. If None, all presets are included.

    Returns:
        Tuple of (files_to_copy, set_of_used_font_names)
    """
    files: list[Path] = [BTDT_DIR / relative_path for relative_path in STATIC_FILES]
    used_fonts: set[str] = set()

    # Collect presets
    if preset_names:
        # Specific presets requested
        for name in preset_names:
            # Try minified first, fall back to non-minified
            min_path = BTDT_DIR / "themes" / "preset" / f"{name}.min.css"
            full_path = BTDT_DIR / "themes" / "preset" / f"{name}.css"

            if min_path.exists():
                files.append(min_path)
                used_fonts.update(extract_fonts_from_preset(min_path))
            elif full_path.exists():
                files.append(full_path)
                used_fonts.update(extract_fonts_from_preset(full_path))
            else:
                print(f"Warning: Preset '{name}' not found", file=sys.stderr)
    else:
        # All presets
        preset_files = sorted(BTDT_DIR.glob(PRESET_GLOB))
        files.extend(preset_files)
        for preset_path in preset_files:
            used_fonts.update(extract_fonts_from_preset(preset_path))

    # Collect only used fonts (or all if no specific presets)
    if preset_names and used_fonts:
        for font_name in sorted(used_fonts):
            font_dir = BTDT_DIR / "fonts" / font_name
            if font_dir.exists():
                files.extend(sorted(font_dir.glob("*")))
    else:
        # All fonts
        files.extend(sorted(BTDT_DIR.glob(FONTS_GLOB)))

    return files, used_fonts


def validate_source_files(files: list[Path], preset_names: list[str] | None = None) -> list[str]:
    """Return validation errors for missing or unexpected files."""
    errors: list[str] = []

    for path in files:
        if not path.is_file():
            errors.append(f"Missing source file: {path}")

    if preset_names:
        # Check that requested presets were found
        found_presets = set()
        for p in files:
            if "themes/preset" in str(p):
                name = p.stem.replace(".min", "").replace(".css", "")
                found_presets.add(name)
        for name in preset_names:
            if name not in found_presets:
                errors.append(f"Requested preset '{name}' was not found in btdt/themes/preset/")
    else:
        # All presets mode - ensure at least one exists
        if not any(path.match("*/themes/preset/*.min.css") for path in files):
            errors.append("No preset .min.css files were found in btdt/themes/preset/.")

    return errors


def copy_files(destination_root: Path, files: list[Path], dry_run: bool) -> int:
    """Copy all selected files into destination_root/btdt."""
    export_root = destination_root / "btdt"

    for source_path in files:
        relative_path = source_path.relative_to(BTDT_DIR)
        target_path = export_root / relative_path

        print(f"{source_path} -> {target_path}")
        if dry_run:
            continue

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

    readme_target = export_root / "README.md"
    print(f"{ROOT_README} -> {readme_target}")
    if not dry_run:
        readme_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT_README, readme_target)

    return len(files) + 1


def main() -> int:
    """Run the export command."""
    args = parse_args()
    destination_root = Path(args.destination).expanduser().resolve()
    export_root = destination_root / "btdt"

    # Parse preset names if provided
    preset_names: list[str] | None = None
    if args.presets:
        preset_names = [p.strip() for p in args.presets.split(",") if p.strip()]

    if export_root.exists() and not args.force:
        print(
            f"Destination already exists: {export_root}. "
            "Use --force to overwrite the export."
        )
        return 0

    files, used_fonts = collect_source_files(preset_names)
    errors = validate_source_files(files, preset_names)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    copied_count = copy_files(destination_root, files, args.dry_run)
    action = "Would copy" if args.dry_run else "Copied"
    print(f"{action} {copied_count} files into {destination_root / 'btdt'}")

    if preset_names and used_fonts:
        print(f"\nFonts detected and included: {', '.join(sorted(used_fonts))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
