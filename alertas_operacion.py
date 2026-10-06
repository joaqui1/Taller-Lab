"""Recolección diaria recuperable y estado público del servicio documental."""
import copy
import json
import os
import time
import uuid
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from alertas_almacen import serializado, guardar_estado, archivar_payload
from alertas_datos import cargar_registro_fuentes, cargar_expedientes, cargar_candidatos, identidad_alerta
from sincronizador_alertas import sincronizar_cpsc, sincronizar_defensa_consumidor, USER_AGENT, _buscar_modelos_candidatos


def ahora():
    return datetime.now(timezone.utc).isoformat()


def edad_horas(fecha):
    try:
        dt = datetime.fromisoformat(fecha)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    except (ValueError, TypeError):
        return None


@serializado
def iniciar(historico=False):
    registro = cargar_registro_fuentes()
    op = registro.setdefault('operacion_historico' if historico else 'operacion', {})
    for item in (registro.get('operacion', {}), registro.get('operacion_historico', {})):
        age = edad_horas(item.get('inicio'))
        if item.get('estado') == 'en_curso' and age is not None and age < 0.1:
            from alertas_persistencia import AlmacenOcupado
            raise AlmacenOcupado('Hay una recolección de alertas en curso')
    run_id = str(uuid.uuid4())
    backup = None
    if not historico:
        from alertas_respaldo import automatico
        backup = automatico()
    if op.get('id'):
        previous = {key: copy.deepcopy(value) for key, value in op.items() if key != 'historial'}
        if previous.get('estado') == 'en_curso':
            previous['estado'] = 'interrumpida'
        op.setdefault('historial', []).append(previous)
        op['historial'] = op['historial'][-30:]
    op.update(id=run_id, inicio=ahora(), estado='en_curso', resultados=[],
              entorno='vercel' if os.getenv('VERCEL') else 'mantenimiento')
    if backup:
        op['respaldo'] = backup
    guardar_estado(registro=registro)
    return run_id, op.get('ultimo_exito')


@serializado
def progreso(run_id, resultado, final=False, historico=False):
    registro = cargar_registro_fuentes()
    op = registro['operacion_historico' if historico else 'operacion']
    if op.get('id') != run_id:
        raise RuntimeError('La ejecución perdió su lease')
    if resultado:
        op['resultados'].append(resultado)
    if final:
        fallos = [r for r in op['resultados'] if not r.get('exito')]
        op.update(fin=ahora(), estado='parcial' if fallos else 'correcto')
        if not fallos:
            op['ultimo_exito'] = op['fin']
    guardar_estado(registro=registro)
    return {key: copy.deepcopy(value) for key, value in op.items() if key != 'historial'}


@serializado
def sincronizar_sernac(aviso, timeout=10):
    """Monitorea las campañas chilenas registradas; no afirma cubrir todo SERNAC."""
    from bs4 import BeautifulSoup
    url = aviso['enlace_original']
    if urlparse(url).hostname != 'www.sernac.cl' or not url.startswith('https://'):
        raise ValueError('URL SERNAC inválida')
    registro = cargar_registro_fuentes()
    info = registro.setdefault('sernac_cl', {})
    consultas = info.setdefault('campanas', {})
    item = consultas.setdefault(aviso['id_aviso'], {})
    item['ultima_consulta'] = ahora()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(3_000_001)
        if len(raw) > 3_000_000:
            raise ValueError('Respuesta SERNAC demasiado grande')
        html = raw.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1')
        if title is None or 'alerta' not in title.get_text().lower():
            raise ValueError('Respuesta SERNAC sin título de alerta')
        for element in soup(['script', 'style', 'nav', 'footer', 'form']):
            element.decompose()
        text = soup.get_text(' ', strip=True)
        start = text.find(title.get_text(' ', strip=True))
        text = text[start:]
        for delimiter in ('Servicio Nacional del Consumidor (SERNAC) / Oficinas', 'Ver más', 'Evalúe este contenido'):
            text = text.split(delimiter)[0]
        if len(text) < 200:
            raise ValueError('Aviso SERNAC incompleto')
        snapshot = archivar_payload({'url': url, 'contenido': html})
        payload = {'url': url, 'titulo': title.get_text(' ', strip=True), 'texto': text}
        version = archivar_payload(payload)
        item.update(estado='EXITOSA', ultimo_exito=ahora(), captura_respuesta=snapshot,
                    version_fuente=version, error_reciente=None)
        cands = cargar_candidatos()
        cand_id = 'cand-sernac-' + aviso['id_aviso']
        cand = next((c for c in cands if c['id'] == cand_id), None)
        coincidencias = _buscar_modelos_candidatos(text)
        if cand is None:
            cand = {'id': cand_id, 'fuente': 'SERNAC', 'id_externo': aviso['id_aviso'], 'estado_revision': 'PENDIENTE'}
            cands.append(cand)
        elif cand.get('version_fuente') != version:
            cand.setdefault('historial_cambios', []).append({'fecha': ahora(), 'hash_anterior': cand.get('version_fuente'), 'hash_nuevo': version})
            cand['estado_revision'] = 'MODIFICADO_PENDIENTE'
        cand.update(titulo=payload['titulo'], fecha_aviso=aviso['fecha'], fecha_deteccion=ahora(),
                    enlace_original=url, payload_original=payload, version_fuente=version,
                    coincidencia_modelo=coincidencias[0][0] if coincidencias else None,
                    coincidencias_adicionales=[c[0] for c in coincidencias],
                    resumen={'descripcion': text[:600]},
                    consulta={'url': url, 'fecha': ahora(), 'captura_sha256': snapshot})
        info.update(modo='AUTOMATICO_CAMPANAS_CONOCIDAS', ultima_consulta=ahora(),
                    cobertura='Sólo publicaciones SERNAC enlazadas en los expedientes; no búsqueda exhaustiva')
        info['estado'] = 'FALLIDA' if any(c.get('estado') == 'FALLIDA' for c in consultas.values()) else 'EXITOSA'
        info['ultimo_exito'] = min((c.get('ultimo_exito') for c in consultas.values() if c.get('ultimo_exito')), default=None)
        guardar_estado(registro=registro, candidatos=cands)
        return {'exito': True, 'fuente': 'SERNAC', 'aviso': aviso['id_aviso']}
    except Exception:
        item.update(estado='FALLIDA', error_reciente='No se pudo validar la publicación oficial')
        info.update(estado='FALLIDA', ultima_consulta=ahora())
        guardar_estado(registro=registro)
        return {'exito': False, 'fuente': 'SERNAC', 'aviso': aviso['id_aviso']}


