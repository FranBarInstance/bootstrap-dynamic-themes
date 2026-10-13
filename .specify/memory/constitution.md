# Constitution — Bootstrap Dynamic Themes

> **Status:** Draft — not yet ratified. Ratified principles are immutable; amendments follow § Governance.

## Purpose

This constitution holds the founding principles of the project. It prevails over every specification, module, and generator: a specification or implementation that contradicts a principle is invalid until the principle is amended or the contradiction is resolved.

## Core Principles

### I. Bootstrap 6 Compatibility

BTDT and Bootstrap 6 MUST remain compatible in both directions:

- **Contract only** — BTDT consumes Bootstrap 6's public contract — theme token maps, `@layer` order, `.theme-*` classes, and the utilities API — and MUST NOT fork, patch, or modify the Bootstrap component layer.
- **Zero HTML** — theming MUST require zero HTML changes: a themed page uses stock Bootstrap 6 markup.
- **Reversibility** — with all BTDT modules removed, a page MUST render and behave exactly as vanilla Bootstrap 6.
- **Scope discipline** — a module MUST NOT alter appearance or behavior outside its declared scope.
- **No internals** — modules MUST depend only on documented Bootstrap 6 contract; undocumented selectors, variables, or component markup structures MUST NOT be relied upon.

### II. Substitution, Not Override

Theme modules MUST replace defaults by substitution. Modules MUST NOT fight the cascade with `!important` or specificity hacks; user-authored rules ride the framework's reserved `custom` layer.

### III. Modules Are the Unit

Each module — color, font, style, personality — is a self-contained unit: Sass source in, one standalone CSS file out. A module MUST NOT depend on the internals of another module; a preset is a pure combination of modules.

### IV. Runtime Dynamic

Every compiled module MUST be includable, removable, or replaceable in a live page without a rebuild. Module CSS MUST behave identically regardless of load order, relying on `@layer` order and token values alone.

### V. One Source, Computed Derivations

A palette is authored once in a single source format; the generator MUST emit every derived value — the full 9-key theme map for light and dark as `light-dark()` pairs in OKLCH. Hand-declaring a derivation the generator can compute is a defect.

### VI. Specification First

Architecture decisions and contracts live in `.specify/` before the implementation they govern. The specification system is the source of truth; a discrepancy between code and a ratified specification MUST be resolved in one direction or the other, never left silently.

### VII. Bootstrap-Synchronized Versioning

The major and minor version of BTDT track the Bootstrap minor they target: `6.0.x` targets Bootstrap `6.0`. Every BTDT release MUST declare its Bootstrap target.

## Governance

- These principles prevail over every specification, template, and implementation in this repository.
- An amendment requires an explicit user decision, a dated entry in the amendment record, and a review of every specification and rationale affected.
- When two specifications contradict and no specification resolves the conflict, these principles decide.
- New principles follow the numbering system: they are appended with the next roman numeral and never renumber existing ones.
