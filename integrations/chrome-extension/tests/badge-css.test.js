import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';

const badgeCssPath = path.resolve(process.cwd(), 'content', 'badge.css');
const badgeCss = fs.readFileSync(badgeCssPath, 'utf8');

describe('badge tooltip layering styles', () => {
  it('keeps badge in a high stacking context when hovered', () => {
    assert.match(
      badgeCss,
      /\.encypher-badge\s*\{[\s\S]*?z-index\s*:\s*2147483646\s*;[\s\S]*?isolation\s*:\s*isolate\s*;/
    );

    assert.match(
      badgeCss,
      /\.encypher-badge:hover\s*\{[\s\S]*?z-index\s*:\s*2147483647\s*;/
    );
  });

  it('renders tooltip at maximum z-index to avoid page overlays covering it', () => {
    assert.match(
      badgeCss,
      /\.encypher-badge__tooltip\s*\{[\s\S]*?z-index\s*:\s*2147483647\s*;/
    );
  });
});
