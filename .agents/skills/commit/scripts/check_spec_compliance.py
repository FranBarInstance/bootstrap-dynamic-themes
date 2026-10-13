#!/usr/bin/env python3
"""Pre-commit specification compliance check.

Validates staged files against the specification system under .specify/ and
the writing standard .specify/style.md:

- telegraphic style of normative spec.md files (causal connectors, justificatory formulas)
- specification directory naming (.specify/specs/NNN-slug/spec.md)
- rationale naming (.specify/rationale/NNN-slug.md and policy basenames)
- spec reference integrity (`spec NNN` pointers resolve to an existing spec)

Standard library only — run with plain `python3`, no virtual environment required.

Exit codes:
    0 — no issues found
    1 — one or more WARNINGs detected (agent must stop and ask the user)
"""

import re
import subprocess
import sys
from pathlib import Path


# --- Non-telegraphic phrasing patterns (style.md) ---
# Detect causal connectors and justificatory formulas in normative specs.
# Expected false positives may occur in narrative or descriptions;
# any warning must be reviewed manually by the agent/user.

CAUSAL_CONNECTORS_PATTERN = re.compile(
    r"\b(because|since|in order to|therefore|so that|to guarantee)\b",
    re.IGNORECASE,
)

JUSTIFICATORY_FORMULAS_PATTERN = re.compile(
    r"\b(per principle|to ensure|to avoid|to prevent|"
    r"this ensures|this allows|this prevents|this avoids)\b",
    re.IGNORECASE,
)

# --- Naming patterns (style.md) ---
SPEC_DIR_PATTERN = re.compile(r"^\d{3}-[a-z0-9]+(-[a-z0-9]+)*$")
RATIONALE_FILE_PATTERN = re.compile(
    r"^\d{3}(-\d{3})?-[a-z0-9]+(-[a-z0-9]+)*\.md$"
)

# Files scanned for `spec NNN` pointers.
REFERENCE_SCAN_SUFFIXES = (".md", ".scss", ".css", ".py", ".js")


def _get_staged_files() -> list[str]:
    """Return the list of staged files."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [f for f in result.stdout.strip().split("\n") if f]


def _check_spec_telegraphic_style(staged_files: list[str]) -> int:
    """Check that staged spec.md files adhere to telegraphic style (style.md)."""
    warnings = 0

    for filepath in staged_files:
        path = Path(filepath)
        if path.name != "spec.md":
            continue
        # Only check normative specification files
        if not (filepath.startswith(".specify/specs/") or "/.specify/" in filepath):
            continue
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue

        in_code_block = False
        for line_num, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_block = not in_code_block
                continue
            if in_code_block or not stripped:
                continue

            causal_match = CAUSAL_CONNECTORS_PATTERN.search(stripped)
            if causal_match:
                print(
                    f"🟡 WARNING: {filepath}:{line_num} Potential causal connector "
                    f"'{causal_match.group(0)}' (style.md). "
                    f"Check if justification belongs in rationale/."
                )
                warnings += 1

            justif_match = JUSTIFICATORY_FORMULAS_PATTERN.search(stripped)
            if justif_match:
                print(
                    f"🟡 WARNING: {filepath}:{line_num} Potential justificatory formula "
                    f"'{justif_match.group(0)}' (style.md). "
                    f"Check if justification belongs in rationale/."
                )
                warnings += 1

    return warnings


def _check_spec_naming(staged_files: list[str]) -> int:
    """Check specification directory naming (style.md § Structure)."""
    warnings = 0

    for filepath in staged_files:
        if not filepath.startswith(".specify/specs/"):
            continue

        parts = Path(filepath).parts  # (".specify", "specs", ...)
        # Direct placeholder files under specs/ (e.g. README.md) are allowed.
        if len(parts) == 3:
            continue

        spec_dir = parts[2]
        if not SPEC_DIR_PATTERN.match(spec_dir):
            print(
                f"🔴 WARNING: {filepath} lives under '{spec_dir}'; "
                f"specification directories must be named NNN-slug (style.md)."
            )
            warnings += 1
            continue

        # Inside a spec directory, the normative file is spec.md
        inner = parts[3:]
        if inner and inner[-1] != "spec.md":
            print(
                f"🟡 WARNING: {filepath}: files under a specification directory "
                f"should be spec.md (style.md § Structure)."
            )
            warnings += 1

    return warnings


def _check_rationale_naming(staged_files: list[str]) -> int:
    """Check rationale file naming (style.md § Rationale Documents)."""
    warnings = 0

    for filepath in staged_files:
        if not filepath.startswith(".specify/rationale/"):
            continue

        name = Path(filepath).name

        # Top-level placeholder and superseded/ contents are checked loosely.
        if name == "README.md":
            continue
        if "superseded" in Path(filepath).parts:
            continue

        # A rationale for a cross-cutting policy MAY use the policy basename
        # (e.g. style.md); numbered rationales must match NNN-slug.md.
        if not RATIONALE_FILE_PATTERN.match(name) and not name.endswith(".md"):
            print(
                f"🟡 WARNING: {filepath}: rationale files are Markdown "
                f"(style.md § Rationale Documents)."
            )
            warnings += 1
        elif not RATIONALE_FILE_PATTERN.match(name):
            print(
                f"🟡 WARNING: {filepath}: numbered rationales must be named "
                f"NNN-slug.md (or NNN-MMM-slug.md); policy rationales use the "
                f"policy basename (style.md § Rationale Documents)."
            )
            warnings += 1

    return warnings


def _check_spec_references(staged_files: list[str]) -> int:
    """Check that staged files reference spec numbers that exist."""
    warnings = 0
    spec_dir = Path(".specify/specs")

    if not spec_dir.exists():
        return 0

    # Build set of existing spec numbers
    existing_specs: set[str] = set()
    for spec_path in spec_dir.iterdir():
        if spec_path.is_dir():
            existing_specs.add(spec_path.name.split("-")[0])

    # Pattern to match spec references like "spec NNN", "[spec NNN]"
    spec_ref_pattern = re.compile(r"spec\s+(\d{3})")

    for filepath in staged_files:
        if not filepath.endswith(REFERENCE_SCAN_SUFFIXES):
            continue
        if not Path(filepath).exists():
            continue

        # Skip spec files themselves (they define specs, not reference them)
        if filepath.startswith(".specify/"):
            continue

        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except OSError:
            continue

        refs = set(spec_ref_pattern.findall(content))
        for ref in refs:
            if ref not in existing_specs:
                print(
                    f"🟡 WARNING: {filepath} references 'spec {ref}' "
                    f"but no such spec exists under .specify/specs/"
                )
                warnings += 1

    return warnings


def main() -> int:
    """Run all spec compliance checks on staged files."""
    staged_files = _get_staged_files()

    if not staged_files:
        print("No files staged for commit.")
        return 0

    print("Running spec compliance checks on staged files...")
    warnings = 0

    # --- 1. Spec telegraphic style (style.md) ---
    warnings += _check_spec_telegraphic_style(staged_files)

    # --- 2. Specification directory naming ---
    warnings += _check_spec_naming(staged_files)

    # --- 3. Rationale naming ---
    warnings += _check_rationale_naming(staged_files)

    # --- 4. Spec reference integrity ---
    warnings += _check_spec_references(staged_files)

    if warnings > 0:
        print(
            f"❌ Spec compliance check failed with {warnings} warnings. "
            "Please review the output above."
        )
        return 1

    print("✅ Spec compliance checks passed. No issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
