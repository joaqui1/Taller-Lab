"""Conserva la atribución de documentos retirados sin mandar lectores a un 404.

Esto no recupera ni revalida los documentos: la limitación queda explícita.
"""
import json
from pathlib import Path
import re

def main():
    rows = json.loads(Path('destinos-produccion-2026-09-30.json').read_text(encoding='utf-8'))
    records = []
    for row in rows:
        if row.get('status') != 404:
            continue
        url = row['url']
        if 'meli.la/' in url:
            raise ValueError('Una oferta rota debe retirarse o corregirse, no tratarse como fuente histórica: ' + url)
        pattern = re.compile(r'\[([^\]]+)\]\(' + re.escape(url) + r'\)')
        changed = []
        for file in Path('paginas').rglob('*.md'):
            text = file.read_text(encoding='utf-8')
            updated = pattern.sub(lambda m: m[1] + ' (referencia documental histórica; enlace original no disponible al 30/09/2026)', text)
            if updated != text:
                file.write_text(updated, encoding='utf-8')
                changed.append(file.as_posix())
        if changed:
            records.append(dict(url=url, checked='30/09/2026', status=404, files=changed, action='Conservar cita histórica y explicitar indisponibilidad; retirar hipervínculo roto. No equivale a revalidación técnica.'))
    output = Path('fuentes-historicas-no-disponibles-2026-09-30.json')
    previous = json.loads(output.read_text(encoding='utf-8')) if output.exists() else []
    merged = {r['url']:r for r in previous + records}
    output.write_text(json.dumps(list(merged.values()),ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(records)} enlaces retirados conservando la referencia histórica y su limitación explícita.')

if __name__ == '__main__':
    main()
