(function () {
  "use strict";

  const WA_PHONE = "966501940155";
  const CALL_PHONE_DISPLAY = "0503228029";
  const CALL_PHONE_TEL = "+966503228029";
  const WA_BRIEF = encodeURIComponent("أريد استشارة حول تصميم وتطوير متجري الإلكتروني");
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

  function brandMarkup() {
    return `
      <a class="ui-brand" href="/" aria-label="إزهلها — الصفحة الرئيسية">
        <span class="ui-brand__mark">
          <img src="/images/responsive/logo-128.webp" width="128" height="128" alt="شعار إزهلها" decoding="async">
        </span>
        <span>
          <span class="ui-brand__name">إزهلها</span>
          <span class="ui-brand__tagline">شريكك لإطلاق متجر أقوى</span>
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
      ["أعمالنا", "/#work"],
      ["الباقات", "/#packages"],
      ["الخدمات", "/#services"],
      ["كيف نعمل", "/#process"],
      ["المقالات", "/articles.html"],
      ["الأسئلة", "/#faq"]
    ];

    const navLinks = links.map(([label, href]) => {
      const isCurrent = href === "/articles.html" && (currentPath === href || currentPath.startsWith("/articles/"));
      return `<a href="${href}"${isCurrent ? ' aria-current="page"' : ""}>${label}</a>`;
    }).join("");

    const mobileLinks = links.map(([label, href]) => `<a href="${href}"><span>${label}</span>${arrowIcon}</a>`).join("");
    const whatsappUrl = `https://wa.me/${WA_PHONE}?text=${WA_BRIEF}`;

    const header = document.createElement("header");
    header.className = "ui-header";
    header.innerHTML = `
      <div class="ui-header__inner">
        ${brandMarkup()}
        <nav class="ui-nav" aria-label="التنقل الرئيسي">${navLinks}</nav>
        <a class="ui-header__cta" href="${whatsappUrl}" target="_blank" rel="noopener noreferrer">
          ${whatsappIcon}<span>ابدأ مشروعك</span>
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
        <nav class="ui-mobile-nav__links" aria-label="التنقل على الجوال">${mobileLinks}</nav>
        <div class="ui-mobile-nav__cta">
          <a class="ui-button" href="${whatsappUrl}" target="_blank" rel="noopener noreferrer">${whatsappIcon} اطلب استشارة مجانية</a>
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
            <h2>ابدأ من هنا</h2>
            <nav class="ui-footer__links" aria-label="روابط الخدمات">
              <a href="/#packages">الباقات</a>
              <a href="/#services">الخدمات</a>
              <a href="/#work">معرض الأعمال</a>
              <a href="/#contact">اطلب الخدمة</a>
            </nav>
          </div>
          <div class="ui-footer__col">
            <h2>محتوى يساعدك</h2>
            <nav class="ui-footer__links" aria-label="روابط المعرفة">
              <a href="/articles.html">مركز المعرفة</a>
              <a href="/salla-store-design.html">تصميم متجر سلة</a>
              <a href="/zid-store-design.html">تصميم متجر زد</a>
              <a href="/search-engine-optimization.html">تحسين ظهور المتاجر</a>
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
      <a class="ui-button" href="https://wa.me/${WA_PHONE}?text=${WA_BRIEF}" target="_blank" rel="noopener noreferrer">
        ${whatsappIcon}<span>استشارة واتساب</span>
      </a>
      <a class="ui-button ui-button--call" href="tel:${CALL_PHONE_TEL}" aria-label="اتصال مباشر ${CALL_PHONE_DISPLAY}">${CALL_PHONE_DISPLAY}</a>`;
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

  function packageCard({ name, badge, audience, price, features, orderUrl, target, featured }) {
    const items = features.map((feature) => `<li>${feature}</li>`).join("");
    return `
      <article class="ui-package-card${featured ? " ui-package-card--featured" : ""}">
        <span class="ui-package-card__badge">${badge}</span>
        <h3>${name}</h3>
        <p class="ui-package-card__for">${audience}</p>
        <div class="ui-package-card__price"><strong>${price}</strong><span>ريال</span></div>
        <ul>${items}</ul>
        <div class="ui-package-card__actions">
          <a class="ui-button" href="${orderUrl}" target="_blank" rel="noopener noreferrer">اطلب الباقة ${arrowIcon}</a>
          <button class="ui-button ui-button--secondary" type="button" data-package-detail="${target}">عرض كل التفاصيل</button>
        </div>
      </article>`;
  }

  function createPackages() {
    const hero = document.querySelector(".ui-home .hero");
    if (!hero || document.getElementById("packages")) return null;

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
          ${packageCard({
            name: "الذهبية برو",
            badge: "الحل المتكامل",
            audience: "لمن يريد إطلاق متجر وهوية وتجهيزات تسويق كاملة.",
            price: "1,980",
            target: "pro",
            featured: true,
            orderUrl: "https://ezhalhe.com/تطوير-والتصميم-متجر-الالكتروني-الباقة-الذهبية-باقة-برو/p1934611542",
            features: ["هوية بصرية متكاملة", "35 منتجًا وتجهيز الإطلاق", "تخصيص CSS متقدم", "SEO وتحليلات وبكسلات", "دومين وربط تابي وتمارا"]
          })}
          ${packageCard({
            name: "الاحترافية",
            badge: "الأكثر طلبًا للتطوير",
            audience: "للمتاجر القائمة التي تحتاج واجهة أقوى وقياسًا أفضل.",
            price: "1,490",
            target: "professional",
            featured: false,
            orderUrl: "https://ezhalhe.com/الباقة-الاحترافية-—-تطوير-وتصميم-متجر-إلكتروني/p2132256496",
            features: ["رفع 20 منتجًا", "تصميم شعار", "تحسين واجهة المتجر", "تهيئة SEO أساسية", "Analytics وSearch Console"]
          })}
          ${packageCard({
            name: "بلس",
            badge: "للانطلاقة الذكية",
            audience: "للمشروع الجديد الذي يحتاج متجرًا مرتبًا وجاهزًا للبيع.",
            price: "1,099",
            target: "plus",
            featured: false,
            orderUrl: "https://ezhalhe.com/تصميم-المتجر-احترفي-سلة-وزد-باقة-بلس/p560117077",
            features: ["تجهيز متجر أساسي", "رفع 10 منتجات", "تصميم 3 بنرات", "ترتيب الأقسام والواجهة", "تسليم جاهز للانطلاق"]
          })}
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

  function reorderHomepage(packages, process) {
    const main = document.querySelector(".ui-home main");
    if (!main) return;

    const selectors = [
      ".hero",
      "#work",
      "#packages",
      "#services",
      "#process",
      "#testimonials",
      "#why-us",
      ".partners-sec",
      "#faq",
      ".articles-sec",
      "#coupon-salla",
      ".ticker-wrap",
      "#advisor",
      "#contact"
    ];

    const ordered = selectors.map((selector) => main.querySelector(`:scope > ${selector}`) || document.querySelector(`.ui-home ${selector}`)).filter(Boolean);
    if (packages && !ordered.includes(packages)) ordered.splice(2, 0, packages);
    if (process && !ordered.includes(process)) ordered.splice(4, 0, process);
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

  function removeIntrusivePatterns() {
    const announcement = document.getElementById("annBar");
    if (announcement) announcement.hidden = true;

    const consult = document.getElementById("consultPopup");
    const consultTrigger = document.getElementById("consultTrigger");
    if (consult) consult.hidden = true;
    if (consultTrigger) consultTrigger.hidden = true;
  }

  function init() {
    setPageClasses();
    createHeader();

    let packages = null;
    let process = null;
    if (document.body.classList.contains("ui-home")) {
      createHeroVisual();
      packages = createPackages();
      process = createProcess();
      reorderHomepage(packages, process);
    }

    createFooter();
    createStickyContact();
    improveImages();
    improveInteractiveElements();
    removeIntrusivePatterns();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
