#!/bin/bash

if [ ! -z "$PUID" ] && [ ! -z "$PGID" ]; then
    groupmod -g $PGID $APP_USER
    usermod -u $PUID -g $PGID $APP_USER

    chown -R $PUID:$PGID /home/src

    exec gosu $APP_USER python3 /home/src/main.py
else
    chown -R 0:0 /home/src
    
    exec python3 /home/src/main.py
fi