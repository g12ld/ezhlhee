#!/usr/bin/env python3
"""Validate internal links, crawl reachability, and content clusters."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.ezhalhe-sa.com"
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "05-content-architecture"
IA_REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "02-information-architecture"
EXCLUDED = {"404.html", "_new_testi.html", "data-analysis.html", "google387142411d334808.html"}
ANCHOR_RE = re.compile(r'<a\b[^>]*\bhref=["\']([^"\']+)["\']', re.I | re.S)


def local_url(relative: str) -> str:
    return f"{ORIGIN}/" if relative == "index.html" else f"{ORIGIN}/{relative}"


def local_relative(path: str) -> str:
    decoded = unquote(path).lstrip("/")
    return decoded or "index.html"


def main() -> None:
    results: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: str) -> None:
        results.append({"check": name, "passed": passed, "evidence": evidence})

    with (IA_REPORT_DIR / "redirect-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        redirect_sources = {row["source"] for row in csv.DictReader(handle)}

    pages = {}
    for path in sorted(ROOT.rglob("*.html")):
        if any(part in {".git", "reports", "outputs", "scratch"} for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative not in EXCLUDED:
            pages[relative] = path

    broken = []
    redirected = []
    bad_fragments = []
    absolute_internal = []
    graph: dict[str, set[str]] = defaultdict(set)
    inbound: dict[str, set[str]] = defaultdict(set)

    for source_relative, source_path in pages.items():
        content = source_path.read_text(encoding="utf-8")
        source_url = local_url(source_relative)
        for href in ANCHOR_RE.findall(content):
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            parsed = urlsplit(href)
            if parsed.scheme and parsed.scheme not in {"http", "https"}:
                continue
            if parsed.netloc and parsed.netloc.lower() not in {"ezhalhe-sa.com", "www.ezhalhe-sa.com"}:
                continue
            if parsed.netloc:
                absolute_internal.append((source_relative, href))
            resolved = urlsplit(urljoin(source_url, href))
            target_path = unquote(resolved.path) or "/"
            if target_path in redirect_sources:
                redirected.append((source_relative, href))
                continue
            target_relative = local_relative(target_path)
            target_file = ROOT / target_relative
            if not target_file.is_file():
                broken.append((source_relative, href))
                continue
            if target_relative in pages:
                graph[source_relative].add(target_relative)
                inbound[target_relative].add(source_relative)
            fragment = parsed.fragment
            if fragment and target_file.suffix.lower() == ".html":
                target_content = target_file.read_text(encoding="utf-8")
                decoded_fragment = unquote(fragment)
                if not re.search(
                    rf'(?:\bid|\bname)=["\']{re.escape(decoded_fragment)}["\']',
                    target_content,
                    re.I,
                ):
                    bad_fragments.append((source_relative, href))

    check("no-broken-internal-links", not broken, f"broken={len(broken)}")
    check("no-redirecting-internal-links", not redirected, f"redirected={len(redirected)}")
    check("internal-links-host-relative", not absolute_internal, f"absolute_same_domain={len(absolute_internal)}")
    check("internal-fragments-resolve", not bad_fragments, f"invalid_fragments={len(bad_fragments)}")

    orphans = [relative for relative in pages if relative != "index.html" and not inbound[relative]]
    check("no-indexable-orphans", not orphans, f"orphans={len(orphans)}")

    reached = {"index.html"}
    queue = deque(["index.html"])
    while queue:
        current = queue.popleft()
        for target in graph[current]:
            if target not in reached:
                reached.add(target)
                queue.append(target)
    unreachable = sorted(set(pages) - reached)
    check(
        "crawl-reachable-from-home",
        not unreachable,
        f"reached={len(reached)}, total={len(pages)}, unreachable={len(unreachable)}",
    )

    articles = sorted((ROOT / "articles").glob("*.html"))
    byline_missing, related_missing, related_link_errors = [], [], []
    for path in articles:
        content = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        if 'class="article-byline"' not in content or 'datetime="2026-07-15"' not in content:
            byline_missing.append(relative)
        blocks = re.findall(
            r'<aside\b[^>]*class=["\']related-reading["\'][^>]*>(.*?)</aside>',
            content,
            re.I | re.S,
        )
        if len(blocks) != 1:
            related_missing.append(relative)
        elif len(ANCHOR_RE.findall(blocks[0])) != 3:
            related_link_errors.append(relative)
    check("article-author-and-date", not byline_missing, f"articles={len(articles)}, missing={len(byline_missing)}")
    check(
        "article-contextual-links",
        not related_missing and not related_link_errors,
        f"articles={len(articles)}, missing={len(related_missing)}, wrong_link_count={len(related_link_errors)}",
    )

    articles_index = (ROOT / "articles.html").read_text(encoding="utf-8")
    topic_hub_links = re.findall(
        r'<nav\b[^>]*class=["\']topic-hubs["\'][^>]*>.*?</nav>', articles_index, re.I | re.S
    )
    topic_hub_count = len(ANCHOR_RE.findall(topic_hub_links[0])) if len(topic_hub_links) == 1 else 0
    check("topic-hub-navigation", topic_hub_count == 5, f"hub_links={topic_hub_count}")
    check(
        "article-index-complete",
        len(re.findall(r'class=["\']article-card["\']', articles_index, re.I)) == len(articles),
        f"cards={len(re.findall(r'class=[\"\']article-card[\"\']', articles_index, re.I))}, articles={len(articles)}",
    )

    artifact_files = []
    for relative, path in pages.items():
        content = path.read_text(encoding="utf-8")
        if "</content>" in content or '<parameter name="filePath"' in content:
            artifact_files.append(relative)
    check("no-editor-artifacts", not artifact_files, f"files={len(artifact_files)}")

    with (REPORT_DIR / "internal-link-changes.csv").open(encoding="utf-8-sig", newline="") as handle:
        link_changes = list(csv.DictReader(handle))
    with (REPORT_DIR / "content-cluster-map.csv").open(encoding="utf-8-sig", newline="") as handle:
        clusters = list(csv.DictReader(handle))
    check("redirect-link-change-log", len(link_changes) == 755, f"changes={len(link_changes)}")
    check("cluster-inventory-complete", len(clusters) == len(articles), f"rows={len(clusters)}")

    issue_rows = []
    for issue, rows in (
        ("broken", broken), ("redirected", redirected), ("fragment", bad_fragments),
        ("absolute_internal", absolute_internal),
    ):
        issue_rows.extend({"issue": issue, "source_file": source, "href": href} for source, href in rows)
    with (REPORT_DIR / "link-validation-issues.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["issue", "source_file", "href"])
        writer.writeheader()
        writer.writerows(issue_rows)
    inbound_rows = [
        {"file": relative, "inbound_pages": len(inbound[relative]), "crawl_reachable": relative in reached}
        for relative in sorted(pages)
    ]
    with (REPORT_DIR / "inbound-link-inventory.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inbound_rows[0]))
        writer.writeheader()
        writer.writerows(inbound_rows)

    passed = sum(1 for result in results if result["passed"])
    summary = {"checks": len(results), "passed": passed, "failed": len(results) - passed, "results": results}
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Content architecture validation", "",
        f"Result: {passed}/{len(results)} checks passed.", "",
        "| Check | Result | Evidence |", "|---|---|---|",
    ]
    for result in results:
        lines.append(f"| {result['check']} | {'PASS' if result['passed'] else 'FAIL'} | {result['evidence']} |")
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
