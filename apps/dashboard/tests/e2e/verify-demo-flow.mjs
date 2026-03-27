#!/usr/bin/env node
import puppeteer from 'puppeteer';

(async () => {
  // Use the pre-configured demo API key from enterprise_api/app/dependencies.py
  const testApiKey = 'demo-api-key-for-testing';
  console.log('0. Using demo API key for testing...');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--display=:99'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();

  try {
    console.log('1. Navigating to login page...');
    await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2' });

    console.log('2. Logging in with test credentials...');
    await page.type('input[type="email"]', 'test@encypher.com');
    await page.type('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });

    console.log('3. Navigating to playground...');
    await page.goto('http://localhost:3001/playground', { waitUntil: 'networkidle2' });

    console.log('4. Verifying endpoint is "sign"...');
    const endpointId = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const activeButton = buttons.find(btn => btn.classList.contains('bg-blue-50') || btn.classList.contains('bg-blue-900/30'));
      return activeButton ? activeButton.textContent : null;
    });
    if (!endpointId || !endpointId.includes('Sign Content')) {
      throw new Error(`Expected "Sign Content" endpoint, got: ${endpointId}`);
    }
    console.log('✅ Demo starts at Sign endpoint');

    console.log('5. Filling sign form with demo content...');
    await page.evaluate(() => {
      const demoText = 'Breaking: Scientists discover high-energy particles from distant galaxy.';
      const textareas = Array.from(document.querySelectorAll('textarea'));
      const textArea = textareas.find(ta => ta.placeholder?.toLowerCase().includes('sign'));
      if (textArea) {
        textArea.value = demoText;
        textArea.dispatchEvent(new Event('input', { bubbles: true }));
        textArea.dispatchEvent(new Event('change', { bubbles: true }));
      }
    });
    const textValue = await page.evaluate(() => {
      const textareas = Array.from(document.querySelectorAll('textarea'));
      const textArea = textareas.find(ta => ta.placeholder?.toLowerCase().includes('sign'));
      return textArea ? textArea.value : null;
    });
    if (!textValue || !textValue.includes('Scientists discover high-energy particles')) {
      throw new Error('Demo content not set');
    }
    console.log('✅ Demo content populated');

    // Input API key if available
    if (testApiKey) {
      console.log('6. Entering API key for authentication...');
      await page.evaluate((apiKey) => {
        // Select "Custom API Key" option
        const selects = Array.from(document.querySelectorAll('select'));
        const authSelect = selects.find(s => s.value === 'none' || s.value === 'custom' || s.value === 'session');
        if (authSelect) {
          authSelect.value = 'custom';
          authSelect.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Find and fill the API key input
        const inputs = Array.from(document.querySelectorAll('input[type="text"], input[type="password"]'));
        const apiKeyInput = inputs.find(input =>
          input.placeholder?.toLowerCase().includes('api key') ||
          input.placeholder?.toLowerCase().includes('paste')
        );
        if (apiKeyInput) {
          apiKeyInput.value = apiKey;
          apiKeyInput.dispatchEvent(new Event('input', { bubbles: true }));
          apiKeyInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
      }, testApiKey);
      await new Promise(resolve => setTimeout(resolve, 500));
      console.log('✅ API key entered');
    } else {
      console.log('⚠️  No API key available - sign request may fail');
    }

    console.log('7. Clicking "Send Request" to sign...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const sendButton = buttons.find(btn => btn.textContent.includes('Send Request'));
      if (sendButton) sendButton.click();
    });
    await new Promise(resolve => setTimeout(resolve, 5000));

    console.log('8. Checking sign response...');
    const signResponse = await page.evaluate(() => {
      const pre = document.querySelector('pre');
      return pre ? pre.textContent : null;
    });

    if (!signResponse) {
      await page.screenshot({ path: '/tmp/demo-flow-no-response.png' });
      throw new Error('No sign response received - screenshot saved');
    }

    console.log('Sign response:', signResponse.substring(0, 200));

    const signData = JSON.parse(signResponse);
    if (!signData.success || !signData.signed_text) {
      console.log('Sign failed, response:', JSON.stringify(signData, null, 2));
      await page.screenshot({ path: '/tmp/demo-flow-sign-failed.png' });
      throw new Error(`Sign failed: ${signData.error || signData.message || 'Unknown error'}`);
    }
    console.log('✅ Content signed successfully');

    console.log('9. Clicking "Copy to Verify →" button...');
    const clicked = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const copyButton = buttons.find(btn => btn.textContent.includes('Copy to Verify'));
      if (copyButton) {
        copyButton.click();
        return true;
      }
      return false;
    });

    if (!clicked) {
      throw new Error('Copy to Verify button not found after signing');
    }
    console.log('✅ Copy to Verify button clicked');
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log('10. Verifying endpoint switched to "verify"...');
    const verifyEndpointId = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const activeButton = buttons.find(btn => btn.classList.contains('bg-blue-50') || btn.classList.contains('bg-blue-900/30'));
      return activeButton ? activeButton.textContent : null;
    });
    if (!verifyEndpointId || !verifyEndpointId.includes('Verify Content')) {
      throw new Error(`Expected "Verify Content" endpoint, got: ${verifyEndpointId}`);
    }
    console.log('✅ Endpoint switched to Verify');

    console.log('11. Verifying signed content was copied...');
    const verifyTextValue = await page.evaluate(() => {
      const textareas = Array.from(document.querySelectorAll('textarea'));
      const textArea = textareas.find(ta => ta.value.includes('Scientists') || ta.placeholder.includes('Text'));
      return textArea ? textArea.value : null;
    });
    if (!verifyTextValue || !verifyTextValue.includes('Scientists discover high-energy particles')) {
      throw new Error('Signed content not copied to verify');
    }
    console.log('✅ Signed content copied to Verify');

    console.log('12. Clicking "Send Request" to verify...');
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const verifyButton = buttons.find(btn => btn.textContent.includes('Send Request'));
      if (verifyButton) verifyButton.click();
    });
    await new Promise(resolve => setTimeout(resolve, 3000));

    console.log('13. Verifying verification response...');
    const responseText = await page.$eval('pre', el => el.textContent);
    const response = JSON.parse(responseText);
    if (!response.data || !response.data.is_signed) {
      throw new Error('Verification failed');
    }
    console.log('✅ Content verified successfully');

    console.log('\n✅ DEMO FLOW VERIFICATION COMPLETE: Sign → Copy → Verify works correctly!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: '/tmp/demo-flow-error.png' });
    console.log('Screenshot saved to /tmp/demo-flow-error.png');
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
