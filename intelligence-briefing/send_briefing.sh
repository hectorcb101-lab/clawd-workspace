#!/bin/bash
# Send briefing via Telegram and Email
# This script is called by the daily_briefing.py after briefing generation

BRIEFING_TEXT="$1"
EMAIL_HTML="$2"

# Send to Telegram
echo "📱 Sending to Telegram..."
echo "$BRIEFING_TEXT" | clawdbot message send --channel telegram --target 6047368408

# Send to Email
echo "📧 Sending to Email..."
if [ -f "$EMAIL_HTML" ]; then
    HTML_CONTENT=$(cat "$EMAIL_HTML")
    mcporter call google-workspace.send_gmail_message \
        user_google_email="hectorcb101@gmail.com" \
        to="wfmckie@gmail.com" \
        subject="🌍 Daily Intelligence Briefing" \
        body="$HTML_CONTENT" \
        body_format="html"
fi

echo "✅ Delivery complete"
