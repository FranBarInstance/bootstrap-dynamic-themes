#!/usr/bin/env python3
"""Pre-commit safety check: detect sensitive files, excluded paths, absolute paths, and hardcoded secrets.

Standard library only — run with plain `python3`, no virtual environment required.

Exit codes:
    0 — no issues found
    1 — one or more WARNINGs detected (agent must stop and ask the user)
"""

import re
import subprocess
import sys


# 1. Patterns for sensitive file names
SENSITIVE_FILE_PATTERNS = [
    re.compile(r"\.env", re.IGNORECASE),
    re.compile(r"\.pem$", re.IGNORECASE),
    re.compile(r"\.key$", re.IGNORECASE),
    re.compile(r"\.cert$", re.IGNORECASE),
    re.compile(r"\.p12$", re.IGNORECASE),
    re.compile(r"id_rsa"),
    re.compile(r"\.sqlite", re.IGNORECASE),
    re.compile(r"\.db$", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"credential", re.IGNORECASE),
]

# 2. Paths that must never be staged in this repository
EXCLUDED_PATH_PATTERNS = [
    re.compile(r"^\.tmp/(?!README\.md$)"),  # .tmp/README.md is the documented tracked exception
    re.compile(r"(^|/)node_modules/"),
    re.compile(r"(^|/)\.venv/"),
    re.compile(r"(^|/)__pycache__/"),
    re.compile(r"^\.thinking/"),
    re.compile(r"(^|/)AGENTS\.local\.md$"),
]

# 3. Pattern for absolute paths
ABSOLUTE_PATH_PATTERN = re.compile(
    r"/home/|/Users/|/etc/|/var/|C:\\", re.IGNORECASE
)

# 4. Pattern for secrets WITHIN the code
SENSITIVE_CONTENT_PATTERN = re.compile(
    r"password\s*=|api[_-]?key\s*=|secret[_-]?key\s*=|AKIA[0-9A-Z]{16}|Bearer\s+eyJ",
    re.IGNORECASE,
)


def _is_binary(filepath: str) -> bool:
    """Return True if the file appears to be binary."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            f.read(1024)
        return False
    except UnicodeDecodeError:
        return True


def _check_file(filepath: str) -> int:
    """Run all safety checks on a single file. Returns number of warnings found."""
    file_warnings = 0

    # --- Check 1: Sensitive file names ---
    for pattern in SENSITIVE_FILE_PATTERNS:
        if pattern.search(filepath):
            print(
                f"🔴 WARNING: Sensitive file name detected: "
                f"{filepath} (matched: {pattern.pattern})"
            )
            file_warnings += 1

    # --- Check 2: Excluded paths ---
    for pattern in EXCLUDED_PATH_PATTERNS:
        if pattern.search(filepath):
            print(
                f"🔴 WARNING: Staged file is under an excluded path: "
                f"{filepath} (matched: {pattern.pattern})"
            )
            file_warnings += 1

    # --- Checks 3 & 4: Content-based (skip binaries) ---
    if _is_binary(filepath):
        return file_warnings

    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return file_warnings

    # --- Check 3: Absolute paths ---
    abs_matches = []
    for lineno, line in enumerate(lines, 1):
        if ABSOLUTE_PATH_PATTERN.search(line):
            abs_matches.append((lineno, line.rstrip()))
    if abs_matches:
        print(
            f"🟡 WARNING: Potential absolute path "
            f"detected in {filepath}"
        )
        for lineno, line in abs_matches[:3]:
            print(f"  {filepath}:{lineno}: {line}")
        file_warnings += 1

    # --- Check 4: Secrets in content ---
    secret_matches = []
    for lineno, line in enumerate(lines, 1):
        if SENSITIVE_CONTENT_PATTERN.search(line):
            secret_matches.append((lineno, line.rstrip()))
    if secret_matches:
        print(
            f"🔴 WARNING: Potential hardcoded secret "
            f"or credential detected in {filepath}"
        )
        for lineno, line in secret_matches[:3]:
            print(f"  {filepath}:{lineno}: {line}")
        file_warnings += 1

    return file_warnings


def main() -> int:
    """Run safety checks on all staged files. Returns 0 if clean, 1 if warnings found."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print("Error: failed to get staged files.")
        return 1

    staged_files = [f for f in result.stdout.strip().split("\n") if f]

    if not staged_files:
        print("No files staged for commit.")
        return 0

    print("Running safety checks on staged files...")
    warnings = 0

    for filepath in staged_files:
        # Skip files that don't exist on disk (e.g. deleted in the commit)
        try:
            with open(filepath, "rb"):
                pass
        except FileNotFoundError:
            continue

        warnings += _check_file(filepath)

    if warnings > 0:
        print(
            f"❌ Safety check failed with {warnings} warnings. "
            "Please review the output above."
        )
        return 1

    print("✅ Checks completed. No issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
