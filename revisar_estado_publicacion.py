"""Auditoría de lectura: estado editorial, ofertas y rutas del dominio público."""
import concurrent.futures
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import servidor_local as s
from app import app


class Document(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = set()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.add(dict(attrs).get('href', ''))


def inspect_remote(path):
    url = 'https://www.tallerlab.com.ar' + path
    try:
        with urlopen(Request(url, headers={'User-Agent': 'TallerLab-publication-audit/1.0'}), timeout=20) as response:
            html = response.read().decode('utf-8')
            canonical = re.findall(r'<link\s+rel="canonical"\s+href="([^"]+)"', html)
            return {'path': path, 'status': response.status, 'canonical': canonical,
                    'canonical_ok': canonical == [url], 'final_url': response.url}
    except HTTPError as error:
        return {'path': path, 'status': error.code}
    except Exception as error:
        return {'path': path, 'error': str(error)}


def main():
    excluded = []
    for article in s._ALL_DRAFTS:
        if article in s.ALL_ARTICLES:
            continue
        reasons = []
        if not re.search(r'^## Fuentes consultadas\s*$', article['body'], re.MULTILINE):
            reasons.append('Falta encabezado exacto de fuentes')
        for label in ('Dato documentado', 'Análisis TallerLab'):
            if label not in article['body']:
                reasons.append('Falta etiqueta ' + label)
        excluded.append({'url': article['url'], 'file': str(article['path']), 'reasons': reasons,
                         'published': article['published']})
    client = app.test_client()
    missing_offers = []
    for section in ('COMPRESORES', 'GENERADORES', 'HIDROLAVADORAS', 'SIERRAS', 'SOLDADORAS', 'TALADROS'):
        for path, config in getattr(s, section + '_OFFERS').items():
            if path not in s.INDEXABLE_PATH_SET:
                continue
            links = Document(client.get(path).get_data(as_text=True)).links
            for offer in config['offers']:
                if offer['url'] not in links:
                    missing_offers.append({'page': path, **offer})
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        remote = list(pool.map(inspect_remote, sorted(s.INDEXABLE_PATHS)))
        excluded_remote = list(pool.map(inspect_remote, [a['url'] for a in excluded]))
    output = {'drafts': len(s._ALL_DRAFTS), 'served_articles': len(s.ALL_ARTICLES),
              'indexable_routes': len(s.INDEXABLE_PATHS), 'excluded': excluded,
              'missing_offers': missing_offers, 'remote': remote, 'excluded_remote': excluded_remote}
    Path('resultado-revision-publicacion-2026-09-30.json').write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'drafts': output['drafts'], 'served_articles': output['served_articles'],
                      'excluded': len(excluded), 'missing_offers': len(missing_offers),
                      'remote_ok': sum(r.get('status') == 200 and r.get('canonical_ok') for r in remote),
                      'remote_issues': [r for r in remote if r.get('status') != 200 or not r.get('canonical_ok')]},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
