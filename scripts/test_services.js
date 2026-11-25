"use strict";
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),catalog=require('../data/services.json');
test('every verified service has a distinct indexable page and deployable original cover',()=>{
 const sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8'),hub=fs.readFileSync(path.join(root,'services.html'),'utf8');
 assert.equal(catalog.services.length,28);assert.equal(new Set(catalog.services.map(s=>s.path)).size,28);
 assert.equal([...hub.matchAll(/data-service-id="/g)].length,28);
 for(const s of catalog.services){const html=fs.readFileSync(path.join(root,s.path.slice(1)),'utf8');assert.equal([...html.matchAll(/<h1\b/g)].length,1);assert.ok(html.includes(s.sourceUrl));assert.ok(sitemap.includes('https://www.ezhalhe-sa.com'+s.path+'</loc>'));assert.ok(html.includes('href="/services.html"'));assert.ok(!html.includes('FAQPage'));assert.ok(s.price===null||s.price>0);for(const image of [s.image,s.imageSmall]){const b=fs.readFileSync(path.join(root,image.slice(1)));assert.equal(b.toString('ascii',0,4),'RIFF');assert.equal(b.toString('ascii',8,12),'WEBP');}}
});
test('package recommendation prices and limits match the currently published store scope',()=>{
 const {PACKAGES}=require('../js/advisor-data.js'),engine=require('../js/advisor-engine.js');
 assert.deepEqual(Object.values(PACKAGES).map(p=>[p.price,p.limits.products,p.limits.banners]),[[599,10,2],[1099,25,3],[1980,35,6]]);
 assert.equal(engine.recommend({storeStatus:'none',hasLogo:false,productsCount:'<10',budgetPreference:'basic'}).packageId,'gold');
 const homepage=fs.readFileSync(path.join(root,'index.html'),'utf8');const graph=JSON.parse(homepage.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
 const products=[];function walk(n){if(!n||typeof n!=='object')return;if([n['@type']].flat().includes('Product'))products.push(n);Object.values(n).forEach(v=>{if(Array.isArray(v))v.forEach(walk);else walk(v);});}walk(graph);
 for(const p of Object.values(PACKAGES)){const product=products.find(n=>n.name===p.fullName);assert.ok(product,'Missing matching homepage Product: '+p.fullName);assert.equal(Number(product.offers.price),p.price);}
});
function run(initial='https://www.ezhalhe-sa.com/services.html'){
 const filters=['all',...catalog.categories.map(c=>c.id)].map(id=>({dataset:{serviceFilter:id},attributes:{},events:{},setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,f){this.events[k]=f;}}));
 const cards=catalog.services.map(s=>({dataset:{serviceId:s.id,category:s.group,price:s.price===null?'':String(s.price),search:s.name+' '+s.storeName+' '+s.lead},hidden:false,querySelector(){return{textContent:s.name};}}));
 const elements={
 'service-grid':{ordered:[],querySelectorAll(){return cards;},append(card){this.ordered=this.ordered.filter(c=>c!==card);this.ordered.push(card);}},
 'service-search':{value:'',events:{},addEventListener(k,f){this.events[k]=f;},focus(){this.focused=true;}},
 'service-sort':{value:'recommended',options:['recommended','price-low','price-high','name'].map(value=>({value})),events:{},addEventListener(k,f){this.events[k]=f;}},
 'service-count':{},'service-empty':{},'service-reset':{events:{},addEventListener(k,f){this.events[k]=f;}}
 };
 const context={URL,location:new URL(initial),history:{replaceState(...args){this.url=args[2];}},document:{getElementById:id=>elements[id],querySelectorAll:()=>filters},window:{},setTimeout:f=>{f();return 1;},clearTimeout(){}};
 vm.runInNewContext(fs.readFileSync(path.join(root,'js/services.js'),'utf8'),context);
 return {elements,cards,filters,context,visible:()=>elements['service-grid'].ordered.filter(c=>!c.hidden)};
}
test('service filters, Arabic search, empty reset and shared category links work together',()=>{
 const r=run();assert.equal(r.visible().length,28);
 r.filters.find(b=>b.dataset.serviceFilter==='design').events.click();assert.equal(r.visible().length,4);
 r.elements['service-search'].value='إِنْطِلاقَة';r.elements['service-search'].events.input();assert.equal(r.visible().length,1);assert.equal(r.visible()[0].dataset.serviceId,'377589337');
 r.elements['service-search'].value='zzzz-no-service';r.elements['service-search'].events.input();assert.equal(r.visible().length,0);assert.equal(r.elements['service-empty'].hidden,false);
 r.elements['service-reset'].events.click();assert.equal(r.visible().length,28);assert.equal(r.elements['service-search'].focused,true);
 const linked=run('https://www.ezhalhe-sa.com/services.html?category=measurement');assert.equal(linked.visible().length,5);assert.ok(linked.visible().every(c=>c.dataset.category==='measurement'));
});
test('price sorting keeps variable-price services last in both directions',()=>{
 const r=run();for(const value of ['price-low','price-high']){r.elements['service-sort'].value=value;r.elements['service-sort'].events.change();const priced=r.visible().filter(c=>c.dataset.price!=='').map(c=>Number(c.dataset.price));assert.deepEqual(priced,[...priced].sort((a,b)=>value==='price-low'?a-b:b-a));assert.equal(r.visible().at(-1).dataset.price,'');}
});
