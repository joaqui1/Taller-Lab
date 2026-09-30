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
    return re.sub(r'\]\((/(?:soldadora-inverter-160-amp|soldadora-inverter-200-amp|soldadora-mig-con-gas|mig-sin-gas|tig|soldadora-tig-ac-dc|soldadora-de-punto|para-aluminio|esab-handyarc-162i)/)\)', r'](/soldadoras\1)', text)


def main():
    configs = {}
    for number, groups in PLACEMENTS.items():
        file = next((ROOT / 'paginas/soldadoras').glob(f'{number:02d}-*.md'))
        text = MARKER.sub('\n\n', file.read_text(encoding='utf-8'))
        if number == 0:
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
            inserts.append((insertion(text, anchor, mode), block))
        # Posiciones calculadas sobre el original; insertar desde el final.
        for position, block in sorted(inserts, reverse=True):
            text = text[:position].rstrip() + block + text[position:].lstrip('\n')
        if inserts:
            file.write_text(text, encoding='utf-8')
        configs[path] = config
    (ROOT / 'soldadoras-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(OFFERS)} productos; {sum(len(c["offers"]) for c in configs.values())} CTA en {sum(bool(c["offers"]) for c in configs.values())} guías')


if __name__ == '__main__':
    main()
