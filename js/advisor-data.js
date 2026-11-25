(function(root){
"use strict";
const PACKAGES = {
  plus: {
    id: "plus",
    slug: "plus",
    name: "بلس",
    fullName: "باقة بلس",
    price: 1099,
    priceFormatted: "1,099",
    oldPrice: null,
    currency: "ريال",
    badge: "بداية منظمة",
    tagline: "الانطلاق السريع بتكلفة مناسبة",
    bestFor: "لصاحب مشروع يريد متجر مرتب وجاهز بميزانية محدودة.",
    storeUrl: "https://ezhalhe.com/تصميم-المتجر-احترفي-سلة-وزد-باقة-بلس/p560117077",
    features: [
      "إنشاء المتجر وضبط الإعدادات",
      "ترتيب العناصر بالثيم",
      "3 أقسام رئيسية",
      "3 بنرات احترافية",
      "تفعيل مدى وأبل باي وتحويل بنكي",
      "إعداد الشحن (سمسا والأنسب)",
      "10 منتجات مع وصف",
      "الصفحات القانونية"
    ],
    notIncluded: ["شعار / هوية بصرية","تحسين SEO","Google Analytics","أيقونة WhatsApp","توثيق منصة الأعمال","بكسل سناب + تيك توك","CSS متحرك","دومين .com مجاني","تابي وتمارا"],
    limits: { products: 10, banners: 3, sections: 3 },
    color: "#125065"
  },
  professional: {
    id: "professional",
    slug: "professional",
    name: "الاحترافية",
    fullName: "الباقة الاحترافية",
    price: 1490,
    priceFormatted: "1,490",
    oldPrice: 2290,
    currency: "ريال",
    badge: "الأكثر طلباً",
    tagline: "القيمة الأمثل لمعظم المتاجر",
    bestFor: "لمتجر يحتاج واجهة أقوى وهوية أولية وقياس واضح للزيارات.",
    storeUrl: "https://ezhalhe.com/الباقة-الاحترافية-—-تطوير-وتصميم-متجر-إلكتروني/p2132256496",
    features: [
      "إنشاء المتجر وضبط الإعدادات",
      "تصميم شعار احترافي مميز",
      "4 بنرات احترافية",
      "5 أقسام رئيسية",
      "20 منتج بوصف كامل",
      "تفعيل مدى وأبل باي والشحن",
      "تحسين SEO أساسي للمنتجات",
      "ربط Google Analytics",
      "ربط Google Search Console",
      "تفعيل أيقونة WhatsApp",
      "الصفحات القانونية"
    ],
    notIncluded: ["توثيق منصة الأعمال","بكسل سناب + تيك توك","CSS متحرك","دومين .com مجاني"],
    limits: { products: 20, banners: 4, sections: 5 },
    color: "#125065"
  },
  gold: {
    id: "gold",
    slug: "gold",
    name: "الذهبية",
    fullName: "الباقة الذهبية برو",
    price: 1980,
    priceFormatted: "1,980",
    oldPrice: 3200,
    currency: "ريال",
    badge: "استلم متجرك جاهزاً",
    tagline: "الحل الشامل — للشخص اللي يبي يختصر الطريق",
    bestFor: "لصاحب مشروع يريد تجهيز المتجر والهوية والقياس والتكاملات من البداية.",
    storeUrl: "https://ezhalhe.com/تطوير-والتصميم-متجر-الالكتروني-الباقة-الذهبية-باقة-برو/p1934611542",
    features: [
      "دومين .com مجاني لمدة عام",
      "تفعيل المدفوعات: مدى، أبل باي، فيزا، تحويل بنكي",
      "إعداد الشحن: سمسا والأنسب",
      "توثيق منصة الأعمال السعودية",
      "تصميم شعار احترافي + هوية",
      "6 بنرات احترافية",
      "برمجة CSS احترافية متحركة",
      "35 منتجاً باحترافية كاملة + SEO",
      "تفعيل بكسل سناب شات وتيك توك",
      "تابي وتمارا",
      "SEO متقدم وشامل",
      "ربط Google Analytics و Search Console",
      "شهر متابعة بعد التسليم"
    ],
    notIncluded: [],
    limits: { products: 35, banners: 6, sections: "غير محدود" },
    color: "#125065"
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
