#!/bin/bash

echo "[Killing process...]"
pid=$(ps aux | grep "python3 iracing_main.py" | grep -v grep | awk '{print $2}')
kill $pid
echo $pid