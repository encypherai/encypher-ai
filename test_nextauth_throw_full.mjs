import fs from 'fs';
const text = fs.readFileSync('apps/dashboard/node_modules/next-auth/core/routes/callback.js', 'utf8');
const lines = text.split('\n');
const startIndex = lines.findIndex(l => l.includes('user = await provider.authorize'));
for (let i = startIndex - 5; i < startIndex + 40; i++) {
  console.log(i + 1, lines[i]);
}
