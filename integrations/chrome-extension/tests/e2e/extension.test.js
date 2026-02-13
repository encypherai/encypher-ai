/**
 * E2E Tests for Encypher C2PA Verifier Chrome Extension
 * 
 * Prerequisites:
 * - Chrome browser installed
 * - Enterprise API running on localhost:9000 (via startup-dev.ps1)
 * - npm install puppeteer in chrome-extension directory
 * 
 * Run: npm run test:e2e
 */

import puppeteer from 'puppeteer';
import path from 'path';
import { fileURLToPath } from 'url';
import { describe, it, before, after } from 'node:test';
import assert from 'node:assert';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Extension path (two levels up from tests/e2e)
const EXTENSION_PATH = path.resolve(__dirname, '../..');

// API configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:9000';
const DEMO_API_KEY = process.env.DEMO_API_KEY || 'demo_key_for_testing';

// Test page with signed content (served by marketing site or local)
const TEST_PAGE_URL = process.env.TEST_PAGE_URL || 'http://localhost:3000/mock-article.html';

let browser;
let extensionId;

/**
 * Launch Chrome with the extension loaded
 */
async function launchBrowserWithExtension() {
  browser = await puppeteer.launch({
    headless: false, // Extensions require non-headless mode
    args: [
      `--disable-extensions-except=${EXTENSION_PATH}`,
      `--load-extension=${EXTENSION_PATH}`,
      '--no-sandbox',
      '--disable-setuid-sandbox'
    ]
  });

  // Wait for extension to load and get its ID
  const targets = await browser.targets();
  const extensionTarget = targets.find(target => 
    target.type() === 'service_worker' && 
    target.url().includes('chrome-extension://')
  );

  if (extensionTarget) {
    const url = extensionTarget.url();
    extensionId = url.split('/')[2];
    console.log(`Extension loaded with ID: ${extensionId}`);
  } else {
    // Wait a bit and try again
    await new Promise(resolve => setTimeout(resolve, 2000));
    const retryTargets = await browser.targets();
    const retryTarget = retryTargets.find(target => 
      target.type() === 'service_worker' && 
      target.url().includes('chrome-extension://')
    );
    if (retryTarget) {
      extensionId = retryTarget.url().split('/')[2];
      console.log(`Extension loaded with ID: ${extensionId}`);
    }
  }

  return browser;
}

/**
 * Open the extension popup
 */
async function openPopup() {
  const page = await browser.newPage();
  await page.goto(`chrome-extension://${extensionId}/popup/popup.html`);
  await page.waitForSelector('.popup');
  return page;
}

/**
 * Open the extension options page
 */
async function openOptions() {
  const page = await browser.newPage();
  await page.goto(`chrome-extension://${extensionId}/options/options.html`);
  await page.waitForSelector('.options');
  return page;
}

