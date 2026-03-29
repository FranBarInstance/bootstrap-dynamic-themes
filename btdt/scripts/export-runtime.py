#!/usr/bin/env python3
"""Export the minimal BTDT runtime asset subset into a destination directory."""

from __future__ import annotations

import argparse
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


def collect_source_files() -> list[Path]:
    """Return the full list of source files that must be exported."""
    files = [BTDT_DIR / relative_path for relative_path in STATIC_FILES]
    files.extend(sorted(BTDT_DIR.glob(PRESET_GLOB)))
    files.extend(sorted(BTDT_DIR.glob(FONTS_GLOB)))
    return files


def validate_source_files(files: list[Path]) -> list[str]:
    """Return validation errors for missing or unexpected files."""
    errors: list[str] = []

    for path in files:
        if not path.is_file():
            errors.append(f"Missing source file: {path}")

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

    if export_root.exists() and not args.force:
        print(
            f"Destination already exists: {export_root}. "
            "Use --force to overwrite the export."
        )
        return 0

    files = collect_source_files()
    errors = validate_source_files(files)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    copied_count = copy_files(destination_root, files, args.dry_run)
    action = "Would copy" if args.dry_run else "Copied"
    print(f"{action} {copied_count} files into {destination_root / 'btdt'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
