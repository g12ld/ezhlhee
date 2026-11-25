"use strict";

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const reportDir = path.join(root, "reports", "roadmap-implementation", "08-viewport-qa");
const origin = (process.argv[2] || "http://127.0.0.1:4173").replace(/\/$/, "");

function loadPlaywright() {
  const candidates = [
    path.join(root, "node_modules"),
    process.env.NODE_PATH,
    process.env.USERPROFILE
      ? path.join(
          process.env.USERPROFILE,
          ".cache",
          "codex-runtimes",
          "codex-primary-runtime",
          "dependencies",
          "node",
          "node_modules",
        )
      : null,
    process.env.HOME
      ? path.join(
          process.env.HOME,
          ".cache",
          "codex-runtimes",
          "codex-primary-runtime",
          "dependencies",
          "node",
          "node_modules",
        )
      : null,
  ].filter(Boolean);

  for (const candidate of candidates) {
    try {
      return require(require.resolve("playwright", { paths: [candidate] }));
    } catch {
      // Try the next known runtime path.
    }
  }

  throw new Error("Playwright was not found in local or bundled runtime paths.");
}

function pageUrl(pagePath) {
  return `${origin}${pagePath}`;
}

function screenshotName(name, viewport) {
  return `${name}-${viewport.width}.png`;
}

async function waitForStablePage(page) {
  await page.waitForLoadState("load", { timeout: 10000 }).catch(() => {});
  await page.waitForTimeout(500);
}

async function collectPageChecks(page) {
  return page.evaluate(() => {
    const html = document.documentElement;
    const body = document.body;
    const width = html.clientWidth || window.innerWidth;
    const scrollWidth = Math.max(html.scrollWidth, body ? body.scrollWidth : 0);
    const menuButton = document.querySelector("#burg, [aria-controls='ui-mobile-nav']");
    const nav = menuButton ? document.getElementById(menuButton.getAttribute("aria-controls") || "") : null;
    const primaryAction = document.querySelector(".btn-primary, .nav-cta, .booking-submit, .ui-button, a[href='booking.html'], a[href='/booking.html']");
    const activeFilter = document.querySelector(".wf-btn.on, .portfolio-filter[aria-pressed='true']");
    const visibleCards = [...document.querySelectorAll(".work-card, .portfolio-card")].filter((card) => {
      const style = window.getComputedStyle(card);
      return style.display !== "none" && style.visibility !== "hidden";
    });

    return {
      title: document.title,
      path: location.pathname,
      viewport_width: width,
      scroll_width: scrollWidth,
      horizontal_overflow_px: scrollWidth - width,
      main_landmarks: document.querySelectorAll("main").length,
      h1_count: document.querySelectorAll("h1").length,
      skip_link: Boolean(document.querySelector(".skip-link[href='#main-content']")),
      primary_action_visible: Boolean(primaryAction),
      mobile_menu_button_present: Boolean(menuButton),
      mobile_menu_controls_nav: Boolean(menuButton && nav && menuButton.getAttribute("aria-controls") === nav.id),
      active_filter_visible: Boolean(activeFilter),
      visible_cards: visibleCards.length,
      booking_form_present: Boolean(document.getElementById("booking-form")),
      booking_slot_input_present: Boolean(document.getElementById("booking-slot-input")),
    };
  });
}

async function captureScenario(browser, scenario, viewport) {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
    locale: "ar-SA",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();
  const url = pageUrl(scenario.path);
  const imagePath = path.join(reportDir, screenshotName(scenario.name, viewport));

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
    await waitForStablePage(page);
    const checks = await collectPageChecks(page);
    await page.screenshot({ path: imagePath, fullPage: false });
    const screenshotBytes = fs.statSync(imagePath).size;

    return {
      scenario: scenario.name,
      url,
      viewport,
      screenshot: path.relative(root, imagePath).replace(/\\/g, "/"),
      screenshot_bytes: screenshotBytes,
      checks,
      pass:
        checks.horizontal_overflow_px <= 4 &&
        checks.main_landmarks === 1 &&
        checks.h1_count === 1 &&
        checks.skip_link &&
        checks.primary_action_visible &&
        screenshotBytes > 1000,
    };
  } finally {
    await context.close();
  }
}

