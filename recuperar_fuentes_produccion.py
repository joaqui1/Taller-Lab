"""Recupera documentos movidos únicamente tras comprobar respuesta y formato.

No convierte un catálogo nuevo en evidencia de uno histórico ni modifica cifras.
"""
import concurrent.futures
import json
from pathlib import Path
from urllib.parse import urlsplit
from auditar_destinos_produccion import inspect

ROOT = Path(__file__).parent

def main():
    failures = json.loads((ROOT / 'destinos-produccion-2026-09-30.json').read_text(encoding='utf-8'))
    candidates = {}
    for row in failures:
        old = row['url']
        if row.get('status') != 404:
            continue
        parsed = urlsplit(old)
        if '/GLOBALBOM/' in old:
            brand = 'STANLEY' if 'stanley' in parsed.netloc else 'DEWALT'
            candidates[old] = 'https://www.toolservicenet.com/i/' + brand + parsed.path
    candidates['https://www.gammaherramientas.com.ar/producto/compresor-bicilindrico-de-100-l-3-hp/'] = 'https://www.gammaherramientas.com.ar/producto/compresor-bicilindrico-100-l-3-hp/'
    candidates['https://konan.com.ar/media/descargas/KONAN-Catalogo-2025.pdf'] = 'https://www.konan.com.ar/media/descargas/KONAN-Catalogo.pdf'
    candidates['https://btatools.com.ar/catalogo/catalogo-bta-2026-27-1.pdf'] = 'https://drive.google.com/file/d/1DyTARerK_VdMZmHHSjoT3NJL1KkfBhOz/view'
    evidence = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for (old, new), result in zip(candidates.items(), pool.map(inspect, candidates.values())):
            valid = result.get('status') == 200 and not result.get('challenge')
            if new.endswith('.pdf'):
                valid = valid and 'pdf' in result.get('content_type', '').lower()
            files = []
            if valid:
                for file in (ROOT / 'paginas').rglob('*.md'):
                    text = file.read_text(encoding='utf-8')
                    if old in text:
                        file.write_text(text.replace(old, new), encoding='utf-8')
                        files.append(str(file.relative_to(ROOT)))
            evidence.append(dict(old=old, candidate=new, replaced=valid, files=files, response=result))
    output = ROOT / 'fuentes-recuperadas-2026-09-30.json'
    previous = json.loads(output.read_text(encoding='utf-8')) if output.exists() else []
    combined = {row['old']: row for row in previous}
    for row in evidence:
        # Una nueva ejecución sin enlaces pendientes no debe borrar la evidencia
        # de una recuperación ya realizada (incluidas reparaciones manuales).
        if row['files'] or row['old'] not in combined:
            combined[row['old']] = row
    output.write_text(json.dumps(list(combined.values()), ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps([dict(old=r['old'], status=r['response'].get('status'), replaced=r['replaced'], files=len(r['files'])) for r in evidence], ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
