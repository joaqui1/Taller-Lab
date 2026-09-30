"""Inserta los 32 enlaces en las 17 rutas propuestas; conserva las fichas documentales."""
import json
import re
from pathlib import Path
from integrar_sierras_comerciales import insertion
from taladros_comerciales import OFFERS, PLACEMENTS, render_block

ROOT = Path(__file__).parent
MARKER = re.compile(r'\n*<!-- TALADROS-OFERTAS -->.*?<!-- /TALADROS-OFERTAS -->\n*', re.S)
DOCUMENTED = '**Dato documentado:** las cifras y funciones de esta guía se atribuyen a las fuentes citadas; el título de una oferta no confirma el código, la variante ni su contenido.'
ANALYSIS = '**Análisis TallerLab:** los criterios de elección comparan documentación según el trabajo, material y plataforma. No se realizaron pruebas físicas ni se verificaron precio, stock o contenido actual de las publicaciones recibidas.'


def main():
    configs = {}
    for file in sorted((ROOT / 'paginas/taladros').glob('*.md')):
        number = int(file.name.split('-', 1)[0])
        original = file.read_text(encoding='utf-8')
        text = MARKER.sub('\n\n', original)
        labels = [label for phrase, label in [('Dato documentado', DOCUMENTED), ('Análisis TallerLab', ANALYSIS)] if phrase not in text]
        if labels:
            position = text.index('\n## ')
            text = text[:position].rstrip() + '\n\n' + '\n\n'.join(labels) + '\n\n' + text[position:].lstrip('\n')
        if number in PLACEMENTS:
            path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
            keys = [key for key, offer in OFFERS.items() if offer[2] == path]
            assert keys, path
            anchor, mode, title = PLACEMENTS[number]
            position = insertion(text, anchor, mode)
            block = '\n\n<!-- TALADROS-OFERTAS -->\n\n' + render_block(keys, title) + '\n\n<!-- /TALADROS-OFERTAS -->\n\n'
            text = text[:position].rstrip() + block + text[position:].lstrip('\n')
            configs[path] = dict(file=file.name, models=keys, anchor=anchor, position=mode, title=title,
                offers=[dict(model=key, url=OFFERS[key][1], cta=OFFERS[key][3]) for key in keys])
        if text != original:
            file.write_text(text, encoding='utf-8')
    assert {key for config in configs.values() for key in config['models']} == set(OFFERS)
    (ROOT / 'taladros-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{len(OFFERS)} productos, {sum(len(c["offers"]) for c in configs.values())} CTA en {len(configs)} guías; 23 guías con etiquetas de evidencia.')


if __name__ == '__main__':
    main()
