#!/bin/bash
# Run NASA FIRMS Thermal Anomaly Monitor

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/.venv"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Run the monitor
cd "$PROJECT_DIR"
python3 feeds/thermal_monitor.py "$@"
