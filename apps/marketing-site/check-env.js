// check-env.js - Script to check environment variables at container startup
console.log('\n=== ENVIRONMENT VARIABLE CHECK ===');

// List of required environment variables to check
const requiredVars = [
  'NEXT_PUBLIC_ENV',
  'NEXT_PUBLIC_API_BASE_URL',
  'NEXT_PUBLIC_SITE_URL',
  'GOOGLE_CLIENT_ID',
  'GOOGLE_CLIENT_SECRET',
  'GITHUB_CLIENT_ID',
  'GITHUB_CLIENT_SECRET',
  'NEXTAUTH_SECRET',
  'NEXTAUTH_URL'
];

// Check each variable and log its status
requiredVars.forEach(varName => {
  const isConfigured = !!process.env[varName];
  const status = isConfigured ? '✅ YES' : '❌ NO';
  
  // For sensitive variables, don't show the actual value
  const isSensitive = varName.includes('SECRET') || varName.includes('KEY') || varName.includes('TOKEN');
  let valueInfo = '';
  
  if (isConfigured) {
    if (isSensitive) {
      valueInfo = ' (value hidden)';
    } else if (varName.includes('URL')) {
      valueInfo = `: ${process.env[varName]}`;
    }
  }
  
  console.log(`${varName}: ${status}${valueInfo}`);
});

console.log('===================================\n');

// Don't exit the process, just let the script finish
