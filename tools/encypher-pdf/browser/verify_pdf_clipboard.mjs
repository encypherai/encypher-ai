import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import puppeteer from 'puppeteer';

function dumpCodepoints(text) {
  return Array.from(text).map((char) => ({
    char,
    codepoint: `U+${char.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`,
  }));
}

async function main() {
  const [, , pdfPathArg, expectedPathArg, artifactDirArg] = process.argv;
  if (!pdfPathArg || !expectedPathArg) {
    console.error('Usage: node verify_pdf_clipboard.mjs <pdf-path> <expected-text-path> [artifact-dir]');
    process.exit(1);
  }

  const pdfPath = path.resolve(pdfPathArg);
  const expectedPath = path.resolve(expectedPathArg);
  const artifactDir = path.resolve(artifactDirArg || path.dirname(pdfPath));
  await fs.mkdir(artifactDir, { recursive: true });

  const viewerPath = path.resolve(path.dirname(new URL(import.meta.url).pathname), 'viewer.html');
  const viewerUrl = new URL(pathToFileURL(viewerPath));
  viewerUrl.searchParams.set('pdf', pathToFileURL(pdfPath).href);

  const expectedText = await fs.readFile(expectedPath, 'utf8');

  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.goto(viewerUrl.href, { waitUntil: 'networkidle2' });
  await page.waitForFunction(() => window.__encypherPdfState !== undefined);

  const state = await page.evaluate(() => window.__encypherPdfState);
  const screenshotPath = path.join(artifactDir, `${path.basename(pdfPath, '.pdf')}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });

  if (!state.ok) {
    await browser.close();
    console.error(JSON.stringify({ ok: false, error: state.error, screenshotPath }, null, 2));
    process.exit(1);
  }

  const result = {
    ok: state.text === expectedText,
    pdfPath,
    expectedLength: expectedText.length,
    actualLength: state.text.length,
    screenshotPath,
    expectedCodepoints: dumpCodepoints(expectedText),
    actualCodepoints: dumpCodepoints(state.text),
  };

  const reportPath = path.join(artifactDir, `${path.basename(pdfPath, '.pdf')}.verification.json`);
  await fs.writeFile(reportPath, `${JSON.stringify(result, null, 2)}\n`, 'utf8');
  await browser.close();

  if (!result.ok) {
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
