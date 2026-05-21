"""Activity tracker + cooldown logic for claude-project-cleaner.

Timeline:
  0 days (session ends)  → touch last_active timestamp
  7 days idle            → nudge user with cleanup suggestion
  30 days idle           → auto-clean cache only (Category E), keep everything else
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from utils import get_project_root, expand_home


COOLDOWN_NUDGE_DAYS = 7
COOLDOWN_AUTO_DAYS = 30
ACTIVITY_FILE = ".claude/.cleaner_activity.json"


def get_activity_file(project_root: Path = None) -> Path:
    """Get path to activity tracking file for current project."""
    if project_root is None:
        project_root = get_project_root()
    return project_root / ".claude" / ".cleaner_activity.json"


def touch_activity(project_root: Path = None):
    """Record current timestamp as last activity time."""
    af = get_activity_file(project_root)
    af.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if af.exists():
        try:
            data = json.loads(af.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
    data["last_active"] = datetime.now().isoformat()
    data["project"] = str(project_root) if project_root else str(get_project_root())
    af.write_text(json.dumps(data, indent=2))


def check_cooldown(project_root: Path = None) -> dict:
    """Check cooldown status. Returns dict with action recommendation."""
    af = get_activity_file(project_root)
    result = {
        "status": "active",
        "days_idle": 0,
        "action": "none",
        "message": "",
    }

    if not af.exists():
        # First time — initialize
        touch_activity(project_root)
        return result

    try:
        data = json.loads(af.read_text())
    except (json.JSONDecodeError, OSError):
        touch_activity(project_root)
        return result

    last_active_str = data.get("last_active", "")
    if not last_active_str:
        touch_activity(project_root)
        return result

    try:
        last_active = datetime.fromisoformat(last_active_str)
    except ValueError:
        touch_activity(project_root)
        return result

    days_idle = (datetime.now() - last_active).total_seconds() / 86400
    result["days_idle"] = round(days_idle, 1)

    if days_idle >= COOLDOWN_AUTO_DAYS:
        result["status"] = "stale"
        result["action"] = "auto_clean_cache"
        result["message"] = (
            f"Project idle for {int(days_idle)} days. "
            "Safe to auto-clean cache (Category E). "
            "Run /cleanup for full review."
        )
    elif days_idle >= COOLDOWN_NUDGE_DAYS:
        result["status"] = "idle"
        result["action"] = "nudge"
        result["message"] = (
            f"Project idle for {int(days_idle)} days. "
            "Consider running /cleanup to reclaim disk space."
        )
    else:
        result["status"] = "active"
        result["action"] = "none"

    return result


def main():
    """Entry point for Claude Code hooks and manual usage."""
    import argparse
    parser = argparse.ArgumentParser(description="Cooldown tracker for claude-project-cleaner")
    parser.add_argument("action", nargs="?", default="check",
                        choices=["touch", "check", "reset"],
                        help="touch=record activity, check=cooldown status, reset=clear tracking")
    parser.add_argument("--project", default=None, help="Project root path")
    args = parser.parse_args()

    project_root = Path(args.project) if args.project else get_project_root()

    if args.action == "touch":
        touch_activity(project_root)
        print(f"Activity recorded for {project_root.name}")

    elif args.action == "reset":
        af = get_activity_file(project_root)
        if af.exists():
            af.unlink()
            print(f"Activity tracking reset for {project_root.name}")
        else:
            print("No activity file to reset.")

    elif args.action == "check":
        result = check_cooldown(project_root)
        print(json.dumps(result, indent=2))
        if result["message"]:
            print(f"\n{result['message']}")

        # Exit codes for hook automation
        if result["action"] == "auto_clean_cache":
            # Signal that auto-cleanup should run
            sys.exit(2)
        elif result["action"] == "nudge":
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
