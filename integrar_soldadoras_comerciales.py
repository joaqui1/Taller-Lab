"""Integra ofertas en sus posiciones editoriales sin alterar fichas ni tablas."""
import json
import re
from pathlib import Path
from soldadoras_comerciales import OFFERS, PENDING, PLACEMENTS, cta, render_block, url
from integrar_sierras_comerciales import insertion

ROOT = Path(__file__).parent
MARKER = re.compile(r'\n*<!-- SOLDADORAS-OFERTAS -->.*?<!-- /SOLDADORAS-OFERTAS -->\n*', re.S)
ANALYSIS = '**Análisis TallerLab:** los criterios de selección interpretan las fuentes citadas según proceso, consumible y trabajo previsto. No se realizaron pruebas físicas de los productos ni se verificó el contenido actual de las ofertas recibidas.'


def normalize_main_links(text):
    paths = {
        match[1]
        for file in (ROOT / 'paginas/soldadoras').glob('*.md')
        if (match := re.search(r'^url: "([^"]+)"', file.read_text(encoding='utf-8'), re.M))
    }
    return re.sub(
        r'\]\((/[^/()]+/)\)',
        lambda m: '](/soldadoras' + m[1] + ')' if '/soldadoras' + m[1] in paths else m[0],
        text,
    )


def main():
    configs = {}
    config_path = ROOT / 'soldadoras-ofertas.json'
    previous = json.loads(config_path.read_text(encoding='utf-8')) if config_path.exists() else {}
    for number, groups in PLACEMENTS.items():
        file = next((ROOT / 'paginas/soldadoras').glob(f'{number:02d}-*.md'))
        original = file.read_text(encoding='utf-8')
        existing_blocks = [m[0] for m in MARKER.finditer(original)]
        text = MARKER.sub('\n\n', original)
        text = normalize_main_links(text)
        if groups and 'Análisis TallerLab' not in text:
            position = text.index('\n## ')
            text = text[:position].rstrip() + '\n\n' + ANALYSIS + '\n\n' + text[position:].lstrip('\n')
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        config = dict(file=file.name, models=[], offers=[], placements=[], pending=[])
        inserts = []
        for requested, anchor, mode, title in groups:
            keys = [key for key in requested if key in OFFERS]
            config['pending'].extend(dict(model=key, reason=PENDING[key]) for key in requested if key in PENDING)
            if not keys:
                continue
            config['models'].extend(keys)
            config['offers'].extend(dict(model=key, url=url(key), cta=cta(key, number)) for key in keys)
            config['placements'].append(dict(models=keys, anchor=anchor, position=mode, title=title))
            block = '\n\n<!-- SOLDADORAS-OFERTAS -->\n\n' + render_block(keys, title, number) + '\n\n<!-- /SOLDADORAS-OFERTAS -->\n\n'
            # Conservar etiquetas accesibles y redacción del aviso ya revisadas.
            for existing in existing_blocks:
                if f'<h3>{title}</h3>' in existing and set(re.findall(r'href="([^"]+)"', existing)) == {url(key) for key in keys}:
                    label = re.search(r'aria-label="([^"]+)"', existing)
                    if label:
                        block = re.sub(r'aria-label="[^"]+"', lambda m: label[0], block, count=1)
                    if '<p>Enlace de afiliado:' in existing:
                        block = block.replace('<p>Enlaces de afiliado:', '<p>Enlace de afiliado:')
                    break
            inserts.append((insertion(text, anchor, mode), block))
        # Posiciones calculadas sobre el original; insertar desde el final.
        for position, block in sorted(inserts, reverse=True):
            text = text[:position].rstrip() + block + text[position:].lstrip('\n')
        if inserts:
            file.write_text(text, encoding='utf-8')
        old = previous.get(path, {})
        if set(old.get('models', [])) == set(config['models']):
            config['models'] = old['models']
        if sorted(old.get('offers', []), key=lambda o: o['model']) == sorted(config['offers'], key=lambda o: o['model']):
            config['offers'] = old['offers']
        configs[path] = config
    (ROOT / 'soldadoras-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(OFFERS)} productos; {sum(len(c["offers"]) for c in configs.values())} CTA en {sum(bool(c["offers"]) for c in configs.values())} guías')


if __name__ == '__main__':
    main()
