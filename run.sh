#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run crawler
python main.py --url "$1" --pages "$2" --output "$3"
