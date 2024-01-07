#!/bin/bash

if [ ! -z "$PUID" ] && [ ! -z "$PGID" ]; then
    groupmod -g $PGID $APP_USER
    usermod -u $PUID -g $PGID $APP_USER

    chown -R $PUID:$PGID /src

    exec gosu $APP_USER python3 /src/main.py
else
    chown -R 0:0 /src
    
    exec python3 /src/main.py
fi