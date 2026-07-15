from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import re
import shutil
import ssl
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from lxml import etree, html


ROOT = Path(__file__).resolve().parents[1]
PRODUCTION_ORIGIN = "https://www.ezhalhe-sa.com"
NON_WWW_ORIGIN = "https://ezhalhe-sa.com"
USER_AGENT = "Ezhalha-SEO-Baseline/1.0 (+https://www.ezhalhe-sa.com/)"
REDIRECT_STATUSES = {301, 302, 303, 307, 308}
MAX_BODY_BYTES = 1_500_000
FETCH_TIMEOUT_SECONDS = 25


def normalized_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def canonical_url_key(value: str) -> str:
    if not value:
        return ""
    parts = urllib.parse.urlsplit(value)
    scheme = parts.scheme.lower()
    host = (parts.hostname or "").lower()
    port = f":{parts.port}" if parts.port else ""
    path = urllib.parse.quote(urllib.parse.unquote(parts.path or "/"), safe="/%:@-._~")
    return urllib.parse.urlunsplit((scheme, host + port, path, parts.query, ""))


def request_url(value: str) -> str:
    parts = urllib.parse.urlsplit(value)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path or "/"), safe="/%:@-._~")
    query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe="=&%:@/?+-._~")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc.encode("idna").decode("ascii"), path, query, ""))


def file_to_url(path: Path) -> str:
    relative = unicodedata.normalize("NFC", path.relative_to(ROOT).as_posix())
    if relative == "index.html":
        return f"{PRODUCTION_ORIGIN}/"
    encoded = urllib.parse.quote(relative, safe="/%:@-._~")
    return f"{PRODUCTION_ORIGIN}/{encoded}"


def csv_safe(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_safe(row.get(key, "")) for key in fieldnames})


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def decode_body(body: bytes, content_type: str) -> str:
    charset_match = re.search(r"charset=([^;\s]+)", content_type or "", re.I)
    encodings = [charset_match.group(1).strip('"\'')] if charset_match else []
    encodings.extend(["utf-8-sig", "utf-8", "windows-1256"])
    for encoding in encodings:
        try:
            return body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", errors="replace")


def fetch_url(url: str) -> dict[str, Any]:
    chain: list[dict[str, Any]] = []
    current = request_url(url)
    context = ssl.create_default_context()
    opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=context))
    response_headers: dict[str, str] = {}
    body = b""
    error = ""
    final_status = 0

    for _ in range(11):
        request = urllib.request.Request(
            current,
            method="GET",
            headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
        )
        try:
            response = opener.open(request, timeout=FETCH_TIMEOUT_SECONDS)
        except urllib.error.HTTPError as exc:
            response = exc
        except Exception as exc:  # Network evidence must retain the failure instead of aborting the package.
            error = f"{type(exc).__name__}: {exc}"
            break

        final_status = int(response.getcode() or 0)
        response_headers = {key.lower(): value for key, value in response.headers.items()}
        location = response_headers.get("location", "")
        if final_status in REDIRECT_STATUSES and location:
            next_url = urllib.parse.urljoin(current, location)
            chain.append({"url": current, "status": final_status, "location": next_url})
            current = request_url(next_url)
            continue

        try:
            body = response.read(MAX_BODY_BYTES)
        except Exception as exc:
            error = f"body-read {type(exc).__name__}: {exc}"
        break
    else:
        error = "redirect limit exceeded"

    return {
        "requested_url": url,
        "requested_url_ascii": request_url(url),
        "initial_status": chain[0]["status"] if chain else final_status,
        "final_status": final_status,
        "final_url": current,
        "redirect_count": len(chain),
        "redirect_chain": chain,
        "headers": response_headers,
        "body": body,
        "body_text": decode_body(body, response_headers.get("content-type", "")),
        "error": error,
    }


def parse_json_ld(value: str) -> tuple[Any, str]:
    try:
        return json.loads(value), ""
    except json.JSONDecodeError as exc:
        return None, f"{exc.msg} at line {exc.lineno}, column {exc.colno}"


