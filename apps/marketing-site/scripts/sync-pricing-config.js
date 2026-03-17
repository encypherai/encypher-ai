#!/usr/bin/env node
/**
 * Sync pricing-config from canonical source to local directory.
 *
 * This script copies the shared pricing configuration from packages/pricing-config
 * to the local src/lib/pricing-config directory for Railway deployment compatibility.
 *
 * Run automatically before build via package.json prebuild script.
 */

const fs = require('fs');
const path = require('path');

const SOURCE_DIR = path.resolve(__dirname, '../../../packages/pricing-config/src');
const TARGET_DIR = path.resolve(__dirname, '../src/lib/pricing-config');

// Files to sync
const FILES = ['types.ts', 'tiers.ts', 'coalition.ts', 'index.ts'];

// Header to prepend to copied files
const AUTO_GENERATED_HEADER = `/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 *
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 *
 * To update: edit the source file, then run npm run build.
 */

`;

function syncPricingConfig() {
  console.log('[sync-pricing-config] Syncing pricing config...');

  // Check if source exists (may not exist in Railway isolated build)
  if (!fs.existsSync(SOURCE_DIR)) {
    console.log('[sync-pricing-config] Source not found (isolated build), using existing local copy');

    // Verify local copy exists
    if (!fs.existsSync(TARGET_DIR)) {
      console.error('[sync-pricing-config] ERROR: No local pricing-config found!');
      process.exit(1);
    }

    const missingFiles = FILES.filter(f => !fs.existsSync(path.join(TARGET_DIR, f)));
    if (missingFiles.length > 0) {
      console.error(`[sync-pricing-config] ERROR: Missing files: ${missingFiles.join(', ')}`);
      process.exit(1);
    }

    console.log('[sync-pricing-config] Local copy verified ✓');
    return;
  }

  // Ensure target directory exists
  if (!fs.existsSync(TARGET_DIR)) {
    fs.mkdirSync(TARGET_DIR, { recursive: true });
    console.log(`[sync-pricing-config] Created ${TARGET_DIR}`);
  }

  // Copy each file
  for (const file of FILES) {
    const sourcePath = path.join(SOURCE_DIR, file);
    const targetPath = path.join(TARGET_DIR, file);

    if (!fs.existsSync(sourcePath)) {
      console.error(`[sync-pricing-config] ERROR: Source file not found: ${sourcePath}`);
      process.exit(1);
    }

    const content = fs.readFileSync(sourcePath, 'utf8');
    const contentWithHeader = AUTO_GENERATED_HEADER + content;
    fs.writeFileSync(targetPath, contentWithHeader, 'utf8');
    console.log(`[sync-pricing-config] Copied ${file}`);
  }

  console.log('[sync-pricing-config] Sync complete ✓');
}

syncPricingConfig();
