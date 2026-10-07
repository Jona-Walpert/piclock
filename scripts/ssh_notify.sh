#!/bin/sh
# Hook executed by sshd on login
if [ -n "$SSH_CONNECTION" ]; then
    THROTTLE="/tmp/piclock_ssh_throttle"
    NOW=$(date +%s)
    if [ -f "$THROTTLE" ]; then
        LAST=$(cat "$THROTTLE" 2>/dev/null || echo 0)
        DIFF=$((NOW - LAST))
        if [ "$DIFF" -lt 60 ]; then
            exit 0
        fi
    fi
    echo "$NOW" > "$THROTTLE"
    CLIENT_IP=$(echo "$SSH_CONNECTION" | awk '{print $1}')
    python3 /home/pi/piclock/notify.py "SSH Session" "${USER} from ${CLIENT_IP}" --duration 10 >/dev/null 2>&1 &
fi
