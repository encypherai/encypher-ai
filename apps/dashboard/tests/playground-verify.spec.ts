/**
 * Puppeteer test: Playground sign → verify flow
 * 
 * Tests that signed content from the Playground can be verified without losing metadata.
 * This test will fail if normalizeString() strips invisible characters.
 */
import { test, expect } from '@playwright/test';

test.describe('Playground Sign and Verify Flow', () => {
  test('should preserve invisible metadata when copying signed text to verify', async ({ page }) => {
    // Navigate to playground
    await page.goto('http://localhost:3001/playground');
    
    // Wait for page to load
    await page.waitForSelector('[data-testid="playground-container"]', { timeout: 10000 });
    
    // Step 1: Sign content
    await page.click('[data-testid="endpoint-sign"]');
    await page.fill('[data-testid="sign-text-input"]', 'Hello, world.');
    await page.click('[data-testid="execute-button"]');
    
    // Wait for sign response
    await page.waitForSelector('[data-testid="response-success"]', { timeout: 10000 });
    
    // Extract signed_text from response
    const signedText = await page.evaluate(() => {
      const responseEl = document.querySelector('[data-testid="response-json"]');
      if (!responseEl) return null;
      const response = JSON.parse(responseEl.textContent || '{}');
      return response?.data?.signed_text;
    });
    
    expect(signedText).toBeTruthy();
    expect(signedText).not.toBe('Hello, world.'); // Should have metadata
    
    console.log(`Signed text length: ${signedText?.length} bytes`);
    
    // Step 2: Verify the signed content
    await page.click('[data-testid="endpoint-verify"]');
    
    // Fill verify input with signed text
    await page.fill('[data-testid="verify-text-input"]', signedText!);
    
    // Capture the actual request payload before it's sent
    const requestPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/verify') && request.method() === 'POST'
    );
    
    await page.click('[data-testid="execute-button"]');
    
    const request = await requestPromise;
    const requestBody = request.postDataJSON();
    
    console.log(`Request payload text length: ${requestBody?.text?.length} bytes`);
    console.log(`Original signed text length: ${signedText?.length} bytes`);
    
    // CRITICAL CHECK: Request payload should preserve the full signed text
    expect(requestBody?.text?.length).toBe(signedText?.length);
    
    // Wait for verify response
    await page.waitForSelector('[data-testid="response-success"]', { timeout: 10000 });
    
    // Extract verification result
    const verifyResult = await page.evaluate(() => {
      const responseEl = document.querySelector('[data-testid="response-json"]');
      if (!responseEl) return null;
      const response = JSON.parse(responseEl.textContent || '{}');
      return {
        reason_code: response?.data?.reason_code,
        signer_id: response?.data?.signer_id,
        valid: response?.data?.valid,
        correlation_id: response?.correlation_id,
      };
    });
    
    console.log(`Verify result: ${JSON.stringify(verifyResult, null, 2)}`);
    
    // Should NOT be SIGNER_UNKNOWN
    expect(verifyResult?.reason_code).not.toBe('SIGNER_UNKNOWN');
    
    // Should be OK or UNTRUSTED_SIGNER (demo key)
    expect(['OK', 'UNTRUSTED_SIGNER']).toContain(verifyResult?.reason_code);
  });
  
  test('should detect metadata loss when text is trimmed', async ({ page }) => {
    // This test documents the bug: if we manually trim the signed text,
    // verification should fail with SIGNER_UNKNOWN
    
    await page.goto('http://localhost:3001/playground');
    await page.waitForSelector('[data-testid="playground-container"]', { timeout: 10000 });
    
    // Sign content
    await page.click('[data-testid="endpoint-sign"]');
    await page.fill('[data-testid="sign-text-input"]', 'Test content');
    await page.click('[data-testid="execute-button"]');
    await page.waitForSelector('[data-testid="response-success"]', { timeout: 10000 });
    
    const signedText = await page.evaluate(() => {
      const responseEl = document.querySelector('[data-testid="response-json"]');
      if (!responseEl) return null;
      const response = JSON.parse(responseEl.textContent || '{}');
      return response?.data?.signed_text;
    });
    
    // Manually trim the signed text (simulating the bug)
    const trimmedText = signedText?.trim();
    
    console.log(`Original length: ${signedText?.length}, Trimmed length: ${trimmedText?.length}`);
    
    // Verify the trimmed text
    await page.click('[data-testid="endpoint-verify"]');
    await page.fill('[data-testid="verify-text-input"]', trimmedText!);
    await page.click('[data-testid="execute-button"]');
    await page.waitForSelector('[data-testid="response-success"]', { timeout: 10000 });
    
    const verifyResult = await page.evaluate(() => {
      const responseEl = document.querySelector('[data-testid="response-json"]');
      if (!responseEl) return null;
      const response = JSON.parse(responseEl.textContent || '{}');
      return response?.data?.reason_code;
    });
    
    // Trimmed text should fail with SIGNER_UNKNOWN (metadata lost)
    expect(verifyResult).toBe('SIGNER_UNKNOWN');
  });
});
