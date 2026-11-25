"use strict";
// Verify the image bytes, tracked Git objects, and the actual HTML references.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),cp=require('node:child_process');
const root=path.resolve(__dirname,'..');
let sharp;try{sharp=require('sharp');}catch{sharp=require(path.join(root,'scratch/phase1-baseline-20260715/node_modules/sharp'));}
const catalog=JSON.parse(fs.readFileSync(path.join(root,'data/portfolio.json'),'utf8'));
const origin='https://www.ezhalhe-sa.com';
const branch='codex/ui-ux-pro-max-redesign';
const urlPath=p=>p.split('/').map(encodeURIComponent).join('/');
(async()=>{
  const all=new Set(),links=[];
  for(const project of catalog.projects){
    assert(!all.has(project.image),'Duplicate original: '+project.id);
    for(const asset of [project.image,project.thumbnailSmall,project.thumbnail]){
      assert(asset.startsWith('/images/')&&!asset.includes('..'),'Expected same-origin image path');
      const relative=asset.slice(1),bytes=fs.readFileSync(path.join(root,relative));
      const decoded=await sharp(bytes).stats();assert(decoded.channels.length>=3,'Invalid image: '+asset);
      const uploaded=cp.execFileSync('git',['show','origin/'+branch+':'+relative],{cwd:root,maxBuffer:30*1024*1024});
      assert(bytes.equals(uploaded),'Local image differs from published Git image: '+asset);
      all.add(asset);
    }
    links.push({id:project.id,name:project.name,order:project.order,original:origin+urlPath(project.image),thumbnail:origin+urlPath(project.thumbnail),github:'https://github.com/g12ld/ezhlhee/blob/'+branch+urlPath(project.image)});
  }
  for(const filename of ['index.html','portfolio.html']){
    const html=fs.readFileSync(path.join(root,filename),'utf8');
    const cards=[...html.matchAll(/<article\b[^>]*data-project-id="([^"]+)"[^>]*>[\s\S]*?<\/article>/g)];
    assert.deepEqual(cards.map(x=>x[1]),catalog.projects.map(x=>x.id),'Incorrect gallery order in '+filename);
    for(const [i,card] of cards.entries()){
      const project=catalog.projects[i];
      assert(card[0].includes('src="'+project.thumbnail+'"'),'Missing thumbnail: '+project.id);
      assert(card[0].includes(project.thumbnailSmall+' 320w'),'Missing responsive source: '+project.id);
      assert(card[0].includes('href="'+urlPath(project.image)+'"'),'Missing full image link: '+project.id);
      assert(!/\bhidden(?:\s|=|>)/.test(card[0].split('>')[0]),'Project hidden initially: '+project.id);
    }
    assert(html.includes('width="520" height="650" decoding="async"'),'Preview dimensions missing');
  }
  const config=JSON.parse(fs.readFileSync(path.join(root,'vercel.json'),'utf8'));
  assert(config.headers.some(rule=>rule.headers.some(h=>h.key==='Content-Security-Policy'&&h.value.includes("img-src 'self'"))),'CSP must allow own images');
  const ignored=fs.readFileSync(path.join(root,'.vercelignore'),'utf8').split(/\r?\n/);
  assert(!ignored.some(p=>['images','images/','/images/','*.webp','**/*.webp'].includes(p.trim())),'Images excluded from deployment');
  fs.writeFileSync(path.join(root,'data/portfolio-image-links.json'),JSON.stringify({hosting:'Same-origin static assets deployed with the website; GitHub blob URLs are for review only.',projects:links},null,2)+'\n');
  console.log(JSON.stringify({status:'PASS',projects:links.length,decoded_images:all.size,published_git_images:all.size,galleries_checked:2,production_deployment_verified:false}));
})().catch(error=>{console.error(error.message);process.exitCode=1;});
