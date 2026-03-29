#!/usr/bin/env node
/**
 * Build script for Encypher Verify Chrome Extension.
 *
 * Produces a production-ready .zip in dist/ that can be uploaded directly
 * to the Chrome Web Store.  The zip contains only the files Chrome needs —
 * no tests, no node_modules, no dev tooling.
 *
 * Usage:
 *   node scripts/build.js            # production build (no localhost)
 *   node scripts/build.js --dev      # dev build (keeps localhost permissions)
 *
 * Output: dist/encypher-verify-v<version>.zip
 */

import fs from 'fs';
import path from 'path';
import zlib from 'zlib';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const DIST = path.join(ROOT, 'dist');

const isDev = process.argv.includes('--dev');

// Files and directories to include in the zip (relative to ROOT)
const INCLUDE = [
  'manifest.json',
  'background/',
  'content/',
  'icons/',
  'options/',
  'popup/',
];

// Patterns to always exclude (even if inside an INCLUDE dir)
const EXCLUDE_PATTERNS = [
  /node_modules/,
  /\.git/,
  /tests?\//,
  /scripts\//,
  /store-assets\//,
  /dist\//,
  /\.eslintrc/,
  /package(-lock)?\.json/,
  /README\.md$/,
  /PRIVACY\.md$/,
  /SECURITY_CHECKLIST\.md$/,
  /STORE_LISTING\.md$/,
  /USER_JOURNEYS\.md$/,
  /\.DS_Store/,
  /Thumbs\.db/,
];

function shouldExclude(relPath) {
  return EXCLUDE_PATTERNS.some((re) => re.test(relPath));
}

function collectFiles(dir, base = dir) {
  const results = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    const rel = path.relative(base, full);
    if (shouldExclude(rel)) continue;
    if (entry.isDirectory()) {
      results.push(...collectFiles(full, base));
    } else {
      results.push({ full, rel });
    }
  }
  return results;
}

function buildManifest() {
  const raw = JSON.parse(fs.readFileSync(path.join(ROOT, 'manifest.json'), 'utf8'));

  if (!isDev) {
    // Strip localhost / 127.0.0.1 from host_permissions
    raw.host_permissions = (raw.host_permissions || []).filter(
      (p) => !p.includes('localhost') && !p.includes('127.0.0.1')
    );

    // Strip localhost / 127.0.0.1 from externally_connectable.matches
    if (raw.externally_connectable?.matches) {
      raw.externally_connectable.matches = raw.externally_connectable.matches.filter(
        (p) => !p.includes('localhost') && !p.includes('127.0.0.1')
      );
    }

    // Strip dev-only commands from production builds
    if (raw.commands) {
      for (const [key, cmd] of Object.entries(raw.commands)) {
        if (cmd.description && /\bdev\b/i.test(cmd.description)) {
          delete raw.commands[key];
        }
      }
      if (Object.keys(raw.commands).length === 0) delete raw.commands;
    }
  }

  return JSON.stringify(raw, null, 2);
}

