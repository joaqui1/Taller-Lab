"""Integración puntual e idempotente de los afiliados recibidos el 29/09/2026."""
import json
import re
from pathlib import Path
from compresores_comerciales import OFFERS, PLACEMENTS, cta

ROOT = Path(__file__).parent

def section_span(text, heading):
    start = text.index('## ' + heading + '\n')
    end = text.find('\n## ', start + 4)
    return start, len(text) if end < 0 else end

def table_end(text, heading):
    start, end = section_span(text, heading)
    match = re.search(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', text[start:end])
    if not match:
        raise ValueError('No hay tabla: ' + heading)
    return start + match.end()

def main():
    configs = {}
    # El servidor exige etiquetas de atribución incluso en guías con published:true.
    # Completar solo las ausentes para conservar la publicación de las 23 URLs.
    for file in (ROOT / 'paginas/compresores').glob('*.md'):
        text = file.read_text(encoding='utf-8')
        if file.name.startswith('06-') and '## Fuentes consultadas' not in text:
            text = text.replace('## Referencias para identificar perfiles', '## Fuentes consultadas\n\nReferencias para identificar perfiles:')
            file.write_text(text, encoding='utf-8')
        notes = []
        if 'Dato documentado' not in text:
            notes.append('**Dato documentado:** las especificaciones de esta guía se atribuyen a las fichas y documentos enlazados. Un dato no publicado queda pendiente de confirmación.')
        if 'Análisis TallerLab' not in text:
            notes.append('**Análisis TallerLab:** los criterios de elección interpretan esa documentación según el uso previsto; no constituyen una prueba física ni garantizan compatibilidad sin comprobar los requisitos del equipo concreto.')
        if notes:
            position = text.index('\n## ')
            text = text[:position] + '\n' + '\n\n'.join(notes) + '\n' + text[position:]
            file.write_text(text, encoding='utf-8')
    for number, heading, cards_heading, models, mode in PLACEMENTS:
        file = next((ROOT / 'paginas/compresores').glob(f'{number:02d}-*.md'))
        text = file.read_text(encoding='utf-8')
        text = re.sub(r'\n*<!-- COMPRESORES-OFFERS -->\n*', '\n\n', text)
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        available = [model for model in models if model in OFFERS]
        if number == 1:
            text = text.replace('https://meli.la/2m7TJWQ', 'https://meli.la/2Xv53zX')
        start, end = section_span(text, heading)
        section = text[start:end]
        # Mantener el CTA fuera de las celdas de especificaciones.
        if available and number not in {17, 20, 21}:
            table = re.search(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', section)
            rows = table[0].splitlines()
            has_offer_column = rows[0].split('|')[-2].strip() == 'Oferta'
            result = []
            matched = set()
            for index, row in enumerate(rows):
                cells = [cell.strip() for cell in row.strip().strip('|').split('|')]
                previous_offer = None
                if has_offer_column:
                    previous_offer = cells.pop()
                model = next((model for model in available if model.split(' ', 1)[1] in cells[0]), None) if index > 1 else None
                if model:
                    matched.add(model)
                    url = 'https://meli.la/' + OFFERS[model][0]
                    label = 'Ver precio' if number == 1 else cta(number, model)
                    if number == 1:
                        cells[-1] = re.sub(r'\s*·?\s*\[[^\]]+\]\(' + re.escape(url) + r'\)(?:\{:.*?\})?', '', cells[-1])
                        cells[-1] += f' · [{label}]({url})'
                    else:
                        cells = [re.sub(r'\s*·?\s*\[[^\]]+\]\(' + re.escape(url) + r'\)', '', cell) for cell in cells]
                        cells.append(f'[{label}]({url})')
                elif number != 1:
                    documentary = previous_offer if previous_offer and '](https://' in previous_offer and 'meli.la/' not in previous_offer and 'mercadolibre.com' not in previous_offer else '—'
                    cells.append('Oferta' if index == 0 else ':---' if index == 1 else documentary)
                result.append('| ' + ' | '.join(cells) + ' |')
            if matched != set(available):
                raise ValueError(f'Fila ausente: {file.name} / {set(available) - matched}')
            section = section[:table.start()] + '\n'.join(result) + '\n' + section[table.end():]
        text = text[:start] + section + text[end:]
        # Reservar el punto editorial incluso si falta el referido del modelo.
        card_heading = cards_heading or heading
        position = table_end(text, card_heading) if mode == 'table' else section_span(text, card_heading)[1]
        text = text[:position] + '\n<!-- COMPRESORES-OFFERS -->\n\n' + text[position:]
        if available:
            file.write_text(text, encoding='utf-8')
        configs[path] = dict(number=number, file=str(file.relative_to(ROOT)).replace('\\', '/'),
            heading=heading, cards_heading=card_heading, mode=mode, models=models,
            offers=[dict(model=model, url='https://meli.la/' + OFFERS[model][0], cta=cta(number, model)) for model in available],
            pending=[model for model in models if model not in OFFERS])
    (ROOT / 'compresores-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{sum(bool(c["offers"]) for c in configs.values())} guías con cards; {sum(len(c["offers"]) for c in configs.values())} cards; pendientes: {len(set(m for c in configs.values() for m in c["pending"]))}')

if __name__ == '__main__':
    main()