def schema_types(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        raw_type = value.get("@type")
        if isinstance(raw_type, list):
            found.extend(str(item) for item in raw_type)
        elif raw_type:
            found.append(str(raw_type))
        for nested in value.values():
            found.extend(schema_types(nested))
    elif isinstance(value, list):
        for nested in value:
            found.extend(schema_types(nested))
    return found


def meta_value(document: html.HtmlElement, *, name: str = "", prop: str = "") -> str:
    if name:
        nodes = document.xpath(
            "//meta[translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')=$key]/@content",
            key=name.lower(),
        )
    else:
        nodes = document.xpath(
            "//meta[translate(@property,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')=$key]/@content",
            key=prop.lower(),
        )
    return normalized_text(nodes[0]) if nodes else ""


def link_href(document: html.HtmlElement, rel: str) -> list[str]:
    return [
        normalized_text(value)
        for value in document.xpath(
            "//link[contains(concat(' ', translate(normalize-space(@rel),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), ' '), $rel)]/@href",
            rel=f" {rel.lower()} ",
        )
        if normalized_text(value)
    ]


def resolve_internal(base_url: str, href: str) -> tuple[str, bool]:
    href = normalized_text(href)
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return "", False
    resolved = urllib.parse.urljoin(base_url, href)
    parsed = urllib.parse.urlsplit(resolved)
    host = (parsed.hostname or "").lower()
    is_internal = host in {"ezhalhe-sa.com", "www.ezhalhe-sa.com"}
    if is_internal:
        resolved = urllib.parse.urlunsplit((parsed.scheme or "https", parsed.netloc, parsed.path or "/", parsed.query, ""))
    return resolved, is_internal


def parse_local_page(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    text = decode_body(raw, "text/html; charset=utf-8")
    try:
        document = html.fromstring(text)
    except (etree.ParserError, ValueError) as exc:
        return {"file": path.relative_to(ROOT).as_posix(), "parse_error": str(exc), "raw": text, "links": [], "images": [], "schemas": []}

    production_url = file_to_url(path)
    title_nodes = document.xpath("//title/text()")
    h1_nodes = [normalized_text(" ".join(node.itertext())) for node in document.xpath("//h1")]
    canonicals = link_href(document, "canonical")
    html_nodes = document.xpath("/html")
    root_node = html_nodes[0] if html_nodes else None

    schemas: list[dict[str, Any]] = []
    collected_types: list[str] = []
    for index, node in enumerate(document.xpath("//script[translate(@type,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')='application/ld+json']"), start=1):
        raw_schema = node.text or ""
        parsed, error = parse_json_ld(raw_schema)
        types = schema_types(parsed) if not error else []
        collected_types.extend(types)
        schemas.append({"block": index, "valid_json": not bool(error), "error": error, "types": sorted(set(types)), "data": parsed})

    links: list[dict[str, Any]] = []
    for node in document.xpath("//a[@href]"):
        href = normalized_text(node.get("href"))
        resolved, is_internal = resolve_internal(production_url, href)
        links.append(
            {
                "source_file": path.relative_to(ROOT).as_posix(),
                "source_url": production_url,
                "raw_href": href,
                "resolved_url": resolved,
                "is_internal": is_internal,
                "anchor_text": normalized_text(" ".join(node.itertext()))[:500],
                "rel": normalized_text(node.get("rel")),
                "target": normalized_text(node.get("target")),
            }
        )

    images: list[dict[str, Any]] = []
    for node in document.xpath("//img[@src]"):
        src = normalized_text(node.get("src"))
        resolved, is_internal = resolve_internal(production_url, src)
        images.append(
            {
                "source_file": path.relative_to(ROOT).as_posix(),
                "source_url": production_url,
                "raw_src": src,
                "resolved_url": resolved,
                "is_internal": is_internal,
                "alt": normalized_text(node.get("alt")),
                "width": normalized_text(node.get("width")),
                "height": normalized_text(node.get("height")),
                "loading": normalized_text(node.get("loading")),
                "decoding": normalized_text(node.get("decoding")),
                "fetchpriority": normalized_text(node.get("fetchpriority")),
                "srcset": normalized_text(node.get("srcset")),
            }
        )

    for node in document.xpath("//script|//style|//noscript"):
        parent = node.getparent()
        if parent is not None:
            parent.remove(node)
    body_text = normalized_text(" ".join(document.xpath("//body//text()")))
    words = re.findall(r"[\w\u0600-\u06FF]+", body_text, flags=re.UNICODE)

    date_published = meta_value(document, prop="article:published_time")
    date_modified = meta_value(document, prop="article:modified_time")
    author = meta_value(document, name="author")
    for schema in schemas:
        if isinstance(schema.get("data"), dict):
            data = schema["data"]
            date_published = date_published or normalized_text(data.get("datePublished"))
            date_modified = date_modified or normalized_text(data.get("dateModified"))
            raw_author = data.get("author")
            if not author and isinstance(raw_author, dict):
                author = normalized_text(raw_author.get("name"))

    og_images = [meta_value(document, prop="og:image")]
    twitter_images = [meta_value(document, name="twitter:image")]
    asset_urls = [value for value in og_images + twitter_images if value]

    return {
        "file": path.relative_to(ROOT).as_posix(),
        "production_url": production_url,
        "title": normalized_text(title_nodes[0]) if title_nodes else "",
        "description": meta_value(document, name="description"),
        "canonical": canonicals[0] if canonicals else "",
        "canonical_count": len(canonicals),
        "canonical_values": canonicals,
        "robots_meta": meta_value(document, name="robots"),
        "googlebot_meta": meta_value(document, name="googlebot"),
        "lang": normalized_text(root_node.get("lang")) if root_node is not None else "",
        "dir": normalized_text(root_node.get("dir")) if root_node is not None else "",
        "h1_count": len(h1_nodes),
        "h1": " | ".join(h1_nodes)[:1500],
        "og_title": meta_value(document, prop="og:title"),
        "og_description": meta_value(document, prop="og:description"),
        "og_url": meta_value(document, prop="og:url"),
        "og_image": meta_value(document, prop="og:image"),
        "twitter_card": meta_value(document, name="twitter:card"),
        "twitter_title": meta_value(document, name="twitter:title"),
        "twitter_description": meta_value(document, name="twitter:description"),
        "twitter_image": meta_value(document, name="twitter:image"),
        "author": author,
        "date_published": date_published,
        "date_modified": date_modified,
        "word_count": len(words),
        "schema_blocks": len(schemas),
        "schema_types": sorted(set(collected_types)),
        "schema_errors": sum(1 for schema in schemas if not schema["valid_json"]),
        "schemas": schemas,
        "links": links,
        "images": images,
        "asset_urls": asset_urls,
        "parse_error": "",
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def parse_sitemap(path: Path) -> list[dict[str, str]]:
    root = etree.fromstring(path.read_bytes())
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    rows: list[dict[str, str]] = []
    for node in root.xpath("//sm:url", namespaces=namespace):
        def first(tag: str) -> str:
            values = node.xpath(f"sm:{tag}/text()", namespaces=namespace)
            return normalized_text(values[0]) if values else ""

        rows.append({"loc": first("loc"), "lastmod": first("lastmod"), "changefreq": first("changefreq"), "priority": first("priority")})
    return rows


def local_target_path(url: str) -> Path | None:
    parsed = urllib.parse.urlsplit(url)
    if (parsed.hostname or "").lower() not in {"ezhalhe-sa.com", "www.ezhalhe-sa.com"}:
        return None
    decoded = urllib.parse.unquote(parsed.path).lstrip("/")
    if not decoded:
        decoded = "index.html"
    return ROOT / Path(decoded)


def local_file_size(url: str) -> int | str:
    path = local_target_path(url)
    if path and path.is_file():
        return path.stat().st_size
    return ""


def parse_redirect_configs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    vercel_path = ROOT / "vercel.json"
    if vercel_path.exists():
        data = json.loads(vercel_path.read_text(encoding="utf-8-sig"))
        for redirect in data.get("redirects", []):
            rows.append({"platform": "Vercel", "source": redirect.get("source", ""), "destination": redirect.get("destination", ""), "configured_type": "permanent" if redirect.get("permanent") else "temporary"})
    firebase_path = ROOT / "firebase.json"
    if firebase_path.exists():
        data = json.loads(firebase_path.read_text(encoding="utf-8-sig"))
        for hosting in data.get("hosting", []):
            target = hosting.get("target", "default")
            for redirect in hosting.get("redirects", []):
                rows.append({"platform": f"Firebase:{target}", "source": redirect.get("source", ""), "destination": redirect.get("destination", ""), "configured_type": redirect.get("type", "")})
    return rows


def header_value(result: dict[str, Any], name: str) -> str:
    return result.get("headers", {}).get(name.lower(), "")


def compact_chain(result: dict[str, Any]) -> str:
    chain = result.get("redirect_chain", [])
    if not chain:
        return ""
    return " -> ".join(f"{item['status']} {item['location']}" for item in chain)


def is_soft_404(result: dict[str, Any]) -> bool:
    if result.get("final_status") != 200:
        return False
    title_match = re.search(r"(404|not found|غير موجود|لم يتم العثور)", result.get("body_text", "")[:5000], re.I)
    requested_path = urllib.parse.urlsplit(result.get("requested_url", "")).path
    final_path = urllib.parse.urlsplit(result.get("final_url", "")).path
    home_redirect = requested_path not in {"", "/", "/index.html"} and final_path in {"", "/"} and result.get("redirect_count", 0) > 0
    return bool(title_match or home_redirect)


def hash_project_files(output_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    ignored_roots = {".git", "reports", "outputs", "__pycache__"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative.parts and relative.parts[0] in ignored_roots:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        rows.append({"sha256": digest, "size_bytes": path.stat().st_size, "path": relative.as_posix()})
    checksum_path = output_dir / "file-checksums.txt"
    checksum_path.write_text("".join(f"{row['sha256']}  {row['path']}\n" for row in rows), encoding="utf-8")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the immutable Phase 1 SEO baseline package.")
    parser.add_argument("--output", required=True, help="Output directory relative to the project root or absolute.")
    args = parser.parse_args()
    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now(ZoneInfo("Asia/Riyadh")).isoformat(timespec="seconds")
    local_html_files = sorted(path for path in ROOT.rglob("*.html") if ".git" not in path.parts and "reports" not in path.parts and "outputs" not in path.parts)
    pages = [parse_local_page(path) for path in local_html_files]
    page_by_url = {canonical_url_key(page.get("production_url", "")): page for page in pages if page.get("production_url")}

    sitemap_path = ROOT / "sitemap.xml"
    sitemap_rows = parse_sitemap(sitemap_path) if sitemap_path.exists() else []
    sitemap_counts = Counter(canonical_url_key(row["loc"]) for row in sitemap_rows)
    sitemap_keys = set(sitemap_counts)
    redirect_configs = parse_redirect_configs()

    all_links = [link for page in pages for link in page.get("links", [])]
    all_images = [image for page in pages for image in page.get("images", [])]
    urls_to_fetch: set[str] = {page["production_url"] for page in pages if page.get("production_url")}
    urls_to_fetch.update(row["loc"] for row in sitemap_rows if row.get("loc"))
    urls_to_fetch.update(page["canonical"] for page in pages if page.get("canonical"))
    urls_to_fetch.update(link["resolved_url"] for link in all_links if link.get("is_internal") and link.get("resolved_url"))
    urls_to_fetch.update(image["resolved_url"] for image in all_images if image.get("is_internal") and image.get("resolved_url"))
    urls_to_fetch.update(asset for page in pages for asset in page.get("asset_urls", []) if asset.startswith((PRODUCTION_ORIGIN, NON_WWW_ORIGIN, "/")))
    urls_to_fetch.update(f"{PRODUCTION_ORIGIN}{row['source']}" for row in redirect_configs if row.get("source"))
    urls_to_fetch.update(
        {
            "http://ezhalhe-sa.com/",
            "https://ezhalhe-sa.com/",
            "http://www.ezhalhe-sa.com/",
            "https://www.ezhalhe-sa.com/",
            f"{PRODUCTION_ORIGIN}/robots.txt",
            f"{PRODUCTION_ORIGIN}/sitemap.xml",
            f"{PRODUCTION_ORIGIN}/favicon.ico",
            f"{PRODUCTION_ORIGIN}/manifest.json",
            f"{PRODUCTION_ORIGIN}/site.webmanifest",
            f"{PRODUCTION_ORIGIN}/browserconfig.xml",
            f"{PRODUCTION_ORIGIN}/google387142411d334808.html",
            f"{PRODUCTION_ORIGIN}/BingSiteAuth.xml",
        }
    )
    urls_to_fetch = {url for url in urls_to_fetch if url and urllib.parse.urlsplit(url).scheme in {"http", "https"}}

    fetch_results: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(fetch_url, url): url for url in sorted(urls_to_fetch)}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"requested_url": url, "initial_status": 0, "final_status": 0, "final_url": "", "redirect_count": 0, "redirect_chain": [], "headers": {}, "body": b"", "body_text": "", "error": f"{type(exc).__name__}: {exc}"}
            fetch_results[canonical_url_key(url)] = result

    def result_for(url: str) -> dict[str, Any]:
        return fetch_results.get(canonical_url_key(url), {"requested_url": url, "initial_status": 0, "final_status": 0, "final_url": "", "redirect_count": 0, "redirect_chain": [], "headers": {}, "body": b"", "body_text": "", "error": "not fetched"})

    url_rows: list[dict[str, Any]] = []
    candidate_urls = sorted(set(urls_to_fetch), key=canonical_url_key)
    for url in candidate_urls:
        result = result_for(url)
        page = page_by_url.get(canonical_url_key(url), {})
        sources: list[str] = []
        if page:
            sources.append("local-html")
        if canonical_url_key(url) in sitemap_keys:
            sources.append("sitemap")
        if any(canonical_url_key(link.get("resolved_url", "")) == canonical_url_key(url) for link in all_links):
            sources.append("internal-link")
        if any(canonical_url_key(image.get("resolved_url", "")) == canonical_url_key(url) for image in all_images):
            sources.append("image")
        url_rows.append(
            {
                "requested_url": url,
                "source_types": "|".join(sources) or "important-file/config/host",
                "local_file": page.get("file", ""),
                "initial_status": result.get("initial_status", 0),
                "final_status": result.get("final_status", 0),
                "final_url": result.get("final_url", ""),
                "redirect_count": result.get("redirect_count", 0),
                "redirect_chain": compact_chain(result),
                "soft_404_suspected": is_soft_404(result),
                "indexability_baseline": "blocked" if result.get("final_status") != 200 or "noindex" in page.get("robots_meta", "").lower() or "noindex" in header_value(result, "x-robots-tag").lower() else "indexable",
                "in_sitemap": canonical_url_key(url) in sitemap_keys,
                "canonical": page.get("canonical", ""),
                "title": page.get("title", ""),
                "error": result.get("error", ""),
            }
        )

    metadata_rows: list[dict[str, Any]] = []
    canonical_rows: list[dict[str, Any]] = []
    schema_inventory: list[dict[str, Any]] = []
    content_rows: list[dict[str, Any]] = []
    for page in pages:
        result = result_for(page.get("production_url", ""))
        canonical_result = result_for(page.get("canonical", "")) if page.get("canonical") else {}
        metadata_rows.append(
            {
                "file": page.get("file", ""), "url": page.get("production_url", ""), "live_status": result.get("final_status", 0),
                "title": page.get("title", ""), "title_length": len(page.get("title", "")), "description": page.get("description", ""), "description_length": len(page.get("description", "")),
                "canonical": page.get("canonical", ""), "canonical_count": page.get("canonical_count", 0), "robots_meta": page.get("robots_meta", ""), "googlebot_meta": page.get("googlebot_meta", ""),
                "lang": page.get("lang", ""), "dir": page.get("dir", ""), "h1_count": page.get("h1_count", 0), "h1": page.get("h1", ""),
                "og_title": page.get("og_title", ""), "og_description": page.get("og_description", ""), "og_url": page.get("og_url", ""), "og_image": page.get("og_image", ""),
                "twitter_card": page.get("twitter_card", ""), "twitter_title": page.get("twitter_title", ""), "twitter_description": page.get("twitter_description", ""), "twitter_image": page.get("twitter_image", ""),
                "author": page.get("author", ""), "date_published": page.get("date_published", ""), "date_modified": page.get("date_modified", ""),
                "schema_blocks": page.get("schema_blocks", 0), "schema_types": "|".join(page.get("schema_types", [])), "schema_errors": page.get("schema_errors", 0), "parse_error": page.get("parse_error", ""),
            }
        )
        canonical_rows.append(
            {
                "file": page.get("file", ""), "page_url": page.get("production_url", ""), "page_status": result.get("final_status", 0), "canonical": page.get("canonical", ""),
                "canonical_count": page.get("canonical_count", 0), "canonical_status": canonical_result.get("final_status", "") if canonical_result else "", "canonical_final_url": canonical_result.get("final_url", "") if canonical_result else "",
                "self_referencing": canonical_url_key(page.get("production_url", "")) == canonical_url_key(page.get("canonical", "")),
                "canonical_host": urllib.parse.urlsplit(page.get("canonical", "")).hostname or "", "intended_host": "www.ezhalhe-sa.com",
                "issue": "missing" if not page.get("canonical") else ("multiple" if page.get("canonical_count", 0) != 1 else ("non-www" if (urllib.parse.urlsplit(page.get("canonical", "")).hostname or "").lower() == "ezhalhe-sa.com" else "")),
            }
        )
        schema_inventory.append({"file": page.get("file", ""), "url": page.get("production_url", ""), "blocks": page.get("schemas", [])})
        content_rows.append(
            {
                "file": page.get("file", ""), "url": page.get("production_url", ""), "word_count": page.get("word_count", 0), "author": page.get("author", ""),
                "date_published": page.get("date_published", ""), "date_modified": page.get("date_modified", ""), "internal_outlinks": sum(1 for link in page.get("links", []) if link.get("is_internal")),
                "external_outlinks": sum(1 for link in page.get("links", []) if link.get("resolved_url") and not link.get("is_internal")),
            }
        )

    link_rows: list[dict[str, Any]] = []
    broken_rows: list[dict[str, Any]] = []
    redirected_link_rows: list[dict[str, Any]] = []
    inbound = defaultdict(set)
    for link in all_links:
        resolved = link.get("resolved_url", "")
        result = result_for(resolved) if link.get("is_internal") and resolved else {}
        row = {
            **link,
            "target_initial_status": result.get("initial_status", "") if result else "",
            "target_final_status": result.get("final_status", "") if result else "",
            "target_final_url": result.get("final_url", "") if result else "",
            "redirect_count": result.get("redirect_count", "") if result else "",
            "local_target_exists": bool(local_target_path(resolved) and local_target_path(resolved).is_file()) if link.get("is_internal") and resolved else "",
        }
        link_rows.append(row)
        if link.get("is_internal") and resolved:
            inbound[canonical_url_key(resolved)].add(link.get("source_url", ""))
            if result.get("final_status", 0) >= 400 or result.get("final_status", 0) == 0:
                broken_rows.append(row)
            if result.get("redirect_count", 0) > 0:
                redirected_link_rows.append({**row, "redirect_chain": compact_chain(result)})

    orphan_rows: list[dict[str, Any]] = []
    for page in pages:
        url = page.get("production_url", "")
        inlinks = inbound.get(canonical_url_key(url), set())
        if not inlinks:
            orphan_rows.append({"file": page.get("file", ""), "url": url, "live_status": result_for(url).get("final_status", 0), "in_sitemap": canonical_url_key(url) in sitemap_keys, "inbound_internal_pages": 0})

    image_rows: list[dict[str, Any]] = []
    for item in all_images:
        result = result_for(item.get("resolved_url", "")) if item.get("is_internal") else {}
        image_rows.append(
            {
                **item,
                "local_file_exists": bool(local_target_path(item.get("resolved_url", "")) and local_target_path(item.get("resolved_url", "")).is_file()) if item.get("is_internal") else "",
                "local_size_bytes": local_file_size(item.get("resolved_url", "")) if item.get("is_internal") else "",
                "live_status": result.get("final_status", "") if result else "",
                "has_dimensions": bool(item.get("width") and item.get("height")),
                "has_responsive_srcset": bool(item.get("srcset")),
            }
        )

    sitemap_inventory: list[dict[str, Any]] = []
    for index, row in enumerate(sitemap_rows, start=1):
        result = result_for(row["loc"])
        local_page = page_by_url.get(canonical_url_key(row["loc"].replace(NON_WWW_ORIGIN, PRODUCTION_ORIGIN, 1)), {})
        sitemap_inventory.append(
            {
                "position": index, **row, "duplicate_count": sitemap_counts[canonical_url_key(row["loc"])],
                "initial_status": result.get("initial_status", 0), "final_status": result.get("final_status", 0), "final_url": result.get("final_url", ""),
                "redirect_count": result.get("redirect_count", 0), "canonical": local_page.get("canonical", ""), "canonical_matches_loc": canonical_url_key(local_page.get("canonical", "")) == canonical_url_key(row["loc"]),
            }
        )

    redirect_rows: list[dict[str, Any]] = []
    for config in redirect_configs:
        source_url = f"{PRODUCTION_ORIGIN}{config['source']}"
        result = result_for(source_url)
        redirect_rows.append({**config, "source_url": source_url, "live_initial_status": result.get("initial_status", 0), "live_final_status": result.get("final_status", 0), "live_final_url": result.get("final_url", ""), "live_redirect_count": result.get("redirect_count", 0), "live_chain": compact_chain(result), "destination_relevance_review": "required" if config.get("destination") == "/" and config.get("source") not in {"/index.html", "/data-analysis.html"} else ""})
    for source_url in ["http://ezhalhe-sa.com/", "https://ezhalhe-sa.com/", "http://www.ezhalhe-sa.com/", "https://www.ezhalhe-sa.com/"]:
        result = result_for(source_url)
        redirect_rows.append({"platform": "Live host", "source": urllib.parse.urlsplit(source_url).path or "/", "destination": "", "configured_type": "", "source_url": source_url, "live_initial_status": result.get("initial_status", 0), "live_final_status": result.get("final_status", 0), "live_final_url": result.get("final_url", ""), "live_redirect_count": result.get("redirect_count", 0), "live_chain": compact_chain(result), "destination_relevance_review": ""})

    headers_rows: list[dict[str, Any]] = []
    for row in url_rows:
        if "local-html" not in row["source_types"] and row["requested_url"] not in {f"{PRODUCTION_ORIGIN}/robots.txt", f"{PRODUCTION_ORIGIN}/sitemap.xml"}:
            continue
        result = result_for(row["requested_url"])
        headers_rows.append(
            {
                "requested_url": row["requested_url"], "initial_status": result.get("initial_status", 0), "final_status": result.get("final_status", 0), "final_url": result.get("final_url", ""), "redirect_count": result.get("redirect_count", 0), "redirect_chain": compact_chain(result),
                "content_type": header_value(result, "content-type"), "content_length": header_value(result, "content-length"), "cache_control": header_value(result, "cache-control"), "x_robots_tag": header_value(result, "x-robots-tag"),
                "x_content_type_options": header_value(result, "x-content-type-options"), "x_frame_options": header_value(result, "x-frame-options"), "referrer_policy": header_value(result, "referrer-policy"),
                "content_security_policy": header_value(result, "content-security-policy"), "permissions_policy": header_value(result, "permissions-policy"), "strict_transport_security": header_value(result, "strict-transport-security"),
                "server": header_value(result, "server"), "x_vercel_id": header_value(result, "x-vercel-id"), "error": result.get("error", ""),
            }
        )

    important_specs = [
        ("robots.txt", "robots", True), ("sitemap.xml", "sitemap", True), ("favicon.ico", "favicon", False), ("manifest.json", "manifest", False),
        ("site.webmanifest", "manifest", False), ("browserconfig.xml", "browserconfig", False), ("google387142411d334808.html", "google-verification", True), ("BingSiteAuth.xml", "bing-verification", False),
    ]
    important_rows: list[dict[str, Any]] = []
    for relative, kind, expected in important_specs:
        live_url = f"{PRODUCTION_ORIGIN}/{relative}"
        result = result_for(live_url)
        important_rows.append({"kind": kind, "reference": relative, "required_or_expected": expected, "local_exists": (ROOT / relative).is_file(), "live_url": live_url, "live_status": result.get("final_status", 0), "final_url": result.get("final_url", ""), "notes": ""})
    for page in pages:
        for label, value in [("Open Graph image", page.get("og_image", "")), ("Twitter image", page.get("twitter_image", ""))]:
            if not value:
                continue
            resolved = urllib.parse.urljoin(page.get("production_url", ""), value)
            result = result_for(resolved)
            important_rows.append({"kind": label, "reference": page.get("file", ""), "required_or_expected": True, "local_exists": bool(local_target_path(resolved) and local_target_path(resolved).is_file()), "live_url": resolved, "live_status": result.get("final_status", 0), "final_url": result.get("final_url", ""), "notes": ""})
    important_rows.append({"kind": "favicon", "reference": "index.html inline data URI", "required_or_expected": True, "local_exists": True, "live_url": "inline", "live_status": "embedded", "final_url": "", "notes": "Homepage uses an inline SVG data URI; color compliance requires review."})

    search_console_rows = [
        {"area": area, "status": "ACCESS_DENIED_REQUIRES_OWNER_EXPORT", "source": "Google Search Console", "as_of": generated_at, "notes": "The authenticated read-only check returned no access to the URL-prefix property. No Search Console data was read. Structural URL decisions remain blocked until an owner export or authorized account is provided."}
        for area in ["Performance: queries", "Performance: pages", "Page indexing", "Core Web Vitals", "Sitemaps", "Manual actions", "Security issues", "Crawl stats", "URL inspection: critical pages", "Links: external pages"]
    ]
    keywords = [
        "تصميم متجر سلة", "تصميم متجر زد", "إنشاء متجر إلكتروني", "فتح متجر إلكتروني", "دخول التجارة الالكترونية", "تصميم متجر", "تصميم متجر سلة وزد",
        "تصميم متجر احترافي", "تصميم متجر إلكتروني السعودية", "مطور سلة", "مطور زد", "خدمات سلة", "خدمات زد", "SEO سلة", "SEO زد",
    ]
    keyword_rows = [{"query": keyword, "country": "Saudi Arabia", "device": "mobile|desktop", "baseline_source": "Google Search Console", "clicks": "", "impressions": "", "ctr": "", "average_position": "", "status": "REQUIRES_AUTHENTICATED_EXPORT", "as_of": generated_at} for keyword in keywords]
    backlink_rows = [
        {"url": page.get("production_url", ""), "local_file": page.get("file", ""), "gsc_external_links": "", "third_party_backlinks": "", "referring_domains": "", "evidence_status": "UNKNOWN_REQUIRES_EXPORT", "url_change_allowed": "No", "preservation_rule": "Keep URL or approved direct permanent redirect to exact equivalent."}
        for page in pages
    ]

    approved_brand_colors = {"#15B5B0", "#0D2224", "#3BBBC2", "#FFFFFF", "#555555"}
    color_counts: Counter[str] = Counter()
    color_files: defaultdict[str, set[str]] = defaultdict(set)
    for asset_path in sorted(list(ROOT.rglob("*.html")) + list(ROOT.rglob("*.css"))):
        if any(part in {".git", "reports", "outputs"} for part in asset_path.parts):
            continue
        asset_text = asset_path.read_text(encoding="utf-8-sig", errors="replace")
        for match in re.findall(r"#(?:[0-9A-Fa-f]{8}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{3})\b", asset_text):
            value = match.upper()
            if len(value) == 4:
                value = "#" + "".join(character * 2 for character in value[1:])
            elif len(value) == 5:
                value = "#" + "".join(character * 2 for character in value[1:])
            color_counts[value] += 1
            color_files[value].add(asset_path.relative_to(ROOT).as_posix())
    brand_color_rows = [
        {"color": color, "approved_exact_brand_color": color in approved_brand_colors, "occurrences": count, "file_count": len(color_files[color]), "files": "|".join(sorted(color_files[color]))}
        for color, count in sorted(color_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    write_csv(output_dir / "url-inventory.csv", url_rows, ["requested_url", "source_types", "local_file", "initial_status", "final_status", "final_url", "redirect_count", "redirect_chain", "soft_404_suspected", "indexability_baseline", "in_sitemap", "canonical", "title", "error"])
    write_csv(output_dir / "metadata-inventory.csv", metadata_rows, ["file", "url", "live_status", "title", "title_length", "description", "description_length", "canonical", "canonical_count", "robots_meta", "googlebot_meta", "lang", "dir", "h1_count", "h1", "og_title", "og_description", "og_url", "og_image", "twitter_card", "twitter_title", "twitter_description", "twitter_image", "author", "date_published", "date_modified", "schema_blocks", "schema_types", "schema_errors", "parse_error"])
    write_csv(output_dir / "canonical-map.csv", canonical_rows, ["file", "page_url", "page_status", "canonical", "canonical_count", "canonical_status", "canonical_final_url", "self_referencing", "canonical_host", "intended_host", "issue"])
    write_csv(output_dir / "redirect-baseline.csv", redirect_rows, ["platform", "source", "destination", "configured_type", "source_url", "live_initial_status", "live_final_status", "live_final_url", "live_redirect_count", "live_chain", "destination_relevance_review"])
    write_csv(output_dir / "internal-link-graph.csv", link_rows, ["source_file", "source_url", "raw_href", "resolved_url", "is_internal", "anchor_text", "rel", "target", "target_initial_status", "target_final_status", "target_final_url", "redirect_count", "local_target_exists"])
    write_csv(output_dir / "broken-links.csv", broken_rows, ["source_file", "source_url", "raw_href", "resolved_url", "anchor_text", "target_initial_status", "target_final_status", "target_final_url", "redirect_count", "local_target_exists"])
    write_csv(output_dir / "redirected-internal-links.csv", redirected_link_rows, ["source_file", "source_url", "raw_href", "resolved_url", "anchor_text", "target_initial_status", "target_final_status", "target_final_url", "redirect_count", "redirect_chain"])
    write_csv(output_dir / "orphan-pages.csv", orphan_rows, ["file", "url", "live_status", "in_sitemap", "inbound_internal_pages"])
    write_csv(output_dir / "sitemap-inventory.csv", sitemap_inventory, ["position", "loc", "lastmod", "changefreq", "priority", "duplicate_count", "initial_status", "final_status", "final_url", "redirect_count", "canonical", "canonical_matches_loc"])
    write_csv(output_dir / "http-status-and-headers.csv", headers_rows, ["requested_url", "initial_status", "final_status", "final_url", "redirect_count", "redirect_chain", "content_type", "content_length", "cache_control", "x_robots_tag", "x_content_type_options", "x_frame_options", "referrer_policy", "content_security_policy", "permissions_policy", "strict_transport_security", "server", "x_vercel_id", "error"])
    write_csv(output_dir / "important-files-inventory.csv", important_rows, ["kind", "reference", "required_or_expected", "local_exists", "live_url", "live_status", "final_url", "notes"])
    write_csv(output_dir / "image-inventory.csv", image_rows, ["source_file", "source_url", "raw_src", "resolved_url", "is_internal", "local_file_exists", "local_size_bytes", "live_status", "alt", "width", "height", "has_dimensions", "loading", "decoding", "fetchpriority", "srcset", "has_responsive_srcset"])
    write_csv(output_dir / "content-inventory.csv", content_rows, ["file", "url", "word_count", "author", "date_published", "date_modified", "internal_outlinks", "external_outlinks"])
    write_csv(output_dir / "search-console-baseline.csv", search_console_rows, ["area", "status", "source", "as_of", "notes"])
    write_csv(output_dir / "keyword-baseline.csv", keyword_rows, ["query", "country", "device", "baseline_source", "clicks", "impressions", "ctr", "average_position", "status", "as_of"])
    write_csv(output_dir / "backlink-targets.csv", backlink_rows, ["url", "local_file", "gsc_external_links", "third_party_backlinks", "referring_domains", "evidence_status", "url_change_allowed", "preservation_rule"])
    write_csv(output_dir / "brand-color-inventory.csv", brand_color_rows, ["color", "approved_exact_brand_color", "occurrences", "file_count", "files"])

    (output_dir / "structured-data-inventory.json").write_text(json.dumps({"generated_at": generated_at, "pages": schema_inventory}, ensure_ascii=False, indent=2), encoding="utf-8")

    live_sitemap = result_for(f"{PRODUCTION_ORIGIN}/sitemap.xml")
    live_robots = result_for(f"{PRODUCTION_ORIGIN}/robots.txt")
    (output_dir / "sitemap-snapshot.xml").write_text(live_sitemap.get("body_text", ""), encoding="utf-8")
    (output_dir / "robots-snapshot.txt").write_text(live_robots.get("body_text", ""), encoding="utf-8")
    if sitemap_path.exists():
        shutil.copyfile(sitemap_path, output_dir / "repository-sitemap-snapshot.xml")
    if (ROOT / "robots.txt").exists():
        shutil.copyfile(ROOT / "robots.txt", output_dir / "repository-robots-snapshot.txt")

    hash_rows = hash_project_files(output_dir)
    metrics = {
        "generated_at": generated_at,
        "production_origin": PRODUCTION_ORIGIN,
        "local_html_files": len(pages),
        "live_urls_tested": len(url_rows),
        "sitemap_entries": len(sitemap_rows),
        "sitemap_unique_urls": len(sitemap_counts),
        "sitemap_duplicate_entries": sum(count - 1 for count in sitemap_counts.values() if count > 1),
        "sitemap_non_200_final": sum(1 for row in sitemap_inventory if row["final_status"] != 200),
        "sitemap_redirecting": sum(1 for row in sitemap_inventory if row["redirect_count"] > 0),
        "pages_missing_canonical": sum(1 for row in canonical_rows if row["issue"] == "missing"),
        "pages_non_www_canonical": sum(1 for row in canonical_rows if row["issue"] == "non-www"),
        "pages_multiple_canonical": sum(1 for row in canonical_rows if row["issue"] == "multiple"),
        "pages_with_schema": sum(1 for page in pages if page.get("schema_blocks", 0) > 0),
        "schema_json_errors": sum(page.get("schema_errors", 0) for page in pages),
        "internal_links": sum(1 for row in link_rows if row.get("is_internal")),
        "broken_internal_link_occurrences": len(broken_rows),
        "redirected_internal_link_occurrences": len(redirected_link_rows),
        "orphan_pages": len(orphan_rows),
        "image_occurrences": len(image_rows),
        "images_without_dimensions": sum(1 for row in image_rows if not row["has_dimensions"]),
        "images_without_lazy_loading": sum(1 for row in image_rows if not row.get("loading")),
        "project_files_hashed": len(hash_rows),
        "unique_hex_colors": len(brand_color_rows),
        "non_approved_hex_colors": sum(1 for row in brand_color_rows if not row["approved_exact_brand_color"]),
        "approved_brand_color_occurrences": {color: color_counts.get(color, 0) for color in sorted(approved_brand_colors)},
        "search_console_status": "ACCESS_DENIED_REQUIRES_OWNER_EXPORT",
        "backlink_status": "REQUIRES_AUTHENTICATED_EXPORT",
        "production_changed": False,
        "existing_site_files_modified": False,
    }
    (output_dir / "audit-metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest_files = []
    for path in sorted(output_dir.iterdir()):
        if path.is_file() and path.name != "baseline-package-checksums.txt":
            manifest_files.append({"file": path.name, "size_bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    (output_dir / "baseline-manifest.json").write_text(json.dumps({"generated_at": generated_at, "files": manifest_files}, ensure_ascii=False, indent=2), encoding="utf-8")
    checksum_lines = [f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in sorted(output_dir.iterdir()) if path.is_file() and path.name != "baseline-package-checksums.txt"]
    (output_dir / "baseline-package-checksums.txt").write_text("".join(checksum_lines), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
