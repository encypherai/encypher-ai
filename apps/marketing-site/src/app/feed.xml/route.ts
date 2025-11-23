import { NextResponse } from 'next/server';
import { getAllPosts } from '@/lib/blog';
import { getSiteUrl } from '@/lib/env';

export const dynamic = 'force-static';

export async function GET() {
  const site = getSiteUrl();
  const posts = await Promise.resolve(getAllPosts());
  const items = posts
    .map((post) => {
      const link = `${site}/blog/${post.slug}`;
      const pubDate = post.date ? new Date(post.date).toUTCString() : new Date().toUTCString();
      const description = post.excerpt || '';
      return `
  <item>
    <title><![CDATA[${post.title}]]></title>
    <link>${link}</link>
    <guid isPermaLink="true">${link}</guid>
    <pubDate>${pubDate}</pubDate>
    <description><![CDATA[${description}]]></description>
  </item>`;
    })
    .join('');

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Encypher Blog</title>
  <link>${site}/blog</link>
  <description>From the authors of the C2PA text standard: infrastructure for AI content authentication and licensing.</description>
  <language>en-us</language>
  ${items}
</channel>
</rss>`;

  return new NextResponse(rss, {
    status: 200,
    headers: {
      'Content-Type': 'application/xml; charset=utf-8',
      'Cache-Control': 'public, s-maxage=3600, stale-while-revalidate=86400',
    },
  });
}
