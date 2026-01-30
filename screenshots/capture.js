const { chromium } = require('playwright');

async function captureScreenshots() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  const screenshots = [
    { url: 'http://localhost:3000', name: '01-landing-page.png' },
    { url: 'http://localhost:3000#features', name: '02-features.png' },
    { url: 'http://localhost:3000#pricing', name: '03-pricing.png' },
    { url: 'http://localhost:8000/docs', name: '04-backend-docs.png' },
    { url: 'http://localhost:8000/brands', name: '05-brands-page.png' },
  ];

  for (const s of screenshots) {
    try {
      await page.goto(s.url, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(1000);
      await page.screenshot({ path: `/home/ubuntu/clawd/screenshots/${s.name}`, fullPage: false });
      console.log(`✓ Captured: ${s.name}`);
    } catch (e) {
      console.log(`✗ Failed: ${s.name} - ${e.message}`);
    }
  }

  // Full page landing
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/00-landing-full.png', fullPage: true });
  console.log('✓ Captured: 00-landing-full.png (full page)');

  await browser.close();
  console.log('\nDone! Screenshots saved to ~/clawd/screenshots/');
}

captureScreenshots().catch(console.error);
