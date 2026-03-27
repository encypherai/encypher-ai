#!/usr/bin/env node
/**
 * Setup script to create a test API key for E2E testing
 * Creates an API key for test@encypher.com with sign permission
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const TEST_EMAIL = 'test@encypher.com';
const TEST_PASSWORD = 'TestPassword123!';

async function setupTestApiKey() {
  try {
    console.log('1. Logging in as test user...');
    const loginResponse = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: TEST_EMAIL,
        password: TEST_PASSWORD,
      }),
    });

    if (!loginResponse.ok) {
      throw new Error(`Login failed: ${loginResponse.status} ${await loginResponse.text()}`);
    }

    const loginData = await loginResponse.json();
    const accessToken = loginData.access_token || loginData.data?.access_token;

    if (!accessToken) {
      throw new Error('No access token received from login');
    }

    console.log('✅ Login successful');

    console.log('2. Creating API key with sign permission...');
    const createKeyResponse = await fetch(`${API_BASE}/keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        name: 'E2E Test Key',
        permissions: ['sign', 'verify'],
      }),
    });

    if (!createKeyResponse.ok) {
      const errorText = await createKeyResponse.text();
      throw new Error(`Create key failed: ${createKeyResponse.status} ${errorText}`);
    }

    const keyData = await createKeyResponse.json();
    const apiKey = keyData.key || keyData.data?.key;

    if (!apiKey) {
      throw new Error('No API key returned from creation');
    }

    console.log('✅ API key created successfully');
    console.log(`API Key: ${apiKey}`);

    // Return the key for use in tests
    return apiKey;

  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    throw error;
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  setupTestApiKey()
    .then(key => {
      console.log('\n✅ Test API key ready for use');
      process.exit(0);
    })
    .catch(error => {
      console.error('\n❌ Failed to setup test API key');
      process.exit(1);
    });
}

export { setupTestApiKey };
