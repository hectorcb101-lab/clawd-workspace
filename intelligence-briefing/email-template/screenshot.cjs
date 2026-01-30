const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 600, height: 2000 });
  
  const htmlPath = path.join(__dirname, '..', 'data', 'cache', 'email.html');
  await page.goto(`file://${htmlPath}`);
  
  const outputPath = path.join(__dirname, '..', 'email-preview.png');
  await page.screenshot({ 
    path: outputPath,
    fullPage: true 
  });
  
  console.log(`✅ Screenshot saved to: ${outputPath}`);
  
  await browser.close();
})();
