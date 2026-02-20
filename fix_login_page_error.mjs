import fs from 'fs';
const file = 'apps/dashboard/src/app/login/page.tsx';
let content = fs.readFileSync(file, 'utf8');

// Replace the error setting logic to use the decoded error for everything
content = content.replace(
  "setError(result.error === 'CredentialsSignin' ? 'Invalid email or password' : result.error);",
  "setError(decodedError === 'CredentialsSignin' ? 'Invalid email or password' : decodedError);"
);

fs.writeFileSync(file, content);
console.log('Fixed page.tsx');
