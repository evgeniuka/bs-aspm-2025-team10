import { expect, test } from "@playwright/test";
import { loginAs } from "./helpers";

test("trainer edits, reorders, saves, and reloads a program", async ({ page }) => {
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();

  const clientsResponse = await page.request.get("/api/v1/clients");
  expect(clientsResponse.ok()).toBeTruthy();
  const clients = (await clientsResponse.json()) as Array<{ id: number; name: string }>;
  const maya = clients.find((client) => client.name === "Maya Levi") ?? clients[0];
  await page.goto(`/clients/${maya.id}`);
  await expect(page.getByText("Client profile")).toBeVisible();
  await page.locator('a[href^="/programs/"]').first().click();

  await expect(page.getByText("Today's plan")).toBeVisible();
  await expect(page.getByRole("button", { name: "Start session" })).toBeVisible();
  await page.getByRole("button", { name: "Edit plan" }).click();
  await expect(page.getByText("Edit plan")).toBeVisible();
  await expect(page.getByRole("button", { name: "Save program" })).toBeDisabled();

  const updatedName = `Strength Block ${Date.now()}`;
  await page.getByLabel("Program name").fill(updatedName);
  await page.getByLabel("Coach notes").fill("Progression target: keep two reps in reserve and watch hinge control.");
  await page.getByRole("button", { name: /Move .* down/ }).first().click();
  await page.getByLabel(/Coach cue for /).first().fill("Brace before the first rep; slow eccentric.");

  const saveProgram = page.waitForResponse((response) => response.url().includes("/programs/") && response.request().method() === "PATCH" && response.ok());
  await page.getByRole("button", { name: "Save program" }).click();
  await saveProgram;
  await expect(page.getByText("Program saved.")).toBeVisible();

  await page.reload();
  await expect(page.getByRole("heading", { name: updatedName })).toBeVisible();
  await expect(page.getByText("Today's plan")).toBeVisible();
  await page.getByRole("button", { name: "Edit plan" }).click();
  await expect(page.getByLabel("Coach notes")).toHaveValue("Progression target: keep two reps in reserve and watch hinge control.");
  await expect(page.getByLabel(/Coach cue for /).first()).toHaveValue("Brace before the first rep; slow eccentric.");
});
