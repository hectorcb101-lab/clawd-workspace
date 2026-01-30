const { chromium } = require('playwright');

async function captureMore() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  // Full page landing
  console.log('Capturing full landing page...');
  await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/00-landing-full.png', fullPage: true });
  console.log('✓ 00-landing-full.png');

  // Testimonials section
  await page.goto('http://localhost:3000#testimonials', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/05-testimonials.png' });
  console.log('✓ 05-testimonials.png');

  // FAQ section
  await page.goto('http://localhost:3000#faq', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/06-faq.png' });
  console.log('✓ 06-faq.png');

  // Backend brands (simpler request)
  await page.goto('http://localhost:8000/brands', { timeout: 15000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/07-brands.png' });
  console.log('✓ 07-brands.png');

  // Backend gallery  
  await page.goto('http://localhost:8000/gallery', { timeout: 15000 });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: '/home/ubuntu/clawd/screenshots/08-gallery.png' });
  console.log('✓ 08-gallery.png');

  await browser.close();
  console.log('\nDone!');
}

captureMore().catch(e => console.error('Error:', e.message));
