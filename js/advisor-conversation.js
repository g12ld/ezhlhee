(function(root){
"use strict";
const data = typeof module !== "undefined" && module.exports ? require("./advisor-data.js") : null;
const packages = data ? data.PACKAGES : root.ADVISOR_PACKAGES;
const engine = data ? require("./advisor-engine.js") : root.AdvisorEngine;
function normalize(value){
  return String(value || "").toLowerCase().replace(/[أإآ]/g,"ا").replace(/[ً-ْ]/g,"")
    .replace(/[٠-٩]/g,c=>String(c.charCodeAt(0)-1632)).replace(/[۰-۹]/g,c=>String(c.charCodeAt(0)-1776))
    .replace(/[–—]/g,"-").trim();
}
function extract(message,state){
  const text=normalize(message), out={};
  const has=pattern=>pattern.test(text);
  if(has(/ما عندي متجر|بدون متجر|من الصفر/)) out.storeStatus="none";
  else if(has(/اطور متجري|تطوير متجري|عندي متجر/)) out.storeStatus=has(/جديد|تو فتحت|توي فاتح/) ? "new" : "existing";
  else if(has(/خدمة محددة|خدمه محدده/)) out.storeStatus="specific";
  if(has(/سلة|salla/) && !has(/زد|zid/)) out.platform="salla";
  if(has(/زد|zid/) && !has(/سلة|salla/)) out.platform="zid";
  if(has(/ما اعرف|غير متاكد/) && has(/سلة|salla/) && has(/زد|zid/)) out.platform="unknown";
  if(text==="غير متاكد") out.platform="unknown";
  for(const [pattern,label] of [[/عطور|مسك|عود/,"عطور وعود"],[/عبايات/,"عبايات"],[/ملابس|ازياء/,"أزياء"]]){
    if(has(pattern)) out.businessType=label;
  }
  if(has(/ما عندي شعار|بدون شعار|ولا شعار/)){out.hasLogo=false;out.hasIdentity=false;}
  else if(has(/شعار فقط/)){out.hasLogo="onlyLogo";out.hasIdentity=false;}
  else if(has(/عندي شعار|هوية جاهزة/)){out.hasLogo=true;out.hasIdentity=has(/هوية جاهزة/);}
  if(has(/ما عندي هوية|بدون هوية/)) out.hasIdentity=false;
  const count=text.match(/(?:^|\s)(\d+)\s*منتج/);
  if(has(/اقل من 10/)) out.productsCount="<10";
  else if(has(/10\s*(?:-|الى)\s*20/)) out.productsCount="10-20";
  else if(has(/20\s*(?:-|الى)\s*35/)) out.productsCount="20-35";
  else if(has(/^اكثر(?: من 35)?$/)) out.productsCount="more";
  else if(count){const n=Number(count[1]);out.productsCount=n<10?"<10":n<=20?"10-20":n<=35?"20-35":"more";}
  if(has(/^ما اعرف(?: حتى الان)?$/) && !state.productsCount) out.productsCount="unknown";
  if(has(/الاساسيات|الاشياء الاساسية|ارخص|اقل تكلفة/)){out.budgetPreference="basic";out.needsFullSetup=false;}
  else if(has(/متجر احترافي/)){out.budgetPreference="pro";out.needsFullSetup=false;}
  else if(has(/تسليم كامل|تسلموني|كل شي|يستلم|يتولى/)){out.budgetPreference="full";out.needsFullSetup=true;}
  const issues=[];
  for(const [pattern,id] of [[/شكل|تصميم|قديم/,"design"],[/جوال/,"mobile"],[/سرعة|بطي/,"speed"],[/seo|جوجل|google|بحث/,"seo"],[/تتبع|بكسل|طلبات قليلة/,"tracking"],[/دفع|شحن/,"payment_shipping"],[/تطوير شامل/,"full"]]){
    if(has(pattern)) issues.push(id);
  }
  if(has(/^الاثنين$/)) issues.push("design","mobile");
  if(issues.length) out.issues=[...new Set([...(state.issues||[]),...issues])];
  const selected=[];
  for(const [pattern,id] of [[/شعار/,"logo"],[/بنر|بنرات/,"banners"],[/seo|تحسين.*بحث/,"seo"],[/رفع.*منتج/,"products-upload"],[/تعديل.*ثيم/,"theme-edit"]]){
    if(has(pattern) && !has(/ما عندي|بدون|ولا شعار/)) selected.push(id);
  }
  if((out.storeStatus||state.storeStatus)==="specific" && selected.length) out.requestedServices=[...new Set([...(state.requestedServices||[]),...selected])];
  if(has(/^ما جهزت شي/)) out.preparedItems=["none"];
  if(has(/اجهزه للبيع/)) out.goal="sell";
  if(has(/شكل احترافي/)) out.goal="design";
  if(out.needsFullSetup) out.goal="full";
  const url=String(message).match(/https?:\/\/[^\s<>]+/i);
  if(url) out.storeUrl=url[0].slice(0,300);
  return out;
}
function next(state){
  if(!state.storeStatus || state.storeStatus==="unknown") return {field:"storeStatus",question:"عندك متجر حاليًا، أو تبي تبدأ من الصفر؟",suggestions:["ما عندي متجر","عندي متجر جديد","أبي أطور متجري","أبي خدمة محددة"]};
  if(state.storeStatus==="specific"){
    if(!(state.requestedServices||[]).length) return {field:"requestedServices",question:"وش الخدمة اللي تحتاجها؟",suggestions:["تصميم شعار","تصميم بنرات","تحسين SEO","تعديل الثيم"]};
    return null;
  }
  if(state.storeStatus==="existing"){
    if(!(state.issues||[]).length) return {field:"issues",question:"وش أكثر شيء تبي تحسنه في متجرك؟",suggestions:["شكل المتجر","تجربة الجوال","سرعة المتجر","تطوير شامل"]};
    if(!state.platform) return {field:"platform",question:"متجرك على أي منصة؟",suggestions:["سلة","زد","غير متأكد"]};
    return null;
  }
  if(!state.productsCount) return {field:"productsCount",question:"تقريبًا كم منتج تبي نجهزه في المتجر؟",suggestions:["أقل من 10","10–20","20–35","أكثر من 35","ما أعرف"]};
  if(state.hasLogo==null) return {field:"hasLogo",question:"عندك شعار وهوية جاهزة؟",suggestions:["عندي شعار وهوية جاهزة","عندي شعار فقط","ما عندي شعار"]};
  if(!state.budgetPreference) return {field:"budgetPreference",question:"وش مستوى التجهيز اللي تفضله؟",suggestions:["الأساسيات فقط","متجر احترافي","تسليم كامل"]};
  return null;
}
function reply(message,state){
  state=state||{};
  const extracted=extract(message,state), merged=Object.assign({},state,extracted), step=next(merged);
  const text=normalize(message);
  let answer=step ? "تمام، فهمت عليك.\n\n"+step.question : "صار عندي تصور لاحتياجك. تقدر تشوف التوصية وتراجع ملخص طلبك قبل فتح واتساب.";
  if(/اسعار|تكلفة|سعر/.test(text)) answer=Object.values(packages).map(p=>p.fullName+": "+p.priceFormatted+" ريال").join("\n")+"\nالأسعار لا تشمل أي إضافات خارج نطاق الباقة."+(step?"\n\n"+step.question:"");
  if(!step && /ليش|لماذا|قارن|الفرق/.test(text)){
    const rec=engine.recommend(merged);
    if(rec) answer=/قارن|الفرق/.test(text) && rec.type==="package" ? engine.buildCompare(merged,rec.packageId) : "سبب الترشيح:\n"+rec.reasons.join("\n");
  }
  if(merged.productsCount==="more") answer+="\nعدد منتجاتك يتجاوز 35 منتجًا؛ نحدد تكلفة المنتجات الإضافية بعد مراجعة الطلب.";
  return {message:answer,extracted,missingFields:step?[step.field]:[],nextQuestion:step?step.question:"",suggestions:step?step.suggestions:["عرض التوصية","أرسل طلبي واتساب","أبدأ من جديد"]};
}
const api={normalize,extract,next,reply};
if(typeof module!=="undefined" && module.exports) module.exports=api;
else root.AdvisorConversation=api;
})(typeof window!=="undefined"?window:globalThis);
