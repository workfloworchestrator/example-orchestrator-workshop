#!/bin/bash
python main.py db init
python main.py db upgrade heads
uvicorn --proxy-headers --workers 4 --host 0.0.0.0 --port 8080 $UVICORN_ARGS main:app