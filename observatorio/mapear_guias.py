"""Genera observatorio/guias_por_modelo.json: qué guías publicadas mencionan cada modelo seguido.

Se ejecuta localmente (necesita las dependencias del sitio): python -m observatorio.mapear_guias
El resultado se versiona; el build del observatorio solo lee el JSON.
"""
import json
from pathlib import Path

from observatorio.gratuito import MANIFEST, normalized

OUTPUT = Path(__file__).resolve().parent / 'guias_por_modelo.json'


def main():
    import servidor_local as site
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    indexable = set(site.INDEXABLE_PATHS)
    articles = [a for a in site.ALL_ARTICLES if a['url'] in indexable]
    result = {}
    for model in manifest['models']:
        key, brand = normalized(model['model']), normalized(model['brand'])
        scored = []
        for a in articles:
            body = normalized(a['body'])
            if key not in body or brand not in body:
                continue
            score = body.count(key) + (20 if key in normalized(a['url']) else 0) + (10 if key in normalized(a['title']) else 0) + (3 if a['section'] == model['category'] else 0)
            scored.append((score, a['url'], a['title']))
        scored.sort(key=lambda s: (-s[0], s[1]))
        result[model['id']] = [{'url': url, 'title': title} for _, url, title in scored[:3]]
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'OK: {sum(bool(v) for v in result.values())} de {len(result)} modelos con guía.')


if __name__ == '__main__':
    main()
