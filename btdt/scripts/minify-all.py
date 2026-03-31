#!/usr/bin/env python3
"""Run BTDT minification across all standard asset directories.

This is a Python equivalent of `btdt/scripts/minify-all`, using only the
standard library. It delegates the actual work to `minify.py` and
intentionally uses the local `.venv` inside `btdt/scripts/`, matching
the Bash wrapper behaviour.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
MINIFY_PY = SCRIPT_DIR / "minify.py"
VENV_PYTHON_POSIX = SCRIPT_DIR / ".venv" / "bin" / "python"
VENV_PYTHON_WINDOWS = SCRIPT_DIR / ".venv" / "Scripts" / "python.exe"

NORMAL_DIRS = [
    SCRIPT_DIR / "../css",
    SCRIPT_DIR / "../js",
    SCRIPT_DIR / "../themes/colors",
    SCRIPT_DIR / "../themes/fonts",
    SCRIPT_DIR / "../themes/modes",
    SCRIPT_DIR / "../themes/styles",
]

PRESET_DIRS = [
    SCRIPT_DIR / "../themes/preset",
]


def resolve_python_executable() -> Path:
    """Return the Python interpreter from scripts/.venv, matching minify-all."""
    if VENV_PYTHON_POSIX.exists():
        return VENV_PYTHON_POSIX
    if VENV_PYTHON_WINDOWS.exists():
        return VENV_PYTHON_WINDOWS

    raise FileNotFoundError(
        "Could not find the local virtualenv Python for btdt/scripts/.venv. "
        "Expected one of:\n"
        f"- {VENV_PYTHON_POSIX}\n"
        f"- {VENV_PYTHON_WINDOWS}\n"
        "Create the virtual environment and install the minify dependencies first."
    )


def run_minify(mode: str, target: Path) -> None:
    """Run the underlying minify.py script for one target directory."""
    python_executable = resolve_python_executable()
    command = [str(python_executable), str(MINIFY_PY), mode, str(target.resolve())]
    subprocess.run(command, cwd=SCRIPT_DIR, check=True)


def main() -> int:
    """Run normal minification first, then preset bundling/minification."""
    for directory in NORMAL_DIRS:
        run_minify("normal", directory)

    for directory in PRESET_DIRS:
        run_minify("preset", directory)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
