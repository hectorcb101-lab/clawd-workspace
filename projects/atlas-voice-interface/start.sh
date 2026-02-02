#!/bin/bash
# Start Atlas Voice Interface

cd "$(dirname "$0")"

# Check if already running on port 3000
if lsof -i :3000 >/dev/null 2>&1; then
    echo "Atlas Voice Interface is already running on port 3000"
    lsof -i :3000 | grep LISTEN
    exit 0
fi

# Create logs dir if needed
mkdir -p logs

# Start in background
echo "🏛️ Starting Atlas Voice Interface..."
nohup node server.js > logs/server.log 2>&1 &
SERVER_PID=$!

sleep 2

if lsof -i :3000 >/dev/null 2>&1; then
    echo "✅ Started successfully (PID: $SERVER_PID)"
    echo ""
    echo "📡 Access via SSH tunnel:"
    echo "   ssh -L 3000:localhost:3000 ubuntu@<vps-ip>"
    echo "   Then open: http://localhost:3000"
else
    echo "❌ Failed to start"
    cat logs/server.log
    exit 1
fi
