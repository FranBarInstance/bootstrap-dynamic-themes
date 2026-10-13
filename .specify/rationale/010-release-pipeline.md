# Rationale — 010 Release Pipeline

> **Status:** Draft, accompanies the draft specification.

## Context

BTDT lives on top of a moving Bootstrap 6 line that was alpha at writing time (6.0.0-alpha.1, October 2026). BootstrapDyn (the v5 sibling) needed a heavy extractor because Bootstrap 5 hardcoded design values inside component CSS; Bootstrap 6 already emits tokens as CSS variables, so the extraction step collapses into compilation plus a manifest. The pipeline shape follows from that difference.

## Decisions and motives

**Decision: pin one exact Bootstrap target per BTDT release.**
Motive: the whole promise of constitution I (compatibility, reversibility, no internals) is testable only against a known Bootstrap. Floating targets make every guarantee unfalsifiable.
Alternatives considered: range-based dependencies (rejected: silent breakage between patches); manual "tested with" notes (rejected: not enforceable in CI).

**Decision: the token manifest is a committed, diffed artifact.**
Motive: token drift between Bootstrap versions is the single realistic source of incompatibility. A committed manifest turns drift into a reviewable diff and gives the future module/variable contract and the editor one machine-readable source of truth for which variables exist.
Alternatives considered: diffing compiled CSS text (rejected: noisy, unclassified); keeping the manifest out of the repo (rejected: no history, no CI gate).

**Decision: generation is reproducible and outputs are not hand-edited.**
Motive: the visual designer and the CLI must emit the same bytes for the same input; byte-identical output makes cache, review, and regression checks trivial. Hand-edits in output directories silently break that property.
Alternatives considered: allowing hand-tweaks in generated files (rejected: forks the single-source principle, V).

**Decision: release gates (reversibility, load order, coverage).**
Motive: constitution I and IV state guarantees; gates make them mechanically checkable rather than aspirational.
Alternatives considered: manual QA per release (rejected: does not scale across Bootstrap patch releases).

**Decision: provenance is a sidecar record; identical output covers generated modules and presets only.**
Motive: a target pin embedded in a committed artifact changes on every retarget, which would make the identical-output requirement impossible to satisfy by construction. A Bootstrap patch routinely changes component CSS without touching tokens, so requiring `base.css` itself to stay identical would block the automatic release path in the common case; it must instead equal a fresh deterministic compile of the new pin.
Alternatives considered: pin banners inside compiled CSS (rejected: defeats the identical-output requirement); omitting provenance from the pipeline (rejected: provenance must stay reviewable per the pinning decision); requiring `base.css` byte-identical across patch targets (rejected: unsatisfiable in the common case, and BTDT wants the patch's component fixes).

**Decision: gate terms (reference page, default module set, canonical load order) are defined in the specification itself.**
Motive: the gates block releases, and a gate phrased over undefined terms is not mechanically checkable. The terms land in 010 because the specs that would naturally own them (module contract, presets) do not exist yet.
Alternatives considered: leaving the terms to future specs (rejected: the gates stay inexecutable until those specs exist); defining them in OVERVIEW (rejected: OVERVIEW is non-normative).

## Consequences

- Every Bootstrap 6.x release triggers a BTDT pipeline run; most runs are expected to be automatic (empty diff), with manual work only when tokens change.
- The manifest file becomes a load-bearing artifact for the module contract, the palette source, and the editor.
- Output directories (`base/`, `themes/`) are disposable; sources are the only authored truth.

## Relationships

- Constitution: I (compatibility), IV (runtime dynamic), V (one source), VII (synchronized versioning).
- Specs: 001 (module/variable contract), 002 (palette source), 005 (personality), 006 (presets, load order), 007 (generators).
