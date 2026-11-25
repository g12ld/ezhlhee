(function(){
"use strict";
function track(name,params){if(typeof window.gtag==="function")window.gtag("event",name,params||{});}
function init(){
  const galleries=[...document.querySelectorAll('[data-gallery]')];
  if(!galleries.length)return;
  const dialog=document.getElementById('portfolio-dialog');
  const fullImage=document.getElementById('portfolio-dialog-image');
  let opener=null,currentGallery=null,currentId=null;
  function visibleCards(gallery){return [...gallery.querySelectorAll('[data-project-id]')].filter(card=>!card.hidden);}
  function updatePosition(){
    const cards=visibleCards(currentGallery),index=cards.findIndex(card=>card.dataset.projectId===currentId);
    document.getElementById('portfolio-dialog-position').textContent=(index+1)+' من '+cards.length;
    dialog.querySelector('[data-gallery-previous]').disabled=index<=0;
    dialog.querySelector('[data-gallery-next]').disabled=index>=cards.length-1;
  }
  function show(card){
    currentId=card.dataset.projectId;
    const link=card.querySelector('[data-gallery-open]'),image=card.querySelector('img');
    document.getElementById('portfolio-dialog-title').textContent=card.dataset.name;
    document.getElementById('portfolio-dialog-meta').textContent='منصة '+card.dataset.platform;
    fullImage.width=Number(card.dataset.imageWidth)||520;fullImage.height=Number(card.dataset.imageHeight)||650;
    fullImage.src=link.href;fullImage.alt=image.alt;
    dialog.querySelector('.ez-gallery-dialog__image').scrollTop=0;
    updatePosition();track('portfolio_project_view',{project_id:currentId});
  }
  function move(offset){
    const cards=visibleCards(currentGallery),index=cards.findIndex(card=>card.dataset.projectId===currentId);
    if(cards[index+offset])show(cards[index+offset]);
  }
  function apply(gallery){
    const grid=gallery.querySelector('[data-gallery-grid]');
    const filter=gallery.querySelector('[aria-pressed="true"][data-filter]')?.dataset.filter||'all';
    const sort=gallery.querySelector('[data-gallery-sort]')?.value||'original';
    const cards=[...grid.querySelectorAll('[data-project-id]')];
    cards.sort(sort==='name'?(a,b)=>a.dataset.name.localeCompare(b.dataset.name,'ar')||Number(a.dataset.order)-Number(b.dataset.order):(a,b)=>Number(a.dataset.order)-Number(b.dataset.order));
    cards.forEach(card=>{card.hidden=filter!=='all'&&card.dataset.platform!==filter;grid.append(card);});
    gallery.querySelector('[data-gallery-count]').textContent='عرض '+cards.filter(card=>!card.hidden).length+' من '+cards.length+' تصميمًا';
  }
  galleries.forEach(gallery=>{
    gallery.addEventListener('click',event=>{
      const filter=event.target.closest('[data-filter]');
      if(filter){
        gallery.querySelectorAll('[data-filter]').forEach(button=>button.setAttribute('aria-pressed',String(button===filter)));
        apply(gallery);track('portfolio_filter',{platform:filter.dataset.filter});return;
      }
      const link=event.target.closest('[data-gallery-open]');
      if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey||!dialog||typeof dialog.showModal!=='function')return;
      event.preventDefault();opener=link;currentGallery=gallery;
      show(link.closest('[data-project-id]'));dialog.showModal();
      document.body.classList.add('ez-gallery-open');dialog.querySelector('[data-gallery-close]').focus();
    });
    gallery.querySelector('[data-gallery-sort]')?.addEventListener('change',()=>apply(gallery));
    apply(gallery);
  });
  if(dialog){
    dialog.querySelector('[data-gallery-close]').addEventListener('click',()=>dialog.close());
    dialog.querySelector('[data-gallery-previous]').addEventListener('click',()=>move(-1));
    dialog.querySelector('[data-gallery-next]').addEventListener('click',()=>move(1));
    dialog.addEventListener('close',()=>{document.body.classList.remove('ez-gallery-open');fullImage.removeAttribute('src');opener?.focus();});
    dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
    dialog.addEventListener('keydown',event=>{if(['ArrowRight','ArrowLeft'].includes(event.key)&&!event.target.matches('input,textarea,select')){event.preventDefault();move(event.key==='ArrowLeft'?1:-1);}});
  }
  document.querySelectorAll('[data-case-study]').forEach(link=>link.addEventListener('click',()=>track('case_study_view',{case_study:link.dataset.caseStudy})));
  track('portfolio_view');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
