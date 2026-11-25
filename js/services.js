(function(){
 'use strict';
 const grid=document.getElementById('service-grid');if(!grid)return;
 const cards=[...grid.querySelectorAll('[data-service-id]')];
 const input=document.getElementById('service-search'),sort=document.getElementById('service-sort'),count=document.getElementById('service-count'),empty=document.getElementById('service-empty');
 const filters=[...document.querySelectorAll('[data-service-filter]')];
 const normalize=s=>String(s).normalize('NFKD').replace(/[\u064B-\u065F\u0670\u0640]/g,'').replace(/[أإآٱ]/g,'ا').replace(/ى/g,'ي').toLocaleLowerCase('ar');
 const entries=cards.map((card,index)=>({card,index,text:normalize(card.dataset.search),name:card.querySelector('h3').textContent.trim(),price:card.dataset.price===''?null:Number(card.dataset.price)}));
 const initial=new URL(location.href);let category=initial.searchParams.get('category')||'all';if(!filters.some(b=>b.dataset.serviceFilter===category))category='all';
 input.value=initial.searchParams.get('q')||'';if([...sort.options].some(o=>o.value===initial.searchParams.get('sort')))sort.value=initial.searchParams.get('sort');
 function apply(updateUrl){
  const words=normalize(input.value.trim()).split(/\s+/).filter(Boolean);
  filters.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.serviceFilter===category)));
  const ordered=[...entries].sort((a,b)=>{
   if(sort.value==='name')return a.name.localeCompare(b.name,'ar')||a.index-b.index;
   if(sort.value.startsWith('price-')){if(a.price===null&&b.price===null)return a.index-b.index;if(a.price===null)return 1;if(b.price===null)return -1;return (sort.value==='price-low'?a.price-b.price:b.price-a.price)||a.index-b.index;}
   return a.index-b.index;
  });let visible=0;
  ordered.forEach(e=>{const show=(category==='all'||e.card.dataset.category===category)&&words.every(w=>e.text.includes(w));e.card.hidden=!show;if(show)visible++;grid.append(e.card);});
  count.textContent='عرض '+visible+' من '+cards.length+' خدمة وباقة';empty.hidden=visible!==0;
  if(updateUrl){const u=new URL(location.href);for(const key of ['category','q','sort'])u.searchParams.delete(key);if(category!=='all')u.searchParams.set('category',category);if(input.value.trim())u.searchParams.set('q',input.value.trim());if(sort.value!=='recommended')u.searchParams.set('sort',sort.value);history.replaceState(null,'',u.pathname+u.search+u.hash);}
 }
 filters.forEach(b=>b.addEventListener('click',()=>{category=b.dataset.serviceFilter;apply(true);if(typeof window.gtag==='function')window.gtag('event','services_filter',{category});}));
 let timer;input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>apply(true),120);});
 sort.addEventListener('change',()=>apply(true));
 document.getElementById('service-reset').addEventListener('click',()=>{input.value='';category='all';sort.value='recommended';apply(true);input.focus();});
 apply(false);
})();
