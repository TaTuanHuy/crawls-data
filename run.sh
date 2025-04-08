#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run crawler
python main.py --url "$1" --pages "$2" --output "$3"

#Run:  python3 run_test_main.py src/output/_20250311_124206.json
