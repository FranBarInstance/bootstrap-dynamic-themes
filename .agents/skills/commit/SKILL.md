---
name: commit
description: Group changes into semantic commits following repository standards.
---

# Semantic Commit Only

This skill guides you through the process of grouping current changes into meaningful semantic commits.

## Rules and Constraints

- **MANDATORY - Explicit Request**: **NEVER** perform a commit unless the user has explicitly requested it in the current or immediate past turn. Do not assume that finishing a task implies permission to commit.
- **Full Repository Inspection**: Before proposing any commit, inspect the current state:
  - `git status --short`
  - `git diff --stat`
  - `git diff`
  - `git log --oneline -10`
- **Semantic Grouping**: Identify related file groups by intent:
  - `feat`: New features
  - `fix`: Bug fixes
  - `refactor`: Code changes that neither fix a bug nor add a feature
  - `docs`: Documentation only changes
  - `test`: Adding missing tests or correcting existing tests
  - `chore`: Changes to the build process or auxiliary tools and libraries
  - `perf`: Code changes that improve performance
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
  - `ci`: Changes to CI configuration files and scripts
- **Independence**: Create multiple commits when there are independent changes. Do not mix unrelated changes in the same commit.
- **Contextual Messages**: Use the user's prompt and conversation context to adjust commit messages, but ensure they accurately describe the changes.
- **No Footers**: Commit messages MUST NOT contain footers, signatures, or attributions of any kind (`Co-Authored-By`, `Generated with …`, `🤖`, or equivalents). The message ends with the last line of its body.
- **Excluded Directories**: Ensure no files from `.tmp/`, `node_modules/`, `.venv/`, or `__pycache__/` are ever staged or committed.
- **Security Check**: Before committing, check for sensitive or suspicious files (`.env`, tokens, credentials, keys, secrets). **Stop and ask if any are found.**
- **Absolute Path Check**: Ensure all paths are relative to the repository. **Never include absolute system paths** (e.g., `/home/user/...`).
- **Safety Script**: Run `python3 .agents/skills/commit/scripts/check_commit_safety.py` after staging each group. The script uses exit codes: **`exit 0`** means no issues; **`exit 1`** means warnings were found. Check the exit code — do **not** rely on parsing stdout. It checks sensitive file names, excluded paths (`.tmp/`, `node_modules/`, `.venv/`, `__pycache__/`, `.thinking/`, `AGENTS.local.md`), absolute paths, and hardcoded secrets. Standard library only — no virtual environment needed.
- **Intentional False Positives**: The safety script is intentionally strict and does **not** support automated exceptions (white-lists), as this could lead to security gaps. Expect false positives in documentation, module names, or security logic. If a warning occurs, you **must** analyze the output, explain why it is a false positive, and wait for explicit human validation before proceeding.
- **Spec Compliance Script**: Run `python3 .agents/skills/commit/scripts/check_spec_compliance.py` after staging each group that touches `.specify/`. The script validates specification form against `style.md` (telegraphic form, causal/justificatory wording, spec and rationale naming, `spec NNN` reference integrity). Exit code **`exit 0`** means clean; **`exit 1`** means violations found — stop and analyze. Standard library only — no virtual environment needed.
- **Scripts Read the Staged Set**: The safety and spec compliance scripts operate on `git diff --cached` (staged files). Running them with nothing staged is a no-op that reports "no files staged" — always run them AFTER `git add`, never as a pre-flight substitute for staging.
- **NEVER Auto-fix Specification Violations**: When a specification violation is detected (wrong format, missing fields, contradictions), **STOP and REPORT to the user**. Do NOT automatically fix the violation. **You cannot know in advance whether the fix belongs in the code or in the specification itself.** The correct action is:
  1. Report the violation clearly
  2. Search for references across the codebase (modules, generators, other specs, documentation)
  3. Present the findings to the user
  4. **ASK the user** whether to fix the code, modify the specification, or handle it differently
  5. WAIT for explicit confirmation before making any changes
  - **Exception**: If the user explicitly requests you to make the correction (e.g., "fix it yourself", "go ahead and correct it"), you may proceed without further questions. In that case, perform a thorough search-and-replace, verify all references are updated, and re-run all checks.
