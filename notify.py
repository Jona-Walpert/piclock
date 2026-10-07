"""Notification and message dispatching utility for PiClock.

Can be called from the CLI, scripts, or hooks (e.g. SSH logins, updates):
    python3 notify.py "SSH Session" "pi connected from 192.168.2.150"
    python3 notify.py "System Update" "Update installed successfully"
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

QUEUE_FILE = Path("/tmp/piclock_notify.json")


def send_notification(title: str, message: str, duration_sec: int = 8) -> bool:
    """Dispatches a notification to the running PiClock instance."""
    payload = {
        "title": title,
        "message": message,
        "duration": duration_sec,
        "timestamp": time.time(),
        "time_str": datetime.now().strftime("%H:%M:%S"),
    }

    try:
        tmp_file = QUEUE_FILE.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(payload))
        tmp_file.replace(QUEUE_FILE)
        print(f">> Notification queued: [{title}] {message} ({duration_sec}s)")
        return True
    except Exception as e:
        print(f"Failed to queue notification: {e}", file=sys.stderr)
        return False


def get_pending_notification():
    """Reads and removes pending notification, if any."""
    if not QUEUE_FILE.exists():
        return None

    try:
        content = QUEUE_FILE.read_text()
        QUEUE_FILE.unlink(missing_ok=True)
        return json.loads(content)
    except Exception:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send notifications to PiClock display")
    parser.add_argument("title", help="Notification title (e.g. 'SSH Login', 'System Update')")
    parser.add_argument("message", help="Notification message text")
    parser.add_argument("--duration", type=int, default=8, help="Display duration in seconds (default: 8)")
    args = parser.parse_args()

    success = send_notification(args.title, args.message, duration_sec=args.duration)
    sys.exit(0 if success else 1)
