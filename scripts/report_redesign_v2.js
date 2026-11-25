"use strict";
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const root=path.resolve(__dirname,".."),dest=path.join(root,"docs/redesign-v2");
const originals=[];
function walk(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){if(entry.isDirectory()){if(entry.name!=="v2")walk(path.join(dir,entry.name));}else{const file=path.join(dir,entry.name),buffer=fs.readFileSync(file);originals.push({path:path.relative(root,file).replaceAll("\\","/"),bytes:buffer.length,sha256:crypto.createHash("sha256").update(buffer).digest("hex")});}}}
walk(path.join(root,"images"));
fs.writeFileSync(path.join(dest,"asset-inventory.json"),JSON.stringify({recorded:"2026-11-25",note:"Inventory after migration. Original image files were not written by the redesign. This is not a historical checksum comparison.",originals,new_derivatives:fs.readdirSync(path.join(root,"images/v2")).map(file=>({path:"images/v2/"+file,bytes:fs.statSync(path.join(root,"images/v2",file)).size}))},null,2));
const before=fs.statSync(path.join(root,"scratch/redesign-v2-backup/index.html")).size;
const after=fs.statSync(path.join(root,"index.html")).size;
console.log(JSON.stringify({original_images_retained:originals.length,homepage_html_before_bytes:before,homepage_html_after_bytes:after,html_reduction_percent:Math.round(100*(1-after/before))}));
