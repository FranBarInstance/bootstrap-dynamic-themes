# Agent Instructions — Bootstrap Dynamic Themes

Skills are located in `.agent/skills/`. Each skill has a `SKILL.md` with detailed rules.
**ALWAYS read the relevant `SKILL.md` BEFORE doing any work in that area.**

## Skill Trigger Map

| When the user asks to… | Read this skill first |
|---|---|
| Create a new **color** (a color palette, a new color file, new color variables) | `.agent/skills/create-color-theme/` |
| Add a new font or typography option | `.agent/skills/create-font-module/` |
| Create a new style modifier (borders, shadows, rounding, spacing, gradients, accent…) | `.agent/skills/create-style-module/` |
| Create or refine a **personality** layer (`personality-*`) that gives a theme a final finish without redefining it | `.agent/skills/create-theme-personality/` |
| Create a new **theme** or **preset** (a named theme that combines color + font + styles) | `.agent/skills/create-theme-preset/` |

## Core Concepts Summary

- **Fonts** (`btdt/themes/fonts/`): Typography modules using Google Fonts, mapping variables like `--bs-body-font-family`.
- **Colors** (`btdt/themes/colors/`): Palettes of CSS variables (primary, secondary, etc.). They contain only color data.
- **Styles** (`btdt/themes/styles/`): Structural modifiers (borders, shadows, rounding, spacing) that change the UI feel.
- **Personalities** (`btdt/themes/styles/personality-*.css`): Final finish layers that add character to an existing theme without fundamentally changing its identity. They should work across palettes and usually act through contour, shadow, texture, filter, or surface treatment.
- **Themes / Presets** (`btdt/themes/preset/`): Files that combine exactly **one** of each previous item via `@import` to create a complete look.

## Cross-cutting Rule — Catalog Sync
After creating, editing, or removing ANY module
(color, font, style, personality, or preset), always run:

1. `btdt/scripts/sync-configs.py`
2. `btdt/scripts/minify-all.py`