def ejecutar(historico=False):
    if os.getenv('VERCEL'):
        from alertas_persistencia import configurado
        if not configurado():
            raise RuntimeError('La actualización requiere ALERTAS_DATABASE_URL persistente')
    run_id, ultimo = iniciar(historico=historico)
    budget = min(240, max(30, int(os.getenv('ALERTAS_RUN_BUDGET_SECONDS', '210'))))
    deadline = time.monotonic() + budget
    exps = cargar_expedientes()
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
    if ultimo:
        since = (datetime.fromisoformat(ultimo) - timedelta(days=2)).strftime('%Y-%m-%d')
    tasks = []
    if not historico:
        tasks = [('cpsc_novedades', lambda: sincronizar_cpsc('novedades', timeout=15, desde=since)),
                 ('argentina', lambda: sincronizar_defensa_consumidor(timeout=15))]
    known = {}
    for exp in exps:
        for al in exp['alertas']:
            key, number = identidad_alerta(al)
            if key == 'cpsc':
                known[(key, number)] = al
            elif key == 'sernac_cl':
                known[(key, number)] = al
    for (source, number), al in (known.items() if not historico else []):
        if source == 'cpsc':
            tasks.append(('cpsc_id_' + number, lambda n=number: sincronizar_cpsc('id:' + n, timeout=15, numero=n)))
        else:
            tasks.append(('sernac_' + number, lambda a=al: sincronizar_sernac(a, timeout=15)))
    if historico:
        for brand in sorted({e['marca'] for e in exps}):
            tasks.append(('historico_cpsc_' + brand, lambda b=brand: sincronizar_cpsc(b, timeout=30)))
    for name, operation in tasks:
        if deadline - time.monotonic() < (65 if historico else 35):
            progreso(run_id, {'tarea': name, 'exito': False, 'motivo': 'Presupuesto agotado; pendiente de próxima ejecución'}, historico=historico)
            continue
        result = None
        for attempt in range(2):
            try:
                result = operation()
            except Exception:
                result = {'exito': False, 'error': 'Fallo de procesamiento; revisar registros del servidor'}
            if result.get('exito'):
                break
        progreso(run_id, dict(result, tarea=name, intentos=attempt+1), historico=historico)
    result = progreso(run_id, None, final=True, historico=historico)
    result['modo'] = 'historico' if historico else 'diario'
    return result


def estado_publico():
    registro = cargar_registro_fuentes()
    operation = registro.get('operacion', {})
    age = edad_horas(operation.get('ultimo_exito'))
    status = 'sin_programacion_verificada' if not operation else 'correcto'
    if operation and (age is None or age > 48 or operation.get('estado') != 'correcto'):
        status = 'requiere_atencion'
    from alertas_persistencia import database_url
    backend = 'postgresql' if database_url() else ('sqlite' if os.getenv('ALERTAS_STATE_PATH') else 'snapshot')
    if os.getenv('VERCEL') and (backend != 'postgresql' or operation.get('entorno') != 'vercel'):
        status = 'sin_programacion_verificada'
    pending = [c for c in cargar_candidatos() if c.get('estado_revision') in ('PENDIENTE', 'MODIFICADO_PENDIENTE')]
    sources = []
    for key in ('cpsc', 'defensa_consumidor_ar', 'sernac_cl'):
        info = registro.get(key, {})
        sources.append({'fuente': key, 'estado': info.get('estado', 'PENDIENTE'),
            'ultimo_intento': info.get('ultima_consulta'), 'ultimo_exito': info.get('ultimo_exito'),
            'modo': info.get('modo'), 'cobertura': info.get('cobertura', 'Consulte la metodología; no acredita cobertura exhaustiva')})
    return {'estado': status, 'editor': 'Joaquín Vallasciani', 'persistencia': backend,
        'entorno_ultima_ejecucion': operation.get('entorno', 'sin_registro'), 'ultima_ejecucion': operation.get('fin'),
        'conciliacion_historica': {'estado': registro.get('operacion_historico', {}).get('estado', 'no_ejecutada'),
                                 'ultimo_exito': registro.get('operacion_historico', {}).get('ultimo_exito')},
        'ultimo_exito': operation.get('ultimo_exito'), 'horas_desde_exito': round(age, 1) if age is not None else None,
        'candidatos_pendientes': len(pending), 'pendientes_con_coincidencia': sum(bool(c.get('coincidencia_modelo')) for c in pending),
        'expedientes': len(cargar_expedientes()), 'fuentes': sources}


if __name__ == '__main__':
    import sys
    result = estado_publico() if '--estado' in sys.argv else ejecutar(historico='--historico' in sys.argv)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('estado') in ('parcial', 'requiere_atencion'):
        raise SystemExit(1)
