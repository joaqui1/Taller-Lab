from pathlib import Path
import csv, json, re, unicodedata
from collections import Counter
ROOT=Path(r'C:\Users\joaqu\Desktop\keywords')
OUT=Path(__file__).parent/'analisis-amoladoras'
OUT.mkdir(exist_ok=True)
def norm(s):
    return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))).strip()
def read(p,sep=','):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f,delimiter=sep))
base=read(ROOT/'keywords_amoladora.csv')
sem=read(ROOT/'semrush/semrush_amoladoras.csv')
for r in sem:r['source']='semrush_amoladoras.csv'
adds=read(ROOT/'semrush/semrush_consulta_adicional.csv',';')
additional=[]
for r in adds:
    k=norm(r['Palabra clave'])
    if 'amoladora' in k or k.startswith('disco '):
        additional.append(dict(keyword=r['Palabra clave'],intent=r['Intención'],volume=r['Volumen'],kd=r['KD %'],cpc=r['CPC (USD)'],source='semrush_consulta_adicional.csv'))
allsem=sem+additional
bkeys={norm(r['Keyword']) for r in base}
summary=dict(base_rows=len(base),base_unique=len(bkeys),volume_distribution=Counter(r['Avg. monthly searches'] for r in base),sem_rows=len(sem),additional_rows=len(additional),sem_unique=len({norm(r['keyword']) for r in allsem}),sem_missing_base=[r['keyword'] for r in allsem if norm(r['keyword']) not in bkeys],sem_volume_na=sum(r['volume']=='n/d' for r in allsem),sem_volume_zero=sum(r['volume']=='0' for r in allsem))
(OUT/'datos.json').write_text(json.dumps(dict(summary=summary,sem=allsem),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('ADICIONALES:',json.dumps(additional,ensure_ascii=False))
print('INFORMATIVAS:',json.dumps([r['Keyword'] for r in base if re.search(r'\b(como|que|cual|sirve|diferencia|mejor|seguridad)\b',norm(r['Keyword']))][:140],ensure_ascii=False))
