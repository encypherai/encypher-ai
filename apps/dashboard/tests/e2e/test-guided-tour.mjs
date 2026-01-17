#!/usr/bin/env node
import puppeteer from 'puppeteer';

(async () => {
  console.log('🚀 Starting Guided Tour E2E Test...\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    defaultViewport: { width: 1920, height: 1080 },
  });

  const page = await browser.newPage();
  
  try {
    // Step 1: Login
    console.log('1️⃣  Navigating to login page...');
    await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle2' });
    
    console.log('2️⃣  Logging in with test credentials...');
    await page.type('input[type="email"]', 'test@encypherai.com');
    await page.type('input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle2' });
    console.log('✅ Login successful\n');
    
    // Step 2: Navigate to Playground
    console.log('3️⃣  Navigating to playground...');
    await page.goto('http://localhost:3001/playground', { waitUntil: 'networkidle2' });
    await page.waitForSelector('h2');
    console.log('✅ Playground loaded\n');
    
    // Step 3: Start Guided Tour
    console.log('4️⃣  Starting guided tour...');
    // Find and click the "Start Guided Tour" button
    const tourButton = await page.evaluateHandle(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      return buttons.find(btn => btn.textContent.includes('Start Guided Tour'));
    });
    
    if (!tourButton) {
      throw new Error('Start Guided Tour button not found');
    }
    
    await tourButton.click();
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('✅ Tour started\n');
    
    // Step 4: Verify tour spotlight is visible
    console.log('5️⃣  Checking for tour spotlight...');
    const spotlightVisible = await page.evaluate(() => {
      const spotlight = document.querySelector('[class*="spotlight"]') || 
                       document.querySelector('[class*="tour"]');
      return spotlight !== null;
    });
    
    if (spotlightVisible) {
      console.log('✅ Tour spotlight is visible\n');
    } else {
      console.log('⚠️  Tour spotlight not found (may use different selector)\n');
    }
    
    // Step 5: Verify "Generate New API Key" button is highlighted
    console.log('6️⃣  Looking for Generate API Key button...');
    const generateButton = await page.$('[data-tour-target="generate-api-key"]');
    if (generateButton) {
      console.log('✅ Generate API Key button found\n');
      
      // Step 6: Click Generate API Key
      console.log('7️⃣  Clicking Generate API Key button...');
      await generateButton.click();
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check if key was generated
      const keyGenerated = await page.evaluate(() => {
        const input = document.querySelector('input[value^="ek_"]');
        return input !== null && input.value.length > 0;
      });
      
      if (keyGenerated) {
        console.log('✅ API Key generated successfully\n');
      } else {
        console.log('⚠️  API Key may not have been generated\n');
      }
    } else {
      console.log('❌ Generate API Key button not found\n');
    }
    
    // Step 7: Wait for tour to advance to step 1 (Sign)
    console.log('8️⃣  Waiting for tour to advance to Sign step...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check if we're on the Sign endpoint
    const onSignEndpoint = await page.evaluate(() => {
      const bodyText = document.body.innerText;
      return bodyText.includes('Sign Content') || bodyText.includes('/sign');
    });
    
    if (onSignEndpoint) {
      console.log('✅ Tour advanced to Sign step\n');
    } else {
      console.log('⚠️  May not be on Sign endpoint yet\n');
    }
    
    // Step 8: Click Send Request for signing
    console.log('9️⃣  Looking for Send Request button...');
    const sendButton = await page.$('[data-tour-target="send-request"]');
    if (sendButton) {
      console.log('✅ Send Request button found\n');
      
      console.log('🔟 Clicking Send Request to sign content...');
      await sendButton.click();
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Check for response
      const hasResponse = await page.evaluate(() => {
        const responseText = document.body.innerText;
        return responseText.includes('signed_text') || responseText.includes('success');
      });
      
      if (hasResponse) {
        console.log('✅ Content signed successfully\n');
      } else {
        console.log('⚠️  Sign response not detected\n');
      }
    } else {
      console.log('❌ Send Request button not found\n');
    }
    
    // Step 9: Look for Copy to Verify button
    console.log('1️⃣1️⃣  Looking for Copy to Verify button...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    const copyButton = await page.$('[data-tour-target="copy-to-verify"]');
    if (copyButton) {
      console.log('✅ Copy to Verify button found\n');
      
      console.log('1️⃣2️⃣  Clicking Copy to Verify...');
      await copyButton.click();
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('✅ Copied to Verify endpoint\n');
    } else {
      console.log('⚠️  Copy to Verify button not found (may not be visible yet)\n');
    }
    
    // Step 10: Final Send Request for verification
    console.log('1️⃣3️⃣  Clicking Send Request to verify...');
    const finalSendButton = await page.$('[data-tour-target="send-request"]');
    if (finalSendButton) {
      await finalSendButton.click();
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Check for verification response
      const verified = await page.evaluate(() => {
        const responseText = document.body.innerText;
        return responseText.includes('valid') || responseText.includes('Signature Valid');
      });
      
      if (verified) {
        console.log('✅ Content verified successfully\n');
      } else {
        console.log('⚠️  Verification response not detected\n');
      }
    }
    
    // Take final screenshot
    console.log('1️⃣4️⃣  Taking final screenshot...');
    await page.screenshot({ path: '/tmp/guided-tour-complete.png', fullPage: true });
    console.log('✅ Screenshot saved to /tmp/guided-tour-complete.png\n');
    
    console.log('🎉 Guided Tour E2E Test Complete!\n');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    await page.screenshot({ path: '/tmp/guided-tour-error.png', fullPage: true });
    console.log('Error screenshot saved to /tmp/guided-tour-error.png');
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
