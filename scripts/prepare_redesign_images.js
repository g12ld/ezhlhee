"use strict";
const fs=require("node:fs"),path=require("node:path");
const root=path.resolve(__dirname,"..");
let sharp;
try{sharp=require("sharp");}catch{sharp=require(path.join(root,"scratch/phase1-baseline-20260715/node_modules/sharp"));}
(async()=>{
  for(const name of ["lara","duk","lana"]){
    await sharp(path.join(root,"images/v2",name+"-preview.webp")).resize(360,480).webp({quality:84}).toFile(path.join(root,"images/v2",name+"-preview-360.webp"));
  }
  const file=path.join(root,"index.html");
  let html=fs.readFileSync(file,"utf8");
  for(const name of ["lara","duk","lana"]){
    const source=`src="/images/v2/${name}-preview.webp"`;
    if(!html.includes(`${name}-preview-360.webp`)) html=html.replaceAll(source,`${source} srcset="/images/v2/${name}-preview-360.webp 360w, /images/v2/${name}-preview.webp 525w" sizes="(max-width: 599px) 60vw, (max-width: 959px) 45vw, 525px"`);
  }
  fs.writeFileSync(file,html);
  console.log("Responsive preview derivatives prepared.");
})();
