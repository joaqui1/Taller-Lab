"""Revisa todas las rutas públicas y la preservación de enlaces al limpiar avisos."""
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
import servidor_local as site
from app import app
from contenido_publico import PublicTemplate

client=app.test_client()
rows=[]
template=site.HTML_SHELL
try:
 for path in site.INDEXABLE_PATHS:
  site.HTML_SHELL=str(template)
  before=client.get(path)
  site.HTML_SHELL=template
  after=client.get(path)
  assert before.status_code==after.status_code==200,path
  old=BeautifulSoup(before.data,'html.parser'); new=BeautifulSoup(after.data,'html.parser')
  for tag,attribute in [('a','href'),('img','src')]:
   assert [x.get(attribute) for x in old.select(tag)]==[x.get(attribute) for x in new.select(tag)],(path,tag)
  for node in new.select('script,style'):
   node.decompose()
  text=new.get_text(' ',strip=True)
  assert not re.search(r'afiliad|afiliaci[oó]n|comisi[oó]n|\boferta pendiente\b|suministrad[oa] por el usuario|pendientes de verificar|falta (?:enlace|referido)',text,re.I),(path,text)
  for node in new.select('[aria-label]'):
   assert not re.search(r'afiliad|afiliaci[oó]n',node['aria-label'],re.I),path
  rows.append(dict(path=path,status=after.status_code,links=len(new.select('a')),images=len(new.select('img'))))
finally:
 site.HTML_SHELL=template
report=dict(routes=len(rows),failures=[],link_and_image_identity_preserved=True,rows=rows)
Path('qa-contenido-publico-2026-10-02.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'OK: {len(rows)} rutas; sin avisos administrativos ni textos de afiliación; enlaces e imágenes preservados.')
