"use strict";
const fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,"..");
const catalogPath=path.join(root,"data/portfolio.json");
const catalog=JSON.parse(fs.readFileSync(catalogPath,"utf8"));
let sharp;try{sharp=require("sharp");}catch{sharp=require(path.join(root,"scratch/phase1-baseline-20260715/node_modules/sharp"));}
const esc=value=>String(value||"").replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fileUrl=value=>value.split('/').map(encodeURIComponent).join('/');
const toolbar=(prefix)=>`<div class="ez-gallery-toolbar"><div class="portfolio-toolbar" role="group" aria-label="تصفية التصاميم حسب المنصة">${[['all','الكل'],['سلة','سلة'],['زد','زد'],['توسع','توسع']].map(([value,label])=>`<button class="portfolio-filter" type="button" data-filter="${value}" aria-pressed="${value==='all'}">${label}</button>`).join('')}</div><label class="ez-gallery-sort" for="${prefix}-sort">الترتيب<select id="${prefix}-sort" data-gallery-sort><option value="original">ترتيب المعرض</option><option value="name">الاسم</option></select></label></div><p class="ez-gallery-count" role="status" aria-live="polite" data-gallery-count>عرض ${catalog.projects.length} من ${catalog.projects.length} تصميمًا</p>`;
function cards(){return catalog.projects.map(project=>`<article class="portfolio-card ez-project" id="project-${project.id}" data-platform="${esc(project.platform)}" data-project-id="${project.id}" data-order="${project.order}" data-image-width="${project.width}" data-image-height="${project.height}" data-name="${esc(project.name)}"><a class="ez-project__image" href="${fileUrl(project.image)}" data-gallery-open="${project.id}" aria-label="عرض تصميم ${esc(project.name)} كاملًا"><img src="${project.thumbnail}" srcset="${project.thumbnailSmall} 320w, ${project.thumbnail} 520w" sizes="(max-width: 599px) calc(100vw - 40px), (max-width: 959px) 45vw, 380px" width="520" height="650" alt="${esc(project.alt)}" loading="lazy" decoding="async"></a><div class="ez-project__meta"><div><h3>${esc(project.name)}</h3><p>${esc(project.category && project.category!==project.name ? project.category : 'تصميم واجهة متجر')}</p></div><span>${esc(project.platform)}</span></div><a class="ez-gallery-view" href="${fileUrl(project.image)}" data-gallery-open="${project.id}">عرض التصميم كاملًا</a></article>`).join('\n');}
const dialog=`<dialog id="portfolio-dialog" class="ez-gallery-dialog" aria-labelledby="portfolio-dialog-title"><div class="ez-gallery-dialog__header"><div><h2 id="portfolio-dialog-title">عرض التصميم</h2><p id="portfolio-dialog-meta"></p></div><button type="button" data-gallery-close aria-label="إغلاق معاينة التصميم">إغلاق</button></div><div class="ez-gallery-dialog__image"><img id="portfolio-dialog-image" alt="معاينة التصميم المختار" width="520" height="650" decoding="async"></div><div class="ez-gallery-dialog__controls"><button type="button" data-gallery-previous>التصميم السابق</button><span id="portfolio-dialog-position" role="status"></span><button type="button" data-gallery-next>التصميم التالي</button></div></dialog>`;
(async()=>{
  const imageDir=path.join(root,"images/portfolio");fs.mkdirSync(imageDir,{recursive:true});
  for(const project of catalog.projects){
    const input=path.join(root,project.image.slice(1));
    const info=await sharp(input).metadata();
    project.width=info.width;project.height=info.height;
    project.thumbnail=`/images/portfolio/${project.id}-520.webp`;
    project.thumbnailSmall=`/images/portfolio/${project.id}-320.webp`;
    for(const width of [320,520]){
      const height=Math.round(width*1.25),output=path.join(root,`images/portfolio/${project.id}-${width}.webp`);
      if(!fs.existsSync(output))await sharp(input).resize(width,height,{fit:"cover",position:"top"}).webp({quality:82}).toFile(output);
    }
  }
  fs.writeFileSync(catalogPath,JSON.stringify(catalog,null,2)+'\n');
  const pagePath=path.join(root,"portfolio.html");let page=fs.readFileSync(pagePath,"utf8");
  const backupDir=path.join(root,"scratch/full-portfolio-backup");fs.mkdirSync(backupDir,{recursive:true});
  if(!fs.existsSync(path.join(backupDir,"portfolio.html")))fs.copyFileSync(pagePath,path.join(backupDir,"portfolio.html"));
  const sectionStart=page.indexOf('    <section class="portfolio-grid-section');
  const sectionEnd=page.indexOf('    <section class="case-study-system"',sectionStart);
  if(sectionStart<0||sectionEnd<0)throw new Error('Expected portfolio sections not found');
  page=page.slice(0,sectionStart)+`    <section class="portfolio-grid-section ez-full-gallery" aria-labelledby="portfolio-grid-title" data-gallery><div class="ez-section-head"><div><span class="ez-eyebrow">أعمالنا، بكل تفاصيلها</span><h2 id="portfolio-grid-title">${catalog.projects.length} تصميمًا، وتجارب مختلفة.</h2></div></div>${toolbar('portfolio')}<div class="portfolio-grid ez-projects" id="portfolio-grid" data-gallery-grid>${cards()}</div></section>\n\n`+page.slice(sectionEnd);
  page=page.replace('هذه الصفحة تعرض نماذج فعلية من واجهات المتاجر الموجودة في ملفات المشروع. نعرض الحقائق المتوفرة فقط: اسم المتجر، المنصة، القطاع، ونطاق العمل الظاهر من المحتوى الحالي.','تصفّح أعمالنا على سلة وزد وتوسع. من الأزياء والعناية إلى العود والمنتجات الطبيعية، لكل متجر طريقة عرض تناسبه. افتح أي تصميم لمشاهدة الواجهة كاملة.');
  page=page.replace('id="portfolio-title">أعمال إزهلها في متاجر سلة وزد','id="portfolio-title">تصاميم متاجر، لكل طموح');
  page=page.replace('فلتر الأعمال حسب المنصة.','استعرض جميع التصاميم أو اختر المنصة.');
  page=page.replace('راجع شكل العرض على الصفحة الرئيسية للمتجر.','افتح التصميم لتشاهد تفاصيل الواجهة كاملة.');
  page=page.replace('/portfolio.js?v=20260905-godmode','/portfolio.js?v=20261125-full');
  if(page.includes('id="portfolio-dialog"'))page=page.replace(/<dialog id="portfolio-dialog"[\s\S]*?<\/dialog>/,dialog);
  else page=page.replace('</body>',dialog+'\n</body>');
  fs.writeFileSync(pagePath,page);
  const homePath=path.join(root,"index.html");let home=fs.readFileSync(homePath,"utf8");
  if(!fs.existsSync(path.join(backupDir,"index.html")))fs.copyFileSync(homePath,path.join(backupDir,"index.html"));
  const homeStart=home.search(/<section\b[^>]*\bid="work"/);
  const homeEnd=home.indexOf('<section class="ez-section ez-services-section"',homeStart);
  if(homeStart<0||homeEnd<0)throw new Error('Expected homepage sections not found');
  home=home.slice(0,homeStart)+`<section class="ez-section ez-full-gallery" id="work" aria-labelledby="work-title" data-gallery><div class="ez-container"><div class="ez-section-head"><div><span class="ez-eyebrow">من أعمالنا</span><h2 id="work-title">كل متجر،<br>حكاية وتصميم يخصّه.</h2><p>كل تصاميمنا في مكان واحد. تصفّحها بالترتيب، وافتح أي تصميم لتشاهد الواجهة كاملة.</p></div><a class="ez-text-link" href="/portfolio.html">صفحة الأعمال الكاملة</a></div>${toolbar('home')}<div class="ez-projects" data-gallery-grid>${cards()}</div></div></section>\n`+home.slice(homeEnd);
  if(home.includes('id="portfolio-dialog"'))home=home.replace(/<dialog id="portfolio-dialog"[\s\S]*?<\/dialog>/,dialog);
  else home=home.replace('</body>',dialog+'\n<script src="/portfolio.js?v=20261125-full" defer></script>\n</body>');
  fs.writeFileSync(homePath,home);
  console.log(JSON.stringify({projects:catalog.projects.length,homepage_cards:catalog.projects.length,portfolio_cards:catalog.projects.length,original_images_unchanged:true}));
})().catch(error=>{console.error(error.message);process.exitCode=1;});
