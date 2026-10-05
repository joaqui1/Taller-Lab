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
    print(f"OK: observatorio con {summary['observations']} observaciones y {len(summary['routes'])} páginas verificadas.")


HISTORY_URL = os.environ.get('OBSERVATORIO_HISTORY_URL', 'https://raw.githubusercontent.com/joaqui1/Taller-Lab/observatorio-datos/precios-observatorio.json')


def latest_history(default):
    """Usa el historial diario de la rama observatorio-datos si es más reciente que la copia versionada.

    Así cada deploy de www (por ejemplo, disparado por el workflow con un deploy hook) publica en el
    dominio principal las mismas capturas que GitHub Pages. Si la descarga falla, usa la copia local.
    """
    import json
    import tempfile
    import urllib.request
    from observatorio.gratuito import read_history
    try:
        with urllib.request.urlopen(HISTORY_URL, timeout=20) as response:
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
        print(f'Aviso: se usa el historial versionado ({type(error).__name__}: {error}).')
    return default


if __name__ == '__main__':
    main()
