"""Comprueba rutas y metadatos del centro publicado, sin realizar mutaciones."""
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

SITE = 'https://www.tallerlab.com.ar'
PATHS = ['/alertas/', '/alertas/dewalt-dws780/', '/alertas/dewalt-dw8307/',
         '/alertas/makita-dgp180/', '/alertas/dewalt-dws713/', '/alertas/metodologia/',
         '/alertas/estado/', '/alertas/editorial/', '/api/alertas/estado',
         '/datos/alertas/avisos.csv', '/datos/alertas/avisos.json']


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.h1 = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'h1':
            self.h1 += 1
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')


def check(path):
    request = urllib.request.Request(SITE+path, headers={'User-Agent': 'TallerLab-verificacion-publica/1.0'})
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            raw = response.read()
            result = {'ruta': path, 'http': response.status, 'bytes': len(raw),
                      'robots': response.headers.get('X-Robots-Tag'), 'correcto': response.status == 200}
            if 'text/html' in response.headers.get('Content-Type', ''):
                metadata = Metadata()
                metadata.feed(raw.decode('utf-8'))
                result.update(h1=metadata.h1, canonical=metadata.canonical)
                result['correcto'] &= metadata.h1 == 1 and metadata.canonical == SITE+path
            if path == '/api/alertas/estado':
                data = json.loads(raw)
                result['servicio'] = data
                result['correcto'] &= data.get('estado') == 'correcto' and data.get('persistencia') == 'postgresql'
            if path in ('/alertas/estado/', '/alertas/editorial/'):
                result['correcto'] &= 'noindex' in (result['robots'] or '')
            return result
    except (OSError, ValueError) as exc:
        return {'ruta': path, 'correcto': False, 'error': type(exc).__name__}


if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(check, PATHS))
    report = {'fecha_utc': datetime.now(timezone.utc).isoformat(), 'sitio': SITE,
              'correcto': all(result['correcto'] for result in results), 'rutas': results}
    Path('qa-alertas-publico-2026-10-04.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True))
    raise SystemExit(0 if report['correcto'] else 1)
