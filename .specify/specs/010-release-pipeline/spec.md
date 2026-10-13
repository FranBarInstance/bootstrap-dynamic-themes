# 010 — Release Pipeline

> **Status:** Draft.

## Scope

The BTDT build, verification, and release process for the 6.x line.

## Bootstrap target pinning

- Each BTDT release MUST pin exactly one Bootstrap 6.x version (the target).
- The target MUST be declared in release metadata and recorded in the base build provenance.
- Base build provenance MUST be a sidecar record; compiled CSS MUST NOT embed the target pin.
- The base build MUST read the Bootstrap source from an exact pin; floating version ranges MUST NOT be used.

## Base build

- The fixed component layer (`base.css`) MUST be compiled from a BTDT-owned entry file listing every `@forward` explicitly.
- `base.css` MUST NOT contain BTDT-authored rules; BTDT rules live only in personality modules.
- `base.min.css` MUST be produced from `base.css` by the pipeline minifier.

## Token manifest

- The pipeline MUST extract a token manifest from the compiled `base.css`: every custom property emitted or consumed, with its default value and its light/dark pair state.
- The manifest MUST be committed as pipeline output.
- Manifest extraction MUST be deterministic for a given pinned target.

## Target diff

- When the pinned target changes, the pipeline MUST diff the new manifest against the previous one.
- The diff MUST classify every change: added token, removed token, renamed candidate, changed default.
- A removed or renamed token consumed by any BTDT source or module MUST block the release until resolved.
- An added token MUST be assigned a providing module before release.

## Module and preset generation

- Every module CSS MUST be generated from single sources (palettes, scales, fonts).
- Hand-edited files inside generated output directories MUST NOT be committed.
- Generation MUST be reproducible: identical sources and identical target MUST produce byte-identical output.
- A preset MUST be the concatenation of its active modules in canonical load order; preset CSS MUST be generated, never authored.

## Gate terms

- Reference page: a committed fixture page exercising every Bootstrap 6 component and every token consumed by modules, at `test/reference.html`. It MUST contain standard Bootstrap 6 markup only.
- Default module set: the modules generated from the default palette source.
- Canonical load order: the fixed module order the generator applies to preset concatenation and `<link>` emission. The order MUST be deterministic and stable across releases.

## Release gates

- Reversibility: with all BTDT modules removed, the reference page MUST render identically to the same page under vanilla pinned Bootstrap (visual diff of zero).
- Load order: computed values on the reference page MUST be identical under every permutation of module load order.
- Coverage: every token consumed by `base.css` MUST appear in the manifest and MUST receive a value from the default module set.
- A release MUST NOT ship while any gate fails.

## Release record

- A release MUST bump the BTDT patch per the synchronized versioning policy (constitution VII).
- A release MUST record: pinned target, changelog entry, and tag.
- Re-running the pipeline against a new patch target with an empty token diff and unchanged sources MUST leave generated modules and presets byte-identical to the previous BTDT release.
- `base.css` and `base.min.css` MUST equal a fresh deterministic compile of the new target; release metadata, provenance, and the release record are outside the identical-output scope.
- Base build determinism: identical target and identical entry file MUST compile to byte-identical `base.css`.

## Open decisions (draft)

| Decision | Options | Resolution |
|---|---|---|
| Base scope | full vs trimmed `@forward` entry | open |
| Palette source format | own (JSON/YAML) vs Sass maps | open |
| Generator host | Node only vs shared with browser editor | open |
| Canonical load order rule | layer-then-name vs dependency-derived | open |
| Default palette source | stock Bootstrap 6 palette vs BTDT default theme | open |
