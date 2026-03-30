# Skill: Create Color Theme

## When to use this skill
Use this skill when the user explicitly asks to:
- "create a new **color**", "create a color palette", "add a new color to the system"
- "I need a new color variant called…", "design a color palette for…"
- Create the raw color CSS variables file for a new palette (not a full theme)

> **Note**: If the user asks to "create a theme" or "create a preset", use `create-theme-preset` instead. A color is just one part of a theme.

This skill allows the AI to design and implement new color palettes for the Bootstrap Dynamic Themes (BTDT) system.

## Project Context
The application is a dynamic theme engine for Bootstrap 5. Themes are injected at runtime. Color themes must define core Bootstrap variables and handle component-specific overrides to ensure a premium look.

## Directory Structure
Color themes are stored in: `btdt/themes/colors/[theme-name].css`
The starting point is always the template: `btdt/themes/colors/_template_.css`.

## Implementation Guidelines

### 0. Research & Reference (MANDATORY)
Before starting, you MUST open `btdt/themes/colors/_template_.css` and base the new theme on it.
You MAY also read existing themes for inspiration (recommended: `btdt/themes/colors/corporate.css` and `btdt/themes/colors/white.css`), but the template is the source of truth for structure.

For advanced color theory and aesthetic guidelines, consult: `btdt/docs/color-system.md`.

### 1. Template-First Workflow (CRITICAL)
- Copy `btdt/themes/colors/_template_.css` to `btdt/themes/colors/[theme-name].css`.
- Only edit the variables and tokens provided by the template.
- Do NOT create new selectors, classes, or overrides.
- Do NOT overwrite existing class blocks; the template already contains all required structure.

### 1.1 Contrast Awareness (CRITICAL)
Set the contrast-related variables in the template so that:
- If the `--bs-primary` or `--bs-secondary` color is light (e.g., pastels, lime, yellow), text on those backgrounds uses a dark color (e.g., `#1a1a1a`).
- Conversely, for dark primary colors, text uses white.
- **Navbar Toggler**: The current app no longer uses a filter-based SVG icon for the navbar toggler.
  The icon now inherits `currentColor` from the navbar, so getting `--bs-primary-contrast` and related contrast colors right is enough.

### 1.2 Component Overrides
Do not add or modify component override selectors. All required overrides must already exist in the template.

### 1.2.1 Very Light Themes (Note)
In very light themes, some elements may need theme-specific tweaks (for example, the checkbox checkmark in `btdt/themes/colors/white.css`). Only add such rules when they are strictly necessary, and never modify `btdt/css/color-theme-rules.css`.

### 1.3 Custom Accent Color
- **Default**: Set `--accent-color` (and its RGB version) to be the SAME as `--bs-primary`.
- **Refinement (Optional)**: If a subtle variation is desired to make the accent stand out:
  - **For Dark Primary themes**: Use a slightly LIGTHER version (tint) of the primary color.
  - **For Light Primary themes**: Use a slightly DARKER version (shade) of the primary color.
- **Goal**: The accent should feel like a natural extension of the primary brand color, providing a premium, integrated look instead of a sharp, high-contrast break.
- **SVG Sync**: Keep the embedded SVG tokens in the template aligned with the colors they represent.
  Today this mainly affects `--bs-accordion-btn-active-icon` and `--bs-form-switch-focus-bg`.

### 2. Button Overrides
Only adjust the template variables used by button styles. Do not edit selector blocks.

### 3. Utility Classes
Do not add or modify utility class selectors. The template defines them.

### 4. Catalog Sync (CRITICAL)
After creating or removing a color module, do NOT edit `btdt/js/config-colors.js` manually.

Instead, run:
- `btdt/scripts/sync-configs.py`

This regenerates `btdt/js/config-colors.js` from the filesystem and keeps the editor catalog aligned with the real modules.

If the task also requires minified assets to be updated, run after that:
- `btdt/scripts/minify-all.py`

Order matters:
1. `btdt/scripts/sync-configs.py`
2. `btdt/scripts/minify-all.py`

### 5. Accessibility & Legibility (Crucial)
The template already includes any required link legibility rules. Do not add or duplicate selector blocks.

## Aesthetic Standards
- Avoid generic colors. Use harmonious, curated palettes (e.g., Pastel, Midnight, Earth tones).
- **Background Color (IMPORTANT)**: By default, the body background (`--bs-body-bg`) MUST be white (`#ffffff`).
  - Only use off-white or very light tinted tones (e.g., `#f8f9fa`, `#fffcf2`) if the USER explicitly asks for a "creative", "imaginative", or "themed" approach, or if the specific aesthetic (like "Autumn" or "Vintage") strongly requires it.
- For "Dark" themes, ensure subtle contrast rather than pure black (#000). Use deep grays or navy.
- For "Light" themes, ensure the primary color isn't too bright to wash out text.

## Example Reference
See `btdt/themes/colors/corporate.css` for structural examples.
