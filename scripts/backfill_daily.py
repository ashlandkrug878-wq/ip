"""Import historical concept deliverables without altering user reviews/pools.

Run with a source workspace path. Original descriptions are retained verbatim.
"""
import base64
import io
import json
import re
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1])

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def image(data, dest):
    im = Image.open(io.BytesIO(data)).convert('RGB')
    im.thumbnail((768, 768))
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, 'WEBP', quality=80)
    if dest.stat().st_size > 150*1024:
        im.save(dest, 'WEBP', quality=65)
    assert dest.stat().st_size <= 150*1024

def urls(text):
    return [{'t': u, 'url': u} for u in dict.fromkeys(re.findall(r'https?://[^\s<>"\)]+', text)) if 'chatgpt.com/library' not in u]

def md_rows(text):
    out = {}
    for ln in text.splitlines():
        if not ln.startswith('|'): continue
        cells = [x.strip().replace('**','') for x in ln.strip('|').split('|')]
        m = re.match(r'^(0[1-9])(?:\s+(.+))?$', cells[0])
        if not m: continue
        n = int(m[1]); rest = cells[1:]
        if m[2]: name = m[2]
        else: name = rest.pop(0)
        if len(rest)>=4: out[n] = [name,*rest]
    return out

configs = {
  23: ('ip-lab-20261023.md','ip-lab-20261023-assets','ip-lab-20261023-overview.png'),
  24: ('deliverable/2026-10-24-chaowan-ip-lab.md','deliverable/images','deliverable/overview-01-09.png'),
  25: ('deliverables/chaowan-ip-lab-2026-10-25.md','deliverables','deliverables/chaowan-ip-overview-2026-10-25.png'),
  26: ('ip-lab-20261026.md','deliverables-20261026','deliverables-20261026/ip-lab-20261026-overview.png'),
  27: ('ip-lab-20261027/report.md','ip-lab-20261027/images','ip-lab-20261027/overview.png'),
  28: ('deliverable/潮玩IP原点实验室_2026-10-28.md','deliverable/images','deliverable/chaowan-ip-lab-overview-2026-10-28.jpg'),
}
jobs = json.loads((ROOT/'queue/image-jobs.json').read_text())
manifest = []
for day in range(20,29):
    date=f'2026-10-{day}'; batch=f'daily-202610{day}'; cards=[]
    archive=ROOT/'research/daily'/batch
    archive.mkdir(parents=True, exist_ok=True)
    if day in (20,21,22):
        p = SRC/('backfill-sources/ip-lab-20261020.html' if day==20 else 'backfill-sources/day21/ip-lab-20261021.html' if day==21 else 'ip-lab-20261022.html')
        raw=p.read_text(); soup=BeautifulSoup(raw,'html.parser')
        table=soup.find('table'); rows={}
        for tr in table.find_all('tr')[1:]:
            c=[td.get_text(' ',strip=True) for td in tr.find_all(['td','th'])]
            m=re.match(r'(0[1-9])\s+(.+)',c[0])
            if m: rows[int(m[1])]=[m[2].replace(' ★',''),*c[1:]]
        if day==22:
            array=re.search(r'const D\s*=\s*(\[.*?\]);',raw,re.S).group(1)
            data=json.loads(subprocess.check_output(['node','-e','console.log(JSON.stringify('+array+'))'],text=True))
        for h in soup.find_all('h3') if day!=22 else []:
            m=re.match(r'(?:方案\s*)?(0[1-9])\s*[：:]?\s*(.+)',h.get_text(' ',strip=True))
            if not m: continue
            n=int(m[1]); name=m[2].split('/')[0].strip()
            if day==21:
                section=h.find_parent('section'); text=section.get_text('\n',strip=True); im=section.find('img')
            else:
                parts=[]; im=None
                for sibling in h.next_siblings:
                    if getattr(sibling,'name',None) in ('h2','h3'):break
                    if hasattr(sibling,'get_text'):
                        parts.append(sibling.get_text('\n',strip=True))
                        if getattr(sibling,'name',None)=='img':im=sibling
                text=h.get_text()+'\n'+'\n'.join(parts)
            assert im is not None, (day,n)
            imgsrc=im['src']; imgbytes=base64.b64decode(imgsrc.split(',',1)[1]) if imgsrc.startswith('data:') else (p.parent/imgsrc).read_bytes()
            row=rows[n]; cards.append((n,name,row[1],row[2],row[3],row[4],text,imgbytes))
        if day==22:
            for x in data:
                n=int(x[0]); row=rows[n]
                labels=['编号','暂定名','原型','句式','表达','原点及证据','情绪性格背景','经典动作','外壳与头部','色彩材质','首品与假设价格','系列','文案','撞车检查','风险','五项设计预评','中文提示词','English prompt']
                text='\n\n'.join(k+'：'+v for k,v in zip(labels,x))
                cards.append((n,x[1],row[1],x[4],row[3],x[10],text,(SRC/f'ip-lab-20261022-assets/{n:02}.png').read_bytes()))
        # Keep evidence and report text, but do not duplicate embedded image megabytes.
        reporttext=soup.get_text('\n',strip=True)
        if day==22:reporttext+='\n\n'+'\n\n'.join(c[6] for c in cards)
        reporttext+='\n\n来源链接\n'+'\n'.join(a['href'] for a in soup.find_all('a',href=True))
    else:
        rel,idir,overview=configs[day];raw=(SRC/rel).read_text();reporttext=raw;rows=md_rows(raw)
        sections=list(re.finditer(r'^#{2,3}\s+(?:方案\s*)?(0[1-9])\s*[：:]?\s+(.+)$',raw,re.M))
        for k,m in enumerate(sections):
            n=int(m[1]);end=sections[k+1].start() if k+1<len(sections) else len(raw)
            text=raw[m.start():end];row=rows[n]; name=row[0]
            folder=SRC/idir
            matches=sorted(folder.glob(f'{n:02}*.png'))
            if day==24: matches=[z for z in matches if z.stem!=f'{n:02}']
            if day==28: matches=[z for z in matches if z.stem==f'{n:02}']
            assert len(matches)==1,(day,n,matches)
            cards.append((n,name,row[1],row[2],row[3],row[4],text,matches[0].read_bytes()))
    assert len(cards)==9,(day,len(cards))
    (archive/'report.txt').write_text(reporttext)
    save(ROOT/'data/batches'/f'{batch}.json',{'title':f'{date} · 每日完整概念（历史导入）','date':date,'timing':'历史原件导入；证据、价格与设计预评均保持生成当日语境，不代表当前验证。','learned':'本次仅导入，不把AI推荐或设计预评当作用户选择。','origins':[{'name':c[2],'links':urls(reporttext)} for c in cards],'source':'daily-lab','report':f'research/daily/{batch}/report.txt'})
    for n,name,origin,expr,mark,product,text,imbytes in cards:
        iid=f'{batch}-{n:02}'; output=f'images/{iid}/base-01.webp'
        image(imbytes,ROOT/output)
        # Explicitly flag source-summary differences instead of silently renaming historical cards.
        card={'batch':batch,'order':n,'name':name,'en':iid,'type':'每日完整概念 · 历史导入','stage':'concept','source':'daily-lab','expr':expr,'origin':origin,'mark':mark,'biz':product,'complete_card':text,'report':f'research/daily/{batch}/report.txt','links':urls(reporttext),'prompt_revision':1,'zh':'','enp':'','imported_at':'2026-10-28','review_disclaimer':'未做商标检索；价格为假设；五项测试为设计预评。'}
        # Extract prompts where labelled, while retaining untouched source text above.
        en=re.search(r'(?:English(?:\s+prompt)?|EN|Prompt EN)\s*[:：*]*\s*`?([^\n]+)',text,re.I)
        if en:card['enp']=en[1].strip(' `*')
        zh=re.search(r'(?:中文(?:出图)?提示词|CN 提示词|中文提示|中文|中)\s*[:：*]*\s*`?([^\n]+)',text)
        if zh:card['zh']=zh[1].split(' English:')[0].strip(' `*')
        if not (card['zh'] or card['enp']):card['zh']='见下方完整原始方案卡中的中英文提示词。'
        path=ROOT/'data/ips'/f'{iid}.json'
        if path.exists():
            assert json.loads(path.read_text())==card, 'Existing card differs: '+iid
        else:save(path,card)
        if not any(j.get('ip')==iid and j.get('kind')=='base' for j in jobs):
            jobs.append({'id':f'{iid}-base-01','ip':iid,'name':name,'kind':'base','prompt_en':card['enp'],'prompt_zh':card['zh'],'size':'768x768','status':'done','output':output,'created':date,'note':'历史原图导入，未重新生成；未做量产验证','prompt_revision':1,'image_revision':1})
        manifest.append({'id':iid,'name':name,'date':date,'image':output})
save(ROOT/'queue/image-jobs.json',jobs)
save(ROOT/'research/daily/backfill-manifest.json',{'imported_at':'2026-10-28','count':len(manifest),'items':manifest,'note':'历史原始报告优先；聊天摘要名称有出入时未静默替换。'})
print(json.dumps({'count':len(manifest),'batches':9,'names':[x['name'] for x in manifest]},ensure_ascii=False))
