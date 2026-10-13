# OVERVIEW — Bootstrap Dynamic Themes

> **Status:** Draft. Non-normative orientation only: this document MUST NOT add, weaken, or reinterpret a normative requirement (`style.md` § Scope).

## Project

Bootstrap Dynamic Themes (BTDT) is a dynamic theming system for Bootstrap 6. It supplies generated, swappable CSS modules that assign values to Bootstrap's theme tokens — color, typography, shape, shadows, and optional personality rules — so a page can include, drop, or replace a theme at runtime without a rebuild and without touching Bootstrap's component CSS or the page's HTML.

BTDT is not a Bootstrap fork, not a build-time configuration layer, and not a collection of static stylesheets. Its purpose is the generation, packaging, and runtime exchange of token-value modules, plus the tooling (generators and a visual designer) that produces them from single-source palettes.

## Specification system organization

| Path | Role | Normative? |
|---|---|---|
| `.specify/memory/constitution.md` | Founding principles; prevails over every specification and implementation | Yes (Draft, not yet ratified) |
| `.specify/style.md` | Writing standard for normative documents | Yes |
| `.specify/specs/NNN-slug/spec.md` | Numbered specifications — executable contracts | Yes |
| `.specify/rationale/NNN-slug.md` | Decision memory: motives, alternatives, consequences | No |
| `.specify/OVERVIEW.md` | This document: entry point, terminology, organization | No |

Specifications are written under `specs/` as `NNN-slug/spec.md`, following `style.md`, with an optional matching rationale in `rationale/NNN-slug.md` when a decision needs justification.

## Terminology

- **Module** — a self-contained unit of theming: Sass source in, one standalone CSS file out. A module's role is to assign values to variables; it never contains component rules (personality is the only exception and rides the reserved `custom` layer).
- **Variable / token** — a CSS custom property that holds one design value (a radius, a shadow, a color key). Components read variables; they never hardcode values.
- **Theme color** — one named color of a palette, expanded into the 9-key set (`base, fg, fg-emphasis, bg, bg-subtle, bg-muted, border, focus-ring, contrast`) as `light-dark()` pairs.
- **Palette** — the single-source definition of a set of theme colors; input to the generator.
- **Base** — the trimmed Bootstrap 6 CSS (own `@forward` entry) plus the fixed component layer; common to every theme and never modified by a module.
- **Preset** — a named combination of active modules; equivalent to their concatenation, offered as a single-file convenience.
- **Personality** — optional theme rules (outline, texture, filter, shadow behavior) that live in the `custom` layer; the only module kind containing rules rather than variable assignments.
- **Generator** — the tooling that derives every module's variable assignments from single sources (palettes, scales, fonts).
- **Substitution** — replacing a module's CSS file (or its `<link>`) to change theme values; the mechanism BTDT is built on, in contrast to overriding with cascade weight.
- **Dark mode** — the dark `color-scheme` variant of a theme. Its derivation approach is not yet specified; no requirement is stated here.
