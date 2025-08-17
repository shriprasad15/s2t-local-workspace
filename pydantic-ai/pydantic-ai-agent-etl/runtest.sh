#!/bin/bash

# Default parameter values
HELP=false
LIST=false
RUN=""

# Function to show help
show_help() {
    echo -e "\nTest Runner Help"
    echo "================"
    echo "Usage: ./run.sh [-h] [-l] [-r <test_pattern>]"
    echo -e "\nOptions:"
    echo "  -h             Show this help message"
    echo "  -l             List all available tests"
    echo "  -r <pattern>   Run specific tests (e.g., 'test_insert_document' or 'test_get_documents')"
    echo "  (no options)   Run all tests"
    echo
}

# Parse command-line arguments
while getopts "hlr:" opt; do
    case $opt in
        h) HELP=true ;;
        l) LIST=true ;;
        r) RUN=$OPTARG ;;
        *) show_help; exit 1 ;;
    esac
done

# Show help if requested
if $HELP; then
    show_help
    exit 0
fi

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install pytest requests pytest-cov pydantic pytest-asyncio

# Handle different execution modes
if $LIST; then
    pytest tests/test_api_client.py --collect-only -q
elif [ -n "$RUN" ]; then
    pytest tests/test_api_client.py -v -k "$RUN"
else
    pytest tests/test_api_client.py -v
fi

# Deactivate virtual environment
deactivate
