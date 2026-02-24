'use strict';

const fs = require('fs');
const matter = require('gray-matter');

const filePath = process.env.NEW_FILE;
const siteUrl = 'https://encypherai.com';
const webServiceUrl = process.env.WEB_SERVICE_URL;
const secret = process.env.NEWSLETTER_BROADCAST_SECRET;

if (!filePath) {
  console.error('Error: NEW_FILE environment variable not set');
  process.exit(1);
}

if (!webServiceUrl || !secret) {
  console.error('Error: WEB_SERVICE_URL or NEWSLETTER_BROADCAST_SECRET not set');
  process.exit(1);
}

const content = fs.readFileSync(filePath, 'utf8');
const { data } = matter(content);

const filename = filePath.split('/').pop().replace(/\.md$/, '');
const title = data.title || '';
const excerpt = data.excerpt || data.description || '';
const image = data.image || data.headerImage || data.coverImage || null;
const postUrl = `${siteUrl}/blog/${filename}`;
const imageUrl = image ? `${siteUrl}${image.startsWith('/') ? '' : '/'}${image}` : null;

if (!title || !excerpt) {
  console.error('Error: Missing required frontmatter fields (title or excerpt/description)');
  console.error('Found fields:', Object.keys(data).join(', '));
  process.exit(1);
}

console.log('Broadcasting newsletter for:', title);
console.log('Post URL:', postUrl);
if (imageUrl) console.log('Image URL:', imageUrl);

const payload = {
  title,
  excerpt,
  post_url: postUrl,
  image_url: imageUrl,
  secret,
};

fetch(`${webServiceUrl}/api/v1/newsletter/broadcast`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
})
  .then(async (res) => {
    const body = await res.text();
    if (!res.ok) {
      console.error(`Broadcast failed with status ${res.status}:`, body);
      process.exit(1);
    }
    console.log('Broadcast successful:', body);
  })
  .catch((err) => {
    console.error('Request error:', err.message);
    process.exit(1);
  });
