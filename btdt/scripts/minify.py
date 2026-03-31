#!/usr/bin/env python3
"""BTDT CSS/JS minification and preset bundling utility."""
import argparse
import re
import sys
from pathlib import Path

EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
IMPORT_RE = re.compile(
    r"""
    @import
    \s+
    (?:
        url\(
            \s*
            (?:
                (?P<url_double>"[^"]+")
                |
                (?P<url_single>'[^']+')
                |
                (?P<url_bare>[^)\s]+)
            )
            \s*
        \)
        |
        (?P<plain_double>"[^"]+")
        |
        (?P<plain_single>'[^']+')
    )
    (?P<tail>\s+[^;]+)?
    \s*;
    """,
    re.VERBOSE,
)


def should_skip_dir(path: Path) -> bool:
    """Return True when the path belongs to an excluded build or cache directory."""
    return any(part in EXCLUDE_DIRS for part in path.parts)


def is_minified(path: Path) -> bool:
    """Return True for already-minified CSS or JS files."""
    return path.name.endswith(".min.js") or path.name.endswith(".min.css")


def iter_targets(target: Path, mode: str):
    """Yield source files to process from a single file or a directory tree."""
    if target.is_file():
        if target.name.startswith("_") or is_minified(target):
            return
        yield target
        return

    if not target.is_dir():
        raise FileNotFoundError(f"'{target}' is not a valid file or directory")

    suffixes = {".css", ".js"} if mode == "normal" else {".css"}
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if should_skip_dir(path.parent):
            continue
        if path.name.startswith("_"):
            continue
        if path.suffix not in suffixes or is_minified(path):
            continue
        yield path


def write_minified(output_path: Path, content: str) -> None:
    """Write minified content next to its source file using UTF-8."""
    if output_path.suffix == ".css" and content == "":
        content = "/* empty */\n"
    output_path.write_text(content, encoding="utf-8")


def get_cssmin():
    """Import and return the CSS minifier on demand."""
    try:
        from rcssmin import cssmin  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing 'rcssmin'. Install script dependencies with: "
            "pip install -r btdt/scripts/requirements.txt"
        ) from exc
    return cssmin


def get_jsmin():
    """Import and return the JS minifier on demand."""
    try:
        from rjsmin import jsmin  # pylint: disable=import-outside-toplevel
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Missing 'rjsmin'. Install script dependencies with: "
            "pip install -r btdt/scripts/requirements.txt"
        ) from exc
    return jsmin


def minify_standard_file(path: Path) -> None:
    """Minify a regular source CSS or JS file into its .min counterpart."""
    try:
        source = path.read_text(encoding="utf-8")
        if path.suffix == ".js":
            jsmin = get_jsmin()
            output = path.with_suffix(".min.js")
            write_minified(output, jsmin(source))
            print(f"[JS]  {path}")
        elif path.suffix == ".css":
            cssmin = get_cssmin()
            output = path.with_suffix(".min.css")
            write_minified(output, cssmin(source))
            print(f"[CSS] {path}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] {path}: {exc}")


def resolve_css_imports(path: Path, stack=None, root_path: Path | None = None) -> str:
    """Resolve local preset @import statements recursively into a single CSS string."""
    stack = stack or []
    resolved_path = path.resolve()
    root_path = root_path or resolved_path

    if resolved_path in stack:
        chain = " -> ".join(str(item) for item in [*stack, resolved_path])
        raise ValueError(f"Circular @import detected: {chain}")

    source = path.read_text(encoding="utf-8")
    current_stack = [*stack, resolved_path]

    def replace_import(match):
        """Inline a supported local import, or leave unsupported imports untouched."""
        relative = next(
            (
                value
                for value in (
                    match.group("url_double"),
                    match.group("url_single"),
                    match.group("url_bare"),
                    match.group("plain_double"),
                    match.group("plain_single"),
                )
                if value is not None
            ),
            None,
        )
        if relative is None:
            raise ValueError(f"Could not parse @import in {path}")

        relative = relative.strip().strip('"').strip("'")

        tail = (match.group("tail") or "").strip()
        if re.match(r"^(url\()?https?://", relative, re.IGNORECASE):
            return match.group(0)
        if tail:
            return match.group(0)

        imported_path = (path.parent / relative).resolve()
        if not imported_path.exists():
            raise FileNotFoundError(f"Import '{relative}' does not exist in {path}")

        inlined = resolve_css_imports(imported_path, current_stack, root_path)

        if "@font-face" in inlined and "src:" in inlined:
            inlined = rewrite_font_urls(inlined, imported_path, root_path)

        return inlined

    return IMPORT_RE.sub(replace_import, source)


def rewrite_font_urls(css: str, css_path: Path, root_path: Path) -> str:
    """Rewrite relative font URLs in @font-face rules to be relative to root_path."""
    try:
        rel_path = css_path.parent.relative_to(root_path.parent)
        prefix = str(rel_path).replace("\\", "/") + "/" if rel_path.parts else ""
    except ValueError:
        import os
        prefix = os.path.relpath(css_path.parent, root_path.parent).replace("\\", "/") + "/"

    if prefix and prefix != "./":
        css = re.sub(r"url\((['\"]?)([^)'\"]+)\.ttf\1\)", rf"url(\1{prefix}\2.ttf\1)", css)
        css = re.sub(r"url\((['\"]?)([^)'\"]+)\.woff2\1\)", rf"url(\1{prefix}\2.woff2\1)", css)

    return css


def hoist_imports_to_top(css: str) -> str:
    """Move any remaining @import rules to the beginning of the stylesheet."""
    imports: list[str] = []

    def collect_import(match):
        imports.append(match.group(0).strip())
        return ""

    body = IMPORT_RE.sub(collect_import, css).strip()
    if not imports:
        return body
    if not body:
        return "\n".join(imports) + "\n"
    return "\n".join(imports) + "\n\n" + body


def minify_preset_file(path: Path) -> None:
    """Bundle a BTDT preset CSS file by inlining imports, then write its .min.css output."""
    if path.suffix != ".css":
        print(f"[SKIP] {path}: preset mode only supports CSS files")
        return

    try:
        cssmin = get_cssmin()
        bundled = resolve_css_imports(path)
        bundled = hoist_imports_to_top(bundled)
        output = path.with_suffix(".min.css")
        write_minified(output, cssmin(bundled))
        print(f"[PRESET] {path}")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[ERROR] {path}: {exc}")


def parse_args():
    """Parse CLI arguments for normal or preset minification."""
    parser = argparse.ArgumentParser(
        description=(
            "Minify CSS/JS files or bundle preset CSS files "
            "by inlining their @import dependencies."
        )
    )
    parser.add_argument(
        "mode",
        choices=("normal", "preset"),
        help="Processing mode: standard minification or preset bundling/minification",
    )
    parser.add_argument(
        "target",
        help="File or directory to process",
    )
    return parser.parse_args()


def main():
    """CLI entry point for BTDT asset minification."""
    args = parse_args()
    target = Path(args.target)

    try:
        paths = list(iter_targets(target, args.mode))
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        sys.exit(1)

    if not paths:
        print("No files to process")
        sys.exit(0)

    for path in paths:
        if args.mode == "normal":
            minify_standard_file(path)
        else:
            minify_preset_file(path)


if __name__ == "__main__":
    main()
