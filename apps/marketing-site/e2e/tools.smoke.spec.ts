import { expect, test } from "@playwright/test";

test("tools page loads", async ({ page, request }) => {
  const legacyDecode = await request.post("/api/tools/decode", {
    data: { encoded_text: "test" },
  });
  expect(legacyDecode.status()).toBe(410);

  await page.goto("/tools");

  await expect(page.getByRole("heading", { name: "Encypher Tools" })).toBeVisible();

  await page.getByRole("link", { name: "Sign/Verify" }).click();
  await expect(page).toHaveURL(/\/tools\/sign-verify/);

  await expect(page.getByRole("heading", { name: "Encypher Sign/Verify Tool" })).toBeVisible();
  await expect(page.getByRole("button", { name: /Switch to Verify/i })).toBeVisible();

  await page.getByRole("button", { name: /Switch to/i }).click();
  await expect(page.getByRole("button", { name: /Switch to Sign/i })).toBeVisible();
});
