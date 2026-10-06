"""Bloqueo entre procesos, recuperación de escrituras y capturas inmutables.

Los JSON siguen siendo portables. Un diario permite terminar una escritura
interrumpida antes de servir o editar los datos. El directorio debe ser duradero.
"""
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
import hashlib
import json
import os
import threading

_mutex = threading.RLock()
_local = threading.local()


def solo_lectura():
    from alertas_persistencia import configurado
    return os.environ.get("ALERTAS_SOLO_LECTURA") == "1" or bool(
        os.environ.get("VERCEL") and not configurado() and not os.environ.get("ALERTAS_DATA_DIR"))


def _directorio():
    import alertas_datos
    return alertas_datos.DATOS_DIR


def _reemplazar(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    temp.replace(path)


def _recuperar():
    directory = _directorio()
    journal = directory / "transaccion.json"
    if not journal.exists():
        return
    entries = json.loads(journal.read_text(encoding="utf-8"))
    allowed = {"registro_fuentes.json", "candidatos_revision.json", "modelos_expedientes.json"}
    if not isinstance(entries, dict) or not set(entries).issubset(allowed):
        raise ValueError("Diario de alertas inválido")
    for name, value in entries.items():
        _reemplazar(directory / name, value)
    journal.unlink()


@contextmanager
def bloqueo_datos(lectura=False):
    with _mutex:
        if getattr(_local, "depth", 0):
            _local.depth += 1
            try:
                yield
            finally:
                _local.depth -= 1
            return
        directory = _directorio()
        from alertas_persistencia import configurado, transaccion
        if configurado():
            _local.depth = 1
            try:
                with transaccion(directory, lectura=lectura):
                    yield
            finally:
                _local.depth = 0
            return
        if solo_lectura():
            if (directory / "transaccion.json").exists():
                raise RuntimeError("Snapshot de alertas incompleto: recuperar antes de publicar")
            yield
            return
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / ".lock").open("a+b") as handle:
            handle.seek(0, 2)
            if handle.tell() == 0:
                handle.write(b"0")
                handle.flush()
            handle.seek(0)
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            _local.depth = 1
            try:
                _recuperar()
                yield
            finally:
                _local.depth = 0
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def serializado(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with bloqueo_datos():
            return fn(*args, **kwargs)
    return wrapper


def lectura_serializada(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with bloqueo_datos(lectura=True):
            return fn(*args, **kwargs)
    return wrapper


@serializado
def guardar_estado(*, registro=None, candidatos=None, expedientes=None):
    if solo_lectura():
        raise RuntimeError("Alertas en modo lectura: sincronizar en un almacén duradero y publicar un snapshot")
    entries = {}
    if registro is not None:
        entries["registro_fuentes.json"] = registro
    if candidatos is not None:
        entries["candidatos_revision.json"] = candidatos
    if expedientes is not None:
        from alertas_datos import validar_expediente
        for exp in expedientes:
            validar_expediente(exp)
        entries["modelos_expedientes.json"] = expedientes
    from alertas_persistencia import configurado, guardar
    if configurado():
        for name, value in entries.items():
            guardar(name, value)
    else:
        _reemplazar(_directorio() / "transaccion.json", entries)
        _recuperar()


@lectura_serializada
def leer_documento(nombre, default):
    from alertas_persistencia import configurado, leer
    if configurado():
        return leer(nombre, default)
    path = _directorio() / nombre
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else default


@serializado
def archivar_payload(payload):
    if solo_lectura():
        raise RuntimeError("No se pueden archivar capturas en modo lectura")
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    from alertas_persistencia import configurado, guardar_captura
    if configurado():
        guardar_captura(digest, raw)
        return digest
    directory = _directorio() / "capturas"
    directory.mkdir(exist_ok=True)
    path = directory / (digest + ".json")
    if path.exists():
        if path.read_text(encoding="utf-8") != raw:
            raise ValueError("Captura existente no coincide con su hash")
    else:
        temp = path.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        temp.replace(path)
    return digest


@lectura_serializada
def leer_captura(digest):
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        raise ValueError('Identificador de captura inválido')
    from alertas_persistencia import configurado, captura
    if configurado():
        raw = captura(digest)
        if raw is None:
            raise FileNotFoundError('Captura no disponible')
    else:
        raw = (_directorio() / "capturas" / (digest + ".json")).read_text(encoding='utf-8')
    if hashlib.sha256(raw.encode('utf-8')).hexdigest() != digest:
        raise ValueError('Captura corrupta')
    return json.loads(raw)


def captura_verificable(digest):
    try:
        leer_captura(digest)
        return True
    except (OSError, ValueError):
        return False
