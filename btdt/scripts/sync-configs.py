#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Regenerate BTDT config catalogs from the filesystem and CSS metadata.

This script keeps the editor/runtime catalogs in sync with the real theme files:
- btdt/js/config-colors.js
- btdt/js/config-fonts.js
- btdt/js/config-presets.js
- btdt/js/config-ui.js

It also emits warnings when modules do not follow the conventions documented in
.agent/skills/.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BTDT_DIR = ROOT / "btdt"
JS_DIR = BTDT_DIR / "js"
THEMES_DIR = BTDT_DIR / "themes"

COLOR_DIR = THEMES_DIR / "colors"
FONT_DIR = THEMES_DIR / "fonts"
PRESET_DIR = THEMES_DIR / "preset"
STYLE_DIR = THEMES_DIR / "styles"

COLOR_RULES_IMPORT = '@import "../../css/color-theme-rules.min.css";'

CONFIG_COLORS = JS_DIR / "config-colors.js"
CONFIG_FONTS = JS_DIR / "config-fonts.js"
CONFIG_PRESETS = JS_DIR / "config-presets.js"
CONFIG_UI = JS_DIR / "config-ui.js"

STYLE_ORDER = [
    "background",
    "borders",
    "rounding",
    "shadows",
    "spacing",
    "gradients",
    "accent",
    "accentSize",
    "accentColor",
]

PRESET_IMPORT_ORDER = [
    "fonts",
    "colors",
    "background",
    "borders",
    "rounding",
    "shadows",
    "spacing",
    "gradients",
    "accent",
    "accentSize",
    "accentColor",
]

PRESET_METADATA_KEYS = [
    "colors",
    "fonts",
    "background",
    "borders",
    "rounding",
    "shadows",
    "spacing",
    "gradients",
    "accent",
    "accentSize",
    "accentColor",
]

VAR_RE = re.compile(r"--(?P<name>[\w-]+)\s*:\s*(?P<value>[^;]+);")
IMPORT_RE = re.compile(r'@import\s+"(?P<path>[^"]+)";')
FONT_LABEL_RE = re.compile(r"--bs-body-font-family\s*:\s*(?P<value>[^;]+);")
METADATA_RE = re.compile(r'--preset-(?P<key>[\w-]+)\s*:\s*"(?P<value>[^"]+)";')


class WarningCollector:
    """Collect validation warnings to print at the end of the run."""

    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, message: str) -> None:
        """Add a single warning message."""
        self.items.append(message)

    def extend(self, messages: list[str]) -> None:
        """Add multiple warning messages."""
        self.items.extend(messages)

@dataclass(frozen=True)
class PresetValidationContext:
    """Shared lookup tables used while validating presets."""

    available_colors: set[str]
    available_fonts: set[str]
    available_styles: dict[str, list[str]]
    warnings: WarningCollector


def list_source_css(directory: Path) -> list[Path]:
    """Return non-minified source CSS files for a theme directory."""
    return sorted(
        path
        for path in directory.glob("*.css")
        if not path.name.endswith(".min.css") and not path.name.startswith("_")
    )


