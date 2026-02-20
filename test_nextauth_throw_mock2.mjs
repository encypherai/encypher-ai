import { readFileSync, writeFileSync } from 'fs';

const path = 'apps/dashboard/src/app/api/auth/[...nextauth]/route.ts';
let code = readFileSync(path, 'utf8');

// Undo the first test
code = code.replace(
  'async authorize(credentials) {\n        throw new Error("MFA_REQUIRED:test-token");',
  'async authorize(credentials) {'
);

writeFileSync(path, code);
