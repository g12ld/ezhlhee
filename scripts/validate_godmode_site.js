"use strict";

const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const ignoreDirs = new Set([".git", "node_modules", "scratch", "reports", ".vercel"]);
const htmlFiles = [];
const errors = [];
const warnings = [];
const pageMetadataAuditExcluded = new Set([
  "_new_testi.html",
  "data-analysis.html",
  "google387142411d334808.html",
]);

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (!ignoreDirs.has(entry.name)) walk(path.join(dir, entry.name));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith(".html")) {
      htmlFiles.push(path.join(dir, entry.name));
    }
  }
}

function rel(file) {
  return path.relative(root, file).replace(/\\/g, "/");
}

function stripHashAndQuery(value) {
  return value.split("#")[0].split("?")[0];
}

function localTarget(file, rawUrl) {
  if (!rawUrl || rawUrl.startsWith("#")) return null;
  if (/^(https?:|mailto:|tel:|sms:|whatsapp:|data:|javascript:)/i.test(rawUrl)) return null;

  const clean = decodeURI(stripHashAndQuery(rawUrl));
  if (!clean) return null;

  if (clean.startsWith("/")) {
    return path.join(root, clean === "/" ? "index.html" : clean.slice(1));
  }

  return path.resolve(path.dirname(file), clean);
}

function existsAsPageOrAsset(target) {
  if (fs.existsSync(target)) return true;
  if (!path.extname(target) && fs.existsSync(`${target}.html`)) return true;
  if (fs.existsSync(path.join(target, "index.html"))) return true;
  return false;
}

function findAttributes(tag, attr) {
  const regex = new RegExp(`${attr}\\s*=\\s*["']([^"']+)["']`, "gi");
  const values = [];
  let match;
  while ((match = regex.exec(tag))) values.push(match[1]);
  return values;
}

function auditHtml(file) {
  const source = fs.readFileSync(file, "utf8");
  const fileRel = rel(file);
  const noindex = /<meta\s+name=["']robots["'][^>]+noindex/i.test(source);
  const skipPageMetadata = pageMetadataAuditExcluded.has(fileRel);

  if (!skipPageMetadata && !/<title>[^<]{8,}<\/title>/i.test(source)) {
    warnings.push(`${fileRel}: missing or very short title`);
  }

  if (!skipPageMetadata && !/<meta\s+name=["']description["'][^>]+content=["'][^"']{40,}["']/i.test(source)) {
    warnings.push(`${fileRel}: missing or very short meta description`);
  }

  if (!skipPageMetadata && !noindex && !/<link\s+rel=["']canonical["'][^>]+href=["']https:\/\/www\.ezhalhe-sa\.com\//i.test(source)) {
    warnings.push(`${fileRel}: missing canonical on indexable page`);
  }

  const h1Count = (source.match(/<h1\b/gi) || []).length;
  if (!skipPageMetadata && !noindex && h1Count !== 1) {
    warnings.push(`${fileRel}: expected one H1, found ${h1Count}`);
  }

  const ids = findAttributes(source, "id");
  const seen = new Set();
  ids.forEach((id) => {
    if (seen.has(id)) errors.push(`${fileRel}: duplicate id "${id}"`);
    seen.add(id);
  });

  const jsonLdBlocks = source.match(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi) || [];
  jsonLdBlocks.forEach((block, index) => {
    const json = block.replace(/^<script[^>]*>/i, "").replace(/<\/script>$/i, "").trim();
    try {
      JSON.parse(json);
    } catch (error) {
      errors.push(`${fileRel}: invalid JSON-LD block ${index + 1}`);
    }
  });

  const imgTags = source.match(/<img\b[^>]*>/gi) || [];
  imgTags.forEach((tag) => {
    if (!/\salt\s*=/i.test(tag)) warnings.push(`${fileRel}: image missing alt attribute`);
  });

  const tags = source.match(/<(a|img|script|link)\b[^>]*>/gi) || [];
  tags.forEach((tag) => {
    const isLinkStylesheet = /^<link/i.test(tag) && /rel=["']stylesheet["']/i.test(tag);
    const attr = /^<a/i.test(tag) || isLinkStylesheet ? "href" : "src";
    const values = findAttributes(tag, attr);
    values.forEach((value) => {
      const target = localTarget(file, value);
      if (target && !existsAsPageOrAsset(target)) {
        warnings.push(`${fileRel}: missing local target ${value}`);
      }
    });
  });
}

function auditSitemap() {
  const sitemap = path.join(root, "sitemap.xml");
  if (!fs.existsSync(sitemap)) {
    errors.push("sitemap.xml is missing");
    return;
  }

  const source = fs.readFileSync(sitemap, "utf8");
  const locs = [...source.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);
  const required = [
    "https://www.ezhalhe-sa.com/",
    "https://www.ezhalhe-sa.com/salla-store-design.html",
    "https://www.ezhalhe-sa.com/zid-store-design.html",
    "https://www.ezhalhe-sa.com/search-engine-optimization.html",
    "https://www.ezhalhe-sa.com/articles.html",
    "https://www.ezhalhe-sa.com/portfolio.html",
    "https://www.ezhalhe-sa.com/booking.html",
    "https://www.ezhalhe-sa.com/about.html",
    "https://www.ezhalhe-sa.com/privacy.html",
  ];

  required.forEach((url) => {
    if (!locs.includes(url)) errors.push(`sitemap.xml: missing ${url}`);
  });

  locs.forEach((url) => {
    if (!url.startsWith("https://www.ezhalhe-sa.com/")) {
      warnings.push(`sitemap.xml: noncanonical host ${url}`);
      return;
    }

    const pathname = decodeURI(new URL(url).pathname);
    const target = path.join(root, pathname === "/" ? "index.html" : pathname.slice(1));
    if (!existsAsPageOrAsset(target)) warnings.push(`sitemap.xml: target does not exist ${url}`);
  });
}

function auditRobots() {
  const robots = path.join(root, "robots.txt");
  if (!fs.existsSync(robots)) {
    errors.push("robots.txt is missing");
    return;
  }

  const source = fs.readFileSync(robots, "utf8");
  if (!/Sitemap:\s*https:\/\/www\.ezhalhe-sa\.com\/sitemap\.xml/i.test(source)) {
    warnings.push("robots.txt: missing canonical sitemap reference");
  }
  if (/Disallow:\s*\/(css|js|images|ui-system)/i.test(source)) {
    errors.push("robots.txt: blocks important static assets");
  }
}

walk(root);
htmlFiles.forEach(auditHtml);
auditSitemap();
auditRobots();

console.log(`Audited ${htmlFiles.length} HTML files.`);
console.log(`Errors: ${errors.length}`);
errors.slice(0, 40).forEach((message) => console.error(`ERROR ${message}`));
if (errors.length > 40) console.error(`ERROR ...and ${errors.length - 40} more`);
console.log(`Warnings: ${warnings.length}`);
warnings.slice(0, 80).forEach((message) => console.warn(`WARN ${message}`));
if (warnings.length > 80) console.warn(`WARN ...and ${warnings.length - 80} more`);

if (errors.length) process.exitCode = 1;
