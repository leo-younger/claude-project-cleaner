"""Full scan engine — walks all 12 Claude Code storage locations."""

import sys
from pathlib import Path
from datetime import datetime
from utils import (
    expand_home, get_claude_home, get_project_root,
    run_cmd, file_info, parse_version, save_json
)

# 12 known Claude Code scan locations
SCAN_LOCATIONS = [
    ("global_skills", "~/.claude/skills/"),
    ("global_plugins", "~/.claude/plugins/"),
    ("global_projects_memory", "~/.claude/projects/"),
    ("global_commands", "~/.claude/commands/"),
    ("global_hooks", "~/.claude/hooks/"),
    ("global_settings", "~/.claude/settings.json"),
    ("global_cache", "~/.claude/cache/"),
    ("project_claude_dir", "<project>/.claude/"),
    ("project_skills", "<project>/.claude/skills/"),
    ("global_npm", "__npm_ls_global__"),
    ("global_pip", "__pip_list__"),
    ("project_node_modules", "<project>/node_modules/"),
]


def scan_entry(entry_path: Path) -> dict:
    """Scan a single file or directory entry."""
    info = file_info(entry_path)
    info["name"] = entry_path.name
    return info


# Files to skip during scanning (pipeline's own outputs)
SKIP_NAMES = {
    "scan_result.json", "classified.json", "CLAUDE-CLEANUP-REPORT.md",
    "CLAUDE-CLEANUP-DONE.md", "dry_run.json", "cleanup_done.json",
}


def scan_filesystem(scan_root: Path, max_depth: int = 3) -> list[dict]:
    """Walk a directory and collect metadata for all entries."""
    items = []
    if not scan_root.exists():
        return items
    # If it's a file, scan as single entry
    if scan_root.is_file():
        if scan_root.name in SKIP_NAMES:
            return []
        return [scan_entry(scan_root)]
    try:
        for entry in scan_root.iterdir():
            if entry.name in SKIP_NAMES:
                continue
            info = file_info(entry)
            info["name"] = entry.name
            if entry.is_dir():
                children = []
                if max_depth > 0:
                    try:
                        for child in entry.iterdir():
                            cinfo = file_info(child)
                            cinfo["name"] = child.name
                            children.append(cinfo)
                    except PermissionError:
                        pass
                info["children"] = children
            items.append(info)
    except PermissionError:
        pass
    return items


def scan_npm_global() -> list[dict]:
    """Scan globally installed npm packages (MCP dependency source)."""
    code, out, err = run_cmd(["npm", "ls", "-g", "--depth=0", "--json"], timeout=20)
    items = []
    if code == 0:
        try:
            import json
            data = json.loads(out)
            deps = data.get("dependencies", {})
            npm_root = None
            # Try to find global npm root
            rc, root_out, _ = run_cmd(["npm", "root", "-g"], timeout=5)
            if rc == 0:
                npm_root = Path(root_out)
            for name, info in deps.items():
                item = {
                    "name": name,
                    "path": str(npm_root / name) if npm_root else "global npm",
                    "version": info.get("version", "unknown"),
                    "exists": True,
                    "is_dir": True,
                    "source": "npm global",
                    "size": 0,
                }
                if npm_root:
                    pkg_path = npm_root / name
                    item["size"] = sum(f.stat().st_size for f in pkg_path.rglob("*") if f.is_file())
                items.append(item)
        except Exception:
            pass
    return items


def scan_pip_global() -> list[dict]:
    """Scan user-level pip packages (MCP dependency source)."""
    code, out, err = run_cmd(["pip", "list", "--user", "--format=json"], timeout=15)
    items = []
    if code == 0:
        try:
            import json
            data = json.loads(out)
            for pkg in data:
                items.append({
                    "name": pkg.get("name", "unknown"),
                    "path": f"pip user: {pkg.get('name')}",
                    "version": pkg.get("version", "unknown"),
                    "exists": True,
                    "is_dir": False,
                    "source": "pip user",
                    "size": 0,
                })
        except Exception:
            pass
    return items


def scan_all(project_root: Path = None, claude_home: Path = None) -> dict:
    """Run full scan across all 12 locations. Returns structured result."""
    if project_root is None:
        project_root = get_project_root()

    results = {
        "scan_time": datetime.now().isoformat(),
        "project_root": str(project_root),
        "hostname": __import__("platform").node(),
        "locations": {},
        "total_items": 0,
    }

    for loc_name, loc_path in SCAN_LOCATIONS:
        items = []

        if loc_path.startswith("__npm_ls"):
            items = scan_npm_global()
        elif loc_path.startswith("__pip_list"):
            items = scan_pip_global()
        elif loc_path.startswith("<project>"):
            rel = loc_path.replace("<project>", str(project_root))
            actual_path = Path(rel)
            items = scan_filesystem(actual_path, max_depth=3)
        else:
            # Use custom claude_home if provided, otherwise resolve ~
            if claude_home and loc_path.startswith("~/.claude"):
                rel = loc_path[2:]  # strip ~/
                actual_path = claude_home / rel.lstrip("/")
            else:
                actual_path = expand_home(loc_path)
            items = scan_filesystem(actual_path, max_depth=3)

        resolved = str(loc_path)
        if not loc_path.startswith("__"):
            if claude_home and loc_path.startswith("~/.claude"):
                rel = loc_path[2:]
                resolved = str(claude_home / rel.lstrip("/"))
            else:
                resolved = str(expand_home(loc_path))

        results["locations"][loc_name] = {
            "path": loc_path,
            "resolved_path": resolved,
            "items": items,
            "count": len(items),
        }
        results["total_items"] += len(items)

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Claude Project Cleaner — Scanner")
    parser.add_argument("project_root", nargs="?", default=None, help="Project root directory")
    parser.add_argument("--claude-home", default=None, help="Override ~/.claude path (for testing)")
    args = parser.parse_args()

    project_root = Path(args.project_root) if args.project_root else Path.cwd()
    claude_home = Path(args.claude_home) if args.claude_home else None

    print(f"Scanning Claude Code assets for project: {project_root.name}")
    results = scan_all(project_root, claude_home=claude_home)

    output_file = project_root / ".claude" / "scan_result.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    save_json(output_file, results)

    print(f"   Scanned {len(results['locations'])} locations, {results['total_items']} items found")
    print(f"   Report saved to: {output_file}")
    return results


if __name__ == "__main__":
    main()
