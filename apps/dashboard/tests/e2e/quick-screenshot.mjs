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
    // Go to playground
    await page.goto('http://localhost:3001/playground', { 
      waitUntil: 'domcontentloaded',
      timeout: 8000 
    });
    
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Click tour button if it exists
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const tourBtn = buttons.find(b => b.textContent.includes('Start Guided Tour'));
      if (tourBtn) tourBtn.click();
    });
    
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    await page.screenshot({ path: '/tmp/tour-spotlight-fixed.png' });
    console.log('✅ Screenshot saved to /tmp/tour-spotlight-fixed.png');
    
  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: '/tmp/tour-error.png' });
  } finally {
    await browser.close();
  }
})();