- **Test Execution (Recommended)**: Before committing code changes, run the repository's test command if one is defined (e.g., `npm test`). For docs-only or config-only changes, tests may be skipped (but verify with user).
- **Spec Compliance Review**: Before staging a group that modifies module sources (Sass/CSS modules, generators, build scripts) or `.specify/`, read the relevant specification files and verify the changes do not contradict them. The specs under `.specify/` are the source of truth; if code differs from a spec, the spec wins and the discrepancy must be resolved before committing.
- **Spec Consistency Review (`.specify/` changes)**: When a commit includes any change under `.specify/`, perform a cross-specification consistency review before creating the commit. This review checks consistency **between specification files** (spec-to-spec), not code-to-spec: the changes must not introduce contradictions and must remain consistent with the entire current specification. Read the changed spec files together with the full specification system (`.specify/OVERVIEW.md`, `.specify/memory/constitution.md`, `.specify/style.md`, and every spec the change references or affects). If a contradiction or inconsistency is found, **STOP, offer the user a solution, and ask for confirmation** before proceeding. Never auto-fix a specification inconsistency.
- **No Side Effects**:
  - Do NOT use `--no-verify`.
  - Do NOT amend commits.
  - Do NOT revert existing changes.
- **Push Policy**: Do **NOT** perform `git push` unless specifically requested by the user in a separate turn. This skill is only for committing.

## Specification Compliance Rules

When modifying files under `.specify/`, module sources (color, font, style, personality), or the generators, verify compliance with these concrete rules:

### Specification Writing Rules (style.md)

- **Telegraphic form**: Normative specification documents (`spec.md`) MUST be concise lists of verifiable requirements.
- **No causal connectors**: Avoid words such as `because`, `since`, `in order to`, `therefore`, `so that`, `to guarantee` in requirements.
- **No justificatory formulas**: Avoid phrases like `to ensure`, `to avoid`, `to prevent`, `per principle`. Motives and decision context belong in `rationale/`.
- **Soft wrap**: Specification documents use one source line per paragraph; no manual hard wrapping.
- **False positives**: The compliance script flags potential causal or justificatory words with `🟡 WARNING`. Analyze flagged lines to determine whether they are genuine violations or acceptable false positives.

## Specification Consistency Review (`.specify/` changes)

**Trigger**: A commit group that stages any file under `.specify/`.

**Scope**: Consistency between specification files, not between code and specifications. The review verifies that the changed specification does not contradict the rest of the specification system.

**Procedure**:

1. Identify every staged file under `.specify/`.
2. Read the changed files together with the full current specification system:
   - `.specify/OVERVIEW.md` (project, principles, terminology, organization).
   - `.specify/memory/constitution.md` (the constitution principles — they prevail over every specification).
   - `.specify/style.md` (writing standard and review checklist).
   - Every specification the change references or affects (follow `spec NNN` pointers, and any shared contract such as module file naming, token names, or `@layer` order).
3. Verify the change is consistent with the current specification. Check, at minimum:
   - **No contradictions**: the change does not conflict with, weaken, or reinterpret an existing normative requirement (`style.md` § Scope: `OVERVIEW.md` and `rationale/` MUST NOT add, weaken, or reinterpret a normative requirement).
   - **Constitution compliance**: the change does not violate any constitution principle.
   - **Terminology**: terms match the definitions in `OVERVIEW.md` (§ Terminology); any new non-obvious term is defined.
   - **References**: every `spec NNN` pointer resolves to an existing document and section.
   - **Status coherence**: a definitive specification does not silently depend on a draft specification; status metadata is clearly labelled and non-normative.
   - **Cross-spec contract values**: a fixed contract value (e.g. module naming suffixes, token names, load order) is not defined differently in two specifications.

**On inconsistency**:

1. **STOP** — do not create the commit.
2. **REPORT** the contradiction or inconsistency with the specific files and the conflicting requirement(s).
3. **OFFER a solution** — propose options to the user, for example:
   - Modify the changed specification to remove the contradiction.
   - Modify the existing specification (and its rationale) that it contradicts.
   - Split or defer the change until the dependent specifications are updated.
