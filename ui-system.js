(function () {
  "use strict";

  const CONFIG = window.EZHALHA_CONFIG || {};
  const COMPANY = CONFIG.company || {};
  const URLS = CONFIG.urls || {};
  const PACKAGES = Array.isArray(CONFIG.packages) ? CONFIG.packages : [];
  const PORTFOLIO = Array.isArray(CONFIG.portfolio) ? CONFIG.portfolio : [];
  const WA_PHONE = COMPANY.whatsappNumber || "966503228029";
  const CALL_PHONE_DISPLAY = COMPANY.phoneDisplay || "+966 50 322 8029";
  const CALL_PHONE_TEL = COMPANY.phoneTel || "+966503228029";
  const BOOKING_URL = URLS.booking || "/booking.html";
  const PORTFOLIO_URL = URLS.portfolio || "/portfolio.html";
  const ABOUT_URL = URLS.about || "/about.html";
  const PRIVACY_URL = URLS.privacy || "/privacy.html";
  const ARTICLES_URL = URLS.articles || "/articles.html";
  const STORE_DOMAIN = COMPANY.storeDomain || "https://ezhalhe.com";
  const WA_BRIEF_TEXT = "مرحباً، أريد استشارة حول تصميم أو تطوير متجري الإلكتروني.";
  const HOME_PATHS = new Set(["/", "/index.html"]);

  const menuIcon = `
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path d="M4 7h16M4 12h16M4 17h16"/>
    </svg>`;

  const closeIcon = `
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <path d="m6 6 12 12M18 6 6 18"/>
    </svg>`;

  const arrowIcon = `
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M5 12h14M13 6l6 6-6 6"/>
    </svg>`;

  const whatsappIcon = `
    <svg aria-hidden="true" width="19" height="19" viewBox="0 0 24 24" fill="currentColor">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884M20.464 3.488A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/>
    </svg>`;

  function whatsappHref(message = WA_BRIEF_TEXT) {
    return `https://wa.me/${WA_PHONE}?text=${encodeURIComponent(message)}`;
  }

  function storeHref(url, campaign) {
    try {
      const target = new URL(url, STORE_DOMAIN);
      target.searchParams.set("utm_source", "ezhalhe-sa");
      target.searchParams.set("utm_medium", "website");
      target.searchParams.set("utm_campaign", campaign || "site");
      return target.toString();
    } catch {
      return url || STORE_DOMAIN;
    }
  }

  function track(eventName, params) {
    if (typeof window.gtag === "function") {
      window.gtag("event", eventName, params || {});
    }
  }

  function formatSar(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return String(value || "");
    return number.toLocaleString("en-US");
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function brandMarkup() {
    return `
      <a class="ui-brand" href="/" aria-label="إزهلها — الصفحة الرئيسية">
        <span class="ui-brand__mark">
          <img src="/images/responsive/logo-128.webp" width="128" height="128" alt="شعار إزهلها" decoding="async">
        </span>
        <span>
          <span class="ui-brand__name">إزهلها</span>
          <span class="ui-brand__tagline">تصميم وتجهيز المتاجر الإلكترونية</span>
        </span>
      </a>`;
  }

  function pageKey(pathname) {
    if (HOME_PATHS.has(pathname)) return "home";
    if (pathname === "/articles.html" || pathname === "/blog.html") return "articles";
    if (pathname.startsWith("/articles/")) return "article";
    return "inner";
  }

  function setPageClasses() {
    const key = pageKey(window.location.pathname);
    document.body.classList.remove("ui-pending");
    document.body.classList.add("ui-pro", key === "home" ? "ui-home" : "ui-inner-page", `ui-page-${key}`);

    const main = document.querySelector("main") || document.querySelector(".content");
    if (main && !main.id) main.id = "main-content";

    const existingSkip = document.querySelector('.skip-link[href="#main-content"]');
    if (existingSkip) {
      existingSkip.classList.add("ui-skip-link");
    } else if (!document.querySelector(".ui-skip-link")) {
      const skip = document.createElement("a");
      skip.className = "ui-skip-link";
      skip.href = "#main-content";
      skip.textContent = "تجاوز إلى المحتوى";
      document.body.prepend(skip);
    }
  }

  function createHeader() {
    const currentPath = window.location.pathname;
    const links = [
      ["الرئيسية", "/"],
      ["الخدمات", "/#services"],
      ["أعمالنا", PORTFOLIO_URL],
      ["الباقات", "/#packages"],
      ["المعرفة", ARTICLES_URL]
    ];

    const navLinks = links.map(([label, href]) => {
      const isCurrent =
        (href === "/" && HOME_PATHS.has(currentPath)) ||
        (href === ARTICLES_URL && (currentPath === href || currentPath.startsWith("/articles/"))) ||
        href === currentPath;
      return `<a href="${href}"${isCurrent ? ' aria-current="page"' : ""}>${label}</a>`;
    }).join("");

    const mobileLinks = links.map(([label, href]) => `<a href="${href}"><span>${label}</span>${arrowIcon}</a>`).join("");
    const mobileExtraLinks = [
      ["تصميم متجر سلة", "/salla-store-design.html"],
      ["تصميم متجر زد", "/zid-store-design.html"],
      ["تحسين SEO", "/search-engine-optimization.html"],
      ["عن إزهلها", ABOUT_URL]
    ].map(([label, href]) => `<a href="${href}"><span>${label}</span>${arrowIcon}</a>`).join("");

    const header = document.createElement("header");
    header.className = "ui-header";
    header.innerHTML = `
      <div class="ui-header__inner">
        ${brandMarkup()}
        <nav class="ui-nav" aria-label="التنقل الرئيسي">${navLinks}</nav>
        <a class="ui-header__cta" href="${BOOKING_URL}" data-track-event="hero_booking_click">
          <span>احجز استشارة</span>
        </a>
        <button class="ui-menu-button" type="button" aria-label="فتح القائمة" aria-controls="ui-mobile-nav" aria-expanded="false">
          ${menuIcon}
        </button>
      </div>`;

    const oldHeader = document.querySelector("body > header, body > .main-header, header");
    if (oldHeader) oldHeader.replaceWith(header);
    else document.body.prepend(header);

    const mobileNav = document.createElement("div");
    mobileNav.id = "ui-mobile-nav";
    mobileNav.className = "ui-mobile-nav";
    mobileNav.setAttribute("aria-hidden", "true");
    mobileNav.innerHTML = `
      <div class="ui-mobile-nav__scrim" data-ui-close-menu></div>
      <div class="ui-mobile-nav__panel" role="dialog" aria-modal="true" aria-label="قائمة الموقع">
        <div class="ui-mobile-nav__top">
          ${brandMarkup()}
          <button class="ui-mobile-nav__close" type="button" aria-label="إغلاق القائمة" data-ui-close-menu>${closeIcon}</button>
        </div>
        <nav class="ui-mobile-nav__links" aria-label="التنقل على الجوال">${mobileLinks}${mobileExtraLinks}</nav>
        <div class="ui-mobile-nav__cta">
          <a class="ui-button" href="${BOOKING_URL}" data-track-event="hero_booking_click">احجز استشارة مجانية</a>
          <a class="ui-button ui-button--secondary" href="${whatsappHref("مرحباً، أريد استفساراً سريعاً عن خدمات إزهلها.")}" target="_blank" rel="noopener noreferrer" data-track-event="whatsapp_click">${whatsappIcon} واتساب</a>
        </div>
      </div>`;
    header.after(mobileNav);

    const openButton = header.querySelector(".ui-menu-button");
    const closeButton = mobileNav.querySelector(".ui-mobile-nav__close");
    let previousFocus = null;

    const closeMenu = () => {
      mobileNav.setAttribute("aria-hidden", "true");
      openButton.setAttribute("aria-expanded", "false");
      document.body.classList.remove("ui-menu-open");
      if (previousFocus instanceof HTMLElement) previousFocus.focus();
    };

    const openMenu = () => {
      previousFocus = document.activeElement;
      mobileNav.setAttribute("aria-hidden", "false");
      openButton.setAttribute("aria-expanded", "true");
      document.body.classList.add("ui-menu-open");
      window.requestAnimationFrame(() => closeButton.focus());
      window.setTimeout(() => {
        if (mobileNav.getAttribute("aria-hidden") === "false") closeButton.focus();
      }, 240);
    };

    openButton.addEventListener("click", openMenu);
    mobileNav.querySelectorAll("[data-ui-close-menu]").forEach((element) => element.addEventListener("click", closeMenu));
    mobileNav.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && mobileNav.getAttribute("aria-hidden") === "false") closeMenu();
    });
  }

  function createFooter() {
    const footer = document.createElement("footer");
    footer.className = "ui-footer";
    footer.innerHTML = `
      <div class="ui-footer__inner">
        <div class="ui-footer__grid">
          <div class="ui-footer__about">
            ${brandMarkup()}
            <p>وكالة سعودية متخصصة في تصميم وتطوير متاجر سلة وزد، من وضوح الفكرة حتى إطلاق متجر موثوق وجاهز للبيع.</p>
          </div>
          <div class="ui-footer__col">
            <h2>الخدمات</h2>
            <nav class="ui-footer__links" aria-label="روابط الخدمات">
              <a href="/salla-store-design.html">تصميم متجر سلة</a>
              <a href="/zid-store-design.html">تصميم متجر زد</a>
              <a href="/search-engine-optimization.html">SEO للمتاجر</a>
              <a href="/#services">كل الخدمات</a>
            </nav>
          </div>
          <div class="ui-footer__col">
            <h2>قرار الشراء</h2>
            <nav class="ui-footer__links" aria-label="روابط قرار الشراء">
              <a href="${PORTFOLIO_URL}">أعمالنا</a>
              <a href="/#packages">الباقات</a>
              <a href="${BOOKING_URL}">احجز استشارة</a>
              <a href="${storeHref(STORE_DOMAIN, "footer_store")}" target="_blank" rel="noopener noreferrer">الشراء من المتجر</a>
            </nav>
          </div>
          <div class="ui-footer__col">
            <h2>المعرفة والشركة</h2>
            <nav class="ui-footer__links" aria-label="روابط المعرفة">
              <a href="${ARTICLES_URL}">مركز المعرفة</a>
              <a href="${ABOUT_URL}">عن إزهلها</a>
              <a href="${PRIVACY_URL}">سياسة الخصوصية</a>
              <a href="tel:${CALL_PHONE_TEL}">${CALL_PHONE_DISPLAY}</a>
            </nav>
          </div>
        </div>
        <div class="ui-footer__bottom">
          <span>© ${new Date().getFullYear()} إزهلها. جميع الحقوق محفوظة.</span>
          <span>نخدم أصحاب المتاجر في المملكة العربية السعودية</span>
        </div>
      </div>`;

    const oldFooter = document.querySelector("body > footer, footer");
    if (oldFooter) oldFooter.replaceWith(footer);
    else document.body.append(footer);
  }

  function createStickyContact() {
    if (document.querySelector(".ui-sticky-contact")) return;
    const bar = document.createElement("div");
    bar.className = "ui-sticky-contact";
    bar.setAttribute("aria-label", "تواصل سريع");
    bar.innerHTML = `
      <a class="ui-button" href="${BOOKING_URL}" data-track-event="hero_booking_click">
        <span>احجز استشارة</span>
      </a>
      <a class="ui-button ui-button--secondary" href="${whatsappHref("مرحباً، أحتاج استفساراً سريعاً عن خدمات إزهلها.")}" target="_blank" rel="noopener noreferrer" data-track-event="whatsapp_click">
        ${whatsappIcon}<span>واتساب</span>
      </a>`;
    document.body.append(bar);
  }

  function createHeroVisual() {
    const heroInner = document.querySelector(".ui-home .hero-inner");
    if (!heroInner || heroInner.querySelector(".ui-hero__visual")) return;

    const copy = document.createElement("div");
    copy.className = "ui-hero__copy";
    [...heroInner.children].forEach((child) => copy.append(child));
    heroInner.append(copy);

    const visual = document.createElement("div");
    visual.className = "ui-hero__visual";
    visual.setAttribute("aria-label", "نماذج من متاجر سلة التي صممناها");
    visual.innerHTML = `
      <span class="ui-hero__proof">أعمال حقيقية على منصة سلة</span>
      <figure class="ui-hero__screen">
        <img src="/images/responsive/lana-badawood-salla-gold-pro-360.webp" width="360" height="7335" alt="واجهة متجر لانا للأزياء على منصة سلة" decoding="async" fetchpriority="low">
      </figure>
      <figure class="ui-hero__screen">
        <img src="/images/responsive/duk-altayeb-salla-gold-pro-360.webp" width="360" height="4417" alt="واجهة متجر دوك الطيب للعود والمسك على منصة سلة" decoding="async" fetchpriority="low">
      </figure>
      <figure class="ui-hero__screen">
        <img src="/images/responsive/lara-alsaad-boutique-salla-gold-pro-360.webp" width="360" height="7417" alt="واجهة متجر لارا السعد بوتيك على منصة سلة" decoding="async" fetchpriority="low">
      </figure>`;
    heroInner.append(visual);

    copy.querySelectorAll('.hero-btns a[href="#compare"]').forEach((link) => {
      link.href = "#packages";
    });
  }

  function tuneHomepageHero() {
    const hero = document.querySelector(".ui-home .hero");
    if (!hero) return;

    const pill = hero.querySelector(".hero-pill");
    if (pill) pill.innerHTML = '<span class="hero-pill-dot"></span>متخصصون في متاجر سلة وزد للسوق السعودي';

    const title = hero.querySelector("h1");
    if (title) title.innerHTML = 'نبني متاجر <em>سلة</em> و<em>زد</em><br>جاهزة للبيع والنمو';

    const sub = hero.querySelector(".hero-sub");
    if (sub) {
      sub.textContent = "تصميم، إعداد، مدفوعات، شحن، SEO، تحليلات، وتجهيز إطلاق واضح لتاجر سعودي يريد متجرًا عمليًا لا مجرد واجهة جميلة.";
    }

    const buttons = hero.querySelector(".hero-btns");
    if (buttons) {
      buttons.innerHTML = `
        <a href="${BOOKING_URL}" class="btn-primary" data-track-event="hero_booking_click">احجز استشارة مجانية</a>
        <a href="${PORTFOLIO_URL}" class="btn-outline" data-track-event="portfolio_view">شاهد أعمالنا</a>
        <a href="#packages" class="btn-link">قارن الباقات</a>`;
    }

    const consult = hero.querySelector(".hero-consult");
    if (consult) {
      consult.innerHTML = `
        <a rel="noopener noreferrer" href="${whatsappHref("مرحباً، شاهدت موقع إزهلها وأريد استفساراً سريعاً.")}" target="_blank" class="btn-consult" data-track-event="whatsapp_click">
          ${whatsappIcon}
          سؤال سريع على واتساب
        </a>
        <a href="tel:${CALL_PHONE_TEL}" class="btn-call" aria-label="اتصال مباشر ${CALL_PHONE_DISPLAY}">اتصال ${CALL_PHONE_DISPLAY}</a>`;
    }

    const stats = hero.querySelector(".hero-stats");
    if (stats) {
      stats.innerHTML = `
        <div class="hstat"><div class="hstat-n">سلة</div><div class="hstat-l">تصميم وتجهيز</div></div>
        <div class="hstat"><div class="hstat-n">زد</div><div class="hstat-l">تصميم وتطوير</div></div>
        <div class="hstat"><div class="hstat-n">2022</div><div class="hstat-l">بداية النشاط</div></div>
        <div class="hstat"><div class="hstat-n">Meet</div><div class="hstat-l">استشارة مجانية</div></div>`;
    }
  }

  function createMerchantRouter() {
    const hero = document.querySelector(".ui-home .hero");
    if (!hero || document.getElementById("merchant-router")) return null;

    const section = document.createElement("section");
    section.id = "merchant-router";
    section.className = "ui-router";
    section.setAttribute("aria-labelledby", "merchant-router-title");
    section.innerHTML = `
      <div class="ui-router__inner">
        <div class="ui-section-heading">
          <span class="ui-eyebrow">مسار سريع</span>
          <h2 id="merchant-router-title">وش تحتاج لمتجرك؟</h2>
          <p>اختر الحالة الأقرب لك، وسنرتب لك المسار المناسب بدون تسجيل أو خطوات طويلة.</p>
        </div>
        <div class="ui-router__layout">
          <div class="ui-router__choices" role="tablist" aria-label="اختيار حالة المتجر">
            <button type="button" role="tab" aria-selected="true" aria-controls="router-new" id="router-tab-new" data-router-choice="new">أبي أفتح متجر جديد</button>
            <button type="button" role="tab" aria-selected="false" aria-controls="router-improve" id="router-tab-improve" data-router-choice="improve">عندي متجر وأبي أطوره</button>
            <button type="button" role="tab" aria-selected="false" aria-controls="router-unsure" id="router-tab-unsure" data-router-choice="unsure">محتار بين سلة وزد</button>
          </div>
          <div class="ui-router__panels">
            <article id="router-new" role="tabpanel" aria-labelledby="router-tab-new" data-router-panel="new">
              <span class="ui-router__badge">مسار الإطلاق</span>
              <h3>ابدأ بمتجر واضح على سلة أو زد</h3>
              <p>نراجع المنتجات والميزانية ونحدد هل تحتاج بلس، الاحترافية، أو الذهبية برو قبل تحويلك للشراء.</p>
              <ul>
                <li>اختيار منصة مناسبة للمشروع.</li>
                <li>تجهيز الأقسام والواجهة والمنتجات الأساسية.</li>
                <li>ربط المدفوعات والشحن والقياس حسب الحاجة.</li>
              </ul>
              <div class="ui-router__actions">
                <a class="ui-button" href="${BOOKING_URL}?intent=new-store" data-track-event="merchant_router_complete" data-track-label="new">احجز استشارة الإطلاق</a>
                <a href="/salla-store-design.html">تفاصيل تصميم متجر سلة</a>
              </div>
            </article>
            <article id="router-improve" role="tabpanel" aria-labelledby="router-tab-improve" data-router-panel="improve" hidden>
              <span class="ui-router__badge">مسار التطوير</span>
              <h3>طوّر متجر قائم بدون تغيير كل شيء</h3>
              <p>نحدد نقاط الضعف في الواجهة والجوال وصفحات المنتجات والقياس، ثم نقترح تحسينات قابلة للتنفيذ.</p>
              <ul>
                <li>تحسين تجربة المستخدم والواجهة.</li>
                <li>تهيئة SEO وSearch Console وAnalytics.</li>
                <li>عرض أعمال مشابهة قبل تحديد الباقة.</li>
              </ul>
              <div class="ui-router__actions">
                <a class="ui-button" href="${BOOKING_URL}?intent=improve-store" data-track-event="merchant_router_complete" data-track-label="improve">احجز استشارة التطوير</a>
                <a href="${PORTFOLIO_URL}">شاهد أعمال مشابهة</a>
              </div>
            </article>
            <article id="router-unsure" role="tabpanel" aria-labelledby="router-tab-unsure" data-router-panel="unsure" hidden>
              <span class="ui-router__badge">مسار الاختيار</span>
              <h3>نقارن سلة وزد حسب مشروعك</h3>
              <p>نراجع طبيعة المنتجات، حجم التشغيل، احتياج التخصيص، والميزانية حتى لا تختار منصة بناءً على الانطباع فقط.</p>
              <ul>
                <li>سلة مناسبة لكثير من بدايات المتاجر السعودية.</li>
                <li>زد مناسبة عندما تحتاج تجربة إدارة مختلفة أو نموذج تشغيل محدد.</li>
                <li>WooCommerce خيار عند الحاجة لتخصيص تقني أوسع.</li>
              </ul>
              <div class="ui-router__actions">
                <a class="ui-button" href="${BOOKING_URL}?intent=platform-choice" data-track-event="merchant_router_complete" data-track-label="unsure">احجز استشارة الاختيار</a>
                <a href="/zid-store-design.html">تفاصيل تصميم متجر زد</a>
              </div>
            </article>
          </div>
        </div>
      </div>`;

    hero.after(section);

    const choices = [...section.querySelectorAll("[data-router-choice]")];
    const panels = [...section.querySelectorAll("[data-router-panel]")];
    const activate = (choice) => {
      track("merchant_router_start", { route: choice });
      choices.forEach((button) => button.setAttribute("aria-selected", String(button.dataset.routerChoice === choice)));
      panels.forEach((panel) => {
        panel.hidden = panel.dataset.routerPanel !== choice;
      });
    };

    choices.forEach((button, index) => {
      button.addEventListener("click", () => activate(button.dataset.routerChoice));
      button.addEventListener("keydown", (event) => {
        if (!["ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        const direction = event.key === "ArrowRight" ? -1 : 1;
        const nextIndex =
          event.key === "Home" ? 0 :
          event.key === "End" ? choices.length - 1 :
          (index + direction + choices.length) % choices.length;
        choices[nextIndex].focus();
        activate(choices[nextIndex].dataset.routerChoice);
      });
    });

    return section;
  }

  function createProofSection() {
    const router = document.getElementById("merchant-router");
    if (!router || document.getElementById("proof")) return null;

    const proofItems = (PORTFOLIO.length ? PORTFOLIO : [
      {
        name: "متجر لانا",
        platform: "سلة",
        category: "أزياء نسائية",
        image: "/images/responsive/lana-badawood-salla-gold-pro-360.webp",
        alt: "واجهة متجر لانا للأزياء على منصة سلة",
        summary: "واجهة متجر أزياء على سلة من الأعمال المحفوظة في المشروع."
      },
      {
        name: "لارا السعد بوتيك",
        platform: "سلة",
        category: "أزياء وإكسسوارات",
        image: "/images/responsive/lara-alsaad-boutique-salla-gold-pro-360.webp",
        alt: "واجهة متجر لارا السعد بوتيك على منصة سلة",
        summary: "واجهة متجر بوتيك تعتمد على إبراز المنتجات والتصنيفات."
      },
      {
        name: "Siwar Altyeb",
        platform: "زد",
        category: "عطور وعود",
        image: "/images/responsive/swartyp_zid-360.webp",
        alt: "واجهة متجر Siwar Altyeb على منصة زد",
        summary: "نموذج موثق لمنصة زد ضمن قطاع العطور والعود."
      }
    ]).slice(0, 4);

    const cards = proofItems.map((item) => `
      <article class="ui-proof-card">
        <img src="${escapeHtml(item.image)}" width="360" height="520" loading="lazy" decoding="async" alt="${escapeHtml(item.alt)}">
        <div>
          <span>${escapeHtml(item.platform)} · ${escapeHtml(item.category)}</span>
          <h3>${escapeHtml(item.name)}</h3>
          <p>${escapeHtml(item.summary)}</p>
        </div>
      </article>`).join("");

    const section = document.createElement("section");
    section.id = "proof";
    section.className = "ui-proof";
    section.setAttribute("aria-labelledby", "proof-title");
    section.innerHTML = `
      <div class="ui-proof__inner">
        <div class="ui-section-heading ui-section-heading--center">
          <span class="ui-eyebrow">أعمال حقيقية</span>
          <h2 id="proof-title">نماذج مختارة قبل عرض كل التفاصيل</h2>
          <p>نبدأ بإثبات مختصر حتى يعرف التاجر شكل العمل، ثم يمكنه فتح معرض الأعمال الكامل عند الحاجة.</p>
        </div>
        <div class="ui-proof__grid">${cards}</div>
        <div class="ui-proof__action">
          <a class="ui-button ui-button--secondary" href="${PORTFOLIO_URL}" data-track-event="portfolio_view">شاهد كل الأعمال</a>
          <a class="ui-button" href="${BOOKING_URL}?intent=similar-project" data-track-event="hero_booking_click">ناقش مشروعاً مشابهاً</a>
        </div>
      </div>`;

    router.after(section);
    return section;
  }

  function rebuildHomepageServices() {
    const section = document.querySelector(".ui-home #services");
    if (!section || section.dataset.uiServiceFamilies === "true") return;
    section.dataset.uiServiceFamilies = "true";
    section.className = "ui-service-families";
    section.setAttribute("aria-labelledby", "services-title");
    section.innerHTML = `
      <div class="ui-service-families__inner">
        <div class="ui-section-heading">
          <span class="ui-eyebrow">الخدمات</span>
          <h2 id="services-title">خدمات مرتبة حسب مرحلة التاجر</h2>
          <p>بدلاً من قائمة طويلة، نبدأ بالمشكلة التجارية ثم نحدد التنفيذ المناسب على سلة أو زد أو WooCommerce.</p>
        </div>
        <div class="ui-service-family-grid">
          <article class="ui-service-family-card">
            <span>01</span>
            <h3>إطلاق متجر جديد</h3>
            <p>اختيار المنصة، تجهيز الهيكل، تصميم الواجهة، رفع المنتجات، وربط الأساسيات المطلوبة للبيع.</p>
            <div><a href="/salla-store-design.html">سلة</a><a href="/zid-store-design.html">زد</a><a href="${BOOKING_URL}?intent=new-store">استشارة إطلاق</a></div>
          </article>
          <article class="ui-service-family-card">
            <span>02</span>
            <h3>تطوير متجر قائم</h3>
            <p>تحسين الواجهة وتجربة الجوال وصفحات المنتجات وترتيب المسار قبل شراء العميل.</p>
            <div><a href="${PORTFOLIO_URL}">أعمال مشابهة</a><a href="${BOOKING_URL}?intent=improve-store">استشارة تطوير</a></div>
          </article>
          <article class="ui-service-family-card">
            <span>03</span>
            <h3>النمو والقياس</h3>
            <p>SEO، Search Console، Google Analytics، بكسلات الحملات، وقياس التحويلات بدون إرسال بيانات شخصية للتحليلات.</p>
            <div><a href="/search-engine-optimization.html">خدمة SEO</a><a href="${BOOKING_URL}?intent=growth">راجع فرص النمو</a></div>
          </article>
          <article class="ui-service-family-card">
            <span>04</span>
            <h3>التأسيس والتوثيق</h3>
            <p>خدمات داعمة مثل التوثيق، الدومين، وبعض التكاملات المرتبطة بإطلاق متجر سعودي جاهز.</p>
            <div><a href="/store-verification.html">توثيق المتجر</a><a href="/secure-payments.html">الدفع الآمن</a></div>
          </article>
        </div>
      </div>`;
  }

  function packageCard({ name, badge, audience, price, features, orderUrl, target, featured }) {
    const items = features.map((feature) => `<li>${feature}</li>`).join("");
    const bookingPackageUrl = `${BOOKING_URL}?package=${encodeURIComponent(target || name)}`;
    return `
      <article class="ui-package-card${featured ? " ui-package-card--featured" : ""}">
        <span class="ui-package-card__badge">${badge}</span>
        <h3>${name}</h3>
        <p class="ui-package-card__for">${audience}</p>
        <div class="ui-package-card__price"><strong>${price}</strong><span>ريال</span></div>
        <ul>${items}</ul>
        <div class="ui-package-card__actions">
          <a class="ui-button" href="${bookingPackageUrl}" data-track-event="package_select" data-track-label="${target || name}">احجز استشارة ${arrowIcon}</a>
          <a class="ui-button ui-button--secondary" href="${storeHref(orderUrl, target || "package")}" target="_blank" rel="noopener noreferrer" data-track-event="store_purchase_click" data-track-label="${target || name}">شراء الباقة</a>
          <button class="ui-button ui-button--secondary" type="button" data-package-detail="${target}">عرض كل التفاصيل</button>
        </div>
      </article>`;
  }

  function createPackages() {
    const hero = document.querySelector(".ui-home .hero");
    if (!hero || document.getElementById("packages")) return null;

    const packageSource = PACKAGES.length ? PACKAGES : [
      {
        id: "plus",
        nameAr: "بلس",
        badge: "بداية منظمة",
        audience: "لتاجر جديد يحتاج متجرًا مرتبًا وجاهزًا للبيع بدون تعقيد.",
        priceSar: 1099,
        topFeatures: ["تجهيز متجر أساسي", "رفع 10 منتجات", "تصميم 3 بنرات", "ترتيب الأقسام والواجهة", "تسليم جاهز للانطلاق"],
        storeUrl: `${STORE_DOMAIN}/تصميم-المتجر-احترفي-سلة-وزد-باقة-بلس/p560117077`
      },
      {
        id: "professional",
        nameAr: "الاحترافية",
        badge: "الأقرب لمعظم المتاجر",
        audience: "لمتجر يحتاج واجهة أقوى وهوية أولية وقياس واضح للزيارات.",
        priceSar: 1490,
        topFeatures: ["رفع 20 منتجًا", "تصميم شعار", "تحسين واجهة المتجر", "تهيئة SEO أساسية", "Analytics وSearch Console"],
        storeUrl: `${STORE_DOMAIN}/الباقة-الاحترافية-—-تطوير-وتصميم-متجر-إلكتروني/p2132256496`
      },
      {
        id: "golden-pro",
        nameAr: "الذهبية برو",
        badge: "إطلاق متكامل",
        audience: "لصاحب مشروع يريد تجهيز المتجر والهوية والقياس والتكاملات من البداية.",
        priceSar: 1980,
        topFeatures: ["هوية بصرية متكاملة", "35 منتجًا", "تخصيص CSS", "SEO وتحليلات وبكسلات", "دومين وربط تابي وتمارا"],
        storeUrl: `${STORE_DOMAIN}/تطوير-والتصميم-متجر-الالكتروني-الباقة-الذهبية-باقة-برو/p1934611542`
      }
    ];

    const packageCards = packageSource.map((pkg) => packageCard({
      name: pkg.nameAr || pkg.name,
      badge: pkg.badge,
      audience: pkg.audience,
      price: formatSar(pkg.priceSar),
      target: pkg.id === "golden-pro" ? "pro" : pkg.id,
      featured: pkg.id === "professional",
      orderUrl: pkg.storeUrl,
      features: pkg.topFeatures || []
    })).join("");

    const section = document.createElement("section");
    section.id = "packages";
    section.className = "ui-packages";
    section.setAttribute("aria-labelledby", "packages-title");
    section.innerHTML = `
      <div class="ui-packages__inner">
        <div class="ui-section-heading ui-section-heading--center">
          <span class="ui-eyebrow">باقات واضحة بدون تعقيد</span>
          <h2 id="packages-title">اختر الباقة الأقرب لمرحلة متجرك</h2>
          <p>ثلاثة مستويات عملية، من التجهيز الأساسي إلى إطلاق علامة تجارية متكاملة.</p>
        </div>
        <div class="ui-package-grid">
          ${packageCards}
        </div>
        <div class="ui-packages__note" aria-label="مزايا مشتركة">
          <span>أسعار واضحة</span><span>تنفيذ مخصص لمنصتك</span><span>دعم بعد التسليم</span><span>استشارة قبل البدء</span>
        </div>
      </div>`;
    hero.after(section);

    const packageSections = ["pro", "professional", "plus", "compare"]
      .map((id) => document.getElementById(id))
      .filter(Boolean);

    if (packageSections.length) {
      const details = document.createElement("details");
      details.className = "ui-package-details";
      details.innerHTML = `
        <summary>التفاصيل الكاملة ومقارنة الباقات</summary>
        <div class="ui-package-details__content"></div>`;
      section.querySelector(".ui-packages__inner").append(details);
      const detailsContent = details.querySelector(".ui-package-details__content");
      packageSections.forEach((packageSection) => detailsContent.append(packageSection));

      section.querySelectorAll("[data-package-detail]").forEach((button) => {
        button.addEventListener("click", () => {
          details.open = true;
          const target = document.getElementById(button.dataset.packageDetail);
          window.requestAnimationFrame(() => target?.scrollIntoView({ behavior: "smooth", block: "start" }));
        });
      });
    }

    return section;
  }

  function createProcess() {
    const work = document.getElementById("work");
    if (!work || document.getElementById("process")) return null;

    const section = document.createElement("section");
    section.id = "process";
    section.className = "ui-process";
    section.setAttribute("aria-labelledby", "process-title");
    section.innerHTML = `
      <div class="ui-process__inner">
        <div class="ui-section-heading">
          <span class="ui-eyebrow">رحلة واضحة من البداية</span>
          <h2 id="process-title">كيف نطلق متجرك؟</h2>
          <p>خطوات قصيرة وواضحة تبقيك مطّلعًا على المشروع حتى التسليم.</p>
        </div>
        <div class="ui-process__grid">
          <article class="ui-process__step"><h3>نفهم مشروعك</h3><p>نراجع نشاطك ومنتجاتك والمنصة والهدف من المتجر.</p></article>
          <article class="ui-process__step"><h3>نرتب التجربة</h3><p>نحدد الهيكل والأقسام ومسار العميل قبل بدء التصميم.</p></article>
          <article class="ui-process__step"><h3>نصمم ونجهز</h3><p>نبني الواجهة ونرفع المحتوى ونربط الأدوات المطلوبة.</p></article>
          <article class="ui-process__step"><h3>نختبر ونسلم</h3><p>نفحص الجوال والطلب والسرعة ثم نسلمك متجرًا جاهزًا.</p></article>
        </div>
      </div>`;
    work.after(section);
    return section;
  }

  function reorderHomepage(router, proof, packages, process) {
    const main = document.querySelector(".ui-home main");
    if (!main) return;

    const selectors = [
      ".hero",
      "#smart-advisor",
      "#merchant-router",
      "#proof",
      "#packages",
      "#services",
      "#work",
      "#process",
      "#testimonials",
      "#why-us",
      ".partners-sec",
      "#faq",
      ".articles-sec",
      "#coupon-salla",
      ".ticker-wrap",
      "#contact"
    ];

    const ordered = selectors.map((selector) => main.querySelector(`:scope > ${selector}`) || document.querySelector(`.ui-home ${selector}`)).filter(Boolean);
    if (router && !ordered.includes(router)) ordered.splice(1, 0, router);
    if (proof && !ordered.includes(proof)) ordered.splice(2, 0, proof);
    if (packages && !ordered.includes(packages)) ordered.splice(3, 0, packages);
    if (process && !ordered.includes(process)) ordered.splice(6, 0, process);
    ordered
      .filter((section) => !section.matches(".hero"))
      .forEach((section) => main.append(section));
  }

  function improveImages() {
    const images = [...document.images];
    images.forEach((image, index) => {
      image.decoding = "async";
      if (!image.hasAttribute("loading") && index > 1) image.loading = "lazy";

      const width = Number(image.getAttribute("width"));
      const height = Number(image.getAttribute("height"));
      if (width > 0 && height > 0) {
        image.style.setProperty("--ui-image-ratio", `${width} / ${height}`);
        if (height / width > 2.4) image.classList.add("ui-image--tall");
        if (width / height > 1.8) image.classList.add("ui-image--wide");
      }
    });
  }

  function improveInteractiveElements() {
    document.querySelectorAll('.work-card[role="button"][aria-label]').forEach((card) => {
      card.removeAttribute("aria-label");
    });

    document.querySelectorAll('[role="button"][tabindex="0"]').forEach((element) => {
      if (element.dataset.uiKeyboardReady) return;
      element.dataset.uiKeyboardReady = "true";
      element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          element.click();
        }
      });
    });
  }

  function wireAnalytics() {
    document.addEventListener("click", (event) => {
      const tracked = event.target.closest("[data-track-event]");
      if (tracked) {
        track(tracked.dataset.trackEvent, tracked.dataset.trackLabel ? { label: tracked.dataset.trackLabel } : {});
        return;
      }

      const link = event.target.closest("a[href]");
      if (!link) return;

      const href = link.getAttribute("href") || "";
      if (href.includes("wa.me/")) {
        track("whatsapp_click");
      } else if (href.startsWith(STORE_DOMAIN)) {
        track("store_purchase_click");
      }
    }, { capture: true });
  }

  function removeIntrusivePatterns() {
    const announcement = document.getElementById("annBar");
    if (announcement) announcement.hidden = true;

    const consult = document.getElementById("consultPopup");
    const consultTrigger = document.getElementById("consultTrigger");
    if (consult) consult.hidden = true;
    if (consultTrigger) consultTrigger.hidden = true;

    const oldAdvisor = document.getElementById("advisor");
    if (oldAdvisor && document.getElementById("merchant-router")) oldAdvisor.hidden = true;
  }

  function createContextualCta() {
    if (document.body.classList.contains("ui-home")) return;
    if (window.location.pathname === BOOKING_URL) return;
    if (document.querySelector(".ui-contextual-cta")) return;

    const main = document.querySelector("main");
    if (!main) return;

    const path = window.location.pathname;
    let title = "ناقش مشروعك قبل اختيار الباقة";
    let text = "احجز استشارة Google Meet مجانية لنراجع المنصة والاحتياج والباقة المناسبة بدون تحويلك للشراء مبكراً.";
    let intent = "inner-page";

    if (path.includes("salla-store-design")) {
      title = "هل سلة مناسبة لمشروعك؟";
      text = "نراجع نوع المنتجات والميزانية ونحدد نطاق تصميم متجر سلة قبل بدء التنفيذ.";
      intent = "salla";
    } else if (path.includes("zid-store-design")) {
      title = "هل زد مناسبة لطريقة تشغيل متجرك؟";
      text = "نقارن احتياجك مع إمكانات زد ونقترح مساراً عملياً للإطلاق أو التطوير.";
      intent = "zid";
    } else if (path.includes("search-engine-optimization")) {
      title = "راجع فرص ظهور متجرك في البحث";
      text = "نناقش صفحات المنتجات، Search Console، والمشاكل التي تمنع المتجر من اكتساب زيارات مفيدة.";
      intent = "seo";
    } else if (path.includes("articles")) {
      title = "حوّل القراءة إلى قرار عملي";
      text = "إذا احتجت تطبيق ما قرأته على متجرك، احجز استشارة قصيرة ونرتب لك الخطوة التالية.";
      intent = "article";
    }

    const section = document.createElement("section");
    section.className = "ui-contextual-cta";
    section.setAttribute("aria-labelledby", "contextual-cta-title");
    section.innerHTML = `
      <div>
        <span class="ui-eyebrow">الخطوة التالية</span>
        <h2 id="contextual-cta-title">${title}</h2>
        <p>${text}</p>
      </div>
      <div class="ui-contextual-cta__actions">
        <a class="ui-button" href="${BOOKING_URL}?intent=${encodeURIComponent(intent)}" data-track-event="hero_booking_click">احجز استشارة مجانية</a>
        <a class="ui-button ui-button--secondary" href="${whatsappHref("مرحباً، أريد استفساراً عن " + title)}" target="_blank" rel="noopener noreferrer" data-track-event="whatsapp_click">واتساب سريع</a>
      </div>`;

    main.append(section);
  }

  function init() {
    setPageClasses();
    createHeader();

    let packages = null;
    let process = null;
    let router = null;
    let proof = null;
    if (document.body.classList.contains("ui-home")) {
      createHeroVisual();
      tuneHomepageHero();
      router = createMerchantRouter();
      proof = createProofSection();
      packages = createPackages();
      rebuildHomepageServices();
      process = createProcess();
      reorderHomepage(router, proof, packages, process);
    }

    createContextualCta();
    createFooter();
    createStickyContact();
    improveImages();
    improveInteractiveElements();
    wireAnalytics();
    removeIntrusivePatterns();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
