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
    console.log('Logging in...');
    await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2' });
    await page.type('input[type="email"]', 'test@encypherai.com');
    await page.type('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    
    console.log('Navigating to playground...');
    await page.goto('http://localhost:3001/playground', { waitUntil: 'networkidle2' });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    console.log('Starting tour...');
    const tourButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(btn => btn.textContent.includes('Start Guided Tour'));
    });
    
    if (tourButton) {
      await tourButton.click();
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      console.log('Taking screenshot...');
      await page.screenshot({ 
        path: '/tmp/tour-spotlight-test.png', 
        fullPage: false 
      });
      console.log('✅ Screenshot saved to /tmp/tour-spotlight-test.png');
    } else {
      console.log('❌ Tour button not found');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();
