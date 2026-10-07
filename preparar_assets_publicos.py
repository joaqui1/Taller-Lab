"""Publica los assets fuente en el directorio servido por el CDN de Vercel."""
import os
from pathlib import Path
import shutil


def main(root=None):
    root = Path(root or Path(__file__).resolve().parent)
    source = root / 'assets'
    destination = root / 'public' / 'assets'
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for file in source.rglob('*'):
        if file.is_file():
            target = destination / file.relative_to(source)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, target)
            assert target.read_bytes() == file.read_bytes(), file
            count += 1
    print(f'OK: {count} assets preparados para el CDN.')
    from observatorio.estatico import build_site, verify_publication
    from observatorio.gratuito import DEFAULT_HISTORY
    history = latest_history(DEFAULT_HISTORY)
    if not history.is_file():
        raise RuntimeError('Falta el historial del observatorio: no se puede publicar una versión incompleta')
    summary = build_site(history, root / 'public', standalone=False)
    verify_publication(root / 'public', summary)
    # La función serverless no necesariamente incluye public/, servido por el CDN.
    # Solo un build completo puede declarar estas rutas desde el sitemap dinámico.
    manifest = root / 'public' / 'assets' / 'datos' / 'observatorio-publicacion.json'
    target = source / 'datos' / manifest.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest, target)
    # Vercel (Flask) toma public/ antes de ejecutar este build: lo generado aquí no llega al CDN.
    # Se copia a una carpeta que sí entra en la función, que sirve las páginas y descargas.
    published = root / 'observatorio_publicado'
    shutil.rmtree(published, ignore_errors=True)
    shutil.copytree(root / 'public' / 'datos', published / 'datos')
    dataset = root / 'public' / 'assets' / 'datos' / 'precios-observatorio-publico.json'
    shutil.copy2(dataset, source / 'datos' / dataset.name)
    verify_publication_copy(root / 'public', published, source / 'datos' / dataset.name)
    print(f"OK: observatorio con {summary['observations']} observaciones y {len(summary['routes'])} páginas verificadas.")


def verify_publication_copy(public, published, dataset):
    """Detiene el build si la copia servida por la función no es idéntica a lo generado."""
    origin = public / 'datos'
    files = [f for f in origin.rglob('*') if f.is_file()]
    if not files:
        raise RuntimeError('El observatorio no generó archivos para publicar')
    for file in files:
        copy = published / 'datos' / file.relative_to(origin)
        if not copy.is_file() or copy.read_bytes() != file.read_bytes():
            raise RuntimeError(f'Copia incompleta del observatorio: {copy}')
    if dataset.read_bytes() != (public / 'assets' / 'datos' / dataset.name).read_bytes():
        raise RuntimeError('Copia incompleta del dataset público del observatorio')


DEFAULT_HISTORY_URL = 'https://raw.githubusercontent.com/joaqui1/Taller-Lab/observatorio-datos/precios-observatorio.json'
HISTORY_URL = os.environ.get('OBSERVATORIO_HISTORY_URL', DEFAULT_HISTORY_URL)


def latest_history(default):
    """Usa el historial diario de la rama observatorio-datos si es más reciente que la copia versionada.

    Así cada deploy de www (por ejemplo, disparado por el workflow con un deploy hook) publica en el
    dominio principal las mismas capturas que GitHub Pages. Si la descarga falla, usa la copia local.
    """
    import json
    import re
    import tempfile
    import time
    import urllib.parse
    import urllib.request
    from observatorio.gratuito import read_history
    try:
        # Raw GitHub puede resolver una rama a una versión anterior incluso con
        # query distinta. Resolver la referencia por API y descargar el commit
        # inmutable evita publicar una ejecución anterior tras el deploy hook.
        url = HISTORY_URL
        if url == DEFAULT_HISTORY_URL:
            ref_url = 'https://api.github.com/repos/joaqui1/Taller-Lab/git/ref/heads/observatorio-datos'
            ref_request = urllib.request.Request(ref_url + '?publication=' + str(time.time_ns()),
                                                 headers={'Cache-Control': 'no-cache', 'User-Agent': 'TallerLab-Publicacion/1.0'})
            with urllib.request.urlopen(ref_request, timeout=20) as response:
                ref = json.load(response)
            sha = ref.get('object', {}).get('sha', '')
            if ref.get('ref') != 'refs/heads/observatorio-datos' or not re.fullmatch(r'[0-9a-f]{40}', sha):
                raise ValueError('GitHub no devolvió el commit de la rama de datos')
            url = DEFAULT_HISTORY_URL.replace('/observatorio-datos/', '/' + sha + '/')
            print(f'OK: historial fijado al commit {sha}.')
        parts = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
        query.append(('publication', str(time.time_ns())))
        url = urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))
        request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(20_000_000)
        target = Path(tempfile.mkdtemp()) / 'precios-observatorio.json'
        target.write_bytes(data)
        remote = read_history(target)
        local = read_history(default) if default.is_file() else {'run': {}}
        remote_at, local_at = remote.get('run', {}).get('finished_at', ''), local.get('run', {}).get('finished_at', '')
        if remote_at and remote_at > local_at:
            print(f'OK: historial remoto más reciente ({remote_at}).')
            return target
        print('OK: la copia versionada del historial está al día.')
    except Exception as error:
        if os.environ.get('VERCEL_ENV') == 'production':
            raise RuntimeError('No se pudo confirmar el historial remoto; se conserva el despliegue anterior') from error
        print(f'Aviso: se usa el historial versionado ({type(error).__name__}: {error}).')
    return default


if __name__ == '__main__':
    main()
