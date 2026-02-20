import { expect, test } from "@playwright/test";

test("wordpress pricing shows only Free + Enterprise with add-ons", async ({ page }) => {
  await page.goto("/tools/wordpress");

  const pricingSection = page.locator("section").filter({ hasText: "Simple, Transparent Pricing" });
  const planTitle = pricingSection.locator("[data-slot='card-title']");

  await expect(page.getByRole("heading", { name: "Simple, Transparent Pricing" })).toBeVisible();
  await expect(planTitle.filter({ hasText: "Free" })).toBeVisible();
  await expect(planTitle.filter({ hasText: "Enterprise" })).toBeVisible();

  await expect(pricingSection.getByText("Starter", { exact: true })).toHaveCount(0);
  await expect(pricingSection.getByText("Professional", { exact: true })).toHaveCount(0);

  await expect(pricingSection.getByText("Minor Add-ons", { exact: true })).toBeVisible();
  await expect(pricingSection.getByText("Whitelabel verification", { exact: false })).toBeVisible();
});
