"""Session-scoped cleaner — parses the CURRENT conversation transcript and shows
what this specific session downloaded, created, or installed. Only affects this session."""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def get_current_transcript() -> Path:
    """Read session ID from environment or find most recent transcript."""
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if session_id:
        return Path.home() / ".claude" / "projects" / "D--java-project" / f"{session_id}.jsonl"

    # Fallback: find the most recently modified transcript
    projects_dir = Path.home() / ".claude" / "projects"
    newest = None
    newest_time = 0
    if projects_dir.exists():
        for proj_dir in projects_dir.iterdir():
            if proj_dir.is_dir():
                for f in proj_dir.glob("*.jsonl"):
                    mtime = f.stat().st_mtime
                    if mtime > newest_time:
                        newest_time = mtime
                        newest = f
    return newest


def parse_transcript(transcript_path: Path) -> list[dict]:
    """Extract all tool_use actions from a transcript file.

    Transcript format: each line is a JSON record. Assistant records have
    message.content[] with tool_use blocks. User records have tool_result blocks.
    """
    actions = []
    if not transcript_path or not transcript_path.exists():
        return actions

    with open(transcript_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Only process assistant messages — they contain tool_use
            if record.get("type") != "assistant":
                continue

            message = record.get("message", {})
            for block in message.get("content", []):
                if block.get("type") == "tool_use":
                    actions.append({
                        "tool": block.get("name", ""),
                        "input": block.get("input", {}),
                        "time": record.get("timestamp", ""),
                        "cwd": record.get("cwd", ""),
                    })

    return actions


def classify_actions(actions: list[dict]) -> dict:
    """Classify session actions into: installs, file_creates, file_edits, skills_loaded."""
    result = {
        "installs": [],       # npm install, pip install, git clone, etc.
        "file_creates": [],   # Write tool calls
        "file_edits": [],     # Edit tool calls
        "skills_loaded": [],  # Skill tool calls
        "other_commands": [], # Other bash commands
        "summary": {},
    }

    install_keywords = [
        "npm install", "npm i ", "pip install", "pip3 install",
        "git clone", "go install", "cargo install", "gem install",
        "brew install", "apt install", "apt-get install", "choco install",
        "npx ", "pnpm add", "yarn add", "npm i -g",
    ]

    # Read-only tools — don't affect filesystem, skip in report
    SKIP_TOOLS = {"WebSearch", "WebFetch", "Read", "Grep", "Glob", "TaskList", "TaskGet",
                   "AskUserQuestion", "BashOutput", "TaskOutput", "CronList"}

    for action in actions:
        tool = action.get("tool", "")
        inp = action.get("input", {})

        if tool in SKIP_TOOLS:
            continue

        if tool == "Bash":
            command = inp.get("command", "")
            is_install = any(kw in command for kw in install_keywords)
            if is_install:
                result["installs"].append({
                    "command": command[:200],
                    "description": inp.get("description", ""),
                })
            else:
                result["other_commands"].append({
                    "command": command[:200],
                    "description": inp.get("description", ""),
                })

        elif tool == "Write":
            result["file_creates"].append({
                "path": inp.get("file_path", ""),
                "time": action.get("time", ""),
            })

        elif tool == "Edit":
            result["file_edits"].append({
                "path": inp.get("file_path", ""),
            })

        elif tool == "Skill":
            result["skills_loaded"].append({
                "skill": inp.get("skill", ""),
                "args": inp.get("args", ""),
            })

    # Summary
    result["summary"] = {
        "total_actions": len(actions),
        "installs": len(result["installs"]),
        "files_created": len(result["file_creates"]),
        "files_edited": len(result["file_edits"]),
        "skills_used": len(result["skills_loaded"]),
        "other_commands": len(result["other_commands"]),
    }

    # Deduplicate file paths
    result["file_creates"] = list({f["path"]: f for f in result["file_creates"]}.values())
    result["file_edits"] = list({f["path"]: f for f in result["file_edits"]}.values())

    return result


def generate_session_report(classified: dict, transcript_path: Path) -> str:
    """Generate a session-scoped cleanup report."""
    s = classified["summary"]
    lines = []
    lines.append("# 📋 Session Cleanup Report")
    lines.append(f"> Session: {transcript_path.stem[:20]}...")
    lines.append(f"> Time: {datetime.now().isoformat()}")
    lines.append(f"> Total tool actions analyzed: {s['total_actions']}")
    lines.append("")

    lines.append("## 📊 本次会话做了什么")
    lines.append("")
    lines.append(f"| 类型 | 数量 |")
    lines.append(f"|------|------|")
    lines.append(f"| 📦 安装/下载 | {s['installs']} |")
    lines.append(f"| 📝 创建文件 | {s['files_created']} |")
    lines.append(f"| ✏️ 编辑文件 | {s['files_edited']} |")
    lines.append(f"| 🧠 加载 Skill | {s['skills_used']} |")
    lines.append(f"| ⚡ 其他命令 | {s['other_commands']} |")
    lines.append("")

    if classified["installs"]:
        lines.append("## 📦 本次会话安装/下载的软件")
        lines.append("")
        for inst in classified["installs"]:
            lines.append(f"- `{inst['command']}`")
            if inst["description"]:
                lines.append(f"  - {inst['description']}")
        lines.append("")

    if classified["file_creates"]:
        lines.append("## 📝 本次会话创建的文件")
        lines.append("")
        for f in classified["file_creates"][:30]:
            lines.append(f"- `{f['path']}`")
        if len(classified["file_creates"]) > 30:
            lines.append(f"- ... +{len(classified['file_creates']) - 30} more")
        lines.append("")

    if classified["file_edits"]:
        lines.append("## ✏️ 本次会话编辑的文件")
        lines.append("")
        for f in classified["file_edits"][:20]:
            lines.append(f"- `{f['path']}`")
        lines.append("")

    if classified["skills_loaded"]:
        lines.append("## 🧠 本次会话使用的 Skills")
        lines.append("")
        for sk in classified["skills_loaded"]:
            lines.append(f"- `{sk['skill']}`")
        lines.append("")

    lines.append("---")
    lines.append("> ⚠️ 以上仅统计当前对话窗口的操作，不影响其他项目或历史会话。")

    return "\n".join(lines)


def main():
    transcript_path = None
    if len(sys.argv) > 1:
        transcript_path = Path(sys.argv[1])
    else:
        transcript_path = get_current_transcript()

    if not transcript_path or not transcript_path.exists():
        print("❌ 找不到当前会话 transcript")
        print("   请指定路径: python session_cleaner.py <transcript.jsonl>")
        sys.exit(1)

    print(f"📋 分析会话记录: {transcript_path.name}")
    actions = parse_transcript(transcript_path)
    print(f"   解析到 {len(actions)} 个工具调用")

    classified = classify_actions(actions)
    report = generate_session_report(classified, transcript_path)

    # Save report
    out_dir = Path.cwd() / ".claude"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "SESSION-CLEANUP-REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    print(f"\n{report}")
    print(f"\n📄 报告已保存: {report_path}")

    # Return summary as JSON for programmatic use
    summary_file = out_dir / "session_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(classified["summary"], f, indent=2, ensure_ascii=False)

    return classified


if __name__ == "__main__":
    main()
