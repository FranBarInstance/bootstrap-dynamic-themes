# Specification Writing Standard

## Status

Normative. New normative documents and substantive changes to existing normative documents MUST comply. Existing documents remain legacy until migrated; their migration MUST be completed before they are rejected solely for non-compliance with this standard.

## Purpose

A specification is an executable contract for an autonomous agent: a **list of verifiable requirements** — an order to carry out. The agent applying it usually does not need to know the motive; it must execute.

This standard minimizes text, eliminates redundancy, leaves no room for interpretation, and reduces the AI context needed to apply a specification.

Design context, alternatives, and explanations belong in `rationale/`.

## Scope

Applies to every normative document under `.specify/`: numbered specifications in `.specify/specs/NNN-slug/spec.md`, and any other normative document of the specification system.

The form rules of this standard do not apply to `.specify/OVERVIEW.md` or `rationale/`; the Language requirements below still apply. Those documents MUST NOT add, weaken, or reinterpret a normative requirement.

Templates are non-normative: the form rules do not apply to them, only the obligations of this paragraph and the Language requirements below. A template MUST be designed so that filling it in produces a specification that complies with this standard. Guidance to the author MAY appear in a template only when clearly marked as removable.

## Form: telegraphic

A specification is a list of things, nothing more:

- One requirement per list item.
- Tables for fixed contract values, interfaces, data shapes, and invariants.
- No prose paragraphs.
- No justifications, historical notes, rejected alternatives, or decision context.

## Normative language

- `MUST`: an unconditional requirement.
- `MUST NOT`: an unconditional prohibition.
- `MAY`: a permitted option.
- `SHOULD`: a requirement that permits an explicit, documented exception.

Every normative statement MUST use one of these terms, unless it defines a fixed fact, interface value, data shape, or invariant.

- Use direct declarative or imperative sentences in the present tense.
- Use explicit conditions when behavior depends on a state or event: `When <condition>, <subject> MUST <result>.`
- Do not use causal connectors: `because`, `since`, `in order to`, `therefore`, `so that`, `to guarantee`.
- Do not use justificatory formulas ("per principle X", "to guarantee Y"): state the requirement. A pointer to the governing principle or specification MAY follow in parentheses.

## Conciseness

- Write as little text as possible without omitting conditions, actors, or observable results.
- One idea per list item.
- Remove filler words that do not affect clarity.

## Language

- Every document under `.specify/` MUST be written in English.
- Non-English terms MUST be limited to proper nouns, identifiers, and quoted technical vocabulary.

## Line wrapping

- Every document under `.specify/` MUST use soft wrap: one line per paragraph, no manual line breaks at a fixed column.
- Each list item MUST occupy a single line. Tables and fenced code blocks are exempt: each table row and each code line keeps its own line.
- Existing hard-wrapped documents are legacy until migrated; reflow MUST be completed when they are next substantively edited.

## Content

- Every statement MUST be verifiable by inspection, test, or another stated acceptance criterion.
- A specification MUST NOT contain design justification, historical notes, decision context, or rejected alternatives.
- A specification MUST define terms whose meaning is not unambiguous in the project terminology.
- A specification MUST NOT depend on a rationale document to define or interpret a requirement.

## References

- A reference is a pointer. Format: `spec NNN`.
- A normative reference MUST link to its governing document and section when a section is relevant.
- Do not use causal constructions ("given that spec NNN establishes…").

## Examples

**Not permitted**

> The preset link is re-resolved because the active theme can change at runtime.

**Permitted**

> The loader MUST re-resolve the preset link whenever the active theme changes.

**Not permitted**

> A module may ship a `.min.css` twin, which keeps production loads fast without extra tooling.

**Permitted**

> A module MAY ship a `.min.css` twin. If it exists, the loader MUST resolve it in preference to the source file. If it does not exist, loading MUST be unaffected.

## Rationale Documents

### Structure

`rationale/` is relative to `.specify/`.

```text
.specify/
  specs/
    NNN-slug/
      spec.md
  rationale/
    NNN-slug.md
    style.md
    superseded/
```

- A rationale for a numbered specification MUST use the same `NNN-slug` name.
- A rationale for a decision spanning several specifications MAY use the combined name `NNN-MMM-slug.md`, referenced from the involved specifications.
- A rationale for a cross-cutting policy MAY use that policy's basename, such as `style.md`.

### Purpose and content

A rationale is non-normative decision memory: the **why** that is not in the specification. A rationale is not mandatory; it is recommended when a decision's motive is not evident from the specification alone — a significant decision, a contract change, or a rejected alternative.

- Justify only significant decisions, not every line of the specification.
- A rationale MUST NOT restate the requirements of the specification. It documents only what the specification does not: the motive.
- Each rationale MUST contain:
- `Status`.
- `Context`.
- `Decisions and motives`: for each relevant decision, `Decision`, `Motive`, and `Alternatives considered`.
- `Consequences`.
- `Relationships` (links to the related specifications).
- It MAY contain diagrams, discussion links, implementation notes, and a change history.
- Rationale documents are written in discursive style, with complete justifications.

### Reading rules

An agent applying a specification MUST NOT read `rationale/` during its normal implementation, review, or validation path.

An agent creating or modifying a specification MUST read its associated rationale when one exists. When a decision's motive is not evident from the specification alone, the agent SHOULD create or update the rationale in the same change, covering the decision, its motives, alternatives, or consequences.

An agent MAY read the applicable rationale while applying a specification only when the normative document cannot be applied safely because it is materially unclear, ambiguous, or contradictory. The rationale MAY clarify intent but MUST NOT override the specification. The agent MUST report the defect so that the normative document can be corrected.

### Lifecycle

- When a rationale exists, a changed decision MUST record its date and a concise change summary in it.
- A rationale replaced as a whole MUST be moved to `rationale/superseded/`, marked `superseded`, and link to its replacement.

## Review Checklist

A normative-document review MUST confirm all of the following:

- Telegraphic form: one requirement per list item; tables for fixed values; no prose paragraphs.
- Normative statements use defined normative language or define a fixed contract value.
- No causal connectors or justificatory formulas.
- Conditions, actors, and observable results are explicit.
- References are pointers that link to their governing source.
- Rationale material is absent from the normative contract.
- The associated rationale, when it exists, does not restate the specification.
- Acceptance criteria verify the stated requirements.
- All documents under `.specify/` are written in English.
