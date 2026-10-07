#!/bin/sh
# Hook executed by sshd on login
if [ -n "$SSH_CONNECTION" ]; then
    CLIENT_IP=$(echo "$SSH_CONNECTION" | awk '{print $1}')
    python3 /home/pi/piclock/notify.py "SSH Session" "${USER} from ${CLIENT_IP}" --duration 10 >/dev/null 2>&1 &
fi