4. **ASK for confirmation** — wait for explicit user confirmation before making any change. Never auto-fix a specification inconsistency.

**User Override**: If the user explicitly requests a specific correction, perform the search-and-replace, update every affected specification and the matching rationale (`style.md` § Rationale Documents), and re-run the consistency review before committing.

## Workflow

### Phase 1: Pre-flight Checks (MANDATORY — before any analysis)

Run these validations **first**, before inspecting git state. If any check fails, **stop and report** — do not proceed to analysis.

1. **Security Check**: Scan for sensitive files (`.env`, tokens, credentials, keys, secrets). **Stop and ask if any are found.**
2. **Absolute Path Check**: Ensure all paths are relative to the repository. **Never include absolute system paths** (e.g., `/home/user/...`).
3. **Run Tests**: Run the repository's test command if one is defined (e.g., `npm test`).
   - If any test fails: report the failure and do not proceed until tests pass.
   - For docs-only or config-only changes, tests may be skipped (but verify with user).

**Handling Violations (CRITICAL — applies to all checks above):**

When any check fails (security, safety, spec compliance, or tests), follow this exact sequence:

1. **STOP immediately** — do not proceed with the commit.
2. **REPORT the violation** to the user with:
   - What failed and why
   - The specific file(s) and line(s) affected
   - For identifier violations: search for all references across the codebase using `grep` or code search
   - List ALL locations where the identifier/concept is used
3. **ASK the user** how to proceed:
   - Should the code be fixed to match the spec?
   - Should the specification be updated instead?
   - Is this a false positive that should be ignored?
   - Are there other considerations?
4. **WAIT for explicit confirmation** before making any changes.
5. **IF approved**: perform the agreed changes, verify no references are missed, and re-run all checks.

**NEVER assume you know the correct fix.** The violation might require code changes, spec changes, or both. Only the user can decide.

**User Override**: If the user explicitly requests it (e.g., "fix it yourself", "go ahead and correct it", "make the necessary changes"), you may proceed with the correction without further questions. In that case, perform a thorough search-and-replace, verify all references are updated, and re-run all checks before committing.

### Phase 2: Analyze Repository State

1. Run inspection commands:
   - `git status --short`
   - `git diff --stat`
   - `git diff`
   - `git log --oneline -10`
2. If the user has not explicitly asked for a commit, **stop here** and ask if they wish to commit the changes.

### Phase 3: Propose Plan

Present a plan to the user showing:
- The proposed commits (semantic grouping).
- The files included in each commit.
- The proposed commit message for each.

### Phase 4: Validate with User

Wait for user confirmation. If there is ambiguity, ask for clarification.

### Phase 5: Execute Commits

For each group:
1. Add only the specific files (avoid `git add .`): `git add <files>`
2. Verify staged files: `git status`
3. Run safety script: `python3 .agents/skills/commit/scripts/check_commit_safety.py`
   - If exit code 1: **stop immediately**, analyze false positives, show to user.
4. Run spec compliance script (groups touching `.specify/`): `python3 .agents/skills/commit/scripts/check_spec_compliance.py`
   - If exit code 1: **stop immediately**, analyze violations, show to user.
5. Run Spec Consistency Review (if the group stages any file under `.specify/`): follow the procedure in "Specification Consistency Review". If an inconsistency is found, **stop immediately**, offer a solution, and ask for confirmation.
6. Run tests (if code changes and a test command is defined).
7. Create the commit: `git commit -m "<type>(<scope>): <subject>"`

### Phase 6: Summarize

Provide a summary of the commits created.

## Best Practices

- Use the imperative mood in the subject line (e.g., "add feature" instead of "added feature").
- Keep the first line short (under 50 characters if possible).
- Use module and tool names as scopes when applicable: `color`, `font`, `style`, `personality`, `preset`, `loader`, `generator`, `build`, `spec`, `docs`.
- If no specific scope applies, use the format `<type>: <subject>` (omit the parentheses).
- Use the repository's existing commit style as a reference (the `v5` branch history and tags `0.x`–`3.0.1`).
