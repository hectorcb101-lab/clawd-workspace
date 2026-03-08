#!/usr/bin/env python3
"""
Daily Intelligence Briefing - Main Orchestrator
Collects data, finds patterns, generates insights, and sends to Telegram + Email
"""

import sys
import subprocess
import os
import json
from pathlib import Path

# Add project to path
sys.path.append('/home/ubuntu/clawd/intelligence-briefing')

from collectors.collect_data import collect_all_data
from collectors.collect_geopolitical_simple import collect_geopolitical_events
from analysis.patterns import find_patterns
from analysis.geopolitical_alpha import analyze_geopolitical_alpha
from synthesis.generate_insights import synthesize_insights
from presentation.format_briefing import format_briefing, save_briefing

def generate_email_html(insights):
    """Generate HTML email from insights."""
    try:
        print("📧 Generating HTML email...")
        
        # Save insights to temp file
        temp_insights = Path("/tmp/briefing_insights.json")
        with open(temp_insights, 'w') as f:
            json.dump(insights, f, indent=2)
        
        # Run the React email renderer
        email_template_dir = Path(__file__).parent / "email-template"
        cmd = f"cd {email_template_dir} && npx tsx render.ts {temp_insights} --save"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            html_path = Path(__file__).parent / "data" / "cache" / "email.html"
            print(f"✅ Email HTML generated: {html_path}")
            return html_path
        else:
            print(f"⚠️ Failed to generate email HTML: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"⚠️ Error generating email HTML: {e}")
        return None

def send_to_gmail(html_file, to="wfmckie@gmail.com", subject="🌍 Daily Intelligence Briefing"):
    """Send HTML email via Google Workspace MCP."""
    try:
        if not html_file or not Path(html_file).exists():
            print("⚠️ No HTML file to send")
            return False
        
        print(f"📧 Sending email to {to}...")
        
        # Read HTML
        html_content = Path(html_file).read_text()
        
        # Use mcporter to send via Google Workspace
        cmd = [
            'mcporter', 'call', 'google-workspace.send_gmail_message',
            'user_google_email=hectorcb101@gmail.com',
            f'to={to}',
            f'subject={subject}',
            f'body={html_content}',
            'body_format=html'
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and "Email sent" in result.stdout:
            print("✅ Email sent successfully")
            return True
        else:
            print(f"⚠️ Email send had issues: {result.stdout} {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error sending email: {e}")
        return False

def send_to_telegram(message, chat_id="6047368408"):
    """Send briefing to Telegram using Clawdbot message tool."""
    try:
        # Write message to temp file to avoid shell escaping issues
        temp_file = Path("/tmp/briefing_message.txt")
        with open(temp_file, 'w') as f:
            f.write(message)
        
        # Use clawdbot message send with proper syntax
        cmd = f"clawdbot message send --channel telegram --target {chat_id} < {temp_file}"
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Briefing sent to Telegram successfully")
            return True
        else:
            print(f"⚠️ Telegram send had issues: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️ Error sending to Telegram: {e}")
        return False

def main():
    """Main briefing generation and delivery pipeline."""
    print("=" * 60)
    print("🌍 DAILY INTELLIGENCE BRIEFING")
    print("=" * 60)
    
    try:
        # Step 1: Collect Data
        print("\n[1/7] 📊 Collecting market data from sources...")
        data = collect_all_data()
        print("✅ Market data collection complete")
        
        # Step 1b: Collect Geopolitical Events
        print("\n[1b/7] 🌍 Collecting geopolitical events...")
        geo_events = collect_geopolitical_events()
        print(f"✅ Collected {len(geo_events.get('events', []))} geopolitical events")
        
        # Step 2: Find Patterns
        print("\n[2/7] 🧠 Analyzing market patterns...")
        patterns = find_patterns(data)
        print(f"✅ Found {len(patterns['significant_moves'])} significant moves")
        
        # Step 2b: Analyze Geopolitical Alpha
        print("\n[2b/7] 🎯 Analyzing geopolitical alpha (transmission chains)...")
        geo_alpha = analyze_geopolitical_alpha(geo_events)
        print(f"✅ Generated {len(geo_alpha.get('chains', []))} transmission chains")
        
        # Step 3: Generate Insights
        print("\n[3/7] 💡 Synthesizing insights...")
        insights = synthesize_insights(patterns, geo_alpha)
        print("✅ Insights generated")
        
        # Step 4: Format Telegram Briefing
        print("\n[4/7] 📝 Formatting Telegram briefing...")
        briefing_text = format_briefing(insights)
        print("✅ Telegram briefing formatted")
        
        # Step 5: Generate Email HTML
        print("\n[5/7] 📧 Generating email HTML...")
        email_html = generate_email_html(insights)
        
        # Step 6: Send to both channels
        print("\n[6/7] 📤 Sending briefings...")
        
        telegram_success = send_to_telegram(briefing_text)
        email_success = False
        
        if email_html:
            email_success = send_to_gmail(email_html)
        
        # Save to archive
        text_path, json_path = save_briefing(briefing_text, insights)
        print(f"\n✅ Briefing archived at {text_path}")
        
        # Report results
        if telegram_success and email_success:
            print("\n🎉 Daily briefing complete! Sent to Telegram + Email")
            return 0
        elif telegram_success or email_success:
            channels = []
            if telegram_success:
                channels.append("Telegram")
            if email_success:
                channels.append("Email")
            print(f"\n⚠️ Partial success: Sent to {' + '.join(channels)}")
            return 0
        else:
            print("\n❌ Failed to send briefing to any channel")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error generating briefing: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