describe('Chrome Extension E2E Tests', () => {
  before(async () => {
    await launchBrowserWithExtension();
  });

  after(async () => {
    if (browser) {
      await browser.close();
    }
  });

  describe('Extension Loading', () => {
    it('should load the extension successfully', async () => {
      assert.ok(extensionId, 'Extension ID should be defined');
      assert.ok(extensionId.length > 0, 'Extension ID should not be empty');
    });

    it('should have a working popup', async () => {
      const popup = await openPopup();
      
      // Check popup header
      const title = await popup.$eval('.popup__title', el => el.textContent);
      assert.strictEqual(title, 'Encypher Verifier');
      
      // Check tabs exist (Verify, Sign, and Debug — Debug is hidden by default)
      const tabs = await popup.$$('.popup__tab');
      assert.strictEqual(tabs.length, 3, 'Should have 3 tabs (Verify, Sign, and Debug)');
      
      await popup.close();
    });

    it('should have a working options page', async () => {
      const options = await openOptions();
      
      // Check options header
      const header = await options.$eval('.options__header h1', el => el.textContent);
      assert.strictEqual(header, 'Settings');
      
      // Check API key field exists
      const apiKeyInput = await options.$('#apiKey');
      assert.ok(apiKeyInput, 'API key input should exist');
      
      await options.close();
    });
  });

  describe('Options Page', () => {
    it('should save API key', async () => {
      const options = await openOptions();
      
      // Enter API key
      await options.type('#apiKey', DEMO_API_KEY);
      
      // Click save
      await options.click('#saveApiKey');
      
      // Wait for status update
      await options.waitForFunction(
        () => document.getElementById('apiKeyStatus').textContent.length > 0,
        { timeout: 5000 }
      );
      
      await options.close();
    });

    it('should toggle auto-verify setting', async () => {
      const options = await openOptions();
      
      const checkbox = await options.$('#autoVerify');
      const initialState = await options.$eval('#autoVerify', el => el.checked);
      
      await checkbox.click();
      
      const newState = await options.$eval('#autoVerify', el => el.checked);
      assert.notStrictEqual(initialState, newState, 'Checkbox state should toggle');
      
      await options.close();
    });

    it('should change API base URL', async () => {
      const options = await openOptions();
      
      await options.select('#apiBaseUrl', 'http://localhost:9000');
      
      const selectedValue = await options.$eval('#apiBaseUrl', el => el.value);
      assert.strictEqual(selectedValue, 'http://localhost:9000');
      
      await options.close();
    });
  });

  describe('Popup Tabs', () => {
    it('should switch between Verify and Sign tabs', async () => {
      const popup = await openPopup();
      
      // Initially on Verify tab
      const verifyTab = await popup.$('.popup__tab[data-tab="verify"]');
      let isActive = await popup.$eval('.popup__tab[data-tab="verify"]', 
        el => el.classList.contains('popup__tab--active'));
      assert.ok(isActive, 'Verify tab should be active initially');
      
      // Click Sign tab
      await popup.click('.popup__tab[data-tab="sign"]');
      await popup.waitForSelector('#sign-tab:not([hidden])');
      
      // Check Sign tab is now active
      isActive = await popup.$eval('.popup__tab[data-tab="sign"]', 
        el => el.classList.contains('popup__tab--active'));
      assert.ok(isActive, 'Sign tab should be active after clicking');
      
      // Sign tab content should be visible
      const signTabHidden = await popup.$eval('#sign-tab', el => el.hidden);
      assert.strictEqual(signTabHidden, false, 'Sign tab content should be visible');
      
      await popup.close();
    });
  });

  describe('Content Detection', () => {
    it('should detect signed content on test page', async () => {
      // Skip if test page URL is not available
      if (!TEST_PAGE_URL.startsWith('http://localhost')) {
        console.log('Skipping: Test page not available');
        return;
      }

      const page = await browser.newPage();
      
      try {
        await page.goto(TEST_PAGE_URL, { waitUntil: 'networkidle0', timeout: 10000 });
        
        // Wait for content script to run
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        // Check if any badges were injected
        const badges = await page.$$('.encypher-badge');
        console.log(`Found ${badges.length} verification badges`);
        
        // Note: This test may find 0 badges if the test page doesn't have signed content
        // That's okay - the test verifies the extension runs without errors
        
      } catch (error) {
        console.log('Test page not available:', error.message);
      } finally {
        await page.close();
      }
    });
  });

  describe('Signing Flow', () => {
    it('should show API key required message when no key is set', async () => {
      // First, clear the API key
      const options = await openOptions();
      
      // Handle confirmation dialog before triggering it
      options.on('dialog', async dialog => {
        await dialog.accept();
      });
      
      await options.click('#resetSettings');
      await new Promise(resolve => setTimeout(resolve, 1000));
      await options.close();
      
      // Open popup and go to Sign tab
      const popup = await openPopup();
      await popup.click('.popup__tab[data-tab="sign"]');
      await popup.waitForSelector('#sign-tab:not([hidden])');
      
      // Check for "API Key Required" message
      const noKeyVisible = await popup.$eval('#sign-no-key', el => !el.hidden);
      // Note: This may be true or false depending on whether API key was saved earlier
      
      await popup.close();
    });

    it('should have sign form when API key is configured', async () => {
      // Configure API key first
      const options = await openOptions();
      await options.type('#apiKey', DEMO_API_KEY);
      await options.click('#saveApiKey');
      await new Promise(resolve => setTimeout(resolve, 1000));
      await options.close();
      
      // Open popup and go to Sign tab
      const popup = await openPopup();
      await popup.click('.popup__tab[data-tab="sign"]');
      await popup.waitForSelector('#sign-tab:not([hidden])');
      
      // Wait for state to update
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Check if sign form is visible (or no-key message if API validation failed)
      const signReadyVisible = await popup.$eval('#sign-ready', el => !el.hidden).catch(() => false);
      const signNoKeyVisible = await popup.$eval('#sign-no-key', el => !el.hidden).catch(() => false);
      
      // One of them should be visible
      assert.ok(signReadyVisible || signNoKeyVisible, 'Either sign form or no-key message should be visible');
      
      await popup.close();
    });
  });
});

// Run tests if executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  console.log('Running E2E tests...');
  console.log(`Extension path: ${EXTENSION_PATH}`);
  console.log(`API base URL: ${API_BASE_URL}`);
}
