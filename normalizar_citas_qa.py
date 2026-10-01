"""Cambios permitidos por la auditoría: enlaces recuperados y citas históricas.

Se mantiene la comparación documental: no se ignoran párrafos ni cifras.
"""
import json
from pathlib import Path
import re

def normalized_citations(text):
    for source in json.loads(Path('fuentes-recuperadas-2026-09-30.json').read_text(encoding='utf-8')):
        if source['replaced']:
            text = text.replace(source['old'], source['candidate'])
    for source in json.loads(Path('fuentes-historicas-no-disponibles-2026-09-30.json').read_text(encoding='utf-8')):
        pattern = r'\[([^\]]+)\]\(' + re.escape(source['url']) + r'\)'
        text = re.sub(pattern, lambda m: m[1] + ' (referencia documental histórica; enlace original no disponible al 30/09/2026)', text)
    return text
