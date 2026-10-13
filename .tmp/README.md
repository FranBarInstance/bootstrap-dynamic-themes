# .tmp/

Scratch space for temporary files. Everything in this directory is disposable and must never be committed.

**Agents and tooling should use the `.tmp/agent/` subdirectory for anything temporary**: drafts, intermediate build artifacts, exported dumps, test output, throwaway scripts. Create it if it does not exist yet. This is the designated place to write scratch files so that nothing — agents included — ever needs to touch the filesystem outside the repository sandbox.

Rules:

- Anything here may be deleted at any time, without notice.
- Nothing here is part of the project: no source, no docs, no deliverables.
- Final artifacts belong in their proper tracked location, never here.
- Do not write temporary files anywhere else in or outside the repo; write them under `.tmp/agent/`.
