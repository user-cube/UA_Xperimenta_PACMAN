#!/bin/bash

function kill()
{
    killall python3
}

function deploy()
{
    source venv/bin/activate &
    python3 server.py --ghosts 4 --level 0 --port 8080 &
    sleep 1
    python3 server.py --ghosts 4 --level 0 --port 8081 --map data/map2.bmp &
    sleep 1
    python3 server.py --ghosts 4 --level 0 --port 8082 --map data/map3.bmp &
    sleep 1
    python3 server.py --ghosts 4 --level 0 --port 8083 --map data/map4.bmp
}

trap "kill ; exit 0" SIGINT
source venv/bin/activate &&
deploy
