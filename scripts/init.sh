#!/bin/bash

# Check if both PUID and PGID are set
if [ -n "$PUID" ] && [ -n "$PGID" ]; then
    # Modify the group ID and user ID of the APP_USER
    groupmod -g "$PGID" "$APP_USER" && \
    usermod -u "$PUID" -g "$PGID" "$APP_USER"

    # Set ownership of /home/src recursively
    chown -R "$PUID:$PGID" /home/src

    # Run the Python application as the specified user
    exec gosu "$APP_USER" python3 /home/src/main.py
else
    # If PUID and PGID are not set, run as root
    chown -R 0:0 /home/src

    # Run the Python application as root
    exec python3 /home/src/main.py
fi
