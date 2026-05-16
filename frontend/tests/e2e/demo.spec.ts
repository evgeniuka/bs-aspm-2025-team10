import { expect, test, type Locator, type Page } from "@playwright/test";
import { loginAs } from "./helpers";

async function endActiveSessionIfPresent(page: Page) {
  const resumeCockpit = page.getByRole("link", { name: "Resume cockpit" });
  if (await resumeCockpit.isVisible()) {
    await resumeCockpit.click();
    await expect(page).toHaveURL(/\/sessions\/\d+/);
    await page.getByRole("button", { name: "End session" }).click();
    await expect(page).toHaveURL(/\/sessions\/\d+\/summary/, { timeout: 5000 });
    await page.goto("/dashboard");
    await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();
  }
}

async function replaceField(field: Locator, value: string) {
  await field.fill("");
  await field.pressSequentially(value, { delay: 2 });
  await expect(field).toHaveValue(value);
}

test("demo login opens the realtime cockpit", async ({ page }) => {
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();
  await endActiveSessionIfPresent(page);

  await expect(page.getByRole("button", { name: "Choose clients first" })).toBeDisabled();
  await page.getByLabel("Saved group preset").selectOption({ label: "Core Reset - 3" });
  await expect(page.getByText("3/10 selected")).toBeVisible();
  await expect(page.getByText("Group session")).toBeVisible();
  await expect(page.locator("#live-session").getByText("Dead Bug")).toBeVisible();
  await page.getByRole("button", { name: /Noam Cohen Present/ }).click();
  await expect(page.getByText("2/3 present")).toBeVisible();
  await page.getByRole("button", { name: "Add Maya Levi to session" }).click();
  await expect(page.getByText("Substitute: Maya Levi")).toBeVisible();
  await page.getByRole("button", { name: "Clear" }).click();
  await page.getByRole("button", { name: "Add Maya Levi to session" }).click();
  await expect(page.getByText("1/10 selected")).toBeVisible();
  await page.getByLabel("Workout variant for Maya Levi").selectOption({ label: "Core Stability" });
  await expect(page.getByLabel("Workout variant for Maya Levi").locator("option:checked")).toHaveText("Core Stability");
  const startSoloSession = page.waitForResponse((response) => response.url().includes("/api/v1/sessions") && response.request().method() === "POST" && response.ok());
  await page.getByRole("button", { name: /Start solo training/ }).click();
  await startSoloSession;

  await expect(page).toHaveURL(/\/sessions\/\d+/, { timeout: 10000 });
  await expect(page.getByText("Live cockpit")).toBeVisible();
  await expect(page.getByTestId("connection-state")).toHaveText("live", { timeout: 10000 });
  await expect(page.locator("header").getByText("1 client")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Maya Levi" })).toBeVisible();

  await page.getByLabel("Actual reps for Maya Levi").fill("9");
  await page.getByLabel("Actual weight for Maya Levi").fill("22.5");
  await page.getByRole("button", { name: "Complete set" }).first().click();
  await expect(page.getByText("202.5kg")).toBeVisible();
  await page.getByRole("button", { name: "Undo last set" }).click();
  await expect(page.getByText("0/12")).toBeVisible();
  await page.getByLabel("Actual reps for Maya Levi").fill("9");
  await page.getByLabel("Actual weight for Maya Levi").fill("22.5");
  await page.getByRole("button", { name: "Complete set" }).first().click();
  await page.getByRole("button", { name: "End session" }).click();
  await expect(page.getByText("Session completed")).toBeVisible();
  await expect(page).toHaveURL(/\/sessions\/\d+\/summary/, { timeout: 5000 });
  await expect(page.getByText("Session summary")).toBeVisible();
  await expect(page.getByText("Set 1: 9 reps x 22.5kg = 202.5kg")).toBeVisible();

  const mayaSummary = page.locator('[data-testid^="session-summary-card-"]').filter({ has: page.getByRole("link", { name: "Maya Levi" }) });
  await page.getByLabel("Coach notes for Maya Levi").fill("Strong pacing. Keep hinge pattern stable.");
  await page.getByLabel("Next focus for Maya Levi").fill("Hinge control");
  const saveSummary = page.waitForResponse((response) => response.url().includes("/summary") && response.request().method() === "PATCH" && response.ok());
  await mayaSummary.getByRole("button", { name: "Save" }).click();
  await saveSummary;

  await page.getByRole("link", { name: "Maya Levi" }).click();
  await expect(page).toHaveURL(/\/clients\/\d+/, { timeout: 5000 });
  await expect(page.getByText("Client profile")).toBeVisible();
  await expect(page.getByText("Workout history")).toBeVisible();
});

test("trainer starts a saved training group", async ({ page }) => {
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();
  await endActiveSessionIfPresent(page);

  await expect(page.getByRole("heading", { name: "Saved groups" })).toBeVisible();
  await page.getByRole("button", { name: /Strength Crew/ }).click();
  await expect(page.getByText("Selected group")).toBeVisible();
  await expect(page.locator("#groups").getByText("Maya Levi")).toBeVisible();
  await expect(page.locator("#groups").getByText("Daniel Stein")).toBeVisible();
  await expect(page.locator("#groups").getByText("Amir Haddad")).toBeVisible();

  await page.getByRole("button", { name: "Prepare Strength Crew" }).click();
  await expect(page.getByText("3/10 selected")).toBeVisible();
  await expect(page.getByText("3/3 present")).toBeVisible();
  await expect(page.getByText("Group session")).toBeVisible();

  const startGroupSession = page.waitForResponse(
    (response) => response.url().includes("/api/v1/groups/") && response.request().method() === "POST" && response.ok()
  );
  await page.getByRole("button", { name: /Start 3-client training/ }).click();
  await startGroupSession;
  await expect(page).toHaveURL(/\/sessions\/\d+/, { timeout: 10000 });
  await expect(page.getByText("Live cockpit")).toBeVisible();
  await expect(page.getByTestId("connection-state")).toHaveText("live", { timeout: 10000 });
  await expect(page.locator("header").getByText("3 clients")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Maya Levi" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Daniel Stein" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Amir Haddad" })).toBeVisible();

  await page.getByRole("button", { name: "End session" }).click();
  await expect(page).toHaveURL(/\/sessions\/\d+\/summary/, { timeout: 5000 });
});

test("trainer can prepare a 10-person cockpit from a saved group", async ({ page }) => {
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();
  await endActiveSessionIfPresent(page);

  await page.getByLabel("Saved group preset").selectOption({ label: "Engine Builders - 10" });
  await expect(page.getByText("10/10 selected")).toBeVisible();
  await expect(page.getByText("10/10 present")).toBeVisible();

  const startLargeGroup = page.waitForResponse(
    (response) => response.url().includes("/api/v1/groups/") && response.request().method() === "POST" && response.ok()
  );
  await page.getByRole("button", { name: /Start 10-client training/ }).click();
  await startLargeGroup;

  await expect(page).toHaveURL(/\/sessions\/\d+/, { timeout: 10000 });
  await expect(page.getByText("Live cockpit")).toBeVisible();
  await expect(page.getByTestId("connection-state")).toHaveText("live", { timeout: 10000 });
  await expect(page.locator("header").getByText("10 clients")).toBeVisible();
  await expect(page.getByTestId("cockpit-card")).toHaveCount(10);

  await page.getByRole("button", { name: "End session" }).click();
  await expect(page).toHaveURL(/\/sessions\/\d+\/summary/, { timeout: 5000 });
});

test("trainer manages the active client roster", async ({ page }) => {
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();

  await page.getByRole("link", { name: "Clients" }).click();
  await expect(page).toHaveURL(/\/clients$/);
  await expect(page.getByRole("heading", { name: "Clients" })).toBeVisible();
  await page.getByRole("button", { name: "New client" }).click();

  const clientName = `Portfolio Client ${Date.now()}`;
  await page.getByLabel("Age").fill("33");
  await page.getByLabel("Fitness level").selectOption("Intermediate");
  await replaceField(page.getByLabel("Training goals"), "Build a consistent strength base with two focused weekly sessions.");
  await replaceField(page.getByLabel("Name"), clientName);
  await expect(page.getByRole("button", { name: "Create client" })).toBeEnabled();
  await page.getByRole("button", { name: "Create client" }).click();
  await expect(page.getByText(clientName)).toBeVisible();

  await page.locator("article").filter({ hasText: clientName }).getByRole("button", { name: "Edit" }).click();
  await replaceField(page.getByLabel("Name"), `${clientName} Updated`);
  await page.getByRole("button", { name: "Save client" }).click();
  await expect(page.getByText(`${clientName} Updated`)).toBeVisible();

  page.once("dialog", (dialog) => dialog.accept());
  await page.locator("article").filter({ hasText: `${clientName} Updated` }).getByRole("button", { name: `Archive ${clientName} Updated` }).click();
  await expect(page.getByText(`${clientName} Updated`)).toHaveCount(0);
});

test("client demo opens the client training hub", async ({ page }) => {
  await loginAs(page, "client");
  await expect(page.getByRole("heading", { name: "Training Hub" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Maya Levi" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Today check-in" })).toBeVisible();
  await expect(page.getByText("Your programs")).toBeVisible();
  await expect(page.getByText("Workout history")).toBeVisible();

  await page.getByRole("button", { name: "Energy 2" }).click();
  await page.getByRole("button", { name: "Sleep 3" }).click();
  await page.getByLabel("Pain or limitation notes").fill("Right knee feels sensitive on stairs.");
  await page.getByLabel("Training goal for today").fill("Keep lower-body work conservative.");
  const saveCheckIn = page.waitForResponse((response) => response.url().includes("/trainee/check-in/today") && response.request().method() === "PUT" && response.ok());
  await page.getByRole("button", { name: "Save check-in" }).click();
  await saveCheckIn;
  await expect(page.getByText("Check-in saved")).toBeVisible();

  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(page).toHaveURL(/\/login$/);
  await loginAs(page);
  await expect(page.getByRole("heading", { name: "Trainer dashboard" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Add Maya Levi to session" })).toBeVisible();
  await expect(page.getByText("Intermediate - low energy, pain noted")).toBeVisible();
});
