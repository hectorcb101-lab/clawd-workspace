#!/bin/bash
# Main briefing orchestrator - called by cron
# Generates briefing and sends it via Telegram and Email

set -e

cd /home/ubuntu/clawd/intelligence-briefing

echo "🌍 DAILY INTELLIGENCE BRIEFING"
echo "=============================="

# Step 1: Generate the briefing (this creates the text and HTML files)
echo "[1/3] Generating briefing..."
python3 daily_briefing.py --generate-only

# Step 2: Send via Telegram
echo "[2/3] Sending to Telegram..."
BRIEFING_FILE="/home/ubuntu/clawd/intelligence-briefing/data/history/$(date +%Y-%m-%d)_briefing.txt"
if [ -f "$BRIEFING_FILE" ]; then
    cat "$BRIEFING_FILE" | clawdbot message send --channel telegram --target 6047368408
    echo "✅ Telegram sent"
else
    echo "⚠️ Briefing file not found"
fi

# Step 3: Send via Email
echo "[3/3] Sending to Email..."
EMAIL_HTML="/home/ubuntu/clawd/intelligence-briefing/data/cache/email.html"
if [ -f "$EMAIL_HTML" ]; then
    # Use mcporter directly (not from Python subprocess)
    HTML_CONTENT=$(cat "$EMAIL_HTML")
    echo "$HTML_CONTENT" | mcporter call google-workspace.send_gmail_message \
        user_google_email=hectorcb101@gmail.com \
        to=wfmckie@gmail.com \
        "subject=🌍 Daily Intelligence Briefing - $(date +%B\ %d,\ %Y)" \
        body_format=html \
        --args "{\"body\": $(cat "$EMAIL_HTML" | jq -Rs .)}"
    echo "✅ Email sent"
else
    echo "⚠️ Email HTML not found"
fi

echo "=============================="
echo "✅ Briefing complete"
