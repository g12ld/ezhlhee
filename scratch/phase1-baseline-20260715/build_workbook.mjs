import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = "C:/Projects/ezhlhee";
const reportDir = path.join(root, "reports/phase-1-baseline/2026-07-15");
const outputDir = path.join(root, "outputs/ezhalha-phase1-baseline-20260715");
const previewDir = path.join(outputDir, "previews");
const outputPath = path.join(outputDir, "ezhalha-phase1-baseline.xlsx");

const COLORS = {
  primary: "#15B5B0",
  secondary: "#0D2224",
  cta: "#3BBBC2",
  background: "#FFFFFF",
  text: "#555555",
};

const dataSheets = [
  { name: "URL Inventory", file: "url-inventory.csv", previewCols: 8 },
  { name: "Metadata", file: "metadata-inventory.csv", previewCols: 9 },
  { name: "Canonicals", file: "canonical-map.csv", previewCols: 11 },
  { name: "Redirects", file: "redirect-baseline.csv", previewCols: 11 },
  { name: "Sitemap", file: "sitemap-inventory.csv", previewCols: 12 },
  { name: "Broken Links", file: "broken-links.csv", previewCols: 10 },
  { name: "Redirected Links", file: "redirected-internal-links.csv", previewCols: 10 },
  { name: "Orphans", file: "orphan-pages.csv", previewCols: 5 },
  { name: "Important Files", file: "important-files-inventory.csv", previewCols: 8 },
  { name: "Images", file: "image-inventory.csv", previewCols: 10 },
  { name: "Content", file: "content-inventory.csv", previewCols: 8 },
  { name: "Brand Colors", file: "brand-color-inventory.csv", previewCols: 5 },
  { name: "Search Console", file: "search-console-baseline.csv", previewCols: 5 },
  { name: "Keywords", file: "keyword-baseline.csv", previewCols: 10 },
  { name: "Backlink Gates", file: "backlink-targets.csv", previewCols: 8 },
  { name: "SEO Decisions", file: "seo-decision-log.csv", previewCols: 8 },
  { name: "Security", file: "security-findings.csv", previewCols: 8 },
  { name: "Accessibility", file: "accessibility-baseline.csv", previewCols: 6 },
];

