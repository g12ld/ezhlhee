from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "09-staging-release"
DEFAULT_DEPLOYMENT = "https://ezhlhee-ohd8c23bi-g12lds-projects.vercel.app"


def get_bypass_token() -> str:
    command = ["vercel.cmd", "curl", "/", "--deployment", DEPLOYMENT, "--debug", "--", "--head", "--silent"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45, check=False)
    combined = result.stdout + "\n" + result.stderr
    patterns = [
        r"x-vercel-protection-bypass[=: ]+([A-Za-z0-9_-]+)",
        r"protection-bypass[=: ]+([A-Za-z0-9_-]+)",
        r"_vercel_jwt[=: ]+([A-Za-z0-9._-]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, combined, flags=re.I)
        if match:
            return match.group(1)
    raise RuntimeError("Vercel protection bypass credential was not available to the authenticated CLI.")


def vercel_request(path: str, method: str = "HEAD", data: str | None = None) -> dict[str, object]:
    url = DEPLOYMENT.rstrip("/") + path
    curl_args = ["curl.exe", "--silent", "--show-error", "--dump-header", "-", "--request", method, "--header", f"x-vercel-protection-bypass: {BYPASS_TOKEN}"]
    if method == "HEAD":
        curl_args.append("--head")
    if data is not None:
        curl_args.extend(["--header", "Content-Type: application/json", "--data", data])
    curl_args.append(url)
    result = subprocess.run(curl_args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=45, check=False)
    output = result.stdout
    status_matches = re.findall(r"HTTP/\d(?:\.\d)?\s+(\d{3})", output)
    status = int(status_matches[-1]) if status_matches else 0
    header_block = output.split("\r\n\r\n", 1)[0] if "\r\n\r\n" in output else output.split("\n\n", 1)[0]
    headers: dict[str, str] = {}
    for line in header_block.splitlines()[1:]:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    body = output[len(header_block):].lstrip("\r\n")
    return {"path": path, "method": method, "status": status, "headers": headers, "body": body, "stderr": result.stderr[-1000:], "exit_code": result.returncode}


def sitemap_paths() -> list[str]:
    root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    paths = []
    for loc in root.findall("sm:url/sm:loc", namespace):
        paths.append(urlsplit(loc.text or "").path or "/")
    return paths


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    paths = sitemap_paths()
    crawl_rows: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=18) as pool:
        future_map = {pool.submit(vercel_request, path): path for path in paths}
        for future in as_completed(future_map):
            try:
                response = future.result()
            except Exception as error:  # noqa: BLE001
                response = {"path": future_map[future], "status": 0, "headers": {}, "stderr": str(error)}
            crawl_rows.append({
                "path": response["path"],
                "status": response["status"],
                "content_type": response.get("headers", {}).get("content-type", ""),
                "location": response.get("headers", {}).get("location", ""),
                "error": response.get("stderr", "") if response["status"] == 0 else "",
            })
    crawl_rows.sort(key=lambda row: str(row["path"]))

    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    redirects = config.get("redirects", [])
    path_redirects = [item for item in redirects if not item.get("has")]
    host_redirects = [item for item in redirects if item.get("has")]
    redirect_sources = {item["source"] for item in path_redirects}
    destinations = {urlsplit(item["destination"]).path or "/" for item in path_redirects}
    static_chains = sorted(source for source in redirect_sources if source in destinations)
    sample_indices = sorted({0, 1, 2, 3, 10, 25, 50, 75, 100, 125, 150, len(path_redirects) - 1})
    redirect_samples = [path_redirects[index] for index in sample_indices if 0 <= index < len(path_redirects)]
    runtime_redirects: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        future_map = {pool.submit(vercel_request, item["source"]): item for item in redirect_samples}
        for future in as_completed(future_map):
            item = future_map[future]
            response = future.result()
            runtime_redirects.append({
                "source": item["source"],
                "expected_destination": item["destination"],
                "status": response["status"],
                "location": response.get("headers", {}).get("location", ""),
                "permanent": item.get("permanent") is True,
            })
    runtime_redirects.sort(key=lambda row: str(row["source"]))

    homepage = vercel_request("/", method="GET")
    robots = vercel_request("/robots.txt", method="GET")
    sitemap = vercel_request("/sitemap.xml", method="GET")
    missing = vercel_request("/definitely-not-a-real-page", method="GET")
    asset = vercel_request("/images/og-cover.webp")
    api_get = vercel_request("/api/contact", method="GET")
    api_invalid = vercel_request("/api/contact", method="POST", data='{"name":"","email":"","message":"","website":"","startedAt":1}')
    api_unconfigured = vercel_request("/api/contact", method="POST", data='{"name":"Staging Validation","email":"staging@example.com","message":"Gold Pro release gate validation only.","website":"","startedAt":1}')

    required_headers = {
        "content-security-policy",
        "strict-transport-security",
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
        "permissions-policy",
        "cross-origin-opener-policy",
    }
    home_headers = homepage.get("headers", {})
    crawl_failures = [row for row in crawl_rows if row["status"] != 200]
    runtime_redirect_failures = [row for row in runtime_redirects if row["status"] not in {301, 308} or row["location"] != row["expected_destination"]]
    sitemap_text = str(sitemap.get("body", ""))
    robots_text = str(robots.get("body", ""))
    api_text = " ".join(str(item.get("body", "")) for item in [api_get, api_invalid, api_unconfigured])

    checks = {
        "preview_is_protected_from_indexing": home_headers.get("x-robots-tag") == "noindex",
        "all_119_sitemap_pages_return_200": len(paths) == 119 and not crawl_failures,
        "all_redirects_are_permanent_and_chain_free": len(path_redirects) == 204 and all(item.get("permanent") is True for item in redirects) and not static_chains,
        "apex_host_redirect_is_atomic": len(host_redirects) == 1 and host_redirects[0].get("source") == "/:path*" and host_redirects[0].get("destination") == "https://www.ezhalhe-sa.com/:path*",
        "runtime_redirect_sample_matches_map": not runtime_redirect_failures,
        "security_headers_complete": required_headers.issubset(home_headers),
        "robots_is_200_and_names_production_sitemap": robots["status"] == 200 and "https://www.ezhalhe-sa.com/sitemap.xml" in robots_text,
        "sitemap_is_200_and_www_only": sitemap["status"] == 200 and "https://www.ezhalhe-sa.com/" in sitemap_text and "https://ezhalhe-sa.com/" not in sitemap_text,
        "real_404_status": missing["status"] == 404,
        "webp_asset_is_served": asset["status"] == 200 and "image/webp" in asset.get("headers", {}).get("content-type", ""),
        "contact_get_rejected": api_get["status"] == 405,
        "contact_validation_rejects_bad_payload": api_invalid["status"] == 422,
        "contact_fails_closed_without_credentials": api_unconfigured["status"] == 503,
        "contact_responses_do_not_expose_secrets": not re.search(r"\d{8,12}:[A-Za-z0-9_-]{30,}", api_text),
    }
    passed = all(checks.values())

    with (REPORT_DIR / "staging-crawl.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "status", "content_type", "location", "error"])
        writer.writeheader()
        writer.writerows(crawl_rows)
    with (REPORT_DIR / "redirect-runtime-sample.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "expected_destination", "status", "location", "permanent"])
        writer.writeheader()
        writer.writerows(runtime_redirects)

    payload = {
        "status": "PASS" if passed else "FAIL",
        "deployment": DEPLOYMENT,
        "deployment_type": "protected Vercel preview (non-production)",
        "checks": checks,
        "summary": {
            "sitemap_pages_checked": len(paths),
            "sitemap_page_failures": len(crawl_failures),
            "redirects_static_checked": len(path_redirects),
            "host_redirects_static_checked": len(host_redirects),
            "redirect_runtime_samples": len(runtime_redirects),
            "redirect_runtime_failures": len(runtime_redirect_failures),
            "static_redirect_chains": len(static_chains),
            "security_headers": sorted(required_headers),
        },
        "failures": {
            "crawl": crawl_failures,
            "redirect_runtime": runtime_redirect_failures,
            "redirect_chains": static_chains,
        },
        "api_statuses": {"GET": api_get["status"], "invalid_POST": api_invalid["status"], "unconfigured_valid_POST": api_unconfigured["status"]},
        "notes": [
            "Vercel emits HTTP 308 for permanent redirects configured with permanent=true; the Firebase fallback retains explicit HTTP 301 rules.",
            "The contact endpoint intentionally returns 503 until the owner rotates the exposed Telegram token and supplies the replacement environment credentials.",
            "The preview deployment adds X-Robots-Tag: noindex through Vercel deployment protection; production indexing behavior is not changed.",
        ],
    }
    (REPORT_DIR / "staging-validation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Staging release validation", "", f"**Status:** {payload['status']}", "", f"**Protected preview:** `{DEPLOYMENT}`", "", "## Release gates", ""]
    for name, result in checks.items():
        lines.append(f"- {'PASS' if result else 'FAIL'} — `{name}`")
    lines.extend(["", "## Scope", "", f"- Sitemap pages runtime-crawled: {len(paths)}.", f"- Path redirects statically checked: {len(path_redirects)}; host redirects: {len(host_redirects)}; runtime samples: {len(runtime_redirects)}.", f"- Redirect chains: {len(static_chains)}.", "- Contact endpoint: 405 for GET, 422 for invalid data, 503 fail-closed without release credentials.", "- Production was not deployed or modified."])
    (REPORT_DIR / "staging-validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": payload["status"], **payload["summary"], "checks": checks}, ensure_ascii=False, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    DEPLOYMENT = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DEPLOYMENT
    BYPASS_TOKEN = get_bypass_token()
    main()
