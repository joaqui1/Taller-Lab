import sys, os, json, re, tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
os.environ['RELEVAMIENTO_HABILITADO']='1'
import relevamiento_piloto as rel
from bs4 import BeautifulSoup
html=rel.render_relevamiento_page({'utm_source':'test'})
soup=BeautifulSoup(html,'html.parser')
os.environ['RELEVAMIENTO_ADMIN_KEY']='clave-exclusiva-qa-front'
root=Path(__file__).parent/'tmp'
root.mkdir(exist_ok=True)
original_path=rel.DB_PATH
with tempfile.TemporaryDirectory(prefix='rel-admin-front-',dir=root) as temp:
    rel.DB_PATH=Path(temp)/'test.db'
    admin=BeautifulSoup(rel.render_admin_dashboard({'_authenticated':True,'_csrf':'token-de-prueba'}),'html.parser')
    admin_scripts=[e.string for e in admin.select('script')]
rel.DB_PATH=original_path
out=Path(__file__).parent/'tmp'/'relevamiento-front-fixture.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({'script':soup.script.string,'admin_scripts':admin_scripts,'elements':[{'id':e.get('id'),'name':e.get('name'),'type':e.get('type'),'value':e.get('value','')} for e in soup.select('[id],input[name]')]}),encoding='utf-8')
for label in soup.select('label[for]'):
    target=soup.find(id=label['for'])
    assert target is not None, label['for']
print('Fixture de JavaScript generado y referencias de etiquetas verificadas.')
import subprocess
subprocess.run(['node', 'verificar_relevamiento_front.cjs'], cwd=Path(__file__).parent, check=True)
