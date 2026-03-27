#!/usr/bin/env node
import puppeteer from 'puppeteer';

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();

  try {
    console.log('1. Navigating to login...');
    await page.goto('http://localhost:3001/login', { waitUntil: 'domcontentloaded' });
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('2. Filling login form...');
    await page.type('input[type="email"]', 'test@encypher.com', { delay: 50 });
    await page.type('input[type="password"]', 'TestPassword123!', { delay: 50 });

    console.log('3. Submitting login...');
    await page.click('button[type="submit"]');
    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('4. Navigating to playground...');
    await page.goto('http://localhost:3001/playground', { waitUntil: 'domcontentloaded' });
    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('5. Looking for tour button...');
    const tourButtonExists = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.some(b => b.textContent.includes('Start Guided Tour'));
    });

    if (!tourButtonExists) {
      console.log('⚠️  Tour button not found, taking screenshot of current state...');
      await page.screenshot({ path: '/tmp/playground-no-tour.png', fullPage: true });
      console.log('Screenshot saved to /tmp/playground-no-tour.png');
    } else {
      console.log('✅ Tour button found');

      console.log('6. Clicking tour button...');
      await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button'));
        const tourBtn = buttons.find(b => b.textContent.includes('Start Guided Tour'));
        if (tourBtn) tourBtn.click();
      });

      await new Promise(resolve => setTimeout(resolve, 2000));

      console.log('7. Taking screenshot of spotlight...');
      await page.screenshot({ path: '/tmp/spotlight-final-test.png', fullPage: false });
      console.log('✅ Screenshot saved to /tmp/spotlight-final-test.png');

      // Check if the target button is visible
      const buttonVisible = await page.evaluate(() => {
        const targetBtn = document.querySelector('[data-tour-target="generate-api-key"]');
        if (!targetBtn) return false;

        const rect = targetBtn.getBoundingClientRect();
        const style = window.getComputedStyle(targetBtn);

        return {
          exists: true,
          visible: style.display !== 'none' && style.visibility !== 'hidden',
          opacity: style.opacity,
          position: { top: rect.top, left: rect.left, width: rect.width, height: rect.height }
        };
      });

      console.log('Button visibility:', JSON.stringify(buttonVisible, null, 2));
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/spotlight-error.png', fullPage: true });
    console.log('Error screenshot saved to /tmp/spotlight-error.png');
  } finally {
    await browser.close();
  }
})();
