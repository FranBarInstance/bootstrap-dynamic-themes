# Bootstrap Dynamic Themes

> **Status: rewrite in progress.** This branch (`main`) is the **6.x line** — a from-scratch rewrite on top of Bootstrap 6. It currently contains no code: the architecture and the directory layout are being redesigned before the first commit of the new implementation. For production use, the current stable line lives on the `v5` branch.

## Branch map

| Branch | Line | Bootstrap base | Status |
|---|---|---|---|
| `main` | 6.x | 6.x | 🚧 Rewrite in progress — no code yet |
| `v5` | 3.x | 5.3.8 | Stable / maintenance only (fixes, `3.x.y` releases) |

## Versioning policy

From the 6.x line onward, versions are **synchronized with Bootstrap's first two digits**:

- **Major & Minor** — synchronized with Bootstrap (`6.0.x` targets Bootstrap `6.0`).
- **Patch** — BTDT's own revision.

| BTDT version | Target Bootstrap | Status |
|---|---|---|
| 3.0.1 | 5.3.8 | Final of the 3.x line (`v5` branch) |
| 6.0.x | 6.0 | Rewrite in progress (`main`) |

Versions `0.x`–`3.x` predate this policy and followed BTDT's own numbering.

## From v5 to v6

Bootstrap 6 (`6.0.0-alpha.1`, October 2026) is not an update but a rebuild on native web standards: a much higher browser floor (Chrome/Edge 130, Firefox 132, Safari 18), colors in OKLCH with `color-mix()`, `light-dark()` pairs for light/dark values, CSS `@layer` across the whole framework, Sass modules (`@use`/`@forward`), and ESM-only JavaScript. That is why the 6.x line does not migrate the v5 code — it rewrites everything, including the directory layout.

### What Bootstrap 6 now does natively

Most of the value BTDT provided on top of Bootstrap 5 is now part of the framework itself:

- **Dynamic contrast** — every theme color is a 9-key token map (`base, fg, fg-emphasis, bg, bg-subtle, bg-muted, border, focus-ring, contrast`), so readable text on any background is a token the components consume, not an override rule.
- **Dark mode by default** — light and dark values live together in `light-dark()` pairs, always compiled; no separate dark stylesheet, no `data-bs-theme` juggling for the whole page.
- **Composable theming** — `.theme-*` classes recolor any component through inheritable `--bs-theme-*` tokens; color is no longer baked into per-component classes.
- **Module substitution** — a reserved empty `@layer custom`, token maps that can be partially overridden, and `@forward`-based entry points make "replace the module, don't fight the cascade" an officially supported pattern instead of a workaround with `!important`.

### What Bootstrap 6 still is not

**Dynamic.** Theming in Bootstrap 6 is a build-time activity: you configure Sass maps and recompile. Each color's nine keys must be declared by hand — changing only `base` does not recompute `fg`, `bg-subtle` or `contrast` — and the framework has no runtime notion of a theme, a preset, or a module you can swap in the browser without a build.

That gap is precisely what BTDT 6.x exists to fill: author a palette once, generate the full nine-key light/dark token maps automatically, ship them as swappable CSS modules, and toggle modules and presets at runtime — plus the visual designer Bootstrap 6 does not offer.

## Direction of travel

The 6.x line rebuilds BTDT around what Bootstrap 6 proved:

- **Per-module Sass compiled to separate CSS** — every module (color, font, style, personality) is authored in Sass and compiled to its own standalone CSS file, alongside a trimmed Bootstrap base built from a custom `@forward` entry.
- **Dynamic at runtime** — those compiled files are plain CSS modules that a page can include, drop, or replace live via `<link>` swapping; the framework's `@layer` order keeps the result deterministic regardless of load order.
- **Adapted generators** — the existing BTDT generator tooling is ported to the v6 token format: palettes emit the full 9-key theme maps as `light-dark()` pairs in OKLCH (deriving by computation what Bootstrap 6 asks you to declare by hand), fonts emit v6 typography tokens, styles emit v6 scales (`--radius-0…9`, spacers `0…12`), and presets are pure module combinations.
- **Substitution, not overriding** — modules replace defaults instead of fighting the cascade with `!important`.
- **Dark mode** — the dark values of each palette are derived by the generator; the derivation approach is not yet specified.

## History & license

Everything before the rewrite is preserved on the `v5` branch and in the tags up to `3.0.1`. The 6.x line is MIT-licensed (see `LICENSE`); the third-party works it builds on and their licenses are listed in `THIRD-PARTY.md`.
