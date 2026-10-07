#!/usr/bin/env bash
# ==============================================================================
# PiClock - System & Software Update Script with On-Screen Feedback
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo ">> Starting PiClock update..."

# Show update notification on screen
python3 "$DIR/notify.py" "System Update" "Pulling latest changes..." --duration 10 2>/dev/null || true

# Pull git changes
git pull origin main

# Restart systemd service
if command -v systemctl >/dev/null 2>&1; then
    sudo systemctl restart piclock.service || true
fi

# Show completion notification
python3 "$DIR/notify.py" "Update Complete" "PiClock is up to date!" --duration 8 2>/dev/null || true

echo ">> Update completed successfully!"
