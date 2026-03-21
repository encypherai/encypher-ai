#!/usr/bin/env node
/**
 * Encypher Times -- Site Walkthrough Screenshot Capture
 *
 * Captures a full set of 1080p desktop and mobile screenshots for review,
 * including mock verification result states (verified, tampered).
 *
 * Usage:
 *   node scripts/capture-walkthrough.js [options]
 *
 * Options:
 *   --url <base>    Base URL (default: http://localhost:3070)
 *   --out <dir>     Output directory (default: ./walkthrough)
 *   --zip <path>    Output zip path (default: ./encypher-times-walkthrough.zip)
 *   --skip-states   Skip mock verification state screenshots
 *
 * Prerequisites:
 *   npm install puppeteer   (or use an existing puppeteer installation)
 *   Serve the static build: npx serve out -l 3070
 */

const puppeteer = require("puppeteer");
const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

// -- Config ------------------------------------------------------------------

const args = process.argv.slice(2);
function flag(name) {
  return args.includes("--" + name);
}
function opt(name, fallback) {
  const i = args.indexOf("--" + name);
  return i !== -1 && args[i + 1] ? args[i + 1] : fallback;
}

const BASE = opt("url", "http://localhost:3070");
const OUT = path.resolve(opt("out", "./walkthrough"));
const ZIP_PATH = path.resolve(
  opt("zip", "./encypher-times-walkthrough.zip")
);
const SKIP_STATES = flag("skip-states");

// -- Mock verification result HTML -------------------------------------------

const VERIFIED_HTML = `<div class="p-4 rounded border" id="mock-result" style="background:rgba(183,213,237,0.2); border-color:rgba(0,206,209,0.4);">
  <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#00CED1" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    <span style="font-size:14px; font-weight:700; color:#1B2F50;">Signature Verified</span>
  </div>
  <dl style="font-size:12px;">
    <div style="display:flex; gap:8px; margin-bottom:6px;"><dt style="color:#8a9199; width:112px; flex-shrink:0;">Publisher:</dt><dd style="color:#1a1a1a; font-weight:500;">The Encypher Times</dd></div>
    <div style="display:flex; gap:8px; margin-bottom:6px;"><dt style="color:#8a9199; width:112px; flex-shrink:0;">Signed:</dt><dd style="color:#1a1a1a;">March 20, 2026, 10:00 AM UTC</dd></div>
    <div style="display:flex; gap:8px;"><dt style="color:#8a9199; width:112px; flex-shrink:0;">Status:</dt><dd style="color:#1a1a1a;">Original -- no modifications detected</dd></div>
  </dl>
  <p style="font-size:12px; color:#6b7280; margin-top:12px; line-height:1.6;">This text carries a valid Encypher signature confirming it was published by The Encypher Times and has not been altered since signing.</p>
</div>`;

const TAMPERED_HTML = `<div class="p-4 rounded border" id="mock-result" style="background:rgba(255,251,235,0.6); border-color:rgba(252,211,77,0.6);">
  <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px;">
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
    <span style="font-size:14px; font-weight:700; color:#92400e;">Signature Invalid</span>
  </div>
  <dl style="font-size:12px;">
    <div style="display:flex; gap:8px; margin-bottom:6px;"><dt style="color:#8a9199; width:112px; flex-shrink:0;">Publisher:</dt><dd style="color:#1a1a1a; font-weight:500;">The Encypher Times</dd></div>
    <div style="display:flex; gap:8px;"><dt style="color:#8a9199; width:112px; flex-shrink:0;">Status:</dt><dd style="color:#92400e; font-weight:500;">Modified -- content has been altered since signing</dd></div>
  </dl>
  <p style="font-size:12px; color:#6b7280; margin-top:12px; line-height:1.6;">This text was originally signed but modifications have been detected. The original signature no longer matches the current content.</p>
</div>`;

const SAMPLE_TEXT =
  "The Coalition for Content Provenance and Authenticity announced Thursday that more than 300 organizations have now formally adopted its open standard for digital content verification, marking a turning point in the industry's effort to combat misinformation and establish trust in online media.";

const TAMPERED_TEXT = SAMPLE_TEXT.replace("300", "500");

// -- Helpers -----------------------------------------------------------------

async function shot(page, name, url, w, h, scrollY) {
  await page.setViewport({ width: w, height: h });
  if (url) await page.goto(url, { waitUntil: "networkidle0" });
  if (scrollY !== undefined && scrollY !== null) {
    await page.evaluate(
      (y) => window.scrollTo(0, y === 99999 ? document.body.scrollHeight : y),
      scrollY
    );
  }
  await new Promise((r) => setTimeout(r, 300));
  await page.screenshot({ path: path.join(OUT, name + ".png") });
  console.log("  " + name + ".png");
}

function setTextarea(page, text) {
  return page.evaluate((t) => {
    const textarea = document.querySelector("#verify-text");
    const setter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      "value"
    ).set;
    setter.call(textarea, t);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));
  }, text);
}

function injectResult(page, html) {
  return page.evaluate((h) => {
    const old = document.getElementById("mock-result");
    if (old) old.remove();
    document.querySelector(".space-y-4").insertAdjacentHTML("beforeend", h);
  }, html);
}

function scrollToResult(page) {
  return page.evaluate(() => {
    const el = document.getElementById("mock-result");
    if (el) el.scrollIntoView({ block: "center" });
  });
}

