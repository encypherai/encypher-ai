import fs from 'fs';
// We just need to check what version of NextAuth we are running.
const packageJson = JSON.parse(fs.readFileSync('./apps/dashboard/package.json', 'utf8'));
console.log('NextAuth version:', packageJson.dependencies['next-auth']);
