# 🧹 Claude Project Cleaner

<p align="center">
  <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/leo-younger/claude-project-cleaner/test.yml?label=CI">
  <img alt="License" src="https://img.shields.io/github/license/leo-younger/claude-project-cleaner">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue">
</p>

> **Session-scoped cleanup for Claude Code** — knows exactly what THIS conversation downloaded, created, or changed. Never touches other projects.

After a long Claude Code session, you've installed packages, created files, loaded skills. What's safe to delete? This skill reads your **current conversation transcript** and shows only what happened in this window.

---

## What It Does

```
Say "清理项目" at the end of a session
  │
  ├── Parse current transcript (JSONL)
  ├── Filter out read-only operations (Read, WebSearch, etc.)
  ├── Show what THIS session did:
  │   ├── 📦 Installed (npm install, pip install, git clone...)
  │   ├── 📝 Files created (Write tool calls)
  │   ├── ✏️ Files edited (Edit tool calls)
  │   └── 🧠 Skills loaded
  └── You decide what to clean
```

**Never touches**: other projects, other conversations, global config, global skills.

---

## Quick Start

```bash
git clone https://github.com/leo-younger/claude-project-cleaner.git ~/.claude/skills/claude-project-cleaner
```

Then in any Claude Code session, say **"清理项目"** or **"clean up project"**.

Or run manually:
```bash
python scripts/session_cleaner.py
python scripts/session_cleaner.py ~/.claude/projects/xxx/session.jsonl
```

---

## Cooldown Auto-Cleanup (Optional)

Copy `hooks.json` into your project's `.claude/settings.json`:

| Idle Time | What Happens |
|-----------|-------------|
| Every session end | Records timestamp (Stop hook) |
| 7 days idle | Nudge on next session start |
| 30 days idle | Auto-clean cache (Category E only, safe) |

---

## Bonus: Global Scanner (Legacy)

Also includes a full-disk scanner for deep cleaning:

```bash
python scripts/scanner.py          # Scan 12 Claude Code locations
python scripts/organizer.py        # Classify into 6 categories
python scripts/cleaner.py          # Dry-run preview
python scripts/cleaner.py --auto   # Execute with backup & rollback
```

---

## Requirements

- Python 3.9+
- Zero pip dependencies (stdlib only)

## License

MIT