async function runInteractionChecks(browser) {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    deviceScaleFactor: 1,
    locale: "ar-SA",
    reducedMotion: "reduce",
  });
  const page = await context.newPage();

  try {
    await page.goto(pageUrl("/index.html"), { waitUntil: "domcontentloaded", timeout: 30000 });
    await waitForStablePage(page);

    const menuOpened = await page.evaluate(async () => {
      const button = document.querySelector("#burg, [aria-controls='ui-mobile-nav']");
      if (!button) return false;
      button.click();
      await new Promise((resolve) => window.setTimeout(resolve, 100));
      return button.getAttribute("aria-expanded") === "true";
    });

    await page.keyboard.press("Escape");
    await page.waitForTimeout(100);
    const menuClosed = await page
      .$eval("#burg, [aria-controls='ui-mobile-nav']", (button) => button.getAttribute("aria-expanded") === "false")
      .catch(() => false);

    const dialogOpened = await page.evaluate(async () => {
      const card = document.querySelector(".work-card[role='button']");
      const dialog = document.getElementById("lb");
      if (!card || !dialog) return false;
      card.focus();
      card.dispatchEvent(new KeyboardEvent("keydown", { key: "Enter", bubbles: true }));
      await new Promise((resolve) => window.setTimeout(resolve, 150));
      return dialog.getAttribute("aria-hidden") === "false" && dialog.getAttribute("aria-modal") === "true";
    });

    await page.keyboard.press("Escape");
    await page.waitForTimeout(100);
    const dialogClosed = await page
      .$eval("#lb", (dialog) => dialog.getAttribute("aria-hidden") === "true")
      .catch(() => false);

    return {
      mobile_menu_opens_and_syncs_aria_expanded: menuOpened,
      escape_closes_mobile_menu: menuClosed,
      enter_opens_portfolio_dialog: dialogOpened,
      escape_closes_portfolio_dialog: dialogClosed,
    };
  } finally {
    await context.close();
  }
}

function existingBrowserPaths() {
  const programFiles = [
    process.env.ProgramFiles,
    process.env["ProgramFiles(x86)"],
    process.env.LocalAppData,
  ].filter(Boolean);
  const suffixes = [
    ["Google", "Chrome", "Application", "chrome.exe"],
    ["Microsoft", "Edge", "Application", "msedge.exe"],
  ];

  return programFiles.flatMap((base) => suffixes.map((suffix) => path.join(base, ...suffix))).filter((candidate) => fs.existsSync(candidate));
}

function launchProfiles(chromium) {
  const commonArgs = [
    "--disable-gpu",
    "--disable-gpu-compositing",
    "--disable-gpu-sandbox",
    "--disable-dev-shm-usage",
    "--disable-accelerated-2d-canvas",
    "--disable-features=CalculateNativeWinOcclusion,CanvasOopRasterization,VizDisplayCompositor",
    "--enable-unsafe-swiftshader",
    "--no-first-run",
    "--no-default-browser-check",
    "--use-angle=swiftshader",
    "--use-gl=swiftshader",
  ];

  return [
    {
      name: "playwright-chromium",
      launch: () => chromium.launch({ headless: true, args: commonArgs }),
    },
    ...existingBrowserPaths().map((executablePath) => ({
      name: path.basename(executablePath, ".exe"),
      launch: () => chromium.launch({ executablePath, headless: true, args: commonArgs }),
    })),
  ];
}

