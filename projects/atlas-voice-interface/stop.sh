#!/bin/bash
# Stop Atlas Voice Interface

PID=$(pgrep -f "node.*atlas-voice-interface/server.js")

if [ -n "$PID" ]; then
    echo "Stopping Atlas Voice Interface (PID: $PID)..."
    kill $PID
    sleep 1
    echo "✅ Stopped"
else
    echo "Atlas Voice Interface is not running"
fi
