(function (root, factory) {
  const config = factory();
  if (typeof module === "object" && module.exports) module.exports = config;
  if (root) root.EZHALHA_CONFIG = config;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const STORE_DOMAIN = "https://ezhalhe.com";
  const BUSINESS_DOMAIN = "https://www.ezhalhe-sa.com";

  return {
    company: {
      nameAr: "إزهلها",
      nameEn: "Ezhalha",
      businessDomain: BUSINESS_DOMAIN,
      storeDomain: STORE_DOMAIN,
      email: "mr.leith9999@gmail.com",
      phoneDisplay: "+966 50 322 8029",
      phoneTel: "+966503228029",
      whatsappNumber: "966503228029",
      startedYear: 2022,
      country: "المملكة العربية السعودية",
      city: "الرياض",
      devNotes: [
        "Verify the public email before replacing it with a branded mailbox.",
        "Use portfolio counts only when the owner confirms the count should be a marketing claim."
      ]
    },
    urls: {
      home: "/",
      booking: "/booking.html",
      portfolio: "/portfolio.html",
      about: "/about.html",
      privacy: "/privacy.html",
      articles: "/articles.html",
      salla: "/salla-store-design.html",
      zid: "/zid-store-design.html",
      seo: "/search-engine-optimization.html",
      whatsapp: "https://wa.me/966503228029",
      store: STORE_DOMAIN
    },
    booking: {
      timezone: "Asia/Riyadh",
      durationMinutes: 30,
      bufferMinutes: 0,
      minNoticeHours: 4,
      maxDaysAhead: 21,
      workingDays: [0, 1, 2, 3, 4, 5, 6],
      startTime: "12:00",
      endTime: "22:00"
    },
    packages: [
      {
        id: "plus",
        name: "Plus",
        nameAr: "بلس",
        priceSar: 1099,
        badge: "بداية منظمة",
        audience: "لتاجر جديد يحتاج متجرًا مرتبًا وجاهزًا للبيع بدون تعقيد.",
        topFeatures: ["إعداد المتجر الأساسي", "رفع 10 منتجات", "3 بنرات", "ترتيب الأقسام", "تسليم جاهز للانطلاق"],
        storeUrl: STORE_DOMAIN + "/تصميم-المتجر-احترفي-سلة-وزد-باقة-بلس/p560117077",
        campaign: "package_plus"
      },
      {
        id: "professional",
        name: "Professional",
        nameAr: "الاحترافية",
        priceSar: 1490,
        badge: "الأقرب لمعظم المتاجر",
        audience: "لمتجر يحتاج واجهة أقوى وهوية أولية وقياس واضح للزيارات.",
        topFeatures: ["رفع 20 منتجًا", "تصميم شعار", "تحسين واجهة المتجر", "تهيئة SEO أساسية", "Analytics وSearch Console"],
        storeUrl: STORE_DOMAIN + "/الباقة-الاحترافية-—-تطوير-وتصميم-متجر-إلكتروني/p2132256496",
        campaign: "package_professional"
      },
      {
        id: "golden-pro",
        name: "Golden Pro",
        nameAr: "الذهبية برو",
        priceSar: 1980,
        badge: "إطلاق متكامل",
        audience: "لصاحب مشروع يريد تجهيز المتجر والهوية والقياس والتكاملات من البداية.",
        topFeatures: ["هوية بصرية متكاملة", "35 منتجًا", "تخصيص CSS", "SEO وتحليلات وبكسلات", "دومين وربط تابي وتمارا"],
        storeUrl: STORE_DOMAIN + "/تطوير-والتصميم-متجر-الالكتروني-الباقة-الذهبية-باقة-برو/p1934611542",
        campaign: "package_golden_pro"
      }
    ],
    services: [
      {
        id: "launch",
        title: "إطلاق متجر جديد",
        description: "تجهيز متجر سلة أو زد أو WooCommerce من الهيكل حتى الإطلاق.",
        links: ["/salla-store-design.html", "/zid-store-design.html"]
      },
      {
        id: "improve",
        title: "تطوير متجر قائم",
        description: "تحسين الواجهة وتجربة الجوال وصفحات المنتجات ومسار الشراء.",
        links: ["/#packages", "/portfolio.html"]
      },
      {
        id: "growth",
        title: "النمو والقياس",
        description: "SEO، تحليلات، Search Console، وربط بكسلات الحملات بدون تعقيد.",
        links: ["/search-engine-optimization.html"]
      },
      {
        id: "setup",
        title: "التأسيس والتوثيق",
        description: "دعم الأعمال المرتبطة بإطلاق المتجر مثل الدومين والتوثيق وبعض التكاملات.",
        links: ["/store-verification.html", "/secure-payments.html"]
      }
    ],
    portfolio: [
      {
        id: "lana",
        name: "متجر لانا",
        platform: "سلة",
        category: "أزياء نسائية",
        packageId: "golden-pro",
        image: "/images/responsive/lana-badawood-salla-gold-pro-360.webp",
        fullImage: "/images/lana-badawood-salla-gold-pro.webp",
        alt: "واجهة متجر لانا للأزياء على منصة سلة",
        summary: "واجهة طويلة موثقة بلقطة من المتجر مع تركيز على عرض المنتجات البصرية."
      },
      {
        id: "lara",
        name: "لارا السعد بوتيك",
        platform: "سلة",
        category: "أزياء وإكسسوارات",
        packageId: "golden-pro",
        image: "/images/responsive/lara-alsaad-boutique-salla-gold-pro-360.webp",
        fullImage: "/images/lara-alsaad-boutique-salla-gold-pro.webp",
        alt: "واجهة متجر لارا السعد بوتيك على منصة سلة",
        summary: "تصميم واجهة متجر أزياء يعتمد على إبراز التصنيفات والمنتجات بصريًا."
      },
      {
        id: "duk",
        name: "دوك الطيب",
        platform: "سلة",
        category: "عود ومسك",
        packageId: "golden-pro",
        image: "/images/responsive/duk-altayeb-salla-gold-pro-360.webp",
        fullImage: "/images/duk-altayeb-salla-gold-pro.webp",
        alt: "واجهة متجر دوك الطيب للعود والمسك على منصة سلة",
        summary: "متجر عطور وعود مع واجهة تركز على الثقة والتصنيفات الواضحة."
      },
      {
        id: "rivna",
        name: "Rivna",
        platform: "سلة",
        category: "عسل طبيعي",
        packageId: "golden-pro",
        image: "/images/responsive/rivna-360.webp",
        fullImage: "/images/rivna.webp",
        alt: "واجهة متجر Rivna للعسل الطبيعي على منصة سلة",
        summary: "تصميم متجر منتجات طبيعية مع عرض بصري مناسب للفئات والمنتجات."
      },
      {
        id: "siwar",
        name: "Siwar Altyeb",
        platform: "زد",
        category: "عطور وعود",
        packageId: "golden-pro",
        image: "/images/responsive/swartyp_zid-360.webp",
        fullImage: "/images/swartyp_zid.webp",
        alt: "واجهة متجر Siwar Altyeb على منصة زد",
        summary: "نموذج موثق لمنصة زد ضمن قطاع العطور والعود."
      },
      {
        id: "asl-noura",
        name: "متجر عسل نورة",
        platform: "سلة",
        category: "منتجات طبيعية",
        packageId: "plus",
        image: "/images/responsive/asl_noura_plus-360.webp",
        fullImage: "/images/asl_noura_plus.webp",
        alt: "واجهة متجر عسل نورة على منصة سلة",
        summary: "إطلاق مبسط مناسب لبداية متجر منتجات طبيعية."
      }
    ],
    knowledgeClusters: [
      {
        id: "salla",
        title: "سلة",
        description: "تصميم، إعداد، SEO، وتجربة شراء لمتاجر سلة.",
        page: "/salla-store-design.html"
      },
      {
        id: "zid",
        title: "زد",
        description: "اختيار زد، بناء المتجر، وتجهيز تجربة مناسبة للعلامات السعودية.",
        page: "/zid-store-design.html"
      },
      {
        id: "growth",
        title: "نمو المتجر",
        description: "SEO، التحليلات، صفحات المنتجات، وتحسين التحويل.",
        page: "/search-engine-optimization.html"
      },
      {
        id: "operations",
        title: "تشغيل التجارة السعودية",
        description: "الدفع، التوثيق، الدومين، والحسابات المرتبطة بإطلاق المتجر.",
        page: "/store-verification.html"
      }
    ]
  };
});