async function runSuite(browser, browserName) {
  const scenarios = [
    { name: "home", path: "/index.html", viewports: [{ width: 375, height: 812 }, { width: 768, height: 1024 }, { width: 1024, height: 900 }, { width: 1440, height: 1000 }] },
    { name: "portfolio", path: "/portfolio.html", viewports: [{ width: 375, height: 812 }, { width: 768, height: 1024 }] },
    { name: "booking", path: "/booking.html", viewports: [{ width: 375, height: 812 }, { width: 768, height: 1024 }] },
    { name: "articles", path: "/articles.html", viewports: [{ width: 375, height: 812 }] },
    { name: "salla", path: "/salla-store-design.html", viewports: [{ width: 375, height: 812 }] },
    { name: "zid", path: "/zid-store-design.html", viewports: [{ width: 375, height: 812 }] },
  ];

  const results = [];
  for (const scenario of scenarios) {
    for (const viewport of scenario.viewports) {
      results.push(await captureScenario(browser, scenario, viewport));
    }
  }

  const interactions = await runInteractionChecks(browser);
  const failedResults = results.filter((result) => !result.pass);
  const failedInteractions = Object.entries(interactions)
    .filter(([, passed]) => !passed)
    .map(([name]) => name);
  const passed = failedResults.length === 0 && failedInteractions.length === 0;
  return {
    status: passed ? "PASS" : "FAIL",
    tested_at: new Date().toISOString(),
    origin,
    browser: browserName,
    summary: {
      pages_checked: results.length,
      failed_pages: failedResults.length,
      failed_interactions: failedInteractions.length,
    },
    results,
    interactions,
    failures: {
      pages: failedResults.map((result) => ({
        scenario: result.scenario,
        viewport: result.viewport,
        checks: result.checks,
      })),
      interactions: failedInteractions,
    },
  };
}

function writeReport(payload, launchErrors = []) {
  const output = { ...payload, launch_errors: launchErrors };
  fs.writeFileSync(
    path.join(reportDir, "viewport-browser-validation.json"),
    JSON.stringify(output, null, 2),
    "utf8",
  );

  const lines = [
    "# Browser viewport validation",
    "",
    `**Status:** ${payload.status}`,
    "",
    `Origin: \`${origin}\``,
    `Browser: \`${payload.browser}\``,
    "",
    "## Checks",
    "",
    `- Pages/viewports checked: ${payload.summary.pages_checked}`,
    `- Failed page checks: ${payload.summary.failed_pages}`,
    `- Failed interaction checks: ${payload.summary.failed_interactions}`,
    "",
    "## Screenshots",
    "",
    ...payload.results.map((result) => `- ${result.scenario} ${result.viewport.width}x${result.viewport.height}: \`${result.screenshot}\``),
  ];
  if (launchErrors.length) {
    lines.push("", "## Browser fallback notes", "");
    launchErrors.forEach((item) => lines.push(`- ${item.browser}: ${item.error}`));
  }
  fs.writeFileSync(path.join(reportDir, "viewport-browser-validation.md"), `${lines.join("\n")}\n`, "utf8");

  console.log(JSON.stringify({
    status: payload.status,
    browser: payload.browser,
    pages_checked: payload.summary.pages_checked,
    failed_pages: payload.summary.failed_pages,
    failed_interactions: payload.summary.failed_interactions,
    launch_errors: launchErrors.length,
  }, null, 2));
}

async function main() {
  fs.mkdirSync(reportDir, { recursive: true });
  const { chromium } = loadPlaywright();
  const errors = [];

  for (const profile of launchProfiles(chromium)) {
    let browser;
    try {
      browser = await profile.launch();
      const payload = await runSuite(browser, profile.name);
      writeReport(payload, errors);
      process.exitCode = payload.status === "PASS" ? 0 : 1;
      return;
    } catch (error) {
      errors.push({
        browser: profile.name,
        error: String(error.message || error).split("\n")[0],
      });
    } finally {
      if (browser) await browser.close().catch(() => {});
    }
  }

  const payload = {
    status: "FAIL",
    tested_at: new Date().toISOString(),
    origin,
    browser: "none",
    summary: { pages_checked: 0, failed_pages: 0, failed_interactions: 0 },
    results: [],
    interactions: {},
    failures: { pages: [], interactions: [] },
  };
  writeReport(payload, errors);
  process.exitCode = 1;
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exitCode = 1;
});
