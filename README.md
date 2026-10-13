# Bootstrap Dynamic Themes

> **Status: rewrite in progress.** This branch (`main`) is the **6.x line** — a
> from-scratch rewrite on top of Bootstrap 6. It currently contains no code:
> the architecture and the directory layout are being redesigned before the
> first commit of the new implementation.
>
> For production use, the current stable line lives on the
> [`v5`](../../tree/v5) branch (Bootstrap 5.3.8, latest release `3.0.1`).

## Branch map

| Branch | Line | Bootstrap base | Status |
|---|---|---|---|
| `main` | 6.x | 6.x | 🚧 Rewrite in progress — no code yet |
| `v5` | 3.x | 5.3.8 | Stable / maintenance only (fixes, `3.x.y` releases) |

## Versioning policy

From the 6.x line onward, versions are **synchronized with Bootstrap's first
two digits** (same scheme as [BootstrapDyn](https://github.com/FranBarInstance/BootstrapDyn)):

- **Major & Minor** — synchronized with Bootstrap (`6.0.x` targets Bootstrap `6.0`).
- **Patch** — BTDT's own revision.

| BTDT version | Target Bootstrap | Status |
|---|---|---|
| 3.0.1 | 5.3.8 | Final of the 3.x line (`v5` branch) |
| 6.0.x | 6.0 | Rewrite in progress (`main`) |

Versions `0.x`–`3.x` predate this policy and followed BTDT's own numbering.

## Direction of travel

The 6.x line rebuilds BTDT around what Bootstrap 6 and the BootstrapDyn
experiment proved:

- **Substitution, not overriding** — themeable module files that replace
  defaults instead of fighting the cascade with `!important`.
- **One source format per module + generators** — palettes, styles,
  personalities and presets are authored once and compiled per target.
- **Computed color tokens** — each theme color emits the full 9-key token set
  (`base, fg, fg-emphasis, bg, bg-subtle, bg-muted, border, focus-ring,
  contrast`), light and dark, as `light-dark()` pairs.
- **Dark mode with identity** — dark values derived per palette, not a
  generic grayscale overlay.
- **CSS layers** — contrast and personality layers ride the framework's own
  `@layer` order.

## History

Everything before the rewrite is preserved on the `v5` branch and in the tags
up to `3.0.1`. The full license text (MIT) lives there as well.
