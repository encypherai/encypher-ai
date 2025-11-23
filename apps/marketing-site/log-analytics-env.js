// log-analytics-env.js
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Try to load environment variables from multiple possible files
// Order of precedence: process.env > .env.production > .env.local > .env
const envFiles = ['.env.production', '.env.local', '.env'];

for (const file of envFiles) {
  try {
    const filePath = path.resolve(process.cwd(), file);
    if (fs.existsSync(filePath)) {
      dotenv.config({ path: filePath });
      console.log(`[ENV] Loaded environment variables from ${file}`);
    }
  } catch (error) {
    console.warn(`[ENV] Error loading ${file}: ${error.message}`);
  }
}

// Log the environment variables that are critical for the build
const env = process.env.NEXT_PUBLIC_ENV;
const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const siteUrl = process.env.NEXT_PUBLIC_SITE_URL;

console.log('\n[ENV] Build environment variables:');
console.log(`[ENV] NEXT_PUBLIC_ENV = ${env || 'undefined'}`);
console.log(`[ENV] NEXT_PUBLIC_API_BASE_URL = ${apiBaseUrl || 'undefined'}`);
console.log(`[ENV] NEXT_PUBLIC_SITE_URL = ${siteUrl || 'undefined'}\n`);

if (env === 'production') {
  console.log('[Analytics] Analytics scripts WILL be loaded (NEXT_PUBLIC_ENV=production)');
} else {
  console.log(`[Analytics] Analytics scripts will NOT be loaded (NEXT_PUBLIC_ENV='${env || "undefined"}')`);
}
