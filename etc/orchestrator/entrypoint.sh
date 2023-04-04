#!/bin/bash
python main.py db upgrade heads
pip install -r requirements.txt
uvicorn --proxy-headers --workers 4 --host 0.0.0.0 --port 8080 $UVICORN_ARGS main:app