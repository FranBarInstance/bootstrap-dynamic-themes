# Agent Instructions — Bootstrap Dynamic Themes

Skills are located in `.agents/skills/`. Each skill has a `SKILL.md` with detailed rules. **ALWAYS read the relevant `SKILL.md` BEFORE doing any work in that area.**

## Local Overrides — `AGENTS.local.md`

Before starting any work, check for an `AGENTS.local.md` file at the repository root. If it exists, read it and follow it. Where it adds to or overrides a rule in this file, the local file wins.

## Specifications — Mandatory

- The agent MUST consult the specification system before any architecture.
- `.specify/OVERVIEW.md` MUST be the entry point to the specification system.
- Specifications under `.specify/` MUST take precedence over all other guidance except explicit user instructions.
- All specification documents under `.specify/` MUST be written in English (`.specify/style.md`).
- Specifications are telegraphic; motives live in `rationale/`. The agent MUST NOT read `rationale/` when implementing or reviewing. The agent MAY read it only when modifying a contract or when a spec is materially ambiguous (`.specify/style.md` § Rationale Documents).

## Temporary Files

- All temporary files and scripts created in this repository MUST be placed under `.tmp/agent`. No scratch files elsewhere.
- The `.tmp/` directory always exists in this repository.
- If `.tmp/agent` does not exist yet, the agent MUST create it before writing temporary files there.
- `.tmp/agent` confines scratch files to a single location; files elsewhere risk being committed and may contain sensitive data.

## Line Wrapping

- Every document in this repository MUST use soft wrap.
