"""Comprueba la publicación; una fuente aislada fallida no detiene las demás."""
from datetime import datetime, timezone
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.request import urlopen

from observatorio.estatico import expected_observatory_paths, snapshot
from observatorio.gratuito import MANIFEST


def publication_warning(report, expected_finished_at, now=None):
    run = report['run']
    if run['finished_at'] != expected_finished_at:
        raise ValueError('Pages todavía sirve una captura anterior')
    finished = datetime.fromisoformat(run['finished_at'])
    if finished.tzinfo is None:
        raise ValueError('La captura no tiene zona horaria')
    age = ((now or datetime.now(timezone.utc)) - finished).total_seconds()
    if age < 0 or age > 48 * 3600:
        raise ValueError('La captura publicada está vencida o tiene fecha futura')
    if run['status'] not in ('ok', 'degraded'):
        raise ValueError('La captura no terminó')
    if run['captured'] + run.get('already_captured', 0) <= 0:
        raise ValueError('No se pudo verificar ningún producto')
    if report['unverified'] or report['stale'] or run['status'] == 'degraded':
        return (f"Publicado: {report['unverified']} productos sin verificación y "
                f"{report['stale']} vencidos. Se ocultan y se reintentan en la próxima captura.")
    return None


class PublicationHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.publication = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs.get('href')
        if tag == 'main':
            self.publication = attrs.get('data-publication')


def verify_live_publication(base_url, expected, fetch=None, now=None):
    """Comprueba HTML real, canonical, versión del historial y vigencia por ficha."""
    def download(url):
        with urlopen(url, timeout=25) as response:
            if response.status != 200:
                raise ValueError(f'HTTP {response.status}: {url}')
            return response.read().decode('utf-8-sig')
    fetch = fetch or download
    base = base_url.rstrip('/')
    data = json.loads(fetch(base + '/assets/datos/precios-observatorio-publico.json'))
    published = data['run']['finished_at']
    if datetime.fromisoformat(published) < datetime.fromisoformat(expected):
        raise ValueError('www todavía sirve un historial anterior')
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    rows = snapshot(data, manifest, now)
    report = {'run': data['run'], 'unverified': sum(r['state'] == 'error' for r in rows),
              'stale': sum(r['state'] == 'vencido' for r in rows)}
    warning = publication_warning(report, published, now)
    if all(r['state'] in ('pendiente', 'error', 'vencido') for r in rows):
        raise ValueError('No hay ninguna ficha verificada vigente en www')

    def check(path):
        page = PublicationHTML()
        page.feed(fetch(base + path))
        if page.canonical != 'https://www.tallerlab.com.ar' + path:
            raise ValueError('Canonical ausente o incorrecto: ' + path)
        if page.publication != published:
            raise ValueError('HTML y dataset corresponden a publicaciones distintas: ' + path)
    paths = expected_observatory_paths()
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(check, paths))
    return {'routes': len(paths), 'finished_at': published, 'warning': warning}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--expected', required=True)
    parser.add_argument('--wait-seconds', type=int, default=0)
    args = parser.parse_args()
    deadline = time.monotonic() + args.wait_seconds
    while True:
        try:
            result = verify_live_publication(args.url, args.expected)
            print(json.dumps(result, ensure_ascii=False))
            if result['warning']:
                print('::warning::' + result['warning'])
            return
        except (OSError, ValueError, KeyError, TypeError) as error:
            if time.monotonic() >= deadline:
                raise SystemExit('No se verificó la publicación de www: ' + str(error))
            print('Esperando despliegue de www: ' + str(error), flush=True)
            time.sleep(15)


if __name__ == '__main__':
    main()
