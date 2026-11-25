(function(){
"use strict";
function track(name,params){if(typeof window.gtag==="function")window.gtag("event",name,params||{});}
function init(){
  const button=document.querySelector('.ez-menu-button');
  const nav=document.getElementById('ez-mobile-nav');
  if(button && nav){
    function close(){nav.hidden=true;button.setAttribute('aria-expanded','false');button.setAttribute('aria-label','فتح القائمة');}
    button.addEventListener('click',()=>{const open=nav.hidden;nav.hidden=!open;button.setAttribute('aria-expanded',String(open));button.setAttribute('aria-label',open?'إغلاق القائمة':'فتح القائمة');});
    nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
    document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!nav.hidden){close();button.focus();}});
  }
  document.addEventListener('click',event=>{
    const target=event.target.closest('[data-track-event],a[href]');
    if(!target)return;
    const name=target.dataset.trackEvent || (target.href?.includes('wa.me/')?'whatsapp_click':null);
    if(name)track(name);
  });
  const form=document.getElementById('ez-contact-form');
  if(form){
    const preview=document.getElementById('ez-contact-preview');
    const link=document.getElementById('ez-contact-link');
    const consent=document.getElementById('ez-contact-consent');
    const status=document.getElementById('ez-contact-status');
    form.addEventListener('submit',event=>{
      event.preventDefault();
      if(!form.reportValidity())return;
      const data=new FormData(form);
      const text=['مرحبًا فريق إزهلها،','أرغب في مناقشة مشروعي.','الاسم: '+String(data.get('name')).trim(),'الخدمة: '+data.get('service'),'التفاصيل: '+String(data.get('message')).trim()].join('\n');
      document.getElementById('ez-contact-summary').textContent=text;
      link.href='https://wa.me/'+window.EZHALHA_CONFIG.company.whatsappNumber+'?text='+encodeURIComponent(text);
      preview.hidden=false;consent.checked=false;link.hidden=true;
      status.textContent='راجع الملخص، ثم وافق على مشاركته لفتح واتساب. ترسل الرسالة بنفسك من هناك.';
      track('contact_preview');
    });
    consent.addEventListener('change',()=>{link.hidden=!consent.checked;});
    form.addEventListener('input',event=>{
      if(event.target===consent)return;
      preview.hidden=true;consent.checked=false;link.hidden=true;
    });
  }
  // No personal fields or chat text enter analytics.
  if('IntersectionObserver' in window){
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){track(entry.target.id==='packages'?'view_pricing':'view_service');observer.unobserve(entry.target);}}),{threshold:.3});
    ['packages','services'].forEach(id=>{const section=document.getElementById(id);if(section)observer.observe(section);});
  }
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