// -- Main --------------------------------------------------------------------

async function main() {
  fs.mkdirSync(OUT, { recursive: true });

  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();

  // Dismiss extension banner for most shots
  await page.goto(BASE, { waitUntil: "networkidle0" });
  await page.evaluate(() =>
    sessionStorage.setItem("encypher-ext-banner-dismissed", "1")
  );

  // -- Desktop (1920x1080) ---------------------------------------------------
  console.log("Desktop screenshots...");

  await shot(page, "01-homepage-hero", BASE, 1920, 1080, 0);
  await shot(page, "02-homepage-article-grid", null, 1920, 1080, 800);
  await shot(page, "03-homepage-more-sections", null, 1920, 1080, 1800);
  await shot(page, "04-homepage-footer", null, 1920, 1080, 99999);

  await shot(
    page,
    "05-article-hero",
    BASE + "/article/c2pa-coalition-milestone",
    1920,
    1080,
    0
  );
  await shot(page, "06-article-body", null, 1920, 1080, 900);

  // Signing box
  await page.evaluate(() => {
    const el = document.querySelector(".my-8.p-5");
    if (el) {
      el.scrollIntoView({ block: "start" });
      window.scrollBy(0, -80);
    }
  });
  await new Promise((r) => setTimeout(r, 200));
  await page.screenshot({
    path: path.join(OUT, "07-content-integrity-box.png"),
  });
  console.log("  07-content-integrity-box.png");

  await shot(page, "08-verify-page", BASE + "/verify", 1920, 1080, 0);

  // -- Verification states ---------------------------------------------------
  if (!SKIP_STATES) {
    console.log("Verification result states...");

    // Verified
    await setTextarea(page, SAMPLE_TEXT);
    await injectResult(page, VERIFIED_HTML);
    await new Promise((r) => setTimeout(r, 200));
    await scrollToResult(page);
    await new Promise((r) => setTimeout(r, 200));
    await page.screenshot({
      path: path.join(OUT, "09-verify-state-verified.png"),
    });
    console.log("  09-verify-state-verified.png");

    // Tampered
    await setTextarea(page, TAMPERED_TEXT);
    await injectResult(page, TAMPERED_HTML);
    await new Promise((r) => setTimeout(r, 200));
    await scrollToResult(page);
    await new Promise((r) => setTimeout(r, 200));
    await page.screenshot({
      path: path.join(OUT, "10-verify-state-tampered.png"),
    });
    console.log("  10-verify-state-tampered.png");

    // How It Works with Technical Details expanded
    await page.evaluate(() => {
      const old = document.getElementById("mock-result");
      if (old) old.remove();
      const details = document.querySelector("details");
      if (details) {
        details.open = true;
        details.scrollIntoView({ block: "start" });
        window.scrollBy(0, -40);
      }
    });
    await new Promise((r) => setTimeout(r, 200));
    await page.screenshot({
      path: path.join(OUT, "11-verify-how-it-works.png"),
    });
    console.log("  11-verify-how-it-works.png");
  }

  // -- About page ------------------------------------------------------------
  await shot(page, "12-about-page-top", BASE + "/about", 1920, 1080, 0);
  await shot(page, "13-about-page-bottom", null, 1920, 1080, 99999);

  // -- Extension banner ------------------------------------------------------
  console.log("Extension install banner...");
  await page.evaluate(() =>
    sessionStorage.removeItem("encypher-ext-banner-dismissed")
  );
  await page.goto(BASE, { waitUntil: "networkidle0" });
  await new Promise((r) => setTimeout(r, 4000));
  await page.setViewport({ width: 1920, height: 1080 });
  await page.screenshot({ path: path.join(OUT, "14-extension-banner.png") });
  console.log("  14-extension-banner.png");

  // -- Mobile (375x812) ------------------------------------------------------
  console.log("Mobile screenshots...");
  await page.evaluate(() =>
    sessionStorage.setItem("encypher-ext-banner-dismissed", "1")
  );
  await shot(page, "15-mobile-homepage", BASE, 375, 812, 0);
  await shot(
    page,
    "16-mobile-article",
    BASE + "/article/c2pa-coalition-milestone",
    375,
    812,
    0
  );
  await shot(page, "17-mobile-verify", BASE + "/verify", 375, 812, 0);

  await browser.close();

  const files = fs.readdirSync(OUT).filter((f) => f.endsWith(".png"));
  console.log("\n" + files.length + " screenshots saved to " + OUT);

  // -- Create zip ------------------------------------------------------------
  console.log("Creating zip...");
  const zipScript = path.join(OUT, "_zip.py");
  fs.writeFileSync(
    zipScript,
    [
      "import zipfile, os, sys",
      "out_dir, zip_path = sys.argv[1], sys.argv[2]",
      "zf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)",
      "for f in sorted(os.listdir(out_dir)):",
      "    full = os.path.join(out_dir, f)",
      "    if os.path.isfile(full) and not f.startswith('_'):",
      "        zf.write(full, f)",
      "zf.close()",
      "size_mb = os.path.getsize(zip_path) / (1024 * 1024)",
      "print(f'{zip_path} ({size_mb:.1f} MB)')",
    ].join("\n")
  );
  const result = execSync(
    `python3 "${zipScript}" "${OUT}" "${ZIP_PATH}"`,
    { encoding: "utf-8" }
  );
  fs.unlinkSync(zipScript);
  console.log(result.trim());
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
