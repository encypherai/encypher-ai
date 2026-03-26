#!/usr/bin/env node
/**
 * C2PA Conformance: Adobe Content Credentials Verify Screenshots
 *
 * Uploads each signed file to verify.contentauthenticity.org and captures
 * screenshots of the verification results.
 *
 * Usage:
 *   npx puppeteer browsers install chrome
 *   node enterprise_api/tests/c2pa_conformance/adobe_verify.mjs
 *
 * Output:
 *   docs/c2pa/conformance/evidence/screenshots/{format}_adobe_verify.png
 */

import { readdir, stat } from "fs/promises";
import { join, resolve, dirname, basename, extname } from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SIGNED_DIR = join(__dirname, "signed");
const REPO_ROOT = resolve(__dirname, "..", "..", "..");
const SCREENSHOTS_DIR = join(
  REPO_ROOT,
  "docs",
  "c2pa",
  "conformance",
  "evidence",
  "screenshots"
);
const VERIFY_URL = "https://verify.contentauthenticity.org/inspect";

// Map extension to format name for screenshot filenames
const EXT_TO_NAME = {
  ".jpg": "jpeg",
  ".png": "png",
  ".webp": "webp",
  ".tiff": "tiff",
  ".avif": "avif",
  ".heic": "heic",
  ".heif": "heif",
  ".svg": "svg",
  ".dng": "dng",
  ".mp4": "mp4",
  ".mov": "mov",
  ".avi": "avi",
  ".wav": "wav",
  ".mp3": "mp3",
  ".m4a": "m4a",
  ".pdf": "pdf",
};

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  // Dynamic import of puppeteer
  const puppeteer = await import("puppeteer");

  console.log("Launching browser...");
  const browser = await puppeteer.default.launch({
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
    ],
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  // Get list of signed files
  const files = (await readdir(SIGNED_DIR))
    .filter((f) => f.startsWith("signed_test"))
    .sort();

  console.log(`Found ${files.length} signed files to verify`);
  const results = [];

  for (const file of files) {
    const ext = extname(file);
    const formatName = EXT_TO_NAME[ext] || ext.slice(1);
    const filePath = join(SIGNED_DIR, file);
    const screenshotPath = join(
      SCREENSHOTS_DIR,
      `${formatName}_adobe_verify.png`
    );

    console.log(`\n--- ${formatName.toUpperCase()} (${file}) ---`);

    try {
      // Navigate to verify page (fresh for each file)
      console.log("  Navigating to Adobe verify...");
      await page.goto(VERIFY_URL, {
        waitUntil: "networkidle2",
        timeout: 30000,
      });

      // Wait for the page to fully load
      await sleep(2000);

      // Find the file input element
      // The Adobe verify site uses an input[type=file] for uploads
      const fileInput = await page.$('input[type="file"]');
      if (!fileInput) {
        // Try to find hidden file input via different selectors
        const inputs = await page.$$("input");
        let found = false;
        for (const input of inputs) {
          const type = await page.evaluate(
            (el) => el.getAttribute("type"),
            input
          );
          if (type === "file") {
            await input.uploadFile(filePath);
            found = true;
            break;
          }
        }
        if (!found) {
          console.log("  WARNING: No file input found, trying drag-drop area");
          // Try clicking the upload area to trigger file dialog
          const uploadArea = await page.$('[class*="upload"], [class*="drop"]');
          if (uploadArea) {
            // Set file via evaluate on any file input that might appear
            await page.evaluate(() => {
              const input = document.createElement("input");
              input.type = "file";
              document.body.appendChild(input);
              input.id = "puppet-file-input";
            });
            const puppetInput = await page.$("#puppet-file-input");
            if (puppetInput) {
              await puppetInput.uploadFile(filePath);
            }
          }
          results.push({
            format: formatName,
            status: "skip",
            reason: "no file input",
          });
          continue;
        }
      } else {
        console.log("  Uploading file...");
        await fileInput.uploadFile(filePath);
      }

      // Wait for verification results to appear
      console.log("  Waiting for verification results...");
      await sleep(5000);

      // Wait for results panel -- look for common result indicators
      try {
        await page.waitForSelector(
          '[class*="result"], [class*="manifest"], [class*="credential"], [data-testid]',
          { timeout: 15000 }
        );
      } catch {
        console.log("  Results panel selector not found, taking screenshot anyway");
      }

      // Additional wait for animations/rendering
      await sleep(2000);

      // Take full page screenshot
      console.log(`  Saving screenshot: ${screenshotPath}`);
      await page.screenshot({
        path: screenshotPath,
        fullPage: true,
      });

      results.push({ format: formatName, status: "ok", screenshot: screenshotPath });
      console.log(`  Done: ${formatName}`);
    } catch (err) {
      console.error(`  ERROR: ${err.message}`);
      // Take error screenshot
      try {
        await page.screenshot({
          path: screenshotPath,
          fullPage: true,
        });
        results.push({
          format: formatName,
          status: "error",
          error: err.message,
          screenshot: screenshotPath,
        });
      } catch {
        results.push({
          format: formatName,
          status: "error",
          error: err.message,
        });
      }
    }

    // Brief pause between uploads to avoid rate limiting
    await sleep(2000);
  }

  await browser.close();

  // Print summary
  console.log("\n" + "=".repeat(60));
  console.log("ADOBE VERIFY SCREENSHOT SUMMARY");
  console.log("=".repeat(60));
  for (const r of results) {
    const status = r.status === "ok" ? "OK" : r.status.toUpperCase();
    console.log(`  ${r.format.toUpperCase().padEnd(8)} ${status}`);
  }
  console.log(
    `\nTotal: ${results.length}, OK: ${results.filter((r) => r.status === "ok").length}`
  );
  console.log(`Screenshots: ${SCREENSHOTS_DIR}`);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
