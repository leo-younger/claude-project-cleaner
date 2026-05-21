"""Smart classification engine — categorizes scanned items into 6 categories."""

import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from utils import load_json, save_json, parse_version, format_size, get_claude_home

CATEGORIES = {
    "A_portable_tools": "Portable Tools — reusable across projects",
    "B_project_config": "Project-Local Config — only meaningful here",
    "C_generated_artifacts": "Generated Artifacts — plans, specs, reports",
    "D_knowledge_assets": "Knowledge Assets — memory, context docs",
    "E_cache_redundant": "Cache / Redundant — safe to delete",
    "F_outdated_versions": "Outdated Versions — old copies of same tool",
}

# Classification rules
CACHE_PATTERNS = ["cache", "tmp", "temp", ".cache", "__pycache__", ".npm"]
GENERATED_PATTERNS = ["specs", "plans", "reports", "generated", "build", "dist", "target"]
KNOWLEDGE_PATTERNS = ["memory", "CLAUDE.md", "AGENTS.md", "GEMINI.md", "README"]
CONFIG_PATTERNS = ["settings.json", "hooks", "commands", ".claude-plugin"]


def _parent_name(path_str: str) -> str:
    """Get the immediate parent directory name of a path."""
    from pathlib import PurePath
    p = PurePath(path_str)
    # For a directory "/a/b/c", parent is "b"; for a file "/a/b/f.txt", parent is "b"
    if p.suffix:  # likely a file
        return p.parent.name.lower()
    return p.name.lower() if len(p.parts) > 1 else ""


def classify_location(loc_name: str, items: list, project_root: str) -> list[dict]:
    """Classify items from a single scan location."""
    classified = []
    claude_home = str(get_claude_home())

    for item in items:
        c = {
            "name": item.get("name", "unknown"),
            "path": item.get("path", ""),
            "size_bytes": item.get("size", 0),
            "size_human": format_size(item.get("size", 0)),
            "mtime": item.get("mtime"),
            "source_location": loc_name,
            "version": parse_version(item.get("name", "")),
            "category": None,
            "action": "KEEP",
            "reason": "",
        }

        name_lower = c["name"].lower()
        parent_lower = _parent_name(c["path"])

        # Cross-project detection: is this in claude home (global)?
        c["scope"] = "global" if claude_home in c["path"] else "project"

        # Category E: Cache / Redundant
        # Check item name AND immediate parent (not full path to avoid matching OS temp dirs)
        cache_hit = any(p in name_lower for p in CACHE_PATTERNS)
        cache_hit = cache_hit or any(p in parent_lower for p in CACHE_PATTERNS)
        if cache_hit:
            c["category"] = "E_cache_redundant"
            c["action"] = "AUTO_DELETE"
            c["reason"] = "Cache directory — safe to delete"
        # Category C: Generated Artifacts — check name + parent
        elif any(p in name_lower for p in GENERATED_PATTERNS) or any(p in parent_lower for p in GENERATED_PATTERNS):
            c["category"] = "C_generated_artifacts"
            c["action"] = "SUGGEST_ARCHIVE"
            c["reason"] = "Build/generated output"
        # Global skills, plugins → Category A (portable tools)
        elif loc_name in ("global_skills", "global_plugins", "global_commands"):
            c["category"] = "A_portable_tools"
            c["action"] = "KEEP"
            c["reason"] = "Reusable across projects"
        # Global npm/pip packages → Category A
        elif loc_name in ("global_npm", "global_pip"):
            c["category"] = "A_portable_tools"
            c["action"] = "KEEP"
            c["reason"] = "MCP dependency — may be shared"
        # Project skills → Category A
        elif loc_name == "project_skills":
            c["category"] = "A_portable_tools"
            c["action"] = "KEEP"
            c["reason"] = "Project-level skill, potentially reusable"
        # Category D: Knowledge
        elif loc_name == "global_projects_memory" or any(p in name_lower for p in KNOWLEDGE_PATTERNS):
            c["category"] = "D_knowledge_assets"
            c["action"] = "KEEP"
            c["reason"] = "Project knowledge/memory"
        # Category B: Project config — only for known config names and specific config locations
        elif any(p in name_lower for p in CONFIG_PATTERNS) or loc_name in ("global_settings", "global_hooks"):
            c["category"] = "B_project_config"
            c["action"] = "KEEP"
            c["reason"] = "Configuration — project-specific"
        # Items directly in .claude/ root (not in subdirectories) that are known Claude files
        elif loc_name == "project_claude_dir" and name_lower in ("settings.json", "commands", "hooks", "agents"):
            c["category"] = "B_project_config"
            c["action"] = "KEEP"
            c["reason"] = "Claude project config file"
        # Default
        else:
            c["category"] = "C_generated_artifacts"
            c["action"] = "REVIEW"
            c["reason"] = "Unrecognized — manual review suggested"

        classified.append(c)

    return classified


def _version_tuple(v: str) -> tuple:
    """Parse version string to comparable tuple using only stdlib."""
    import re
    parts = re.split(r'[.-]', v)
    result = []
    for p in parts:
        try:
            result.append(int(p))
        except ValueError:
            result.append(p)
    return tuple(result)


