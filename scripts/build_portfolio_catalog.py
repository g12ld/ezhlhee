"""Recover the original gallery order and metadata from local Git history."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import subprocess,json,re,html

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'logo.webp','og-cover.webp','salla.webp','zid.webp','shopify.webp','wordpress.webp','whatsapp.webp'}
PLATFORMS={'salla':'سلة','zid':'زد','tawsaa':'توسع'}
class Gallery(HTMLParser):
    def __init__(self):
        super().__init__();self.depth=0;self.card=None;self.capture=None;self.items=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);classes=attrs.get('class','').split()
        if self.card is None and tag=='div' and 'work-card' in classes:
            match=re.search(r"openLb\('([^']*)','([^']*)','([^']*)'\)",attrs.get('onclick',''))
            if not match:return
            self.card={'image':'/'+unquote(match[1]).lstrip('/'),'name':match[2],'platform':PLATFORMS.get(attrs.get('data-plat'),'غير محددة'),'platformId':attrs.get('data-plat','unknown'),'packageId':attrs.get('data-pkg',''),'category':''}
            self.depth=1;return
        if self.card is not None:
            if tag=='div':self.depth+=1
            if 'card-cat' in classes:self.capture='category'
            if 'card-title' in classes:self.capture='displayName'
    def handle_endtag(self,tag):
        if self.card is None:return
        if tag=='div':
            self.capture=None;self.depth-=1
            if self.depth==0:self.items.append(self.card);self.card=None
    def handle_data(self,value):
        if self.card is not None and self.capture:self.card[self.capture]=self.card.get(self.capture,'')+value.strip()

def git(*args):return subprocess.run(['git',*args],cwd=ROOT,capture_output=True,encoding='utf8',check=True).stdout
def parsed(source):
    parser=Gallery();parser.feed(source);return parser.items

def main():
    assets={p.name for p in (ROOT/'images').glob('*.webp') if p.name not in EXCLUDED}
    items=parsed(git('show','HEAD:index.html'));seen={Path(i['image']).name for i in items}
    head=git('rev-parse','HEAD').strip()
    for item in items:item['sourceRevision']=head
    missing=assets-seen
    commits=git('log','--all','--format=%H','--','index.html').splitlines()
    for sha in commits:
        if not missing:break
        for item in parsed(git('show',f'{sha}:index.html')):
            name=Path(item['image']).name
            if name in missing:
                item['sourceRevision']=sha;items.append(item);missing.remove(name)
    if missing:raise SystemExit('Missing project metadata: '+', '.join(sorted(missing)))
    # Preserve existing detail anchors already linked from the homepage.
    ids={'lana-badawood-salla-gold-pro.webp':'lana','lara-alsaad-boutique-salla-gold-pro.webp':'lara','duk-altayeb-salla-gold-pro.webp':'duk','swartyp_zid.webp':'siwar','asl_noura_plus.webp':'asl-noura','rivna.webp':'rivna'}
    result=[]
    for index,item in enumerate(items):
        name=Path(item['image']).name
        if name not in assets:continue
        item['id']=ids.get(name,re.sub(r'[^a-z0-9]+','-',Path(name).stem.lower()).strip('-'))
        item['order']=len(result)+1
        item['name']=html.unescape(item.get('displayName') or item['name']).strip()
        item.pop('displayName',None)
        item['alt']=f"تصميم واجهة {item['name']} على منصة {item['platform']}"
        result.append(item)
    if len({i['image'] for i in result})!=len(result):raise SystemExit('Duplicate projects')
    if {Path(i['image']).name for i in result}!=assets:raise SystemExit('Project coverage mismatch')
    historical={line for line in git('log','--all','--format=','--name-only','--','images').splitlines() if line.startswith('images/') and line.count('/')==1}
    absent=[name for name in sorted(historical) if not (ROOT/name).is_file()]
    if absent:raise SystemExit('Missing historical originals: '+', '.join(absent))
    out=ROOT/'data/portfolio.json'
    out.write_text(json.dumps({'orderPolicy':'Original gallery order from Git HEAD, followed by projects recovered from earlier revisions.','projects':result},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'projects':len(result),'recovered_from_older_revisions':sum(i['sourceRevision']!=head for i in result),'missing_originals':absent,'order':[i['id'] for i in result]}))
if __name__=='__main__':main()
