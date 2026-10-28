"""Normalize migration-only fields; do not touch user-owned reviews."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for p in (ROOT/'data/ips').glob('daily-*.json'):
    c=json.loads(p.read_text());c['name']=c['name'].lstrip('｜| ')
    if c['batch']=='daily-20261022':
        c['import_warning']='本批原始报告与对话摘要的部分名字、原点存在差异（例如接接/拍拍鳐、坐醒/串场、成束/墨芽）。本页保留原始报告与对应原图，不把不同设定合并，也未重新设计。'
    p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
q=ROOT/'queue/image-jobs.json';jobs=json.loads(q.read_text())
for j in jobs:
    if j.get('ip','').startswith('daily-'):j['name']=j['name'].lstrip('｜| ')
q.write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n')
p=ROOT/'research/daily/backfill-manifest.json';m=json.loads(p.read_text())
for x in m['items']:x['name']=x['name'].lstrip('｜| ')
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