def read_text(path: Path) -> str:
    """Read a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def humanize_slug(slug: str) -> str:
    """Convert a kebab-case slug into a human-readable title."""
    uppercase_words = {"dm", "eb", "pt", "ui"}
    pieces = []
    for part in slug.split("-"):
        if part.lower() in uppercase_words:
            pieces.append(part.upper())
        else:
            pieces.append(part.capitalize())
    return " ".join(pieces)


def parse_simple_string_map(path: Path) -> dict[str, str]:
    """Parse a simple JS object that maps keys to string values."""
    content = read_text(path)
    pattern = re.compile(
        r"(?:'(?P<qkey>[^']+)'|(?P<key>[A-Za-z_][\w-]*))\s*:\s*'(?P<value>[^']*)'"
    )
    result: dict[str, str] = {}
    for match in pattern.finditer(content):
        key = match.group("qkey") or match.group("key")
        result[key] = match.group("value")
    return result


def parse_color_config(path: Path) -> dict[str, dict[str, str]]:
    """Parse config-colors.js into a Python dictionary."""
    content = read_text(path)
    pattern = re.compile(
        r"(?:'(?P<qkey>[^']+)'|(?P<key>[A-Za-z_][\w-]*))\s*:\s*\{\s*"
        r"primary:\s*'(?P<primary>[^']+)',\s*"
        r"secondary:\s*'(?P<secondary>[^']+)',\s*accent:\s*'(?P<accent>[^']+)'\s*\}"
    )
    result: dict[str, dict[str, str]] = {}
    for match in pattern.finditer(content):
        key = match.group("qkey") or match.group("key")
        result[key] = {
            "primary": match.group("primary"),
            "secondary": match.group("secondary"),
            "accent": match.group("accent"),
        }
    return result


def parse_preset_config(path: Path) -> dict[str, dict[str, str | None]]:
    """Parse config-presets.js into a Python dictionary."""
    content = read_text(path)
    pattern = re.compile(
        r"(?:'(?P<qkey>[^']+)'|(?P<key>[A-Za-z_][\w-]*))\s*:\s*\{\s*title:\s*'(?P<title>[^']*)',\s*"
        r"color:\s*(?P<color>null|'[^']*')\s*\}"
    )
    result: dict[str, dict[str, str | None]] = {}
    for match in pattern.finditer(content):
        color = match.group("color")
        key = match.group("qkey") or match.group("key")
        result[key] = {
            "title": match.group("title"),
            "color": None if color == "null" else color.strip("'"),
        }
    return result


def parse_ui_config(path: Path) -> dict[str, dict[str, str]]:
    """Parse config-ui.js into nested category/value labels."""
    content = read_text(path)
    categories: dict[str, dict[str, str]] = {}
    category_pattern = re.compile(r"(?P<category>\w+)\s*:\s*\{(?P<body>[^}]*)\}", re.DOTALL)
    item_pattern = re.compile(
        r"(?:'(?P<qkey>[^']+)'|(?P<key>[\w-]+))\s*:\s*'(?P<value>[^']*)'"
    )

    for match in category_pattern.finditer(content):
        category = match.group("category")
        body = match.group("body")
        items: dict[str, str] = {}
        for item in item_pattern.finditer(body):
            key = item.group("qkey") or item.group("key")
            items[key] = item.group("value")
        if items:
            categories[category] = items
    return categories


def serialize_js_value(value, indent: int = 0, top_level: bool = False) -> str:
    """Serialize a Python primitive/dict into a JS object literal."""
    space = " " * indent
    next_indent = indent + 2
    next_space = " " * next_indent

    if value is None:
        return "null"
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(value, dict):
        items = list(value.items())
        if not items:
            return "{}"

        multiline = top_level or any(isinstance(v, dict) for _, v in items)
        if not multiline:
            inner = ", ".join(
                f"{serialize_js_key(k)}: {serialize_js_value(v, next_indent)}"
                for k, v in items
            )
            return f"{{ {inner} }}"

        lines = ["{"]
        for key, nested in items:
            line = (
                f"{next_space}{serialize_js_key(key)}: "
                f"{serialize_js_value(nested, next_indent)},"
            )
            lines.append(line)
        lines.append(f"{space}}}")
        return "\n".join(lines)

    raise TypeError(f"Unsupported JS value type: {type(value)!r}")


def serialize_js_key(key: str) -> str:
    """Serialize a JS object key, quoting when required."""
    if re.fullmatch(r"[A-Za-z_]\w*", key):
        return key
    return serialize_js_value(key)


def write_config(path: Path, global_name: str, payload: dict) -> None:
    """Write a source JS config file.

    Minified siblings are intentionally left untouched. They belong to the
    minification pipeline, not to catalog synchronization.
    """
    header = f"// {path.relative_to(ROOT).as_posix()}\n"
    body = serialize_js_value(payload, indent=0, top_level=True)
    path.write_text(f"{header}window.{global_name} = {body};\n", encoding="utf-8")


def parse_css_vars(path: Path) -> dict[str, str]:
    """Extract CSS custom properties from a stylesheet."""
    return {
        match.group("name"): match.group("value").strip()
        for match in VAR_RE.finditer(read_text(path))
    }


def scan_colors(warnings: WarningCollector) -> dict[str, dict[str, str]]:
    """Build color metadata from theme color files."""
    colors: dict[str, dict[str, str]] = {}

    for path in list_source_css(COLOR_DIR):
        slug = path.stem
        content = read_text(path)
        variables = parse_css_vars(path)
        required = ["bs-primary", "bs-secondary", "accent-color"]
        missing = [key for key in required if key not in variables]

        if COLOR_RULES_IMPORT not in content:
            warnings.add(
                f"[color:{slug}] Missing required import: ../../css/color-theme-rules.min.css"
            )
        if missing:
            warnings.add(f"[color:{slug}] Missing required CSS variables: {', '.join(missing)}")
            continue

        colors[slug] = {
            "primary": variables["bs-primary"],
            "secondary": variables["bs-secondary"],
            "accent": variables["accent-color"],
        }

    return dict(sorted(colors.items()))


def derive_font_label(
    path: Path,
    existing_labels: dict[str, str],
    warnings: WarningCollector,
) -> str:
    """Infer a human-readable label for a font module."""
    slug = path.stem
    if slug in existing_labels:
        return existing_labels[slug]

    content = read_text(path)
    match = FONT_LABEL_RE.search(content)
    if match:
        family_value = match.group("value")
        family_names = re.findall(r"'([^']+)'", family_value)
        if family_names:
            return family_names[0]

    warnings.add(
        f"[font:{slug}] Could not infer label from CSS; using slug-derived label"
    )
    return humanize_slug(slug)


def scan_fonts(existing_labels: dict[str, str], warnings: WarningCollector) -> dict[str, str]:
    """Build font metadata from theme font files."""
    fonts: dict[str, str] = {}

    for path in list_source_css(FONT_DIR):
        slug = path.stem
        content = read_text(path)

        if "@import url(" not in content:
            warnings.add(f"[font:{slug}] Missing Google Fonts @import")
        for required in [
            "--bs-body-font-family",
            "--bs-body-font-weight",
            "--bs-body-line-height",
        ]:
            if required not in content:
                warnings.add(f"[font:{slug}] Missing required declaration: {required}")

        fonts[slug] = derive_font_label(path, existing_labels, warnings)

    return dict(sorted(fonts.items()))


def detect_style_categories(warnings: WarningCollector) -> dict[str, list[str]]:
    """Group style modules by their inferred category."""
    categories: dict[str, list[str]] = {key: [] for key in STYLE_ORDER}

    for path in list_source_css(STYLE_DIR):
        name = path.stem
        if name.startswith("accent-"):
            value = name.removeprefix("accent-")
            if value in {"none", "left", "right", "top", "bottom"}:
                categories["accent"].append(value)
            elif value in {"primary", "secondary", "gray"}:
                categories["accentColor"].append(value)
            elif value.isdigit():
                categories["accentSize"].append(value)
            else:
                warnings.add(f"[style:{name}] Unknown accent module value")
            continue

        matched = False
        for prefix in [
            "background",
            "borders",
            "rounding",
            "shadows",
            "spacing",
            "gradients",
        ]:
            marker = f"{prefix}-"
            if name.startswith(marker):
                categories[prefix].append(name.removeprefix(marker))
                matched = True
                break

        if not matched:
            warnings.add(f"[style:{name}] Filename does not match a known style category")

    for category in categories:
        categories[category] = sorted(set(categories[category]), key=style_sort_key)

    return categories


def style_sort_key(value: str):
    """Sort numeric style values numerically before lexical values."""
    return (0, int(value)) if value.isdigit() else (1, value)


def build_ui_config(
    style_categories: dict[str, list[str]],
    existing_ui: dict[str, dict[str, str]],
    warnings: WarningCollector,
) -> dict[str, dict[str, str]]:
    """Build config-ui.js data from detected style files and existing labels."""
    ui: dict[str, dict[str, str]] = {}

    for category in STYLE_ORDER:
        labels = existing_ui.get(category, {})
        values = style_categories[category]
        generated: dict[str, str] = {}
        for value in values:
            if value in labels:
                generated[value] = labels[value]
            else:
                generated[value] = derive_ui_label(category, value)
                warnings.add(
                    f"[ui:{category}] No label found for '{value}'; "
                    f"using fallback '{generated[value]}'"
                )
        ui[category] = generated

    return ui


def derive_ui_label(category: str, value: str) -> str:
    """Create a fallback UI label for a style value."""
    if category == "background":
        if "-" in value:
            left, right = value.split("-", 1)
            return f"{humanize_slug(left)} \u00b7 {humanize_slug(right)}"
        return humanize_slug(value)
    if category == "accentSize" and value.isdigit():
        return f"{value} px"
    if category == "gradients":
        return {"on": "Yes", "off": "No"}.get(value, humanize_slug(value))
    return humanize_slug(value)


def parse_preset_file(path: Path) -> tuple[list[str], dict[str, str]]:
    """Return the import list and metadata block from a preset CSS file."""
    content = read_text(path)
    imports = [match.group("path") for match in IMPORT_RE.finditer(content)]
    metadata = {match.group("key"): match.group("value") for match in METADATA_RE.finditer(content)}
    return imports, metadata


def strip_import_prefix(import_path: str, prefix: str) -> str | None:
    """Return the stem of an import path when it matches a known prefix."""
    if not import_path.startswith(prefix):
        return None
    return Path(import_path).stem.removeprefix(Path(prefix).stem)


def categorize_preset_import(import_path: str) -> tuple[str, str] | None:
    """Map a preset import path to its BTDT category and value."""
    simple_prefixes = {
        "../fonts/": "fonts",
        "../colors/": "colors",
        "../styles/background-": "background",
        "../styles/borders-": "borders",
        "../styles/rounding-": "rounding",
        "../styles/shadows-": "shadows",
        "../styles/spacing-": "spacing",
        "../styles/gradients-": "gradients",
    }
    for prefix, category in simple_prefixes.items():
        if import_path.startswith(prefix):
            stem = Path(import_path).stem
            suffix = prefix.rsplit("/", maxsplit=1)[-1]
            value = stem if category in {"fonts", "colors"} else stem.removeprefix(suffix)
            return (category, value)

    if not import_path.startswith("../styles/accent-"):
        return None

    value = Path(import_path).stem.removeprefix("accent-")
    if value in {"none", "left", "right", "top", "bottom"}:
        return ("accent", value)
    if value in {"primary", "secondary", "gray"}:
        return ("accentColor", value)
    if value.isdigit():
        return ("accentSize", value)
    return None


def collect_preset_import_values(
    slug: str,
    imports: list[str],
    warnings: WarningCollector,
) -> tuple[list[str], dict[str, str]]:
    """Parse and validate the import section of a preset."""
    seen_categories: list[str] = []
    import_values: dict[str, str] = {}

    for import_path in imports:
        categorized = categorize_preset_import(import_path)
        if not categorized:
            warnings.add(f"[preset:{slug}] Unsupported import path: {import_path}")
            continue

        category, value = categorized
        seen_categories.append(category)
        if category in import_values:
            warnings.add(f"[preset:{slug}] Duplicate import category: {category}")
        import_values[category] = value

    return seen_categories, import_values


def validate_preset_metadata(
    slug: str,
    metadata: dict[str, str],
    import_values: dict[str, str],
    warnings: WarningCollector,
) -> None:
    """Validate metadata completeness and consistency for a preset."""
    missing_metadata = [key for key in PRESET_METADATA_KEYS if key not in metadata]
    if missing_metadata:
        warnings.add(f"[preset:{slug}] Missing metadata keys: {', '.join(missing_metadata)}")

    for key in PRESET_METADATA_KEYS:
        if key in metadata and key in import_values and metadata[key] != import_values[key]:
            warnings.add(
                f"[preset:{slug}] Metadata/import mismatch for {key}: "
                f"metadata='{metadata[key]}' import='{import_values[key]}'"
            )


def validate_preset_references(
    slug: str,
    metadata: dict[str, str],
    context: PresetValidationContext,
) -> None:
    """Validate that preset metadata references known modules."""
    color_value = metadata.get("colors")
    font_value = metadata.get("fonts")
    if color_value and color_value not in context.available_colors:
        context.warnings.add(f"[preset:{slug}] References unknown color module '{color_value}'")
    if font_value and font_value not in context.available_fonts:
        context.warnings.add(f"[preset:{slug}] References unknown font module '{font_value}'")

    for key in STYLE_ORDER:
        value = metadata.get(key)
        if value and value not in context.available_styles[key]:
            context.warnings.add(
                f"[preset:{slug}] References unknown {key} module '{value}'"
            )


def validate_preset(
    slug: str,
    imports: list[str],
    metadata: dict[str, str],
    context: PresetValidationContext,
) -> None:
    """Validate structure, metadata and references of a preset CSS file."""
    if len(imports) != 11:
        context.warnings.add(f"[preset:{slug}] Expected 11 imports, found {len(imports)}")

    seen_categories, import_values = collect_preset_import_values(
        slug,
        imports,
        context.warnings,
    )

    if seen_categories != PRESET_IMPORT_ORDER:
        context.warnings.add(
            f"[preset:{slug}] Imports are not in the required order: "
            + " -> ".join(seen_categories or ["<none>"])
        )

    validate_preset_metadata(slug, metadata, import_values, context.warnings)
    validate_preset_references(slug, metadata, context)


def scan_presets(
    existing_presets: dict[str, dict[str, str | None]],
    available_colors: set[str],
    available_fonts: set[str],
    available_styles: dict[str, list[str]],
    warnings: WarningCollector,
) -> dict[str, dict[str, str | None]]:
    """Build preset metadata from preset files and their embedded metadata."""
    presets: dict[str, dict[str, str | None]] = {}
    context = PresetValidationContext(
        available_colors=available_colors,
        available_fonts=available_fonts,
        available_styles=available_styles,
        warnings=warnings,
    )

    for path in list_source_css(PRESET_DIR):
        slug = path.stem
        imports, metadata = parse_preset_file(path)
        validate_preset(slug, imports, metadata, context)

        title = existing_presets.get(slug, {}).get("title") or humanize_slug(slug)
        color = metadata.get("colors")
        if slug == "default" and color is None:
            derived_color = None
        else:
            derived_color = color

        if derived_color is None and slug != "default":
            warnings.add(f"[preset:{slug}] Could not infer swatch color from metadata")

        presets[slug] = {
            "title": title,
            "color": derived_color,
        }

    return dict(sorted(presets.items()))


def compare_existing_keys(
    name: str,
    existing: set[str],
    generated: set[str],
    warnings: WarningCollector,
) -> None:
    """Warn about drift between config files and on-disk modules."""
    removed = sorted(existing - generated)
    added = sorted(generated - existing)
    if removed:
        warnings.add(
            f"[{name}] Entries present in config but not on disk anymore: "
            f"{', '.join(removed)}"
        )
    if added:
        warnings.add(f"[{name}] New entries discovered on disk: {', '.join(added)}")


def main(argv: list[str] | None = None) -> int:
    """Run config synchronization or validation."""
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate BTDT config-*.js files from themes/ "
            "and emit validation warnings."
        )
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and report warnings without writing files.",
    )
    args = parser.parse_args(argv)

    warnings = WarningCollector()

    existing_colors = parse_color_config(CONFIG_COLORS)
    existing_fonts = parse_simple_string_map(CONFIG_FONTS)
    existing_presets = parse_preset_config(CONFIG_PRESETS)
    existing_ui = parse_ui_config(CONFIG_UI)

    colors = scan_colors(warnings)
    fonts = scan_fonts(existing_fonts, warnings)
    style_categories = detect_style_categories(warnings)
    ui = build_ui_config(style_categories, existing_ui, warnings)
    presets = scan_presets(
        existing_presets,
        set(colors.keys()),
        set(fonts.keys()),
        style_categories,
        warnings,
    )

    compare_existing_keys(
        "config-colors",
        set(existing_colors.keys()),
        set(colors.keys()),
        warnings,
    )
    compare_existing_keys("config-fonts", set(existing_fonts.keys()), set(fonts.keys()), warnings)
    compare_existing_keys(
        "config-presets",
        set(existing_presets.keys()),
        set(presets.keys()),
        warnings,
    )

    if not args.check:
        write_config(CONFIG_COLORS, "BTDT_COLORS", colors)
        write_config(CONFIG_FONTS, "BTDT_FONTS", fonts)
        write_config(CONFIG_PRESETS, "BTDT_PRESETS", presets)
        write_config(CONFIG_UI, "BTDT_UI", ui)
        print("Updated config catalogs:")
        print(f"- {CONFIG_COLORS.relative_to(ROOT)}")
        print(f"- {CONFIG_FONTS.relative_to(ROOT)}")
        print(f"- {CONFIG_PRESETS.relative_to(ROOT)}")
        print(f"- {CONFIG_UI.relative_to(ROOT)}")
    else:
        print("Check mode: no files written.")

    if warnings.items:
        print("\nWarnings:")
        for item in warnings.items:
            print(f"- {item}")
    else:
        print("\nNo warnings.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