def find_outdated_versions(classified: list[dict]) -> list[dict]:
    """Find items where multiple versions of the same tool exist."""
    from collections import defaultdict

    version_groups = defaultdict(list)
    for item in classified:
        if item["version"]:
            # Strip version from name for grouping
            base_name = item["name"]
            for sep in ["-", "_", "@"]:
                if sep in base_name:
                    parts = base_name.rsplit(sep, 1)
                    if parse_version(parts[-1]):
                        base_name = parts[0]
                        break
            version_groups[base_name].append(item)

    outdated = []
    for base_name, items in version_groups.items():
        if len(items) > 1:
            try:
                sorted_items = sorted(items, key=lambda x: _version_tuple(x["version"]), reverse=True)
            except Exception:
                sorted_items = items
            latest = sorted_items[0]
            for old in sorted_items[1:]:
                c = dict(old)
                c["category"] = "F_outdated_versions"
                c["action"] = "DELETE_OLD_VERSION"
                c["reason"] = f"Outdated: {old['version']} → latest is {latest['version']}"
                c["latest_version"] = latest["version"]
                c["latest_path"] = latest["path"]
                outdated.append(c)

    return outdated


def classify_all(scan_result: dict) -> dict:
    """Classify all items from scan_result into 6 categories."""
    project_root = scan_result["project_root"]
    all_classified = []

    for loc_name, loc_data in scan_result["locations"].items():
        items = loc_data.get("items", [])
        classified = classify_location(loc_name, items, project_root)
        all_classified.extend(classified)

    # Find outdated versions
    outdated = find_outdated_versions(all_classified)
    for o in outdated:
        # Replace the original entry with the outdated classification
        for i, item in enumerate(all_classified):
            if item["path"] == o["path"] and item["name"] == o["name"]:
                all_classified[i] = o
                break

    # Aggregate stats
    by_category = defaultdict(list)
    for item in all_classified:
        by_category[item["category"]].append(item)

    result = {
        "classified_time": datetime.now().isoformat(),
        "project_root": project_root,
        "total_items": len(all_classified),
        "summary": {
            cat: {
                "count": len(items),
                "total_size": format_size(sum(i.get("size_bytes", 0) for i in items)),
                "actions": list(set(i["action"] for i in items)),
            }
            for cat, items in by_category.items()
        },
        "items": all_classified,
        "by_category": {k: v for k, v in by_category.items()},
    }

    return result


def generate_report(classified: dict) -> str:
    """Generate a Markdown cleanup report."""
    lines = []
    lines.append("# 🧹 Claude Code 项目清理报告")
    lines.append(f"> Project: {Path(classified['project_root']).name}")
    lines.append(f"> Time: {classified['classified_time']}")
    lines.append(f"> Items scanned: {classified['total_items']}")
    lines.append("")

    lines.append("## 📊 概要")
    lines.append("")
    lines.append("| 分类 | 数量 | 总大小 | 建议操作 |")
    lines.append("|------|------|--------|----------|")
    for cat_key, cat_label in CATEGORIES.items():
        stats = classified["summary"].get(cat_key, {"count": 0, "total_size": "0 B", "actions": []})
        actions = ", ".join(stats["actions"]) if stats["actions"] else "—"
        lines.append(f"| {cat_label} | {stats['count']} | {stats['total_size']} | {actions} |")
    lines.append("")

    # Detail per category
    for cat_key, cat_label in CATEGORIES.items():
        items = classified["by_category"].get(cat_key, [])
        if not items:
            continue
        lines.append(f"## {cat_label}")
        lines.append("")
        lines.append("| Name | Path | Size | Action | Reason |")
        lines.append("|------|------|------|--------|--------|")
        for item in items[:50]:  # cap at 50 per category in report
            name = item["name"][:40]
            path = item["path"][:60]
            lines.append(f"| {name} | {path} | {item['size_human']} | {item['action']} | {item['reason']} |")
        if len(items) > 50:
            lines.append(f"| ... | +{len(items) - 50} more items | | | |")
        lines.append("")

    # Actions summary
    lines.append("## 📋 操作摘要")
    lines.append("")
    action_sets = defaultdict(list)
    for item in classified["items"]:
        action_sets[item["action"]].append(item)
    for action, items in action_sets.items():
        total_size = format_size(sum(i.get("size_bytes", 0) for i in items))
        lines.append(f"- **{action}**: {len(items)} items, {total_size}")
    lines.append("")

    # Reclaimable space
    reclaimable = sum(
        i.get("size_bytes", 0)
        for i in classified["items"]
        if i["action"] in ("AUTO_DELETE", "DELETE_OLD_VERSION")
    )
    lines.append(f"## 💾 可回收空间: **{format_size(reclaimable)}**")
    lines.append("")
    lines.append("---")
    lines.append("*Report generated by claude-project-cleaner*")

    return "\n".join(lines)


def main():
    scan_file = None
    if len(sys.argv) > 1:
        scan_file = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
        scan_file = project_root / ".claude" / "scan_result.json"

    if not scan_file.exists():
        print(f"❌ Scan result not found: {scan_file}")
        print("   Run scanner.py first to generate scan data.")
        sys.exit(1)

    print("🧠 Classifying scanned items...")
    scan_result = load_json(scan_file)
    classified = classify_all(scan_result)

    out_dir = scan_file.parent
    json_out = out_dir / "classified.json"
    md_out = out_dir / "CLAUDE-CLEANUP-REPORT.md"

    save_json(json_out, classified)
    report = generate_report(classified)
    md_out.write_text(report, encoding="utf-8")

    print(f"   Classification complete: {classified['total_items']} items → 6 categories")
    print(f"   JSON: {json_out}")
    print(f"   Report: {md_out}")

    return classified


if __name__ == "__main__":
    main()
