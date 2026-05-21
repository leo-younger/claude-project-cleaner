"""Safe cleanup executor — dry-run, backup, execute, rollback."""

import sys
import shutil
import time
from pathlib import Path
from datetime import datetime
from utils import load_json, save_json, format_size, is_safe_to_delete

# Whitelist: paths that are NEVER deleted
WHITELIST = {
    ".git",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "settings.json",
    ".gitignore",
    "README.md",
    "LICENSE",
    "package.json",
    "package-lock.json",
    "pom.xml",
    "build.gradle",
    "src/",
}


def dry_run(classified: dict, project_root: Path) -> dict:
    """Simulate cleanup, return what WOULD happen."""
    preview = {"deletes": [], "keeps": [], "total_reclaimable": 0, "errors": []}

    for item in classified["items"]:
        action = item.get("action", "KEEP")

        if action in ("AUTO_DELETE", "DELETE_OLD_VERSION"):
            path = Path(item["path"])
            if not path.exists():
                preview["errors"].append({"item": item["name"], "reason": "Path does not exist"})
                continue
            if not is_safe_to_delete(path, WHITELIST):
                preview["keeps"].append({**item, "reason": "Whitelist protected"})
                continue
            preview["deletes"].append(item)
            preview["total_reclaimable"] += item.get("size_bytes", 0)
        else:
            preview["keeps"].append(item)

    return preview


def backup_items(items: list[dict], backup_dir: Path):
    """Copy items to backup directory preserving structure."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    for item in items:
        src = Path(item["path"])
        if not src.exists():
            continue
        try:
            # Preserve relative path under backup
            rel = str(src).replace(str(Path.home()), "HOME").replace("\\", "/").replace(":", "_")
            dst = backup_dir / rel.lstrip("/")
            dst.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        except Exception as e:
            print(f"   ⚠️ Backup failed for {src}: {e}")


def execute_deletes(items: list[dict]) -> list[dict]:
    """Delete items. Returns list of errors."""
    errors = []
    for item in items:
        path = Path(item["path"])
        if not path.exists():
            continue
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"   🗑️  Deleted: {item['name']} ({item.get('size_human', '?')})")
        except Exception as e:
            errors.append({"item": item["name"], "path": str(path), "error": str(e)})
            print(f"   ❌ Failed: {item['name']} — {e}")
    return errors


def rollback(backup_dir: Path, project_root: Path):
    """Restore files from a backup directory."""
    if not backup_dir.exists():
        print(f"❌ Backup not found: {backup_dir}")
        return

    print(f"🔄 Rolling back from: {backup_dir}")
    restored = 0
    for src in backup_dir.rglob("*"):
        if src.is_dir():
            continue
        rel = str(src.relative_to(backup_dir))
        orig_path = rel.replace("HOME", str(Path.home())).replace("/", "\\")
        dst = Path(orig_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
            restored += 1
        except Exception as e:
            print(f"   ❌ Rollback failed for {dst}: {e}")
    print(f"   Restored {restored} files")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Claude Project Cleaner — Safe Cleanup")
    parser.add_argument("classified_file", nargs="?", help="Path to classified.json")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    parser.add_argument("--auto", action="store_true", help="Execute cleanup automatically")
    parser.add_argument("--rollback", metavar="TIMESTAMP", help="Rollback to a backup timestamp")
    parser.add_argument("--report-only", action="store_true", help="Generate report only, no changes")
    args = parser.parse_args()

    # Rollback mode — no classified.json needed
    if args.rollback:
        backup_dir = Path.home() / ".claude" / "backup" / args.rollback
        rollback(backup_dir, Path.cwd())
        return

    # Find classified.json
    if args.classified_file:
        classified_file = Path(args.classified_file)
    else:
        classified_file = Path.cwd() / ".claude" / "classified.json"

    if not classified_file.exists():
        print("❌ classified.json not found. Run scanner.py then organizer.py first.")
        sys.exit(1)

    classified = load_json(classified_file)
    project_root = Path(classified["project_root"])

    # Report only
    if args.report_only:
        print("📋 Report-only mode — no changes will be made.")
        return

    # Dry run (always)
    print("🔍 Dry-run preview:")
    preview = dry_run(classified, project_root)
    print(f"   Safe to delete: {len(preview['deletes'])} items")
    print(f"   Reclaimable: {format_size(preview['total_reclaimable'])}")
    print(f"   Kept: {len(preview['keeps'])} items")

    if preview["errors"]:
        print(f"   ⚠️  Errors: {len(preview['errors'])}")
        for e in preview["errors"]:
            print(f"      - {e['item']}: {e['reason']}")

    # Save dry-run result
    dr_file = classified_file.parent / "dry_run.json"
    save_json(dr_file, preview)

    # Auto mode
    if args.auto:
        if not preview["deletes"]:
            print("✅ Nothing to delete.")
            return

        print(f"\n⏳ Auto-cleanup in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)

        # Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path.home() / ".claude" / "backup" / timestamp
        print(f"📦 Backing up to: {backup_dir}")
        backup_items(preview["deletes"], backup_dir)

        # Execute
        print("🧹 Cleaning up...")
        errors = execute_deletes(preview["deletes"])

        # Done report
        done = {
            "timestamp": timestamp,
            "deleted_count": len(preview["deletes"]),
            "reclaimed": format_size(preview["total_reclaimable"]),
            "backup": str(backup_dir),
            "errors": errors,
        }
        done_file = classified_file.parent / "CLAUDE-CLEANUP-DONE.md"
        done_json = classified_file.parent / "cleanup_done.json"
        save_json(done_json, {**done, "items": preview["deletes"]})

        report = [
            "# ✅ 清理完成",
            f"> Time: {timestamp}",
            f"> Deleted: {done['deleted_count']} items",
            f"> Reclaimed: {done['reclaimed']}",
            f"> Backup: {done['backup']}",
            "",
            "## 回滚方法",
            f"```bash",
            f"python cleaner.py --rollback {timestamp}",
            f"```",
        ]
        if errors:
            report.append("\n## ⚠️ 错误")
            for e in errors:
                report.append(f"- {e['item']}: {e['error']}")
        done_file.write_text("\n".join(report), encoding="utf-8")

        print(f"\n✅ Done! Reclaimed: {done['reclaimed']}")
        print(f"   Report: {done_file}")
        print(f"   Rollback: python cleaner.py --rollback {timestamp}")
    else:
        print("\n💡 To execute cleanup, re-run with --auto")
        print("   Or review the dry-run report manually.")


if __name__ == "__main__":
    main()
