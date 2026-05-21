"""Shared utilities for claude-project-cleaner."""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional


def expand_home(path: str) -> Path:
    """Expand ~ to user home directory (cross-platform)."""
    if path.startswith("~"):
        return Path.home() / path[2:] if path.startswith("~/") else Path.home()
    return Path(path)


def get_claude_home() -> Path:
    """Return ~/.claude path."""
    return Path.home() / ".claude"


def get_project_root() -> Optional[Path]:
    """Find the nearest project root by looking for .claude or .git."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / ".claude").exists() or (parent / ".git").exists():
            return parent
    return cwd


def run_cmd(cmd: list[str], timeout: int = 15) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=False)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"Timeout after {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def file_info(path: Path) -> dict:
    """Get metadata for a file or directory."""
    try:
        stat = path.stat() if path.exists() else None
        return {
            "path": str(path),
            "exists": path.exists(),
            "is_dir": path.is_dir(),
            "size": stat.st_size if stat and not path.is_dir() else dir_size(path),
            "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat() if stat else None,
            "atime": datetime.fromtimestamp(stat.st_atime).isoformat() if stat else None,
        }
    except OSError:
        return {"path": str(path), "exists": False, "error": "Permission denied"}


def dir_size(path: Path) -> int:
    """Recursively compute directory size in bytes."""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"


def parse_version(name: str) -> Optional[str]:
    """Try to extract a version number from a directory or file name."""
    import re
    # Match patterns like chromium-120, 2.1.0, v3.0.1, etc.
    patterns = [
        r'[_-](\d+\.\d+(?:\.\d+)?(?:[_-][a-zA-Z0-9]+)?)',
        r'[_-]v?(\d+(?:\.\d+){1,3})',
        r'@(\d+(?:\.\d+){1,3})',
    ]
    for p in patterns:
        m = re.search(p, name)
        if m:
            return m.group(1)
    return None


def load_json(filepath: Path) -> dict:
    """Load and return JSON data."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(filepath: Path, data: dict):
    """Save data as JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def is_safe_to_delete(path: Path, whitelist: set) -> bool:
    """Check if a path is safe to delete based on whitelist rules."""
    path_str = str(path.resolve())
    for item in whitelist:
        if str(Path(item).resolve()) in path_str or path_str in str(Path(item).resolve()):
            return False
    # Never delete .git directories
    if ".git" in path.parts:
        return False
    # Never delete CLAUDE.md
    if path.name == "CLAUDE.md":
        return False
    return True