function columnName(index) {
  let value = index;
  let result = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    result = String.fromCharCode(65 + remainder) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function countCsvRows(text) {
  return text.replace(/^\uFEFF/, "").trimEnd().split(/\r?\n/).length;
}

function countCsvColumns(text) {
  return text.replace(/^\uFEFF/, "").split(/\r?\n/, 1)[0].split(",").length;
}

function safePreviewName(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

await fs.mkdir(previewDir, { recursive: true });

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Summary");
const sources = workbook.worksheets.add("Source Notes");
const dimensions = new Map();

for (const config of dataSheets) {
  const csvText = await fs.readFile(path.join(reportDir, config.file), "utf8");
  const importedWorkbook = await Workbook.fromCSV(csvText, { sheetName: config.name });
  const importedSheet = importedWorkbook.worksheets.getItem(config.name);
  const rows = countCsvRows(csvText);
  const cols = countCsvColumns(csvText);
  const importedRange = importedSheet.getRange(`A1:${columnName(cols)}${rows}`);
  const targetSheet = workbook.worksheets.add(config.name);
  targetSheet.getRange(`A1:${columnName(cols)}${rows}`).values = importedRange.values;
  dimensions.set(config.name, {
    rows,
    cols,
    previewCols: config.previewCols,
  });
}

for (const config of dataSheets) {
  const sheet = workbook.worksheets.getItem(config.name);
  const { rows, cols } = dimensions.get(config.name);
  const lastColumn = columnName(cols);
  const usedRange = sheet.getRange(`A1:${lastColumn}${rows}`);
  const headerRange = sheet.getRange(`A1:${lastColumn}1`);
  const bodyRange = rows > 1 ? sheet.getRange(`A2:${lastColumn}${rows}`) : null;

  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  usedRange.format.font = { color: COLORS.text };
  headerRange.format = {
    fill: COLORS.secondary,
    font: { bold: true, color: COLORS.background },
    wrapText: true,
    verticalAlignment: "center",
  };
  headerRange.format.rowHeight = 30;
  if (bodyRange) {
    bodyRange.format.rowHeight = 20;
    bodyRange.format.verticalAlignment = "center";
    bodyRange.format.wrapText = false;
  }

  for (let column = 1; column <= cols; column += 1) {
    const letter = columnName(column);
    const header = String(sheet.getRange(`${letter}1`).values?.[0]?.[0] || "").toLowerCase();
    let width = 18;
    if (header.includes("url") || header.includes("canonical") || header.includes("destination") || header.includes("location")) width = 42;
    if (header.includes("file") || header.includes("path") || header.includes("reference")) width = 28;
    if (header.includes("title") || header.includes("description") || header.includes("notes") || header.includes("risk") || header.includes("action") || header.includes("decision") || header.includes("evidence") || header.includes("rationale")) width = 36;
    if (header.includes("status") || header.includes("count") || header.includes("length") || header.includes("position") || header.includes("width") || header.includes("height")) width = 14;
    sheet.getRange(`${letter}1:${letter}${rows}`).format.columnWidth = width;
    if (header === "as_of" || header === "date" || header.includes("date_published") || header.includes("date_modified")) {
      sheet.getRange(`${letter}2:${letter}${rows}`).format.numberFormat = "yyyy-mm-dd hh:mm";
    }
  }

  if (["Security", "Accessibility", "SEO Decisions", "Search Console"].includes(config.name) && bodyRange) {
    bodyRange.format.wrapText = true;
    bodyRange.format.rowHeight = config.name === "Search Console" ? 90 : 72;
  }
}

workbook.worksheets.getItem("Search Console").getRange("B1:B11").format.columnWidth = 30;
workbook.worksheets.getItem("Search Console").getRange("D1:D11").format.columnWidth = 22;
workbook.worksheets.getItem("Search Console").getRange("D2:D11").values = Array.from({ length: 10 }, () => ["2026-07-15 12:54 AST"]);
workbook.worksheets.getItem("Keywords").getRange("I1:I16").format.columnWidth = 30;
workbook.worksheets.getItem("Keywords").getRange("J1:J16").format.columnWidth = 22;
workbook.worksheets.getItem("Keywords").getRange("J2:J16").values = Array.from({ length: 15 }, () => ["2026-07-15 12:54 AST"]);
workbook.worksheets.getItem("Backlink Gates").getRange("F1:F124").format.columnWidth = 30;
workbook.worksheets.getItem("Backlink Gates").getRange("H1:H124").format.columnWidth = 46;
workbook.worksheets.getItem("Brand Colors").getRange("B1:B74").format.columnWidth = 24;
workbook.worksheets.getItem("Important Files").getRange("H1:H15").format.columnWidth = 46;

summary.showGridLines = false;
summary.freezePanes.freezeRows(4);
summary.getRange("A1:H2").merge();
summary.getRange("A1").values = [["Ezhalha — Phase 1 SEO Baseline"]];
summary.getRange("A1:H2").format = {
  fill: COLORS.secondary,
  font: { bold: true, color: COLORS.background, size: 18 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
summary.getRange("A3:H3").merge();
summary.getRange("A3").values = [["Generated 2026-07-15 · Production unchanged · Structural implementation paused pending baseline review"]];
summary.getRange("A3:H3").format = {
  fill: COLORS.primary,
  font: { bold: true, color: COLORS.background },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};

summary.getRange("A5:H5").values = [["Metric", "Value", "", "Metric", "Value", "", "Metric", "Value"]];
summary.getRange("A5:H5").format = {
  fill: COLORS.secondary,
  font: { bold: true, color: COLORS.background },
  horizontalAlignment: "center",
};
summary.getRange("A6:A11").values = [["Local HTML pages"], ["Live URLs/assets tested"], ["Final 404 URLs/assets"], ["Sitemap entries"], ["Sitemap duplicate extras"], ["Broken link occurrences"]];
summary.getRange("D6:D11").values = [["Missing canonicals"], ["Non-www canonicals"], ["Redirected link occurrences"], ["Orphan candidates"], ["Pages with JSON-LD"], ["Images missing dimensions"]];
summary.getRange("G6:G11").values = [["Unique hex colors"], ["Non-approved colors"], ["Search Console access"], ["Backlink evidence"], ["Production changed"], ["Tracked site files changed"]];
summary.getRange("B6:B11").formulas = [["=COUNTA('Metadata'!$A$2:$A$1000)"], ["=COUNTA('URL Inventory'!$A$2:$A$2000)"], ["=COUNTIF('URL Inventory'!$E$2:$E$2000,404)"], ["=COUNTA('Sitemap'!$B$2:$B$500)"], ["=COUNTIF('Sitemap'!$F$2:$F$500,2)/2"], ["=COUNTA('Broken Links'!$A$2:$A$5000)"]];
summary.getRange("E6:E11").formulas = [["=COUNTIF('Canonicals'!$K$2:$K$500,\"missing\")"], ["=COUNTIF('Canonicals'!$K$2:$K$500,\"non-www\")"], ["=COUNTA('Redirected Links'!$A$2:$A$5000)"], ["=COUNTA('Orphans'!$A$2:$A$500)"], ["=COUNTIF('Metadata'!$AA$2:$AA$500,\">0\")"], ["=COUNTIF('Images'!$L$2:$L$1000,\"False\")"]];
summary.getRange("H6:H11").formulas = [["=COUNTA('Brand Colors'!$A$2:$A$500)"], ["=COUNTIF('Brand Colors'!$B$2:$B$500,\"False\")"], ["='Search Console'!$B$2"], ["='Backlink Gates'!$F$2"], ["=\"No\""], ["=\"No\""]];

summary.getRange("A13:H13").merge();
summary.getRange("A13").values = [["Release gates"]];
summary.getRange("A13:H13").format = { fill: COLORS.primary, font: { bold: true, color: COLORS.background }, horizontalAlignment: "center" };
summary.getRange("A14:D20").values = [
  ["Gate", "Status", "Evidence", "Requirement"],
  ["Repository/live technical inventory", "READY FOR REVIEW", "Baseline package", "Owner review"],
  ["Search Console performance/indexing", "BLOCKED", "Access denied", "Authorized account or exports"],
  ["Backlink preservation evidence", "BLOCKED", "No export", "Search Console Links or approved backlink export"],
  ["Production behavior", "UNCHANGED", "Repository state", "Keep unchanged until validated release"],
  ["Public Telegram credential", "BLOCKED", "Security finding SEC-001", "Rotation and server-side design approval"],
  ["Phase 1 structural changes", "PAUSED", "Approved safety gate", "Baseline review plus missing evidence"],
];
summary.getRange("A14:D14").format = { fill: COLORS.secondary, font: { bold: true, color: COLORS.background }, wrapText: true };
summary.getRange("A15:D20").format.font = { color: COLORS.text };
summary.getRange("A15:D20").format.rowHeight = 34;
summary.getRange("A15:D20").format.wrapText = true;
summary.getRange("B15:B20").format = { fill: COLORS.cta, font: { bold: true, color: COLORS.secondary }, horizontalAlignment: "center", verticalAlignment: "center" };

for (const range of ["A6:B11", "D6:E11", "G6:H11"]) {
  summary.getRange(range).format.borders = { preset: "outside", style: "thin", color: COLORS.primary };
}
summary.getRange("A6:H11").format.rowHeight = 24;
summary.getRange("A1:H20").format.font = { color: COLORS.text };
summary.getRange("A1:H2").format.font = { bold: true, color: COLORS.background, size: 18 };
summary.getRange("A3:H3").format.font = { bold: true, color: COLORS.background };
summary.getRange("A5:H5").format.font = { bold: true, color: COLORS.background };
summary.getRange("A13:H13").format.font = { bold: true, color: COLORS.background };
summary.getRange("A14:D14").format.font = { bold: true, color: COLORS.background };
summary.getRange("A1:H20").format.verticalAlignment = "center";
summary.getRange("A1:A20").format.columnWidth = 28;
summary.getRange("B1:B20").format.columnWidth = 18;
summary.getRange("C1:C20").format.columnWidth = 24;
summary.getRange("D1:D20").format.columnWidth = 42;
summary.getRange("E1:E20").format.columnWidth = 18;
summary.getRange("F1:F20").format.columnWidth = 4;
summary.getRange("G1:G20").format.columnWidth = 28;
summary.getRange("H1:H20").format.columnWidth = 40;

sources.showGridLines = false;
sources.getRange("A1:D7").values = [
  ["Source", "URL or path", "Captured", "Notes"],
  ["Production origin", "https://www.ezhalhe-sa.com/", "2026-07-15", "Live GET and header crawl"],
  ["Production robots", "https://www.ezhalhe-sa.com/robots.txt", "2026-07-15", "Snapshot included"],
  ["Production sitemap", "https://www.ezhalhe-sa.com/sitemap.xml", "2026-07-15", "Snapshot and row inventory included"],
  ["Repository", "C:/Projects/ezhlhee", "2026-07-15", "Git commit 4505cfe89a5ae5766f94a0b7933ffeeb7b3edfa7"],
  ["Search Console", "https://search.google.com/search-console", "2026-07-15", "Authenticated check returned no access; no private data was read"],
  ["Baseline summary", "reports/phase-1-baseline/2026-07-15/baseline-summary.md", "2026-07-15", "Review gates and limitations"],
];
sources.getRange("A1:D1").format = { fill: COLORS.secondary, font: { bold: true, color: COLORS.background } };
sources.getRange("A1:D7").format.font = { color: COLORS.text };
sources.getRange("A1:D1").format.font = { bold: true, color: COLORS.background };
sources.getRange("A1:D7").format.wrapText = true;
sources.getRange("A1:A7").format.columnWidth = 24;
sources.getRange("B1:B7").format.columnWidth = 48;
sources.getRange("C1:C7").format.columnWidth = 16;
sources.getRange("D1:D7").format.columnWidth = 52;
sources.freezePanes.freezeRows(1);

const summaryInspect = await workbook.inspect({ kind: "table", range: "Summary!A1:H20", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 8 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan" });

const previewSpecs = [
  { name: "Summary", range: "A1:H20" },
  { name: "Source Notes", range: "A1:D7" },
  ...dataSheets.map((config) => {
    const { rows, cols, previewCols } = dimensions.get(config.name);
    return { name: config.name, range: `A1:${columnName(Math.min(cols, previewCols))}${Math.min(rows, 16)}` };
  }),
];

for (const spec of previewSpecs) {
  const preview = await workbook.render({ sheetName: spec.name, range: spec.range, scale: 1, format: "png" });
  await fs.writeFile(path.join(previewDir, `${safePreviewName(spec.name)}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

console.log(JSON.stringify({ outputPath, summaryInspect: summaryInspect.ndjson, formulaErrors: formulaErrors.ndjson, previews: previewSpecs.map((spec) => spec.name) }, null, 2));
