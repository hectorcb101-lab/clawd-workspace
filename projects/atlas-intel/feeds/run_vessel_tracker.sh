#!/bin/bash
# Run the vessel tracker daemon
cd /home/ubuntu/clawd/projects/atlas-intel
source .venv/bin/activate
exec python3 feeds/vessel_tracker.py
