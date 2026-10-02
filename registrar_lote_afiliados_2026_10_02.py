"""Actualiza identidad Bosch y evidencia del bloque comercial de este lote."""
import hashlib
import json
from pathlib import Path
import servidor_local as site

def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

p=Path('afiliados-por-completar.json')
slots=json.loads(p.read_text(encoding='utf-8'))
source=Path('integrar_lote_generadores_hidro_sierras.py').read_text(encoding='utf-8')
exec(source[source.index("slots['Bosch GHP 220"):source.index('p.write_text(json.dumps(slots')])
save(p,slots)
paths=['/generadores/inverter/','/generadores/lusqtoff/','/hidrolavadoras/black-decker/','/sierras/circulares-black-decker/']
p=Path('revision-editorial-por-tandas.json')
ledger=json.loads(p.read_text(encoding='utf-8'))
for article in site.ALL_ARTICLES:
    if article['url'] in paths:
        ledger[article['url']].update(body_sha256=hashlib.sha256(article['body'].encode()).hexdigest(),commercial_followup='2026-10-02: enlaces recibidos asociados al modelo correspondiente; revisión de identidad, foto y bloque comercial, sin nueva lectura integral.')
save(p,ledger)
save('rutas-qa-lote-afiliados-2026-10-02.json',['/','/generadores/','/hidrolavadoras/','/sierras/']+paths+['/hidrolavadoras/bosch/'])
print('Identidad Bosch y seguimiento del lote registrados.')
