const { chromium } = require('playwright');

async function captureBackend() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const pages = [
    { url: 'http://localhost:8000/', name: '09-backend-home.png' },
    { url: 'http://localhost:8000/gallery', name: '10-backend-gallery.png' },
  ];

  for (const p of pages) {
    try {
      await page.goto(p.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `/home/ubuntu/clawd/screenshots/${p.name}` });
      console.log('✓ ' + p.name);
    } catch (e) {
      console.log('✗ ' + p.name + ': ' + e.message);
    }
  }

  await browser.close();
}

captureBackend();
