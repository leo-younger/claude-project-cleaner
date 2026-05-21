# Safety Rules & Whitelist

## Core Principles

1. **Never delete source code** — The project's actual code is sacred
2. **Never delete configuration** — settings.json, CLAUDE.md, package.json stay
3. **Never delete shared tools blindly** — Check cross-project references first
4. **Always backup before delete** — All deletions go through backup first

## Whitelist (NEVER deleted)

```
.git/
.gitignore
.gitattributes
CLAUDE.md
AGENTS.md
GEMINI.md
README.md
LICENSE
settings.json
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
pom.xml
build.gradle
build.gradle.kts
Cargo.toml
Makefile
Dockerfile
docker-compose.yml
.env.example
src/
app/
lib/
main/
```

## Protection Rules

### Rule 1: Whitelist is absolute
If a path matches any whitelist entry, it is NEVER deleted regardless of category classification.

### Rule 2: Global dependency reference counting
Before deleting a global skill/plugin, check if other projects reference it:
- Scan `~/.claude/projects/` for other project memory files
- Check if the skill appears in other project `.claude/skills/`
- If found: downgrade action from DELETE to SUGGEST_ARCHIVE

### Rule 3: Dry-run is mandatory
Even in `--auto` mode, a dry-run preview is always generated first.

### Rule 4: Backup before delete
All deletions are backed up to `~/.claude/backup/<timestamp>/`.
Backups auto-expire after 30 days.

## Rollback Procedure

```bash
# List available backups
ls ~/.claude/backup/

# Rollback to a specific backup
python cleaner.py --rollback 20260521_143000
```

## Manual Override

Users can always:
- Edit `classified.json` to change any item's `action` field before running cleaner
- Use `--report-only` to generate the report without any file changes
- Delete backup directories manually to free space after confirming cleanup
