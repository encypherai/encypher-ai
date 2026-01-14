import { expect, test } from "@playwright/test";

test("publisher demo has no blue/purple gradient buttons", async ({ page }) => {
  test.setTimeout(60_000);
  await page.goto("/publisher-demo", { waitUntil: "domcontentloaded" });

  const forbiddenSelector = [
    'button[class*="bg-gradient-to-r"]',
    'button[class*="from-blue-600"]',
    'button[class*="to-purple-600"]',
    'button[class*="from-blue-700"]',
    'button[class*="to-purple-700"]',
    'button[class*="from-blue-400"]',
    'button[class*="to-purple-400"]',
  ].join(",");

  await expect(page.locator(forbiddenSelector)).toHaveCount(0);

  // Publisher demo is a multi-section animated experience; the CTA may not be immediately
  // visible/scrollable. Click it via the DOM to ensure the modal submit button is also checked.
  await page.waitForSelector('button', { state: 'attached', timeout: 30_000 });
  await page.waitForFunction(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    return buttons.some((btn) => /request a private briefing/i.test(btn.textContent || ''));
  });
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'));
    const cta = buttons.find((btn) =>
      /request a private briefing/i.test(btn.textContent || '')
    );
    if (cta instanceof HTMLButtonElement) {
      cta.click();
    }
  });

  await expect(page.getByRole("heading", { name: /request a private demo/i })).toBeVisible();
  await expect(page.locator(forbiddenSelector)).toHaveCount(0);
});
