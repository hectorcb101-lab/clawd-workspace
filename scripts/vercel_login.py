#!/usr/bin/env python3
"""
Vercel Login via Google OAuth using Playwright
"""

import asyncio
from playwright.async_api import async_playwright

async def login_to_vercel():
    async with async_playwright() as p:
        # Launch browser (headless=False would show UI but we're on VPS)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("[INFO] Navigating to Vercel login...")
        await page.goto("https://vercel.com/login")
        
        # Take screenshot to see what we're dealing with
        await page.screenshot(path="/home/ubuntu/clawd/assets/vercel_login_1.png")
        print("[INFO] Screenshot saved: vercel_login_1.png")
        
        # Look for "Continue with Google" button
        print("[INFO] Looking for Google login button...")
        
        # Wait for page to load
        await page.wait_for_load_state("networkidle")
        
        # Get page content to understand structure
        content = await page.content()
        print(f"[INFO] Page title: {await page.title()}")
        
        # Try to find and click Google login
        try:
            # Look for Google button by various selectors
            google_button = page.locator('button:has-text("Continue with Google")').first
            if await google_button.count() > 0:
                print("[INFO] Found 'Continue with Google' button, clicking...")
                await google_button.click()
                await page.wait_for_load_state("networkidle")
                await page.screenshot(path="/home/ubuntu/clawd/assets/vercel_login_2.png")
                print("[INFO] Screenshot saved: vercel_login_2.png")
            else:
                # Try alternative selectors
                google_button = page.locator('[data-testid="google-button"]').first
                if await google_button.count() > 0:
                    await google_button.click()
                else:
                    print("[INFO] Google button not found with expected selectors")
                    # List all buttons for debugging
                    buttons = await page.locator('button').all_text_contents()
                    print(f"[DEBUG] Available buttons: {buttons[:10]}")
        except Exception as e:
            print(f"[ERROR] Failed to click Google button: {e}")
        
        await page.screenshot(path="/home/ubuntu/clawd/assets/vercel_login_final.png")
        print("[INFO] Final screenshot saved")
        
        await browser.close()
        print("[INFO] Browser closed")

if __name__ == "__main__":
    asyncio.run(login_to_vercel())
