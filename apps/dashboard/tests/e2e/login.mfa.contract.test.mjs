import fs from 'fs';
const file = fs.readFileSync('apps/dashboard/src/app/login/page.tsx', 'utf8');

if (!file.includes('decodeURIComponent(result.error || \'\')')) {
  console.error("Contract failed: login page should decodeURIComponent the NextAuth error");
  process.exit(1);
}

if (!file.includes('decodedError.startsWith(\'MFA_REQUIRED:\')')) {
  console.error("Contract failed: login page should check the decoded error for MFA_REQUIRED");
  process.exit(1);
}

console.log("Contract passed: login page correctly handles NextAuth encoded MFA_REQUIRED error.");
