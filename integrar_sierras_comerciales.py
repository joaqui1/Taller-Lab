"""Inserta referidos en puntos explícitos sin modificar las tablas documentales."""
import json
import re
from pathlib import Path
from sierras_comerciales import OFFERS, PENDING, PLACEMENTS, url

ROOT = Path(__file__).parent
MARKER = re.compile(r'\n*<!-- SIERRAS-OFERTAS -->.*?<!-- /SIERRAS-OFERTAS -->\n*', re.S)

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

def main():
    configs = {}
    for number, (requested, heading, mode) in PLACEMENTS.items():
        file = next((ROOT / 'paginas/sierras').glob(f'{number:02d}-*.md'))
        text = MARKER.sub('\n\n', file.read_text(encoding='utf-8'))
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        keys = [key for key in requested if key in OFFERS and key not in PENDING]
        if keys:
            if number == 4:
                # Sustituir el CTA antiguo; mantener su fuente y explicación de variante.
                text = re.sub(r'(?m)^Si el máximo documentado.*https://meli\.la/1ntghna.*\n', '', text)
            rows = ['| Producto de la oferta | Qué confirmar | Precio y disponibilidad |', '| :--- | :--- | :--- |']
            for key in keys:
                name, _, note = OFFERS[key]
                rows.append(f'| {name} | {note} | [Ver precio →]({url(key)}) |')
            block = '\n\n<!-- SIERRAS-OFERTAS -->\n\n### Consultá estas opciones en Mercado Libre\n\n' + '\n'.join(rows)
            block += '\n\n*Enlaces de afiliado: TallerLab puede recibir una comisión, sin costo adicional para vos. Consultá precio, stock y condiciones de la publicación.*\n\n<!-- /SIERRAS-OFERTAS -->\n\n'
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
            offers=[dict(model=key, url=url(key), cta='Ver precio →') for key in keys],
            pending=[dict(model=key, reason=OFFERS[key][2] if key in PENDING else 'Falta enlace; conservar condición de variante/código de la propuesta.') for key in requested if key not in keys])
    (ROOT / 'sierras-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{sum(bool(c["models"]) for c in configs.values())} guías; {sum(len(c["offers"]) for c in configs.values())} CTA; {len(OFFERS)-len(PENDING)} productos activos; {len(PENDING)} referidos pendientes')

if __name__ == '__main__':
    main()
