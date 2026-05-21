# Claude Code Storage Paths Reference

All known paths where Claude Code stores or downloads files during project work.

## Global Paths (user-level, shared across projects)

| Path | Contents | Safe to clean? |
|------|----------|----------------|
| `~/.claude/skills/` | Symlinks to installed skills | ❌ No — may be shared |
| `~/.claude/plugins/` | Plugin/marketplace cache | ⚠️ Old versions only |
| `~/.claude/projects/` | Per-project memory | ❌ No — knowledge assets |
| `~/.claude/commands/` | Custom slash commands | ❌ No — may be shared |
| `~/.claude/hooks/` | Hook scripts | ❌ No — config |
| `~/.claude/settings.json` | Global config | ❌ NEVER delete |
| `~/.claude/cache/` | Session cache | ✅ Safe to delete |
| `~/.claude/backup/` | Cleaner backup snapshots | ⚠️ Keep recent, delete >30 days |
| `~/.npm/` | npm cache + global packages | ⚠️ Cache only, keep packages |
| `~/.pip/` | pip cache | ✅ Safe (pip will re-download) |

## Project Paths (project-level)

| Path | Contents | Safe to clean? |
|------|----------|----------------|
| `.claude/settings.json` | Project config | ❌ NEVER delete |
| `.claude/skills/` | Project-level skills | ⚠️ Review first |
| `.claude/memory/` | Project memory files | ❌ No — knowledge assets |
| `.claude/commands/` | Project slash commands | ❌ No — config |
| `.claude/agents/` | Sub-agent definitions | ❌ No — config |
| `node_modules/` | Project dependencies | ⚠️ Can reinstall from lockfile |

## MCP-Related Paths

| Type | Typical location | Notes |
|------|-----------------|-------|
| npm MCP servers | Global `node_modules/` or project `node_modules/` | Check if other projects use them |
| pip MCP servers | `~/.local/lib/python*/` or venv | Check virtualenv first |
| uvx MCP servers | `~/.cache/uv/` | Safe to clean old versions |
| Binary MCPs | `~/.local/bin/`, `~/.cargo/bin/` | Manual review |

## Browser / Playwright Paths

| Path | Contents | Safe to clean? |
|------|----------|----------------|
| `~/.cache/ms-playwright/` | Playwright browser binaries | ⚠️ Old versions only |
| `~/.cache/puppeteer/` | Puppeteer Chrome binaries | ⚠️ Old versions only |
| `~/Library/Caches/.../Chromium/` (macOS) | Chromium profiles | ✅ Old profiles |
| `%LOCALAPPDATA%/.../Chromium/` (Windows) | Chromium profiles | ✅ Old profiles |
