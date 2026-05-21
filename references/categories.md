# Classification Rules Reference

## Category Decision Tree

```
Is it in a cache/tmp directory?
  → YES: Category E (Cache / Redundant) → AUTO_DELETE
  → NO: Continue

Is it a global skill, plugin, command, npm/pip package?
  → YES: Category A (Portable Tool) → KEEP
  → NO: Continue

Is it a config file (settings.json, hooks, commands)?
  → YES: Category B (Project-Local Config) → KEEP
  → NO: Continue

Is it a knowledge file (memory, CLAUDE.md, AGENTS.md)?
  → YES: Category D (Knowledge Asset) → KEEP
  → NO: Continue

Is it in a build/generated directory (specs, plans, dist, target)?
  → YES: Category C (Generated Artifact) → SUGGEST_ARCHIVE
  → NO: Default to Category C → REVIEW
```

## Category Details

### A — Portable Tools
Items that work across projects independently.
- **Examples**: gstack skill, frontend-design skill, playwright MCP server, npm global packages
- **Default action**: KEEP
- **When to delete**: User explicitly confirms the tool is no longer needed anywhere

### B — Project-Local Config
Configuration files that only make sense in their current project.
- **Examples**: `.claude/settings.json`, custom hooks, project-specific slash commands
- **Default action**: KEEP (stays with project)
- **When to delete**: Project is being archived/deleted entirely

### C — Generated Artifacts
Files generated during development that may or may not have lasting value.
- **Examples**: `docs/superpowers/specs/`, build output, generated reports
- **Default action**: SUGGEST_ARCHIVE
- **When to delete**: After project handoff, if no archival value

### D — Knowledge Assets
Files that capture project understanding and context.
- **Examples**: `.claude/memory/*.md`, `CLAUDE.md`, `README.md`
- **Default action**: KEEP (valuable context)
- **When to delete**: Never auto-delete; user must manually confirm

### E — Cache / Redundant
Temporary files with no lasting value. Safe to delete.
- **Examples**: `~/.claude/cache/`, `__pycache__/`, `.npm/_cacache/`
- **Default action**: AUTO_DELETE (safe, no user confirm needed in auto mode)
- **When to delete**: Always safe

### F — Outdated Versions
Multiple versions of the same tool. Keep only the latest.
- **Examples**: chromium-115 vs chromium-120, skill v1.0 vs v2.1
- **Default action**: DELETE_OLD_VERSION (keep latest only)
- **When to delete**: After confirming latest version works correctly
