const puppeteer = require('d:/rouca/DVM/workPlace/CareerOS/frontend/node_modules/puppeteer-core');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const VIEWPORT = { width: 390, height: 844, deviceScaleFactor: 2, isMobile: true, hasTouch: true };

const OUT_DIRS = [
  path.resolve(__dirname, 'designs/screenshots'),
  path.resolve(__dirname, 'frontend/public/screenshots')
];

async function saveScreenshot(page, filename) {
  for (const dir of OUT_DIRS) {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    const fullPath = path.join(dir, filename);
    await page.screenshot({ path: fullPath });
    console.log(`Saved: ${fullPath}`);
  }
}

async function run() {
  console.log('Launching Chrome via puppeteer-core at 390x844px...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  await page.setViewport(VIEWPORT);

  // 1. 01-glance-empty.png
  console.log('Scenario 1: Glance Empty State...');
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800));
  await saveScreenshot(page, '01-glance-empty.png');

  // 2. 02-generative-card.png
  console.log('Scenario 2: Generative Card in Stream...');
  await page.goto('http://localhost:3000/?demo=generative', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800));
  await saveScreenshot(page, '02-generative-card.png');

  // 3. 03-progressive-drawer.png
  console.log('Scenario 3: Progressive Depth 3 Drawer (Examine Verdict)...');
  const clickedVerdict = await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent && b.textContent.includes('Examine Verdict'));
    if (btn) {
      btn.click();
      return true;
    }
    return false;
  });
  console.log('Clicked Examine Verdict button:', clickedVerdict);
  await new Promise(r => setTimeout(r, 800)); // wait for drawer animation
  await saveScreenshot(page, '03-progressive-drawer.png');

  // 4. 04-secret-admin-drawer.png
  console.log('Scenario 4: 5-Tap Secret Admin Drawer...');
  await page.goto('http://localhost:3000/', { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 800));

  for (let i = 0; i < 5; i++) {
    const tapped = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find(b => b.textContent && b.textContent.includes('CareerOS Super-Agent v2.0'));
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    });
    console.log(`Tap ${i + 1}/5 status:`, tapped);
    await new Promise(r => setTimeout(r, 150));
  }
  await new Promise(r => setTimeout(r, 800)); // wait for drawer animation
  await saveScreenshot(page, '04-secret-admin-drawer.png');

  await browser.close();
  console.log('Visual QA capture completed successfully.');
}

run().catch(err => {
  console.error('Error during capture:', err);
  process.exit(1);
});
