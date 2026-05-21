# 🧹 Claude Project Cleaner

<p align="center">
  <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/leo-younger/claude-project-cleaner/test.yml?label=CI">
  <img alt="License" src="https://img.shields.io/github/license/leo-younger/claude-project-cleaner">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue">
  <img alt="PRs Welcome" src="https://img.shields.io/badge/PRs-welcome-brightgreen">
</p>

> **Post-project cleanup skill for Claude Code** — scan 12 storage locations, classify into 6 categories, safely delete old versions and cache with backup & rollback.

Stop letting Claude Code clutter pile up. After weeks of work, your machine has GB of cruft from downloaded skills, plugin caches, MCP packages, and browser binaries — with no idea what's safe to delete.

---

## 🎬 Demo

```terminal
$ python scanner.py && python organizer.py && python cleaner.py

🔍 Scanning Claude Code assets for project: springboottest
   Scanned 12 locations, 39 items found

🧠 Classifying scanned items...
   Classification complete: 39 items → 6 categories
   Report: .claude/CLAUDE-CLEANUP-REPORT.md

🧹 Dry-run preview:
   Safe to delete: 18 items
   Reclaimable: 3.6 GB
   Kept: 21 items

💡 To execute cleanup, re-run with --auto
```

---

## ⚡ One-liner Install

```bash
# Clone & install globally
git clone https://github.com/leo-younger/claude-project-cleaner.git ~/.claude/skills/claude-project-cleaner

# Or use the install script
bash install.sh --global

# Windows PowerShell
.\install.ps1 -Global
```

---

## 🚀 Usage

```bash
# Interactive mode (default — safe)
cd scripts/
python scanner.py              # Step 1: Scan 12 locations
python organizer.py            # Step 2: Classify into 6 categories
python cleaner.py              # Step 3: Dry-run preview
python cleaner.py --auto       # Step 4: Execute with backup

# One-shot auto
python scanner.py && python organizer.py && python cleaner.py --auto

# Report only (no changes)
python scanner.py && python organizer.py && python cleaner.py --report-only

# Rollback if needed
python cleaner.py --rollback 20260521_143000
```

Or inside Claude Code: just type **`/cleanup`**

---

## 📊 What It Produces

```
.claude/
├── scan_result.json            # Raw scan data (12 locations × N items)
├── classified.json             # Classification result (machine-readable)
├── CLAUDE-CLEANUP-REPORT.md    # Human-readable cleanup report
├── CLAUDE-CLEANUP-DONE.md      # Execution summary + rollback command
└── backup/<timestamp>/         # Backup before deletion
```

### Example Report

```markdown
# 🧹 Claude Code Project Cleanup Report

## 📊 Summary
| Category               | Count | Size    | Action              |
|------------------------|-------|---------|---------------------|
| A. Portable Tools      | 23    | 450 MB  | KEEP                |
| B. Project Config      | 8     | 12 KB   | KEEP                |
| C. Generated Artifacts | 15    | 34 MB   | SUGGEST_ARCHIVE     |
| D. Knowledge Assets    | 6     | 1.2 MB  | KEEP                |
| E. Cache / Redundant   | 42    | 2.1 GB  | AUTO_DELETE         |
| F. Outdated Versions   | 5     | 1.5 GB  | DELETE_OLD_VERSION  |

## 💾 Reclaimable Space: 3.6 GB
```

---

## 🔍 The 12 Scan Locations

| # | Location | What's there |
|---|----------|-------------|
| 1 | `~/.claude/skills/` | Global installed skills |
| 2 | `~/.claude/plugins/` | Marketplace plugin cache |
| 3 | `~/.claude/projects/` | Per-project memory files |
| 4 | `~/.claude/commands/` | Custom slash commands |
| 5 | `~/.claude/hooks/` | Hook scripts |
| 6 | `~/.claude/settings.json` | Global config (never deleted) |
| 7 | `<project>/.claude/` | Project-level Claude config |
| 8 | `<project>/.claude/skills/` | Project-level skills |
| 9 | Global npm packages | MCP server dependencies |
| 10 | Global pip packages | MCP server dependencies |
| 11 | `<project>/node_modules/` | Project MCP dependencies |
| 12 | `~/.claude/cache/` | Session cache files |

---

## 🧠 Smart Classification

| Category | Action | Examples |
|----------|--------|----------|
| **A. Portable Tools** | `KEEP` | gstack skill, MCP servers |
| **B. Project Config** | `KEEP` | settings.json, hooks |
| **C. Generated Artifacts** | `ARCHIVE` | build output, specs |
| **D. Knowledge Assets** | `KEEP` | CLAUDE.md, memory files |
| **E. Cache / Redundant** | `AUTO_DELETE` | session cache, `__pycache__` |
| **F. Outdated Versions** | `DELETE_OLD` | chromium-115 → chromium-120 |

---

## 🛡️ Safety Guarantees

| Protection | How |
|-----------|-----|
| **Whitelist** | `.git/`, `CLAUDE.md`, `src/`, build configs — NEVER touched |
| **Dry-run first** | Always preview before executing, even in `--auto` mode |
| **Backup** | All deletions backed up to `~/.claude/backup/<timestamp>/` |
| **Rollback** | `python cleaner.py --rollback <timestamp>` restores everything |
| **Reference counting** | Global tools shared by other projects are flagged, not deleted |

---

## 📦 Comparison

| Tool | File cleanup | Claude-aware | Version tracking | Rollback | Zero deps |
|------|:-----------:|:------------:|:----------------:|:--------:|:---------:|
| **claude-project-cleaner** | ✅ | ✅ 12 paths | ✅ | ✅ | ✅ |
| neat-freak | ❌ docs only | ⚠️ partial | ❌ | ❌ | ✅ |
| UFailureSkill | ❌ skills only | ✅ | ❌ | ❌ | ✅ |
| file-organizer | ✅ generic | ❌ | ❌ | ❌ | ❌ |
| knip | ✅ code deps | ❌ | ❌ | ❌ | ❌ |

---

## 📋 Requirements

- Python 3.9+
- Zero pip dependencies — standard library only

---

## 🤝 Contributing

PRs welcome. Check the [issues](https://github.com/leo-younger/claude-project-cleaner/issues) page.

---

## 📜 License

MIT — free for personal and commercial use.
