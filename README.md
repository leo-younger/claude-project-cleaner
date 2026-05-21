# 🧹 Claude Project Cleaner

> 项目结束后的"收纳师" — Stop letting Claude Code clutter pile up.

Claude Code downloads skills, plugins, MCP packages, browser binaries, and caches during every project. After weeks of work, you've got GB of cruft and no idea what's safe to delete.

**Claude Project Cleaner** scans everything, classifies it, and cleans it up — safely, with backups and rollback.

## What It Does

```
 12 storage locations → scanned → 6 categories → cleanup report → safe delete + rollback
```

- 🔍 **Scans 12 locations** where Claude Code stores files
- 🧠 **Classifies into 6 categories**: reusable tools, project config, generated artifacts, knowledge, cache, outdated versions
- 📋 **Generates Markdown + JSON reports** for handoff
- 🗑️ **Auto-deletes cache and old versions** (with backup)
- 🔄 **Full rollback** if anything goes wrong

## Quick Start

```bash
# 1. Clone into your skills directory
git clone https://github.com/YOUR_USER/claude-project-cleaner.git
cp -r claude-project-cleaner ~/.claude/skills/claude-project-cleaner

# 2. Run in any project
cd scripts/
python scanner.py              # Scan all locations
python organizer.py            # Classify + generate report
python cleaner.py              # Dry-run preview
python cleaner.py --auto       # Execute cleanup

# Or: just generate a report (no changes)
python scanner.py && python organizer.py && python cleaner.py --report-only
```

## What Gets Scanned

| # | Location | What's there |
|---|----------|-------------|
| 1 | `~/.claude/skills/` | Installed skills |
| 2 | `~/.claude/plugins/` | Marketplace cache |
| 3 | `~/.claude/projects/` | Project memory |
| 4 | `~/.claude/commands/` | Custom slash commands |
| 5 | `~/.claude/hooks/` | Hook scripts |
| 6 | `~/.claude/settings.json` | Global config |
| 7 | `<project>/.claude/` | Project config |
| 8 | `<project>/.claude/skills/` | Project skills |
| 9 | Global npm packages | MCP dependencies |
| 10 | Global pip packages | MCP dependencies |
| 11 | `<project>/node_modules/` | Project MCP |
| 12 | `~/.claude/cache/` | Session cache |

## The 6 Categories

| Category | Action | Example |
|----------|--------|---------|
| **A. Portable Tools** | Keep | gstack skill, MCP servers |
| **B. Project Config** | Keep | settings.json, hooks |
| **C. Generated Artifacts** | Archive | specs, build output |
| **D. Knowledge Assets** | Keep | CLAUDE.md, memory |
| **E. Cache / Redundant** | **Auto-delete** | `~/.claude/cache/`, `__pycache__` |
| **F. Outdated Versions** | **Delete old** | chromium-115 vs chromium-120 |

## Safety Guarantees

- ✅ **Whitelist protection** — `.git/`, `CLAUDE.md`, source code NEVER touched
- ✅ **Dry-run first** — Always see what will happen before it happens
- ✅ **Backup before delete** — Everything goes to `~/.claude/backup/<timestamp>/`
- ✅ **Full rollback** — `python cleaner.py --rollback <timestamp>`
- ✅ **Reference counting** — Global tools used by other projects are flagged, not deleted

## Example Report

```
# 🧹 Claude Code 项目清理报告

## 📊 Summary
| A. Portable Tools      | 23    | 450 MB   | KEEP                |
| B. Project Config      | 8     | 12 KB    | KEEP                |
| C. Generated Artifacts | 15    | 34 MB    | SUGGEST_ARCHIVE     |
| D. Knowledge Assets    | 6     | 1.2 MB   | KEEP                |
| E. Cache / Redundant   | 42    | 2.1 GB   | AUTO_DELETE         |
| F. Outdated Versions   | 5     | 1.5 GB   | DELETE_OLD_VERSION  |

## 💾 Reclaimable Space: 3.6 GB
```

## Requirements

- Python 3.9+
- No pip install required (standard library only)

## Comparison With Alternatives

| Tool | File cleanup | Claude-aware | Version tracking | Rollback |
|------|:-----------:|:------------:|:----------------:|:--------:|
| **claude-project-cleaner** | ✅ | ✅ 12 paths | ✅ | ✅ |
| neat-freak | ❌ docs only | ⚠️ partial | ❌ | ❌ |
| UFailureSkill | ❌ skills only | ✅ | ❌ | ❌ |
| file-organizer | ✅ generic | ❌ | ❌ | ❌ |
| knip | ✅ code deps | ❌ | ❌ | ❌ |

## License

MIT — free for personal and commercial use.
