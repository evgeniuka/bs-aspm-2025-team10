import { expect, type Page } from "@playwright/test";

const DEMO_EMAIL = {
  trainer: "trainer@fitcoach.dev",
  client: "maya@fitcoach.dev"
} as const;

export async function loginAs(page: Page, role: keyof typeof DEMO_EMAIL = "trainer") {
  await page.context().clearCookies();
  await page.goto("/login");
  await page.getByRole("button", { name: role === "client" ? "Client demo" : "Trainer demo" }).click();
  await expect(page.getByLabel("Email")).toHaveValue(DEMO_EMAIL[role]);

  const loginResponse = page.waitForResponse(
    (response) => response.url().includes("/api/v1/auth/login") && response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Sign in to demo" }).click();
  expect((await loginResponse).ok()).toBeTruthy();
  await expect(page).toHaveURL(role === "client" ? /\/client$/ : /\/dashboard$/, { timeout: 12000 });
}
