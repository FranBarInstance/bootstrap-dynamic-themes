#!/usr/bin/env python3

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
        yield target
        return

    if not target.is_dir():
        raise FileNotFoundError(f"'{target}' no es un archivo o directorio valido")

    suffixes = {".css", ".js"} if mode == "normal" else {".css"}
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if should_skip_dir(path.parent):
            continue
        if path.suffix not in suffixes or is_minified(path):
            continue
        yield path


def write_minified(output_path: Path, content: str) -> None:
    """Write minified content next to its source file using UTF-8."""
    output_path.write_text(content, encoding="utf-8")


def get_cssmin():
    """Import and return the CSS minifier on demand."""
    try:
        from rcssmin import cssmin
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Falta 'rcssmin'. Instala las dependencias con: pip install -r requirements.txt"
        ) from exc
    return cssmin


def get_jsmin():
    """Import and return the JS minifier on demand."""
    try:
        from rjsmin import jsmin
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "Falta 'rjsmin'. Instala las dependencias con: pip install -r requirements.txt"
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


def resolve_css_imports(path: Path, stack=None) -> str:
    """Resolve local preset @import statements recursively into a single CSS string."""
    stack = stack or []
    resolved_path = path.resolve()

    if resolved_path in stack:
        chain = " -> ".join(str(item) for item in [*stack, resolved_path])
        raise ValueError(f"Circular @import detectado: {chain}")

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
            raise ValueError(f"No se pudo interpretar @import en {path}")

        relative = relative.strip().strip('"').strip("'")

        # BTDT preset bundling is local-only: keep external imports and media-specific imports untouched.
        tail = (match.group("tail") or "").strip()
        if re.match(r"^(url\()?https?://", relative, re.IGNORECASE):
            return match.group(0)
        if tail:
            return match.group(0)

        imported_path = (path.parent / relative).resolve()
        if not imported_path.exists():
            raise FileNotFoundError(f"No existe el import '{relative}' en {path}")
        return resolve_css_imports(imported_path, current_stack)

    return IMPORT_RE.sub(replace_import, source)


def hoist_imports_to_top(css: str) -> str:
    """Move any remaining @import rules to the beginning of the stylesheet.

    After preset bundling, external/media-qualified @import rules can remain in
    arbitrary positions. Keeping them at the top avoids invalid CSS ordering
    and keeps downstream minification predictable.
    """
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
        print(f"[SKIP] {path}: preset solo admite archivos CSS")
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
        description="Minifica archivos CSS/JS o compila presets CSS embebiendo sus @import."
    )
    parser.add_argument(
        "mode",
        choices=("normal", "preset"),
        help="Modo de trabajo: minificado normal o minificado especial para presets",
    )
    parser.add_argument(
        "target",
        help="Archivo o directorio a procesar",
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
        print("No hay archivos para procesar")
        sys.exit(0)

    for path in paths:
        if args.mode == "normal":
            minify_standard_file(path)
        else:
            minify_preset_file(path)


if __name__ == "__main__":
    main()
