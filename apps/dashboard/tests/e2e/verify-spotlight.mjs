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
    console.log('1. Logging in...');
    await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2', timeout: 10000 });
    await page.type('input[type="email"]', 'test@encypherai.com');
    await page.type('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 });
    console.log('✅ Logged in');
    
    console.log('2. Going to playground...');
    await page.goto('http://localhost:3001/playground', { waitUntil: 'networkidle2', timeout: 10000 });
    console.log('✅ Playground loaded');
    
    console.log('3. Starting tour...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const clicked = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const tourBtn = buttons.find(b => b.textContent.includes('Start Guided Tour'));
      if (tourBtn) {
        tourBtn.click();
        return true;
      }
      return false;
    });
    
    if (clicked) {
      console.log('✅ Tour started');
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('4. Taking screenshot...');
      await page.screenshot({ path: '/tmp/tour-spotlight-verified.png', fullPage: false });
      console.log('✅ Screenshot saved to /tmp/tour-spotlight-verified.png');
    } else {
      console.log('❌ Tour button not found');
      await page.screenshot({ path: '/tmp/no-tour-button.png' });
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    await page.screenshot({ path: '/tmp/tour-error.png' });
  } finally {
    await browser.close();
  }
})();
