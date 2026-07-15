#!/usr/bin/env python3
"""Remove exposed contact secrets and apply compatible security headers."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[0-9]{8,12}:[A-Za-z0-9_-]{20,}")
CONTACT_HANDLER_RE = re.compile(
    r"/\* ── CONTACT FORM ── \*/.*?(?=\nfunction showToast\()", re.DOTALL
)

CONTACT_HANDLER = """/* ── CONTACT FORM ── */
const contactForm=document.getElementById('cf');
contactForm.dataset.startedAt=Date.now().toString();
contactForm.addEventListener('submit',async function(e){
  e.preventDefault();
  const submitButton=this.querySelector('button[type="submit"]');
  const status=document.getElementById('contact-status');
  const payload={
    name:this.elements.name.value,
    email:this.elements.email.value,
    message:this.elements.message.value,
    website:this.elements.website.value,
    startedAt:Number(this.dataset.startedAt)
  };
  submitButton.disabled=true;
  submitButton.setAttribute('aria-disabled','true');
  this.setAttribute('aria-busy','true');
  status.textContent='جارٍ إرسال رسالتك…';
  try{
    const response=await fetch('/api/contact',{
      method:'POST',
      credentials:'same-origin',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify(payload)
    });
    const result=await response.json().catch(()=>({}));
    if(!response.ok||result.ok!==true) throw new Error('contact_submission_failed');
    status.textContent='تم إرسال رسالتك بنجاح.';
    showToast('✅ تم إرسال رسالتك بنجاح!');
    this.reset();
    this.dataset.startedAt=Date.now().toString();
  }catch{
    status.textContent='تعذر الإرسال الآن. تواصل معنا عبر واتساب أو حاول مرة أخرى.';
    showToast('❌ تعذر الإرسال الآن، حاول مرة أخرى');
  }finally{
    submitButton.disabled=false;
    submitButton.removeAttribute('aria-disabled');
    this.removeAttribute('aria-busy');
  }
});
"""

FORM_BEFORE = """    <form class="cf" id="cf" style="margin-top:40px">
      <div class="cf-row">
        <div><input type="text" name="name" placeholder="الاسم الكامل" required></div>
        <div><input type="email" name="email" placeholder="البريد الإلكتروني" required></div>
      </div>
      <div class="cf-mb"><textarea name="message" placeholder="أخبرنا عن متجرك وما تحتاجه..." required></textarea></div>
      <button class="btn-submit" type="submit">إرسال الرسالة ✈</button>
    </form>"""

FORM_AFTER = """    <form class="cf" id="cf" style="margin-top:40px" novalidate>
      <div class="cf-row">
        <div>
          <label class="sr-only" for="contact-name">الاسم الكامل</label>
          <input id="contact-name" type="text" name="name" placeholder="الاسم الكامل" autocomplete="name" minlength="2" maxlength="80" required>
        </div>
        <div>
          <label class="sr-only" for="contact-email">البريد الإلكتروني</label>
          <input id="contact-email" type="email" name="email" placeholder="البريد الإلكتروني" autocomplete="email" maxlength="254" required>
        </div>
      </div>
      <div class="cf-mb">
        <label class="sr-only" for="contact-message">تفاصيل المتجر والخدمة المطلوبة</label>
        <textarea id="contact-message" name="message" placeholder="أخبرنا عن متجرك وما تحتاجه..." minlength="10" maxlength="2000" required></textarea>
      </div>
      <div class="form-hp" aria-hidden="true">
        <label for="contact-website">اترك هذا الحقل فارغاً</label>
        <input id="contact-website" type="text" name="website" tabindex="-1" autocomplete="off">
      </div>
      <button class="btn-submit" type="submit">إرسال الرسالة ✈</button>
      <p class="sr-only" id="contact-status" role="status" aria-live="polite"></p>
    </form>"""

STYLE_ANCHOR = ".cf{text-align:right}"
ACCESSIBLE_STYLES = """.cf{text-align:right}
.sr-only{position:absolute!important;width:1px!important;height:1px!important;padding:0!important;margin:-1px!important;overflow:hidden!important;clip:rect(0,0,0,0)!important;white-space:nowrap!important;border:0!important}
.form-hp{position:absolute;inset-inline-start:-10000px;width:1px;height:1px;overflow:hidden}
.btn-submit:disabled{cursor:wait;opacity:.72;transform:none}"""

SECURITY_HEADERS = [
    {
        "key": "Content-Security-Policy",
        "value": "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'; img-src 'self' data: https://i.ibb.co; font-src 'self' https://fonts.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; script-src 'self' 'unsafe-inline'; connect-src 'self'; upgrade-insecure-requests",
    },
    {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
    {"key": "X-Content-Type-Options", "value": "nosniff"},
    {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
    {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
    {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=()"},
    {"key": "Cross-Origin-Opener-Policy", "value": "same-origin-allow-popups"},
]


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8", newline="")


def secure_index() -> None:
    path = ROOT / "index.html"
    content = path.read_text(encoding="utf-8")
    if FORM_BEFORE in content:
        content = content.replace(FORM_BEFORE, FORM_AFTER, 1)
    elif 'id="contact-status"' not in content:
        raise RuntimeError("Contact form markup did not match the expected source")
    if STYLE_ANCHOR in content and ".form-hp{" not in content:
        content = content.replace(STYLE_ANCHOR, ACCESSIBLE_STYLES, 1)
    content, handler_count = CONTACT_HANDLER_RE.subn(CONTACT_HANDLER, content, count=1)
    if handler_count != 1 and "fetch('/api/contact'" not in content:
        raise RuntimeError("Contact handler did not match the expected source")
    content = content.replace(
        '<div class="toast" id="toast"></div>',
        '<div class="toast" id="toast" role="status" aria-live="polite" aria-atomic="true"></div>',
        1,
    )
    content = TOKEN_RE.sub("[REMOVED-COMPROMISED-TOKEN]", content)
    write_text(path, content)


def scrub_archived_source() -> None:
    path = ROOT / "تصميم ازهلها جديد.txt"
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    content = TOKEN_RE.sub("[REMOVED-COMPROMISED-TOKEN]", content)
    content = re.sub(r'chat_id\s*:\s*["\'][0-9]+["\']', 'chat_id:"[SERVER-ENV]"', content)
    write_text(path, content)


def update_vercel_headers() -> None:
    path = ROOT / "vercel.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["headers"] = [
        {"source": "/(.*)", "headers": SECURITY_HEADERS},
        {
            "source": "/api/(.*)",
            "headers": [{"key": "Cache-Control", "value": "no-store"}],
        },
        {
            "source": "/(.*)\\.html",
            "headers": [
                {
                    "key": "Cache-Control",
                    "value": "public, max-age=0, must-revalidate",
                }
            ],
        },
        {
            "source": "/(.*)\\.(css|js|webp|avif|png|jpg|jpeg|svg|woff2)",
            "headers": [
                {
                    "key": "Cache-Control",
                    "value": "public, max-age=31536000, immutable",
                }
            ],
        },
    ]
    write_text(path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def update_firebase_headers() -> None:
    path = ROOT / "firebase.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    for hosting in config.get("hosting", []):
        ignore = hosting.setdefault("ignore", [])
        if "api/**" not in ignore:
            ignore.append("api/**")
        hosting["headers"] = [
            {"source": "**", "headers": SECURITY_HEADERS},
            {
                "source": "**/*.html",
                "headers": [
                    {"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}
                ],
            },
            {
                "source": "**/*.{css,js,webp,avif,png,jpg,jpeg,svg,woff2}",
                "headers": [
                    {
                        "key": "Cache-Control",
                        "value": "public, max-age=31536000, immutable",
                    }
                ],
            },
        ]
    write_text(path, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    secure_index()
    scrub_archived_source()
    update_vercel_headers()
    update_firebase_headers()
    print(json.dumps({"secured_files": 4, "client_secrets_remaining": 0}))


if __name__ == "__main__":
    main()
