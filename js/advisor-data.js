(function(root){
"use strict";
const PACKAGES = {
  "plus": {
    "id": "plus",
    "slug": "plus",
    "name": "انطلاقة",
    "fullName": "باقة انطلاقة",
    "price": 599,
    "priceFormatted": "599",
    "oldPrice": null,
    "currency": "ريال",
    "badge": "بداية منظمة",
    "tagline": "باقة انطلاقة لتصميم متجر سلة",
    "bestFor": "ابدأ متجرًا على سلة بنطاق واضح يناسب المشروع الصغير: قسمان، بنران رئيسيان، وتجهيز الدفع والشحن، مع حد أقصى ١٠ منتجات.",
    "storeUrl": "https://ezhalhe.com/p377589337-%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D8%A8%D8%A7%D9%82%D8%A9-%D8%A7%D9%84%D8%A7%D9%86%D8%B7%D9%84%D8%A7%D9%82%D8%A9",
    "features": [
      "تصميم واجهة المتجر وترتيب بداية تجربة التسوق.",
      "إضافة قسمين لتسهيل الوصول إلى المنتجات.",
      "تصميم بنرين رئيسيين متناسقين مع نشاط المتجر.",
      "تفعيل إعدادات الدفع والشحن المتاحة لحسابك.",
      "إضافة المنتجات ضمن حد الباقة البالغ ١٠ منتجات."
    ],
    "notIncluded": [
      "اشتراك سلة وتكلفة الدومين منفصلان عن سعر التنفيذ.",
      "أي منتجات تتجاوز ١٠ أو تصاميم إضافية تحتاج اتفاقًا مستقلًا.",
      "تفعيل بوابات الدفع والشحن مرتبط بموافقة مقدم الخدمة واكتمال بيانات المتجر."
    ],
    "limits": {
      "products": 10,
      "banners": 2,
      "sections": 2
    },
    "color": "#125065",
    "servicePage": "/services/launch-package.html"
  },
  "professional": {
    "id": "professional",
    "slug": "professional",
    "name": "نمو الفضية",
    "fullName": "باقة نمو الفضية",
    "price": 1099,
    "priceFormatted": "1,099",
    "oldPrice": null,
    "currency": "ريال",
    "badge": "لتجهيز المتجر",
    "tagline": "باقة نمو الفضية لتصميم متجر سلة",
    "bestFor": "جهّز متجرك على سلة بواجهة منظمة وثلاثة أقسام وثلاثة بنرات، مع إعداد الصفحات الأساسية وإحصائيات المتجر وإضافة حتى ٢٥ منتجًا.",
    "storeUrl": "https://ezhalhe.com/p560117077-%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D8%A8%D8%A7%D9%82%D8%A9-%D9%86%D9%85%D9%88-%D8%A7%D9%84%D9%81%D8%B6%D9%8A%D8%A9",
    "features": [
      "إنشاء المتجر وضبط الإعدادات الأساسية وترتيب عناصر الثيم.",
      "إضافة ثلاثة أقسام وتصميم ثلاثة بنرات رئيسية.",
      "هيكلة الواجهة والتصنيفات بما يناسب الهوية التجارية.",
      "تجهيز حتى ٢٥ منتجًا من بياناتك وصورك.",
      "إعداد وسائل الدفع والشحن المتاحة للمتجر.",
      "متابعة توثيق المتجر وإضافة أيقونة واتساب.",
      "ربط إحصائيات المتجر وإنشاء صفحات الخصوصية والاستبدال والاسترجاع."
    ],
    "notIncluded": [
      "اشتراك سلة وحجز الدومين غير مشمولين بسعر الباقة.",
      "عدد المنتجات المشمول لا يتجاوز ٢٥ منتجًا.",
      "الموافقات والتوثيق تخضع لمتطلبات الجهة المعنية."
    ],
    "limits": {
      "products": 25,
      "banners": 3,
      "sections": 3
    },
    "color": "#125065",
    "servicePage": "/services/growth-package.html"
  },
  "gold": {
    "id": "gold",
    "slug": "gold",
    "name": "الذهبية برو",
    "fullName": "باقة الذهبية برو",
    "price": 1980,
    "priceFormatted": "1,980",
    "oldPrice": null,
    "currency": "ريال",
    "badge": "نطاق متكامل",
    "tagline": "الباقة الذهبية برو لتصميم المتاجر",
    "bestFor": "تصميم وتجهيز متجر متكامل يشمل الشعار وستة بنرات و٣٥ منتجًا وتخصيص CSS، مع SEO والتحليلات وبكسلات سناب وتيك توك ودومين .com.",
    "storeUrl": "https://ezhalhe.com/p1934611542-%D8%AA%D8%B7%D9%88%D9%8A%D8%B1-%D9%88%D8%A7%D9%84%D8%AA%D8%B5%D9%85%D9%8A%D9%85-%D9%85%D8%AA%D8%AC%D8%B1-%D8%A7%D9%84%D8%A7%D9%84%D9%83%D8%AA%D8%B1%D9%88%D9%86%D9%8A-%D8%A7%D9%84%D8%A8%D8%A7%D9%82%D8%A9-%D8%A7%D9%84%D8%B0%D9%87%D8%A8%D9%8A%D8%A9-%D8%A8%D8%A7%D9%82%D8%A9-%D8%A8%D8%B1%D9%88",
    "features": [
      "تصميم شعار وستة بنرات للعروض والتصنيفات والمنتجات.",
      "تنظيم الثيم وتحسين تجربة التصفح على الجوال وبقية الشاشات.",
      "تجهيز ٣٥ منتجًا بعناوين وأوصاف وتصنيفات وخيارات وصور وتاقات.",
      "تخصيص CSS وألوان الهيدر والفوتر والعناصر والتفاعلات البصرية.",
      "تهيئة SEO للمنتجات والأقسام والمدونة والعناوين والأوصاف والروابط.",
      "ربط Google Analytics وGoogle Search Console.",
      "ربط بكسلات سناب شات وتيك توك وإضافة أيقونة واتساب.",
      "حجز وربط دومين .com ومتابعة توثيق المتجر حسب المتطلبات."
    ],
    "notIncluded": [
      "الخدمات والاشتراكات غير المذكورة في النطاق تُراجع قبل بدء التنفيذ.",
      "SEO والقياس يساعدان في تحسين الظهور وفهم الأداء؛ ترتيب محدد أو مبيعات محددة غير مضمونة.",
      "تُحدد مدة حجز النطاق وتجديده وأي رسوم خارجية عند اعتماد الطلب."
    ],
    "limits": {
      "products": 35,
      "banners": 6,
      "sections": "حسب الاتفاق"
    },
    "color": "#125065",
    "servicePage": "/services/gold-package.html"
  }
};

const SERVICES = [
  { id: "store-design", label: "تصميم متجر", desc: "إنشاء واجهة متجر احترافية" },
  { id: "theme-edit", label: "تعديل ثيم", desc: "تعديل وتخصيص ثيم سلة/زد" },
  { id: "logo", label: "تصميم شعار", desc: "شعار وهوية بصرية" },
  { id: "banners", label: "تصميم بنرات", desc: "بنرات ثابتة ومتحركة" },
  { id: "products-upload", label: "رفع منتجات", desc: "رفع وتنسيق المنتجات" },
  { id: "product-desc", label: "كتابة وصف المنتجات", desc: "وصف تسويقي محسن للسيو" },
  { id: "seo", label: "SEO", desc: "تحسين ظهور متجرك في Google — SEO", tooltip: "SEO — تحسين ظهور متجرك في Google" },
  { id: "ga", label: "Google Analytics", desc: "ربط تحليلات جوجل لمعرفة سلوك الزوار" },
  { id: "search-console", label: "Search Console", desc: "ربط Google Search Console لمراقبة الظهور" },
  { id: "meta-pixel", label: "Meta Pixel", desc: "ربط بكسل فيسبوك/إنستغرام" },
  { id: "tiktok-pixel", label: "TikTok Pixel", desc: "ربط أدوات تتبع إعلانات تيك توك" },
  { id: "snapchat-pixel", label: "Snapchat Pixel", desc: "ربط أدوات تتبع إعلانات سناب" },
  { id: "payments", label: "إعداد الدفع", desc: "تفعيل مدى، أبل باي، فيزا، تحويل" },
  { id: "shipping", label: "إعداد الشحن", desc: "ربط سمسا وشركات الشحن" },
  { id: "domain", label: "دومين", desc: "حجز وربط دومين .com" },
  { id: "whatsapp", label: "أيقونة WhatsApp", desc: "إضافة زر واتساب للمتجر" },
  { id: "other", label: "غير ذلك", desc: "خدمة أخرى — اذكرها لنا" }
];

const ADVISOR_ENTRY_CARDS = [
  { id: "none", icon: "🌱", title: "ما عندي متجر", desc: "أبي أبدأ من الصفر وما أعرف من وين أبدأ.", path: "none" },
  { id: "new", icon: "🛒", title: "عندي متجر جديد", desc: "فتحت متجر سلة أو زد، لكن ما جهزته بشكل كامل.", path: "new" },
  { id: "existing", icon: "🚀", title: "عندي متجر وأبي أطوره", desc: "متجري شغال، لكن أبي أحسن التصميم أو المبيعات أو تجربة العميل.", path: "existing" },
  { id: "specific", icon: "🎯", title: "أبي خدمة محددة", desc: "مثل تصميم، شعار، بنرات، منتجات، SEO أو تعديل ثيم.", path: "specific" },
  { id: "unknown", icon: "💬", title: "مو عارف وش أحتاج", desc: "اسألني كم سؤال وحدد لي المناسب.", path: "unknown", isChat: true }
];

const WHATSAPP_NUMBER = "966503228029";

if(typeof module !== "undefined" && module.exports){
  module.exports = { PACKAGES, SERVICES, ADVISOR_ENTRY_CARDS, WHATSAPP_NUMBER };
}
if(root){
  root.ADVISOR_PACKAGES = PACKAGES;
  root.ADVISOR_SERVICES = SERVICES;
  root.ADVISOR_ENTRY_CARDS = ADVISOR_ENTRY_CARDS;
  root.ADVISOR_WA_NUMBER = WHATSAPP_NUMBER;
}
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : this);
