import { readFileSync, writeFileSync } from 'fs';

const path = 'apps/dashboard/src/app/api/auth/[...nextauth]/route.ts';
let code = readFileSync(path, 'utf8');

// Insert a throw right at the start of authorize
code = code.replace(
  'async authorize(credentials) {',
  'async authorize(credentials) {\n        throw new Error("MFA_REQUIRED:test-token");'
);

writeFileSync(path, code);
