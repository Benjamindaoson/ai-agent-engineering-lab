import { expect, test } from "@playwright/test";

async function expectNoBackendTerms(page: import("@playwright/test").Page) {
  for (const term of [
    "Agent Command Queue",
    "Review Gate",
    "Evidence Store",
    "Skill Passport",
    "Sandbox",
    "Quality Gate",
    "Project Lab",
    "MicroExerciseCoach",
    "Agent Tutor",
    "Agent Trace",
    "AI Dependency Score",
    "Rubric",
    "submitted",
    "unlisted",
    "rag_retrieval_quality",
    "engineering_quality",
    "missing_eval",
  ]) {
    await expect(page.getByText(term)).toHaveCount(0);
  }
}

test("diagnosis-driven learner mission control", async ({ page }) => {
  await page.goto("/coach");
  await expect(page.getByRole("main", { name: "个人训练中枢" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "你的专属 AI Agent 训练中枢" })).toBeVisible();
  await expect(page.getByText("诊断分流完成", { exact: true })).toBeVisible();
  await expect(page.getByText(/Track/)).toBeVisible();

  await expect(page.getByText("多线程训练", { exact: true })).toBeVisible();
  await expect(page.locator(".thread-link")).toHaveCount(6);
  await expect(page.getByText("课程窗口", { exact: true })).toBeVisible();
  await expect(page.getByText("练习窗口", { exact: true })).toBeVisible();
  await expect(page.getByText("项目工作室", { exact: true })).toBeVisible();
  await expect(page.getByText("系统背后的教练组", { exact: true })).toBeVisible();
  await expect(page.locator(".agent-role")).toHaveCount(8);
  await expectNoBackendTerms(page);

  const courseHref = await page.locator('a[href^="/learn/"]').first().getAttribute("href");
  expect(courseHref).toMatch(/^\/learn\//);
  await page.goto(courseHref!);
  await expect(page.locator(".micro-lesson")).toBeVisible();
  await expectNoBackendTerms(page);

  await page.goto("/coach");
  const projectHref = await page.locator('a[href^="/lab/"]').first().getAttribute("href");
  expect(projectHref).toMatch(/^\/lab\//);
  await page.goto(projectHref!);
  await expect(page.locator(".project-canvas")).toBeVisible();
  await expect(page.locator('form input[name="github_repo_url"]')).toBeVisible();
  await expectNoBackendTerms(page);
});
