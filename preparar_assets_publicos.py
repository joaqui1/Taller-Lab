"""Publica los assets fuente en el directorio servido por el CDN de Vercel."""
from pathlib import Path
import shutil


def main():
    root = Path(__file__).resolve().parent
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


if __name__ == '__main__':
    main()
