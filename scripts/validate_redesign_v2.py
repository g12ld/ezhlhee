"""Static release checks; these do not replace responsive browser QA."""
from pathlib import Path
from html.parser import HTMLParser
import json,re

ROOT=Path(__file__).resolve().parents[1]
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack=[]; self.errors=[]; self.tags=[]; self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs); self.tags.append((tag,attrs))
        if attrs.get('id'): self.ids.append(attrs['id'])
        if tag not in VOID:self.stack.append(tag)
    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.stack or self.stack[-1]!=tag:self.errors.append(f'unbalanced </{tag}>')
        elif self.stack:self.stack.pop()

def main():
    html=(ROOT/'index.html').read_text(encoding='utf8'); page=Page(); page.feed(html)
    checks=[]
    def check(name,passed,evidence):checks.append({'check':name,'passed':bool(passed),'evidence':evidence})
    check('homepage-balanced-html',not page.errors and not page.stack,page.errors+page.stack)
    duplicates=sorted({i for i in page.ids if page.ids.count(i)>1})
    check('unique-element-ids',not duplicates,duplicates)
    check('single-main-and-h1',sum(t=='main' for t,a in page.tags)==1 and sum(t=='h1' for t,a in page.tags)==1,'one main landmark and one H1')
    assets=[]; missing=[]; missing_anchors=[]
    for tag,attrs in page.tags:
        value=attrs.get('src') or (attrs.get('href') if tag=='link' else None)
        if value and value.startswith('/'):
            assets.append(value)
            if not (ROOT/value.split('?')[0].lstrip('/')).is_file():missing.append(value)
        if tag=='a':
            href=attrs.get('href','')
            if href.startswith('#') and href[1:] not in page.ids:missing_anchors.append(href)
        if tag=='button' and attrs.get('aria-controls') and attrs['aria-controls'] not in page.ids:missing_anchors.append(attrs['aria-controls'])
    check('homepage-assets-exist',not missing,missing or f'{len(assets)} assets')
    check('homepage-anchor-targets-exist',not missing_anchors,missing_anchors)
    images=[a for t,a in page.tags if t=='img']
    check('descriptive-alt-and-dimensions',all(a.get('alt') and a.get('width') and a.get('height') for a in images),f'{len(images)} images')
    check('chat-share-consent','chatShareConsent' in page.ids and 'ez-contact-consent' in page.ids,'separate review and approval for chat/contact handoff')
    check('homepage-is-static-html',all(x in html for x in ['تصميم متاجر سلة وزد','1,099','599','1,980','ez-projects','svc-home-section']),'headline, work, services and package prices are in source HTML')
    original=ROOT/'scratch/redesign-v2-backup/index.html'
    check('homepage-backup-retained',original.is_file(),str(original.relative_to(ROOT)))
    canonical=re.search(r'<link rel="canonical" href="([^"]+)"',html)
    check('homepage-canonical-preserved',canonical and canonical[1]=='https://www.ezhalhe-sa.com/','existing canonical')
    css=(ROOT/'css/ezhalha-v2.css').read_text(encoding='utf8')
    check('css-blocks-balanced',css.count('{')==css.count('}'),f"{css.count('{')} blocks")
    check('approved-primary-color','--ez-primary:#125065' in css,'owner-approved primary token')
    check('mobile-first-breakpoints',all(f'min-width:{n}px' in css for n in [600,960]),'mobile defaults with progressive 600px/960px enhancements')
    check('reduced-motion-rule','prefers-reduced-motion:reduce' in css,'animation and transition overrides')
    legacy=list(ROOT.glob('*.html'))+list((ROOT/'articles').glob('*.html'))
    scoped=[p for p in legacy if 'ui-system.css' in p.read_text(encoding='utf8')]
    check('shared-inner-page-system',all('ezhalha-v2.css' in p.read_text(encoding='utf8') for p in scoped),f'{len(scoped)} inner pages')
    result={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'browser_qa':'BLOCKED: browser URL policy stopped UI control; no visual assertions made','lighthouse':'NOT RUN'}
    dest=ROOT/'scratch/redesign-v2-qa';dest.mkdir(parents=True,exist_ok=True)
    (dest/'static-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=True))
    raise SystemExit(0 if result['status']=='PASS' else 1)
if __name__=='__main__':main()
