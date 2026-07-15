#!/usr/bin/env python3
"""Validate secret removal, server-side contact handling, and headers."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "reports" / "roadmap-implementation" / "03-security"
TOKEN_RE = re.compile(r"[0-9]{8,12}:[A-Za-z0-9_-]{20,}")
REQUIRED_HEADERS = {
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
}


def main() -> None:
    results: list[dict[str, object]] = []

    def check(name: str, passed: bool, evidence: str) -> None:
        results.append({"check": name, "passed": passed, "evidence": evidence})

    secret_files = []
    direct_client_calls = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", "reports"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".html", ".txt", ".js", ".json", ".py"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if TOKEN_RE.search(content):
            secret_files.append(path.relative_to(ROOT).as_posix())
        if path.suffix.lower() == ".html" and "api.telegram.org" in content:
            direct_client_calls.append(path.relative_to(ROOT).as_posix())
    check("no-token-patterns", not secret_files, f"files={len(secret_files)}")
    check("no-client-telegram-calls", not direct_client_calls, f"files={len(direct_client_calls)}")

    index = (ROOT / "index.html").read_text(encoding="utf-8")
    check(
        "contact-form-server-endpoint",
        "fetch('/api/contact'" in index and "api.telegram.org" not in index,
        "Homepage submits only to the same-origin server endpoint",
    )
    check(
        "contact-form-accessibility",
        all(
            value in index
            for value in (
                'for="contact-name"',
                'for="contact-email"',
                'for="contact-message"',
                'id="contact-status"',
                'aria-live="polite"',
            )
        ),
        "Labels and live status are present",
    )

    endpoint = (ROOT / "api" / "contact.js").read_text(encoding="utf-8")
    check(
        "endpoint-env-only-secrets",
        "process.env.TELEGRAM_BOT_TOKEN" in endpoint
        and "process.env.TELEGRAM_CHAT_ID" in endpoint
        and not TOKEN_RE.search(endpoint),
        "Endpoint reads both credentials from environment variables",
    )
    check(
        "endpoint-defenses",
        all(
            value in endpoint
            for value in (
                "isSameOrigin",
                "rateLimitExceeded",
                "website",
                "MIN_FORM_COMPLETION_MS",
                "response.ok && payload?.ok === true",
                "AbortController",
            )
        ),
        "Origin, rate, honeypot, timing, response, and timeout defenses are present",
    )

    vercel = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    global_rule = next((rule for rule in vercel.get("headers", []) if rule.get("source") == "/(.*)"), None)
    header_names = {header["key"] for header in (global_rule or {}).get("headers", [])}
    check(
        "vercel-security-headers",
        REQUIRED_HEADERS <= header_names,
        f"required={len(REQUIRED_HEADERS)}, present={len(REQUIRED_HEADERS & header_names)}",
    )
    csp = next(
        (header["value"] for header in global_rule["headers"] if header["key"] == "Content-Security-Policy"),
        "",
    ) if global_rule else ""
    check(
        "csp-baseline",
        all(value in csp for value in ("default-src 'self'", "object-src 'none'", "frame-ancestors 'self'", "connect-src 'self'")),
        "CSP constrains default, object, framing, and API connections",
    )

    firebase = json.loads((ROOT / "firebase.json").read_text(encoding="utf-8"))
    firebase_ok = True
    for hosting in firebase.get("hosting", []):
        rule = next((item for item in hosting.get("headers", []) if item.get("source") == "**"), None)
        names = {header["key"] for header in (rule or {}).get("headers", [])}
        firebase_ok = firebase_ok and REQUIRED_HEADERS <= names and "api/**" in hosting.get("ignore", [])
    check(
        "firebase-header-parity",
        firebase_ok,
        "Both alternate Firebase hosting targets carry the same headers and exclude the Vercel API source",
    )

    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    check(
        "environment-template-safe",
        "TELEGRAM_BOT_TOKEN=" in env_example
        and "TELEGRAM_CHAT_ID=" in env_example
        and not TOKEN_RE.search(env_example),
        "Environment template contains names only",
    )

    passed = sum(1 for result in results if result["passed"])
    summary = {
        "checks": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "external_release_requirements": [
            "Revoke the compromised bot token in BotFather",
            "Create a replacement token",
            "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in Vercel staging and production",
        ],
        "results": results,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "validation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Security hardening validation",
        "",
        f"Result: {passed}/{len(results)} static checks passed.",
        "",
        "| Check | Result | Evidence |",
        "|---|---|---|",
    ]
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"| {result['check']} | {status} | {result['evidence']} |")
    lines.extend(
        [
            "",
            "## External release requirements",
            "",
            "- Revoke the compromised bot token in BotFather.",
            "- Create a replacement token.",
            "- Configure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in Vercel staging and production.",
            "- Run the authenticated staging form test before release approval.",
        ]
    )
    (REPORT_DIR / "validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
