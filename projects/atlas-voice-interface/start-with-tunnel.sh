#!/bin/bash
# Start Atlas Voice Interface with public tunnel

cd "$(dirname "$0")"

# Start the server if not running
if ! lsof -i :3000 >/dev/null 2>&1; then
    echo "🏛️ Starting Atlas Voice Interface..."
    mkdir -p logs
    nohup node server.js > logs/server.log 2>&1 &
    sleep 2
fi

# Kill any existing tunnel
pkill -f "cloudflared.*localhost:3000" 2>/dev/null
sleep 1

# Start tunnel
echo "🌐 Creating public tunnel..."
cloudflared tunnel --url http://localhost:3000 2>&1 | tee logs/tunnel.log &

# Wait for URL
sleep 6

# Extract and display URL
URL=$(grep -o 'https://[^[:space:]]*trycloudflare.com' logs/tunnel.log | head -1)

if [ -n "$URL" ]; then
    echo ""
    echo "✅ Atlas Voice Interface is ready!"
    echo ""
    echo "🔗 Access URL: $URL"
    echo ""
    echo "Open in Chrome for best voice support."
    echo "$URL" > TUNNEL_URL.txt
else
    echo "⚠️ Tunnel might still be starting. Check logs/tunnel.log"
fi
