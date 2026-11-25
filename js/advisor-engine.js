(function(root){
"use strict";
const PACKAGES = (root.ADVISOR_PACKAGES || (typeof require!=="undefined" ? require("./advisor-data.js").PACKAGES : {}));
const SERVICES = (root.ADVISOR_SERVICES || []);

function getPkg(id){
  return PACKAGES[id] || null;
}

function recommend(state){
  const result = recommendBase(state);
  if(result && result.type === "package"){
    // Current packages: only gold explicitly includes logo creation.
    if(state.hasLogo===false && result.packageId!=="gold")return buildPackageResult("gold",state);
    const minimum = state.productsCount === "10-20" ? 20 : ["20-35","more"].includes(state.productsCount) ? 35 : 0;
    if(result.package.limits.products < minimum){
      return buildPackageResult(minimum > 20 ? "gold" : "professional", state);
    }
  }
  return result;
}

function recommendBase(state){
  if(!state) return null;
  // Custom service path: if specific and 1-2 services selected -> custom
  if(state.storeStatus === "specific"){
    const count = (state.requestedServices||[]).length;
    if(count >=1 && count <=2){
      return {
        type: "custom",
        packageId: "custom",
        package: null,
        reasons: buildReasons(state, "custom"),
        compare: "",
        confidence: "high"
      };
    }
    if(count >=5){
      // many services => gold
      return buildPackageResult("gold", state);
    }
    if(count >=3){
      return buildPackageResult("professional", state);
    }
    // if no services yet, cannot recommend
    if(count===0) return null;
  }

  // Needs full setup explicit
  if(state.needsFullSetup === true) return buildPackageResult("gold", state);
  if(state.budgetPreference === "full") return buildPackageResult("gold", state);
  if(state.budgetPreference === "basic"){
    // unless complexity high, keep plus
    // but if existing wants full, gold overrides (already handled)
    // check if they have large product count -> suggest pro even if basic
    if(state.productsCount === "20-35" || state.productsCount === "more"){
      return buildPackageResult("professional", state);
    }
    return buildPackageResult("plus", state);
  }
  if(state.budgetPreference === "pro") return buildPackageResult("professional", state);

  // Path logic
  if(state.storeStatus === "none"){
    // Score based method
    let score = 0;
    if(state.hasLogo === false) score += 2;
    else if(state.hasLogo === "onlyLogo") score += 1;
    if(state.hasIdentity === false) score += 1;
    if(state.storeNameStatus === "no" || state.storeNameStatus === "idea") score += 1;
    if(state.productsReady === "no") score += 1;
    else if(state.productsReady === "partial") score += 0.5;
    if(state.productsCount === "20-35") score += 2;
    else if(state.productsCount === "more") score += 3;
    else if(state.productsCount === "10-20") score += 1;
    else if(state.productsCount === "<10") score += 0;
    else if(state.productsCount === "unknown") score += 1;

    // payment/shipping not ready implicit if none
    // if no identity + many products -> gold
    if(score >= 4) return buildPackageResult("gold", state);
    if(score >= 2) return buildPackageResult("professional", state);
    return buildPackageResult("plus", state);
  }

  if(state.storeStatus === "new"){
    // preparedItems analysis
    const items = state.preparedItems || [];
    const hasNone = items.includes("none");
    let missing = 0;
    const all = ["logo","products","payment","shipping","domain","design"];
    if(hasNone) missing = all.length;
    else {
      missing = all.filter(x=> !items.includes(x)).length;
    }
    // goal
    if(state.goal === "full") return buildPackageResult("gold", state);
    if(state.goal === "design" && missing <=2) return buildPackageResult("professional", state);
    if(state.goal === "sell" && missing >=3) return buildPackageResult("gold", state);
    if(missing >=5) return buildPackageResult("gold", state);
    if(missing >=3) return buildPackageResult("professional", state);
    if(missing <=2) {
      // if already has most, maybe plus enough unless they want full
      // but if they said "ما جهزت شيء تقريبًا" -> gold
      if(items.includes("logo") && items.includes("products")) return buildPackageResult("professional", state);
      return buildPackageResult("plus", state);
    }
    return buildPackageResult("professional", state);
  }

  if(state.storeStatus === "existing"){
    const issues = state.issues || [];
    if(issues.includes("full")) return buildPackageResult("gold", state);
    if(issues.includes("unknown")){
      // can't determine, lean to professional with suggestion of full audit
      return buildPackageResult("professional", state);
    }
    if(issues.length >=4) return buildPackageResult("gold", state);
    if(issues.length >=2) {
      // if includes seo+speed+design => gold maybe, else pro
      const heavy = ["seo","speed","tracking","payment_shipping"];
      const heavyCount = issues.filter(x=> heavy.includes(x)).length;
      if(heavyCount>=2) return buildPackageResult("gold", state);
      return buildPackageResult("professional", state);
    }
    if(issues.length ===1){
      const single = issues[0];
      // single banner/product => custom service? but we treat as plus/pro suggestion
      if(["banners","products"].includes(single)){
        // if single small service, could be custom, but since they chose "أبي أطوره" not specific, suggest pro as package upgrade
        return buildPackageResult("professional", state);
      }
      return buildPackageResult("professional", state);
    }
    // no issues yet
    return null;
  }

  if(state.storeStatus === "unknown"){
    // fallback heuristic: if has many signals, gold else professional
    // try to infer via productsCount and businessType
    if(state.productsCount === "more" || state.productsCount === "20-35") return buildPackageResult("gold", state);
    return buildPackageResult("professional", state);
  }

  // generic fallback based on productsCount
  if(state.productsCount === "20-35" || state.productsCount === "more") return buildPackageResult("gold", state);
  if(state.productsCount === "10-20") return buildPackageResult("professional", state);
  return null;
}

function buildPackageResult(pkgId, state){
  const reasons = buildReasons(state, pkgId);
  const compare = buildCompare(state, pkgId);
  return {
    type: "package",
    packageId: pkgId,
    package: getPkg(pkgId),
    reasons,
    compare,
    confidence: "high"
  };
}

function buildReasons(state, pkgId){
  const r=[];
  if(state.storeStatus === "none") r.push("ما عندك متجر حاليًا");
  else if(state.storeStatus === "new") r.push("عندك متجر جديد يحتاج تجهيز");
  else if(state.storeStatus === "existing") r.push("عندك متجر قائم وتبي تطويره");
  else if(state.storeStatus === "specific") r.push("طلبت خدمة محددة");

  if(state.platform === "salla") r.push("متجرك على سلة");
  else if(state.platform === "zid") r.push("متجرك على زد");

  if(state.businessType) r.push(`نشاطك: ${state.businessType}`);

  if(state.hasLogo === false) r.push("ما عندك هوية جاهزة");
  else if(state.hasLogo === "onlyLogo") r.push("عندك شعار فقط بدون هوية متكاملة");
  else if(state.hasLogo === true) r.push("عندك هوية جاهزة");

  if(state.storeNameStatus === "no") r.push("ما حددت اسم المتجر بعد");
  else if(state.storeNameStatus === "idea") r.push("عندك فكرة اسم فقط");

  if(state.productsCount){
    const map = {"<10":"أقل من 10 منتجات","10-20":"من 10 إلى 20 منتج","20-35":"من 20 إلى 35 منتج","more":"أكثر من 35 منتج","unknown":"عدد المنتجات غير محدد"};
    if(map[state.productsCount]) r.push(`عدد المنتجات: ${map[state.productsCount]}`);
  }
  if(state.productsReady === "no") r.push("المنتجات غير جاهزة بعد");
  else if(state.productsReady === "partial") r.push("بعض المنتجات جاهزة");

  if(state.budgetPreference === "full") r.push("تفضل تسليم المشروع كامل");
  else if(state.budgetPreference === "pro") r.push("تفضل متجر احترافي متوازن");
  else if(state.budgetPreference === "basic") r.push("تفضل الأساسيات فقط");

  if(state.needsFullSetup) r.push("طلبت شخص يتولى كل شيء");

  if(state.preparedItems && state.preparedItems.length){
    if(state.preparedItems.includes("none")) r.push("ما جهزت شيء تقريبًا");
    else {
      const labels = {logo:"الشعار",products:"المنتجات",payment:"الدفع",shipping:"الشحن",domain:"الدومين",design:"التصميم"};
      const ready = state.preparedItems.map(x=>labels[x]).filter(Boolean).join("، ");
      if(ready) r.push(`ما جهزته: ${ready}`);
      else if(state.preparedItems.includes("none")) r.push("ما جهزت شيء");
    }
  }
  if(state.goal){
    const gmap = {design:"هدفك شكل احترافي",sell:"هدفك تجهيزه للبيع",full:"هدفك شخص يستلمه كامل",unknown:"هدفك غير واضح بعد"};
    if(gmap[state.goal]) r.push(gmap[state.goal]);
  }
  if(state.issues && state.issues.length){
    if(state.issues.includes("full")) r.push("تحتاج تطوير شامل");
    else {
      const imap = {design:"مشكلة في شكل المتجر",home:"الصفحة الرئيسية تحتاج تحسين",mobile:"تجربة الجوال ضعيفة",banners:"البنرات تحتاج تصميم",products:"صفحة المنتجات",seo:"مشاكل SEO",speed:"سرعة المتجر",payment_shipping:"الدفع والشحن",tracking:"التتبع والإعلانات"};
      const txt = state.issues.map(x=>imap[x]).filter(Boolean).join("، ");
      if(txt) r.push(`أبرز المشاكل: ${txt}`);
    }
  }
  if(state.requestedServices && state.requestedServices.length){
    const svcLabels = SERVICES.filter(s=> state.requestedServices.includes(s.id)).map(s=>s.label).join("، ");
    if(svcLabels) r.push(`الخدمات المطلوبة: ${svcLabels}`);
  }
  if(state.storeUrl) r.push(`رابط المتجر: ${state.storeUrl}`);

  // package-specific justification
  if(pkgId==="gold"){
    if(!r.find(x=>x.includes("هوية"))) {
      // add generic gold justification if not already
    }
  }
  // limit to 6 reasons max for UI clarity
  return r.slice(0,6);
}

function buildCompare(state, pkgId){
  const alternatives=Object.values(PACKAGES).filter(p=>p.id!==pkgId).map(p=>p.fullName+' — '+p.priceFormatted+' ريال ('+p.limits.products+' منتجًا، '+p.limits.banners+' بنرات)');
  return 'للمقارنة: '+alternatives.join('؛ ')+'. راجع التفاصيل والاستثناءات في صفحة كل باقة قبل اعتماد الاختيار.';
}

function getWhatWeDo(pkgId){return getPkg(pkgId)?.features||[];}
function getWhatWeNeed(state, pkgId){
  const needs=[];
  if(!state.businessType) needs.push("اسم النشاط أو الفكرة");
  else needs.push(`تأكيد النشاط: ${state.businessType}`);
  if(pkgId==="plus" || pkgId==="professional" || pkgId==="gold"){
    if(state.productsCount) needs.push(`المنتجات والصور (حوالي ${state.productsCount})`);
    else needs.push("المنتجات والصور");
  }
  needs.push("بيانات حساب سلة/زد عند الحاجة");
  needs.push("ملاحظاتك على التصميم والألوان");
  if(state.storeUrl) needs.push(`رابط متجرك: ${state.storeUrl}`);
  if(state.requestedServices && state.requestedServices.length){
    needs.push("تفاصيل الخدمات المحددة التي اخترتها");
  }
  return needs.slice(0,5);
}
function getAfterDelivery(pkgId){
  if(pkgId==="gold") return "نشرح لك كيف تستخدم سلة أو زد ونتابع معك لمدة شهر إذا واجهتك استفسارات أو مشاكل متعلقة بالعمل المنفذ. شرح إدارة المنتجات والطلبات وأهم الإعدادات.";
  if(pkgId==="professional") return "نسلمك المتجر جاهز مع شرح أساسيات الإدارة (المنتجات والطلبات) ودليل استخدام مختصر.";
  if(pkgId==="plus") return "نسلمك المتجر جاهز للانطلاق مع شرح أساسي للوحة التحكم.";
  return "نسلمك العمل مع شرح الاستخدام.";
}

function isReadyForRecommendation(state){
  if(!state) return false;
  // need at least storeStatus and one more signal
  if(!state.storeStatus) return false;
  if(state.storeStatus==="specific") return (state.requestedServices||[]).length>0;
  if(state.storeStatus==="none"){
    return !!(state.productsCount && state.budgetPreference && state.hasLogo!=null);
  }
  if(state.storeStatus==="new"){
    return !!(state.goal || (state.productsCount && state.budgetPreference && state.hasLogo!=null));
  }
  if(state.storeStatus==="existing"){
    return !!(state.issues||[]).length>0;
  }
  if(state.storeStatus==="unknown"){
    return !!(state.platform || state.productsCount || state.businessType);
  }
  return false;
}

function buildWhatsAppMessage(state, rec){
  const lines=[];
  lines.push("السلام عليكم ليث،");
  lines.push("استخدمت مستشار الموقع وأبي أبدأ مشروع متجر.");
  lines.push("");
  lines.push("حالتي:");
  // dynamic bullets
  if(state.storeStatus==="none") lines.push("• ما عندي متجر حاليًا");
  else if(state.storeStatus==="new") lines.push("• عندي متجر جديد يحتاج تجهيز");
  else if(state.storeStatus==="existing") lines.push("• عندي متجر قائم وأبي أطوره");
  else if(state.storeStatus==="specific") lines.push("• أبي خدمة محددة");
  else if(state.storeStatus) lines.push(`• الحالة: ${state.storeStatus}`);

  if(state.businessType) lines.push(`• النشاط: ${state.businessType}`);
  if(state.platform) {
    const pm = {salla:"سلة",zid:"زد",unknown:"غير محددة"};
    lines.push(`• المنصة: ${pm[state.platform]||state.platform}`);
  } else lines.push("• المنصة: غير محددة");
  if(state.productsCount){
    const pm = {"<10":"أقل من 10","10-20":"10 إلى 20","20-35":"20 إلى 35","more":"أكثر من 35","unknown":"غير محدد"};
    lines.push(`• عدد المنتجات: ${pm[state.productsCount]||state.productsCount}`);
  }
  if(state.hasLogo!==null){
    const lm = {true:"موجود",false:"غير موجود",onlyLogo:"شعار فقط",idea:"فكرة فقط"};
    lines.push(`• الشعار: ${lm[state.hasLogo]||state.hasLogo}`);
  }
  if(state.hasIdentity!==null && state.hasIdentity!==undefined){
    lines.push(`• الهوية: ${state.hasIdentity ? "موجودة":"غير موجودة"}`);
  }
  if(state.preparedItems && state.preparedItems.length){
    const labels = {logo:"الشعار",products:"المنتجات",payment:"الدفع",shipping:"الشحن",domain:"الدومين",design:"التصميم",none:"لا شيء مجهز"};
    const txt = state.preparedItems.map(x=>labels[x]||x).join("، ");
    lines.push(`• ما جهزته: ${txt}`);
  }
  if(state.issues && state.issues.length){
    const imap = {design:"شكل المتجر",home:"الصفحة الرئيسية",mobile:"الجوال",banners:"البنرات",products:"المنتجات",seo:"SEO",speed:"السرعة",payment_shipping:"الدفع والشحن",tracking:"التتبع والإعلانات",full:"تطوير شامل",unknown:"غير محدد"};
    const txt = state.issues.map(x=>imap[x]||x).join("، ");
    lines.push(`• مشاكل المتجر: ${txt}`);
  }
  if(state.requestedServices && state.requestedServices.length){
    const svcLabels = SERVICES.filter(s=> state.requestedServices.includes(s.id)).map(s=>s.label).join("، ");
    lines.push(`• الخدمات المطلوبة: ${svcLabels}`);
  }
  if(state.storeUrl) lines.push(`• رابط المتجر: ${state.storeUrl}`);
  if(state.goal){
    const gmap={design:"شكل احترافي",sell:"تجهيزه للبيع",full:"تسليم كامل",unknown:"غير محدد"};
    lines.push(`• الهدف: ${gmap[state.goal]||state.goal}`);
  }
  lines.push("");
  if(rec && rec.type==="package" && rec.package){
    lines.push(`الباقة التي رشحها لي الموقع:`);
    lines.push(`${rec.package.fullName} — ${rec.package.priceFormatted} ${rec.package.currency}`);
    if(state.productsCount === "more") lines.push("عدد المنتجات يتجاوز 35؛ يلزم تحديد تكلفة الإضافات بعد مراجعة الطلب.");
    lines.push("");
    if(rec.reasons && rec.reasons.length){
      lines.push("سبب الترشيح:");
      rec.reasons.slice(0,3).forEach(r=> lines.push(`• ${r}`));
      lines.push("");
    }
  } else if(rec && rec.type==="custom"){
    const svcLabels = SERVICES.filter(s=> state.requestedServices.includes(s.id)).map(s=>s.label).join("، ");
    lines.push(`الخدمات التي اخترتها:`);
    lines.push(`• ${svcLabels}`);
    if(state.storeUrl) lines.push(`رابط المتجر: ${state.storeUrl}`);
    lines.push("");
  } else {
    lines.push("أحتاج مساعدة في تحديد الباقة الأنسب.");
    lines.push("");
  }
  lines.push("وأرغب أبدأ معكم. بانتظار التفاصيل والتكلفة النهائية.");
  return lines.join("\n");
}

function buildWhatsAppLink(state, rec){
  const msg = buildWhatsAppMessage(state, rec);
  const num = (root.ADVISOR_WA_NUMBER || "966503228029");
  return `https://wa.me/${num}?text=${encodeURIComponent(msg)}`;
}

// Dynamic recalculation helper
function recalcIfNeeded(state, patch){
  const next = Object.assign({}, state, patch);
  // if the change affects recommendation, recompute
  const before = recommend(state);
  const after = recommend(next);
  return { before, after, next };
}

const AdvisorEngine = {
  recommend,
  buildReasons,
  buildCompare,
  getWhatWeDo,
  getWhatWeNeed,
  getAfterDelivery,
  isReadyForRecommendation,
  buildWhatsAppMessage,
  buildWhatsAppLink,
  recalcIfNeeded,
  getPkg
};

if(typeof module !== "undefined" && module.exports) module.exports = AdvisorEngine;
if(root) root.AdvisorEngine = AdvisorEngine;
})(typeof window !== "undefined" ? window : typeof globalThis !== "undefined" ? globalThis : this);
