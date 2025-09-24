#!/bin/bash

echo "[Starting...]"
. venv/bin/activate
nohup python3 iracing_main.py &
