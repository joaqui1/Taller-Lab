"""Respaldo portable con comprobación de integridad y restauración transaccional."""
import hashlib
import io
import json
import re
import zipfile
import base64
from datetime import datetime, timezone
from pathlib import Path

from alertas_almacen import serializado, lectura_serializada, leer_documento, leer_captura, archivar_payload, guardar_estado

NAMES = ('modelos_expedientes.json', 'candidatos_revision.json', 'registro_fuentes.json')


@serializado
def automatico():
    """Una copia previa por día, 14 días, en el mismo almacén persistente."""
    from alertas_persistencia import configurado, execute
    if not configurado():
        return {'estado': 'sin_almacen_persistente'}
    execute('CREATE TABLE IF NOT EXISTS tallerlab_alertas_respaldos (fecha TEXT PRIMARY KEY, payload TEXT NOT NULL, digest TEXT NOT NULL)')
    fecha = datetime.now(timezone.utc).date().isoformat()
    if not execute('SELECT fecha FROM tallerlab_alertas_respaldos WHERE fecha=?', (fecha,)).fetchone():
        raw = respaldo()
        if len(raw) > 20_000_000:
            raise ValueError('Respaldo automático supera 20 MB; revisar retención y cobertura')
        execute('INSERT INTO tallerlab_alertas_respaldos(fecha,payload,digest) VALUES (?,?,?)',
                (fecha, base64.b64encode(raw).decode('ascii'), hashlib.sha256(raw).hexdigest()))
        execute('DELETE FROM tallerlab_alertas_respaldos WHERE fecha NOT IN (SELECT fecha FROM tallerlab_alertas_respaldos ORDER BY fecha DESC LIMIT 14)')
    return {'estado': 'guardado', 'fecha': fecha, 'retencion_dias': 14, 'ubicacion': 'misma_base'}


@lectura_serializada
def anteriores(fecha=None):
    from alertas_persistencia import configurado, execute
    if not configurado():
        return [] if fecha is None else None
    # La tabla se crea con la primera tarea diaria.
    from alertas_persistencia import _local
    if _local.postgres:
        exists = execute("SELECT to_regclass('tallerlab_alertas_respaldos')").fetchone()[0]
    else:
        exists = execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tallerlab_alertas_respaldos'").fetchone()
    if not exists:
        return [] if fecha is None else None
    if fecha is None:
        return [{'fecha': row[0], 'sha256': row[1]} for row in execute('SELECT fecha,digest FROM tallerlab_alertas_respaldos ORDER BY fecha DESC').fetchall()]
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', fecha):
        raise ValueError('Fecha inválida')
    row = execute('SELECT payload,digest FROM tallerlab_alertas_respaldos WHERE fecha=?', (fecha,)).fetchone()
    if not row:
        return None
    raw = base64.b64decode(row[0], validate=True)
    if hashlib.sha256(raw).hexdigest() != row[1]:
        raise ValueError('Respaldo automático corrupto')
    return raw


def referencias(value):
    hashes = set()
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, str) and re.fullmatch('[a-f0-9]{64}', item):
                hashes.add(item)
            hashes.update(referencias(item))
    elif isinstance(value, list):
        for item in value:
            hashes.update(referencias(item))
    return hashes


@lectura_serializada
def respaldo():
    docs = {name: leer_documento(name, [] if name != 'registro_fuentes.json' else {}) for name in NAMES}
    payloads = {name: json.dumps(value, ensure_ascii=False).encode('utf-8') for name, value in docs.items()}
    unavailable = []
    for digest in referencias(list(docs.values())):
        try:
            payload = leer_captura(digest)
        except (ValueError, OSError):
            unavailable.append(digest)
            continue
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        payloads['capturas/'+digest+'.json'] = raw
    manifest = {name: hashlib.sha256(raw).hexdigest() for name, raw in payloads.items()}
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, raw in payloads.items():
            archive.writestr(name, raw)
        archive.writestr('manifest.json', json.dumps({'formato': 1, 'archivos': manifest,
                            'referencias_sin_captura': unavailable}, ensure_ascii=False))
    return output.getvalue()


@serializado
def restaurar(raw):
    if len(raw) > 50_000_000:
        raise ValueError('Respaldo demasiado grande')
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        if sum(i.file_size for i in archive.infolist()) > 100_000_000:
            raise ValueError('Respaldo descomprimido demasiado grande')
        manifest = json.loads(archive.read('manifest.json'))
        if manifest.get('formato') != 1:
            raise ValueError('Formato de respaldo desconocido')
        docs = {}
        captures = []
        for name, digest in manifest['archivos'].items():
            if name not in NAMES and not re.fullmatch(r'capturas/[a-f0-9]{64}\.json', name):
                raise ValueError('Ruta de respaldo inválida')
            content = archive.read(name)
            if hashlib.sha256(content).hexdigest() != digest:
                raise ValueError('Respaldo corrupto')
            value = json.loads(content)
            if name in NAMES:
                docs[name] = value
            else:
                expected = Path(name).stem
                canonical = json.dumps(value, sort_keys=True, ensure_ascii=False).encode('utf-8')
                if hashlib.sha256(canonical).hexdigest() != expected:
                    raise ValueError('Identidad de captura inválida')
                captures.append(value)
        if set(docs) != set(NAMES):
            raise ValueError('Respaldo incompleto')
        from alertas_datos import validar_expediente
        for exp in docs['modelos_expedientes.json']:
            validar_expediente(exp)
        for payload in captures:
            archivar_payload(payload)
        guardar_estado(expedientes=docs[NAMES[0]], candidatos=docs[NAMES[1]], registro=docs[NAMES[2]])
    return {'expedientes': len(docs[NAMES[0]]), 'capturas': len(captures)}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--guardar')
    parser.add_argument('--restaurar')
    args = parser.parse_args()
    if bool(args.guardar) == bool(args.restaurar):
        parser.error('Elegir --guardar o --restaurar')
    if args.guardar:
        path = Path(args.guardar)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(respaldo())
        print('Respaldo guardado')
    else:
        print(json.dumps(restaurar(Path(args.restaurar).read_bytes())))
