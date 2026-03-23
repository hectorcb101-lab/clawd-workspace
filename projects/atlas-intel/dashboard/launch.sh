#!/bin/bash
# ATLAS INTEL Dashboard Launch Script

PORT=8080
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔════════════════════════════════════════════════════╗"
echo "║          ATLAS INTEL Dashboard                     ║"
echo "║          Tactical Intelligence System              ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Starting server on port $PORT..."
echo "Dashboard URL: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$DIR"
python3 -m http.server $PORT