async function build() {
  const manifest = JSON.parse(fs.readFileSync(path.join(ROOT, 'manifest.json'), 'utf8'));
  const version = manifest.version;
  const mode = isDev ? 'dev' : 'prod';
  const zipName = `encypher-verify-v${version}${isDev ? '-dev' : ''}.zip`;
  const zipPath = path.join(DIST, zipName);

  console.log(`\nBuilding Encypher Verify v${version} (${mode})...\n`);

  // Ensure dist/ exists and is clean for this build
  fs.mkdirSync(DIST, { recursive: true });
  if (fs.existsSync(zipPath)) fs.unlinkSync(zipPath);

  // Collect all files to include
  const files = [];
  for (const entry of INCLUDE) {
    const full = path.join(ROOT, entry);
    if (!fs.existsSync(full)) {
      console.warn(`  WARN: ${entry} not found, skipping`);
      continue;
    }
    const stat = fs.statSync(full);
    if (stat.isDirectory()) {
      files.push(...collectFiles(full, ROOT));
    } else {
      const rel = path.relative(ROOT, full);
      if (!shouldExclude(rel)) files.push({ full, rel });
    }
  }

  // Build zip using pure Node.js (no system zip required)
  const chunks = [];

  function uint16LE(n) {
    const b = Buffer.alloc(2);
    b.writeUInt16LE(n, 0);
    return b;
  }
  function uint32LE(n) {
    const b = Buffer.alloc(4);
    b.writeUInt32LE(n >>> 0, 0);
    return b;
  }

  function crc32(buf) {
    const table = crc32.table || (crc32.table = (() => {
      const t = new Uint32Array(256);
      for (let i = 0; i < 256; i++) {
        let c = i;
        for (let j = 0; j < 8; j++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
        t[i] = c;
      }
      return t;
    })());
    let crc = 0xFFFFFFFF;
    for (let i = 0; i < buf.length; i++) crc = table[(crc ^ buf[i]) & 0xFF] ^ (crc >>> 8);
    return (crc ^ 0xFFFFFFFF) >>> 0;
  }

  const centralDir = [];
  let offset = 0;

  for (const { full, rel } of files) {
    const rawContent = rel === 'manifest.json'
      ? Buffer.from(buildManifest(), 'utf8')
      : fs.readFileSync(full);

    const compressed = zlib.deflateRawSync(rawContent, { level: 6 });
    const useCompressed = compressed.length < rawContent.length;
    const fileData = useCompressed ? compressed : rawContent;
    const crc = crc32(rawContent);
    const nameBytes = Buffer.from(rel.replace(/\\/g, '/'), 'utf8');
    const now = new Date();
    const dosDate = ((now.getFullYear() - 1980) << 9) | ((now.getMonth() + 1) << 5) | now.getDate();
    const dosTime = (now.getHours() << 11) | (now.getMinutes() << 5) | Math.floor(now.getSeconds() / 2);

    const localHeader = Buffer.concat([
      Buffer.from([0x50, 0x4B, 0x03, 0x04]),
      uint16LE(20),
      uint16LE(0),
      uint16LE(useCompressed ? 8 : 0),
      uint16LE(dosTime),
      uint16LE(dosDate),
      uint32LE(crc),
      uint32LE(fileData.length),
      uint32LE(rawContent.length),
      uint16LE(nameBytes.length),
      uint16LE(0),
      nameBytes,
    ]);

    centralDir.push({ nameBytes, crc, fileData, rawContent, dosTime, dosDate, offset, useCompressed });
    chunks.push(localHeader, fileData);
    offset += localHeader.length + fileData.length;
  }

  const centralDirStart = offset;
  for (const e of centralDir) {
    const cdEntry = Buffer.concat([
      Buffer.from([0x50, 0x4B, 0x01, 0x02]),
      uint16LE(20),
      uint16LE(20),
      uint16LE(0),
      uint16LE(e.useCompressed ? 8 : 0),
      uint16LE(e.dosTime),
      uint16LE(e.dosDate),
      uint32LE(e.crc),
      uint32LE(e.fileData.length),
      uint32LE(e.rawContent.length),
      uint16LE(e.nameBytes.length),
      uint16LE(0),
      uint16LE(0),
      uint16LE(0),
      uint16LE(0),
      uint32LE(0),
      uint32LE(e.offset),
      e.nameBytes,
    ]);
    chunks.push(cdEntry);
    offset += cdEntry.length;
  }

  const centralDirSize = offset - centralDirStart;
  const eocd = Buffer.concat([
    Buffer.from([0x50, 0x4B, 0x05, 0x06]),
    uint16LE(0),
    uint16LE(0),
    uint16LE(centralDir.length),
    uint16LE(centralDir.length),
    uint32LE(centralDirSize),
    uint32LE(centralDirStart),
    uint16LE(0),
  ]);
  chunks.push(eocd);

  fs.writeFileSync(zipPath, Buffer.concat(chunks));

  // Report
  const zipStat = fs.statSync(zipPath);
  const kb = (zipStat.size / 1024).toFixed(1);
  console.log(`  ✓ ${files.length} files packaged`);
  if (!isDev) {
    console.log('  ✓ localhost permissions stripped from manifest');
  }
  console.log(`  ✓ Output: dist/${zipName} (${kb} KB)\n`);

  if (!isDev) {
    console.log('Next steps:');
    console.log('  1. Upload dist/' + zipName + ' to https://chrome.google.com/webstore/devconsole');
    console.log('  2. Fill in store listing details (see STORE_LISTING.md)');
    console.log('  3. Set privacy policy URL: https://encypher.com/privacy');
    console.log('  4. Upload store-assets/ screenshots and promo images');
    console.log('  5. Submit for review\n');
  }
}

build().catch((err) => {
  console.error('Build failed:', err.message);
  process.exit(1);
});
