import fs from 'fs';
const file = 'apps/dashboard/src/app/login/page.tsx';
let content = fs.readFileSync(file, 'utf8');

// Replace the condition to handle both encoded and unencoded
content = content.replace(
  "if (result.error.startsWith('MFA_REQUIRED:')) {",
  "const decodedError = decodeURIComponent(result.error || '');\n        if (decodedError.startsWith('MFA_REQUIRED:')) {"
);

// Update how the token is extracted
content = content.replace(
  "setMfaToken(result.error.replace('MFA_REQUIRED:', ''));",
  "setMfaToken(decodedError.replace('MFA_REQUIRED:', ''));"
);

fs.writeFileSync(file, content);
console.log('Fixed page.tsx');
