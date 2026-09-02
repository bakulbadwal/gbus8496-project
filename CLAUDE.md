# CLAUDE.md

**Read `AGENTS.md` first — it is the full contract for this repo and applies to Claude Code exactly
as it does to every other agent.** Nothing here overrides it.

Claude-specific notes:

- Before ending a session, put anything a future session needs into a file (`README.md` "Where we
  are" table, `docs/`, or a `notebooks/*_WORKING-NOTES.md`). Never leave a decision only in chat.
- Use a venv (`.venv/`, gitignored). Do not `pip install` into system Python.
- Read PDFs by text extraction (`pypdf`), not page images. Read notebooks as JSON when checking
  that code matches prose — starter-notebook markdown has been stale before.
- Notebook cells written programmatically: every `source` line must end in `\n`, and run
  `compile()` on each code cell before executing, or `nbconvert` can fail while exiting 0.
- Log each session in `AI-USE-NOTE.md` (tool, what, how verified).
