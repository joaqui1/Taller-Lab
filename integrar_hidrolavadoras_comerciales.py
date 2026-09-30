"""Inserción repetible en las posiciones solicitadas, sin alterar tablas editoriales."""
import json
import re
from pathlib import Path
from hidrolavadoras_comerciales import OFFERS, PENDING, PLACEMENTS, REPEATS, url

ROOT = Path(__file__).parent

def insert_after(text, heading, block):
    sections = list(re.finditer(r'(?m)^## .+$', text))
    index = next(i for i, m in enumerate(sections) if m[0][3:].startswith(heading))
    end = sections[index + 1].start() if index + 1 < len(sections) else len(text)
    return text[:end].rstrip() + '\n\n' + block + '\n\n' + text[end:].lstrip('\n')

def main():
    configs = {}
    for number, (heading, requested) in PLACEMENTS.items():
        file = next((ROOT / 'paginas/hidrolavadoras').glob(f'{number:02d}-*.md'))
        text = file.read_text(encoding='utf-8')
        text = re.sub(r'\n*<!-- HIDROLAVADORAS-COMERCIO -->.*?<!-- /HIDROLAVADORAS-COMERCIO -->\n*', '\n\n', text, flags=re.S)
        labels = []
        if 'Dato documentado' not in text:
            labels.append('**Dato documentado:** las especificaciones se atribuyen a las fuentes citadas; las publicaciones comerciales y sus variantes deben cotejarse por código.')
        if 'Análisis TallerLab' not in text:
            labels.append('**Análisis TallerLab:** la selección interpreta la documentación según la tarea; no se realizaron pruebas físicas de estos equipos.')
        if labels:
            position = text.index('\n## ')
            text = text[:position] + '\n\n' + '\n\n'.join(labels) + '\n' + text[position:]
        text = re.sub(r'(?m)^#{2,3} Fuentes(?: y alcance)?$', '## Fuentes consultadas', text)
        text = re.sub(r'(?m)^### Fuentes consultadas$', '## Fuentes consultadas', text)
        models = [k for k in requested if k not in PENDING]
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        if models:
            block = '<!-- HIDROLAVADORAS-COMERCIO -->\n\n<!-- HIDROLAVADORAS-OFERTAS -->\n\n<!-- /HIDROLAVADORAS-COMERCIO -->'
            text = insert_after(text, heading, block)
            if number in REPEATS:
                key = models[0]
                repeat = f'<!-- HIDROLAVADORAS-COMERCIO -->\n\n[Ver precio de {OFFERS[key][0]} {OFFERS[key][1]}]({url(key)})\n\n<!-- /HIDROLAVADORAS-COMERCIO -->'
                text = insert_after(text, REPEATS[number], repeat)
        file.write_text(text, encoding='utf-8')
        configs[path] = dict(file=file.name, anchor=heading, models=models,
            offers=[dict(model=k, url=url(k)) for k in models],
            pending={k: PENDING[k] for k in requested if k in PENDING}, repeat=number in REPEATS and bool(models))
    (ROOT / 'hidrolavadoras-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{sum(bool(c["models"]) for c in configs.values())} guías con ofertas; {sum(len(c["models"]) for c in configs.values())} asociaciones')

if __name__ == '__main__':
    main()
