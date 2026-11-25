"use strict";
// Keep the homepage and advisor on the currently verified store package scope.
const fs=require('node:fs'),path=require('node:path');const root=path.resolve(__dirname,'..');
const {services}=require('../data/services.json');
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mapping=[['plus','377589337','انطلاقة'],['professional','560117077','نمو الفضية'],['gold','1934611542','الذهبية برو']];
const old=require('../js/advisor-data.js').PACKAGES;const packages={};
for(const [id,sourceId,name] of mapping){const s=services.find(x=>x.id===sourceId);packages[id]={...old[id],name,fullName:'باقة '+name,price:s.price,priceFormatted:s.price.toLocaleString('en-US'),oldPrice:null,currency:'ريال',badge:id==='gold'?'نطاق متكامل':id==='professional'?'لتجهيز المتجر':'بداية منظمة',tagline:s.name,bestFor:s.lead,storeUrl:s.sourceUrl,servicePage:s.path,features:s.includes,notIncluded:s.notes,limits:{products:s.products,banners:s.banners,sections:s.sections||'حسب الاتفاق'},color:'#125065'};}
const dataPath=path.join(root,'js/advisor-data.js');let data=fs.readFileSync(dataPath,'utf8');data=data.replace(/const PACKAGES = \{[\s\S]*?\n\};(?=\s*const SERVICES)/,'const PACKAGES = '+JSON.stringify(packages,null,2)+';');fs.writeFileSync(dataPath,data);
const configPath=path.join(root,'data/site-config.js');const config=require(configPath);config.urls.services='/services.html';
config.packages=mapping.map(([id,,name])=>{const p=packages[id];return {id:id==='gold'?'golden-pro':id,name,nameAr:name,priceSar:p.price,badge:p.badge,audience:p.bestFor,topFeatures:p.features,storeUrl:p.storeUrl,servicePage:p.servicePage,campaign:'package_'+id};});
fs.writeFileSync(configPath,'(function(root,factory){const config=factory();if(typeof module==="object"&&module.exports)module.exports=config;if(root)root.EZHALHA_CONFIG=config;})(typeof globalThis!=="undefined"?globalThis:this,function(){return '+JSON.stringify(config,null,2)+';});\n');
const enginePath=path.join(root,'js/advisor-engine.js');let engine=fs.readFileSync(enginePath,'utf8');
engine=engine.replace(/function buildCompare\(state, pkgId\)\{[\s\S]*?\n\}\n\nfunction getWhatWeDo/,`function buildCompare(state, pkgId){
  const alternatives=Object.values(PACKAGES).filter(p=>p.id!==pkgId).map(p=>p.fullName+' — '+p.priceFormatted+' ريال ('+p.limits.products+' منتجًا، '+p.limits.banners+' بنرات)');
  return 'للمقارنة: '+alternatives.join('؛ ')+'. راجع التفاصيل والاستثناءات في صفحة كل باقة قبل اعتماد الاختيار.';
}

function getWhatWeDo`);
engine=engine.replace(/function getWhatWeDo\(pkgId\)\{[\s\S]*?\n\}\nfunction getWhatWeNeed/,`function getWhatWeDo(pkgId){return getPkg(pkgId)?.features||[];}
function getWhatWeNeed`);
const enforce='  if(result && result.type === "package"){';
if(!engine.includes('Current packages: only gold explicitly includes logo creation.'))engine=engine.replace(enforce,enforce+'\n    // Current packages: only gold explicitly includes logo creation.\n    if(state.hasLogo===false && result.packageId!=="gold")return buildPackageResult("gold",state);');
fs.writeFileSync(enginePath,engine);
const homePath=path.join(root,'index.html');let home=fs.readFileSync(homePath,'utf8');
const start=home.search(/<section\b[^>]*\bid="packages"/),end=home.indexOf('<section ',start+10);if(start<0||end<0)throw new Error('Homepage package section missing');
const html=`<section class="ez-section" id="packages" aria-labelledby="packages-title"><div class="ez-container"><div class="ez-section-head"><div><span class="ez-eyebrow">باقات المتجر الحالية</span><h2 id="packages-title">اختر بداية تناسب حجم مشروعك.</h2><p>انطلاقة، نمو الفضية، والذهبية برو. اقرأ النطاق والاستثناءات في صفحة الباقة قبل الطلب.</p></div><a class="ez-text-link" href="/services.html?category=design">كل باقات التصميم</a></div><div class="ez-packages">${mapping.map(([id])=>{const p=packages[id];return `<article class="ez-package${id==='gold'?' ez-package--featured':''}"><span class="ez-eyebrow">${p.badge}</span><h3>${p.fullName}</h3><p>${esc(p.bestFor)}</p><div class="ez-package__price">${p.priceFormatted}<span>ريال</span></div><ul>${['حتى '+p.limits.products+' منتجًا',p.limits.banners+' بنرات',...p.features.slice(0,3)].map(f=>'<li>'+esc(f)+'</li>').join('')}</ul><a class="ez-button" href="${p.servicePage}">تفاصيل الباقة</a><a class="ez-text-link" href="${esc(p.storeUrl)}" target="_blank" rel="noopener">اطلب من المتجر</a></article>`;}).join('')}</div><p class="svc-fine">اشتراكات المنصات والرسوم الخارجية موضحة في تفاصيل كل باقة، والسعر النهائي المعتمد عند الطلب من المتجر.</p></div></section>\n`;
home=home.slice(0,start)+html+home.slice(end);
// Existing JSON-LD Product/Offer nodes must agree with visible package prices.
home=home.replace(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/,(_,raw)=>{
 const graph=JSON.parse(raw);
 function update(node){
  if(!node||typeof node!=='object')return;
  if([node['@type']].flat().includes('Product')){
   const id=/بلس|انطلاقة/.test(node.name)?'plus':/الاحترافية|نمو الفضية/.test(node.name)?'professional':/الذهبية/.test(node.name)?'gold':null;
   if(id){const p=packages[id];node.name=p.fullName;node.description=p.bestFor;node.url='https://www.ezhalhe-sa.com'+p.servicePage;if(node.offers){node.offers.price=String(p.price);node.offers.url=p.storeUrl;}}
  }
  Object.values(node).forEach(value=>{if(Array.isArray(value))value.forEach(update);else update(value);});
 }
 update(graph);return '<script type="application/ld+json">'+JSON.stringify(graph).replace(/</g,'\\u003c')+'</script>';
});
fs.writeFileSync(homePath,home);
console.log(JSON.stringify({packages:mapping.map(([id])=>({id,name:packages[id].name,price:packages[id].price,products:packages[id].limits.products}))}));
