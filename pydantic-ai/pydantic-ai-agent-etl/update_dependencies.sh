#!/bin/bash

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install pyyaml
pip install pyyaml

# Run the Python script
python update_dependencies.py