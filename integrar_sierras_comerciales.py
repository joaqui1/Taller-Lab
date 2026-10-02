"""Inserta referidos en puntos explícitos sin modificar las tablas documentales."""
import json
import re
import argparse
from pathlib import Path
from sierras_comerciales import OFFERS, PENDING, UNMONETIZED, PLACEMENTS, INLINE_SECTIONS, cta, url

ROOT = Path(__file__).parent
MARKER = re.compile(r'\n*<!-- SIERRAS-OFERTAS -->.*?<!-- /SIERRAS-OFERTAS -->\n*', re.S)
DOCUMENTED_ROWS = {
 8: '| Einhell TC-SM 2131/2 Dual · 4300390 | Deslizante: 310 × 62 mm a 90°. Confirmá código y espacio de recorrido. | [Ver ficha del fabricante →](https://www.einhell.com.ar/p/4300390-tc-sm-2131-2-dual/) |',
 14: '| TOTAL TS42182553 | 75 × 130 mm a 90°; disco 254 × 30 mm. No sustituir por TS42182552. | [Ver catálogo del fabricante →](https://amig.es/export_fr/downloadcatalogues/download?id=TOTAL+2026+FR.pdf&type=Catalogues+et+brochures) |',
 17: '| Black+Decker CS1350P · variante AR | 220 V / 50 Hz; disco 184 mm y eje 15,9 mm. Confirmá sufijo y kit. | [Ver manual del fabricante →](https://support.blackanddecker.com/hc/pt/article_attachments/360018582394) |',
}

def insertion(text, heading, mode):
    anchor = re.search(r'(?m)^(#{2,3}) ' + re.escape(heading) + r'\s*$', text)
    if not anchor:
        raise ValueError('Encabezado no encontrado: ' + heading)
    if mode == 'heading':
        return anchor.end()
    if mode == 'table':
        table = re.search(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', text[anchor.end():])
        if not table:
            raise ValueError('Tabla no encontrada: ' + heading)
        return anchor.end() + table.end()
    following = re.search(r'(?m)^#{1,' + str(len(anchor[1])) + r'} ', text[anchor.end():])
    return anchor.end() + following.start() if following else len(text)

def main(pages=None):
    configs = json.loads((ROOT / 'sierras-ofertas.json').read_text(encoding='utf-8')) if pages else {}
    for number, (requested, heading, mode) in PLACEMENTS.items():
        if pages and number not in pages:
            continue
        file = next((ROOT / 'paginas/sierras').glob(f'{number:02d}-*.md'))
        text = MARKER.sub('\n\n', file.read_text(encoding='utf-8'))
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        keys = [key for key in requested if key in OFFERS and key not in PENDING]
        if keys:
            if mode == 'inline':
                offers = [dict(model=key, url=url(key), cta=cta(key), section=INLINE_SECTIONS[key]) for key in keys]
                if not all(text.count(offer['url']) == 1 for offer in offers):
                    raise ValueError(f'Los CTA inline deben aparecer una vez en {file.name}')
                configs[path] = dict(file=file.name, models=keys, anchor=heading, position=mode,
                    offers=offers, pending=[])
                continue
            if number == 4:
                # Sustituir el CTA antiguo; mantener su fuente y explicación de variante.
                text = re.sub(r'(?m)^Si el máximo documentado.*https://meli\.la/1ntghna.*\n', '', text)
            rows = ['| Producto de la oferta | Qué confirmar | Precio y disponibilidad |', '| :--- | :--- | :--- |']
            for key in keys:
                name, _, note = OFFERS[key]
                rows.append(f'| {name} | {note} | [{cta(key)}]({url(key)}) |')
            if number in DOCUMENTED_ROWS:
                rows.append(DOCUMENTED_ROWS[number])
            title = 'Compará los modelos y consultá sus enlaces' if len(rows)>3 else 'Consultá precio y disponibilidad del modelo'
            block = '\n\n<!-- SIERRAS-OFERTAS -->\n\n### ' + title + '\n\n' + '\n'.join(rows)
            if number in DOCUMENTED_ROWS or any(not url(key).startswith('https://meli.la/') for key in keys):
                disclosure = 'Algunos enlaces son de afiliado: TallerLab puede recibir una comisión, sin costo adicional. Consultá precio, stock y condiciones de cada publicación.'
            else:
                disclosure = 'Enlaces de afiliado: TallerLab puede recibir una comisión, sin costo adicional para vos. Consultá precio, stock y condiciones de la publicación.'
            block += f'\n\n*{disclosure}*\n\n<!-- /SIERRAS-OFERTAS -->\n\n'
            position = insertion(text, heading, mode)
            text = text[:position].rstrip() + block + text[position:].lstrip('\n')
            labels = []
            if 'Dato documentado' not in text:
                labels.append('**Dato documentado:** las especificaciones de esta guía se atribuyen a las fuentes enlazadas; confirmá el código de la oferta antes de aplicar esos datos a una unidad.')
            if 'Análisis TallerLab' not in text:
                labels.append('**Análisis TallerLab:** los criterios de selección comparan documentación según el trabajo previsto; no se realizó una prueba física de los equipos.')
            if labels:
                position = text.index('\n## ')
                text = text[:position] + '\n\n' + '\n\n'.join(labels) + '\n' + text[position:]
            file.write_text(text, encoding='utf-8')
        configs[path] = dict(file=file.name, models=keys, anchor=heading, position=mode,
            offers=[dict(model=key, url=url(key), cta=cta(key)) for key in keys],
            pending=[dict(model=key, reason=OFFERS[key][2] if key in PENDING else 'Falta enlace; monetización de discos sin urgencia.' if key == 'PRO19054' else 'Falta enlace; conservar condición de variante/código de la propuesta.') for key in requested if key not in keys and key not in UNMONETIZED],
            unmonetized=[dict(model=key, reason=UNMONETIZED[key]) for key in requested if key in UNMONETIZED])
    (ROOT / 'sierras-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{sum(bool(c["models"]) for c in configs.values())} guías; {sum(len(c["offers"]) for c in configs.values())} CTA; {len(OFFERS)-len(PENDING)} productos activos; {len(PENDING)} referidos pendientes')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages', nargs='+', type=int, help='Actualizar solo las guías indicadas, conservando las demás configuraciones.')
    main(parser.parse_args().pages)
