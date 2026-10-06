"""
Módulo de sincronización y automatización de alertas oficiales para TallerLab.
Integra la API real de CPSC (EE. UU.) y el dataset oficial de Defensa del Consumidor (Argentina).

Reglas de automatización:
1. Guarda registros originales, identificadores únicos, fechas de consulta e historial de hashes.
2. Detecta avisos nuevos y modificaciones de avisos existentes sin sobrescribir arbitrariamente.
3. Las coincidencias automáticas generan CANDIDATOS PENDIENTES DE REVISIÓN.
4. NUNCA publica automáticamente equivalencias de variantes, alcance argentino ni conclusiones de seguridad.
5. Ante un fallo de red o caída de fuente, conserva intactos los datos históricos y registra la contingencia.
   Un fallo NUNCA se interpreta ni se presenta como 'sin alertas'.
6. Valida respuestas de CPSC (rechaza dicts de error o no-listas) y encabezados del CSV de Argentina por nombre.
7. Genera identidades persistentes y estables basadas en hash de contenido, evitando acoplamiento al número de fila.
8. Retorna todas las coincidencias encontradas por aviso para soporte de modelos múltiples.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import re
from alertas_almacen import serializado, guardar_estado, archivar_payload
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from alertas_datos import (
    cargar_candidatos,
    cargar_expedientes,
    cargar_registro_fuentes,
    guardar_candidatos,
    guardar_registro_fuentes,
)

CPSC_API_BASE = "https://www.saferproducts.gov/RestWebServices/Recall"
ARGENTINA_SPREADSHEET_ID = "1eUlKJFk-TYgZcmNd1-OMkMKSpeIOyNIgL4frzkKUnWs"
ARGENTINA_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{ARGENTINA_SPREADSHEET_ID}/gviz/tq?tqx=out:csv"
)

USER_AGENT = "TallerLab-Bot/1.0 (Investigación documental independiente; tallerlab.com.ar)"


def _codigo_en_texto(codigo, texto):
    return bool(codigo and re.search(r"(?<![a-z0-9])" + re.escape(codigo) + r"(?![a-z0-9])", texto))


def _fecha_canonica(fecha):
    fecha = fecha.strip()
    for formato in ("%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(fecha, formato).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return fecha


def _registrar_consulta(info, termino, url):
    info.setdefault("consultas", {})[termino.lower()] = {
        key: info.get(key) for key in ("estado", "ultima_consulta", "ultimo_exito", "error_reciente", "captura_respuesta", "total_recibidos")
    }
    info["consultas"][termino.lower()].update(url=url, termino=termino,
        cobertura="Búsqueda por descripción; no equivale a revisión exhaustiva del fabricante")


def _calcular_hash(payload: Any) -> str:
    """Calcula un hash SHA-256 canónico para detectar modificaciones en los avisos."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# Recalls de vehículos: entraban por palabras del defecto («batería», «manguera»)
# y llenaban la cola editorial. Se descartan sólo si marca y producto no nombran
# una herramienta (un generador Honda o un compresor de una automotriz siguen entrando).
_AUTOMOTRIZ = re.compile(
    r"\b(volkswagen|vw|ford|mercedes|peugeot|citroen|fiat|jeep|ram|dodge|chrysler|chevrolet|"
    r"general motors|audi|nissan|toyota|renault|volvo|jaguar|bmw|hyundai|kia|fca|iveco|scania|"
    r"eximar|automoviles|automobiles|buses y camiones)\b")
_HERRAMIENTA_EXPLICITA = re.compile(
    r"herramient|sierra|amoladora|taladro|ingletadora|compresor|generador|soldador|soldadora|"
    r"hidrolavadora|lijadora|atornillador|esmeril|engrasadora|pistola de grasa|motosierra|bordeadora|cortacesped")


def _es_aviso_automotor(fila, cols) -> bool:
    def campo(nombre):
        i = cols.get(nombre)
        return fila[i] if i is not None and i < len(fila) else ""
    texto = _normalizar_texto(f"{campo('marca')} {campo('producto')}")
    return bool(_AUTOMOTRIZ.search(texto)) and not _HERRAMIENTA_EXPLICITA.search(texto)


def _normalizar_texto(texto: str) -> str:
    """Normaliza texto removiendo tildes y pasando a minúsculas."""
    if not texto:
        return ""
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return sin_tildes.lower().strip()


def _buscar_modelos_candidatos(
    texto: str,
    productos: Optional[List[Dict[str, Any]]] = None,
) -> List[Tuple[str, str]]:
    """
    Evalúa si un aviso oficial menciona uno o varios modelos del catálogo de TallerLab.
    Retorna una lista de tuplas (slug_modelo, motivo_coincidencia) con todas las coincidencias encontradas.
    """
    texto_norm = _normalizar_texto(texto)
    expedientes = cargar_expedientes(forzar_recarga=True)
    coincidencias: List[Tuple[str, str]] = []
    slugs_vistos = set()

    # 1. Evaluar productos estructurados si vienen provistos (ej. CPSC Products)
    if productos:
        for p in productos:
            p_model = _normalizar_texto(p.get("Model") or "")
            p_name = _normalizar_texto(p.get("Name") or "")
            p_desc = _normalizar_texto(p.get("Description") or "")
            p_blob = f"{p_model} {p_name} {p_desc}"

            for exp in expedientes:
                slug = exp["slug"]
                if slug in slugs_vistos:
                    continue
                modelo_base = _normalizar_texto(exp["modelo_base"])
                marca = _normalizar_texto(exp["marca"])

                if _codigo_en_texto(modelo_base, p_blob) and marca in p_blob:
                    coincidencias.append(
                        (slug, f"Mención en producto estructurado CPSC: '{p.get('Name', '')}' ({exp['marca']} {exp['modelo_base']})")
                    )
                    slugs_vistos.add(slug)
                    continue

                for var in exp.get("variantes", []):
                    cod = _normalizar_texto(var["codigo"])
                    if _codigo_en_texto(cod, p_blob):
                        coincidencias.append(
                            (slug, f"Mención de variante '{var['codigo']}' en producto estructurado CPSC")
                        )
                        slugs_vistos.add(slug)
                        break

    # 2. Evaluar texto general (título, descripción, defectos, riesgos)
    for exp in expedientes:
        slug = exp["slug"]
        if slug in slugs_vistos:
            continue

        modelo_base = _normalizar_texto(exp["modelo_base"])
        marca = _normalizar_texto(exp["marca"])

        # Coincidencia por modelo base exacto y marca
        if _codigo_en_texto(modelo_base, texto_norm) and marca in texto_norm:
            coincidencias.append(
                (slug, f"Mención directa de marca '{exp['marca']}' y modelo base '{exp['modelo_base']}'")
            )
            slugs_vistos.add(slug)
            continue

        # Coincidencia por código de variante (ej. DWS780-AR, DGP180ZB) o EAN
        for var in exp.get("variantes", []):
            cod = _normalizar_texto(var["codigo"])
            if _codigo_en_texto(cod, texto_norm):
                coincidencias.append(
                    (slug, f"Mención del código de variante '{var['codigo']}'")
                )
                slugs_vistos.add(slug)
                break
            ean = var.get("codigo_barras")
            if ean and str(ean).isdigit() and _codigo_en_texto(str(ean), texto_norm):
                coincidencias.append(
                    (slug, f"Mención del código de barras / EAN '{ean}'")
                )
                slugs_vistos.add(slug)
                break

    return coincidencias


@serializado
def sincronizar_cpsc(
    termino_busqueda: str = "DeWalt",
    timeout: int = 15,
    desde: Optional[str] = None,
    numero: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Consulta la API real de CPSC por término de búsqueda y detecta avisos nuevos o modificados.
    Valida que la respuesta sea una lista JSON válida. Si falla, preserva datos previos y anota el error.
    """
    registro = cargar_registro_fuentes()
    info_cpsc = registro.setdefault("cpsc", {
        "nombre": "Consumer Product Safety Commission (CPSC) - EE. UU.",
        "endpoint": CPSC_API_BASE,
        "ultima_consulta": None,
        "ultimo_exito": None,
        "estado": "PENDIENTE",
        "error_reciente": None,
        "total_avisos_almacenados": 0,
        "hashes_aviso": {},
    })

    ahora_iso = datetime.now(timezone.utc).isoformat()
    consulta_previa = info_cpsc.get("consultas", {}).get(termino_busqueda.lower(), {})
    info_cpsc["ultimo_exito"] = consulta_previa.get("ultimo_exito")
    info_cpsc["captura_respuesta"] = consulta_previa.get("captura_respuesta")
    info_cpsc["ultima_consulta"] = ahora_iso
    info_cpsc["consulta_actual"] = termino_busqueda
    info_cpsc["modo"] = "AUTOMATICO_PROGRAMABLE"
    info_cpsc['cobertura'] = 'Novedades por publicación, marcas del catálogo y campañas conocidas por ID; no acredita revisión exhaustiva de todas las variantes'

    params = {'format': 'json'}
    if numero:
        params['RecallNumber'] = numero
    elif desde:
        # El servicio devuelve a veces un objeto de error para fecha sin hora.
        params['LastPublishDateStart'] = desde if 'T' in desde else desde + 'T00:00:00'
    else:
        params['RecallDescription'] = termino_busqueda
    url = CPSC_API_BASE + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            contenido = res.read().decode("utf-8")
        recalls = json.loads(contenido)
        if not isinstance(recalls, list):
            raise ValueError("Respuesta CPSC inválida: se esperaba list")
        for aviso in recalls:
            if not isinstance(aviso, dict) or not isinstance(aviso.get("RecallNumber") or aviso.get("RecallID"), (str, int)) or not (aviso.get("RecallNumber") or aviso.get("RecallID")):
                raise ValueError("Aviso CPSC sin identificador válido")
            for campo in ("Products", "Hazards", "Remedies"):
                items = aviso.get(campo)
                if items is None:
                    items = []
                if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
                    raise ValueError(f"Estructura CPSC inválida en {campo}")
                if any(item.get(key) is not None and not isinstance(item[key], str)
                       for item in items for key in ("Name", "Model", "Description")):
                    raise ValueError(f"Texto CPSC inválido en {campo}")
    except Exception as e:
        info_cpsc["estado"] = "FALLIDA"
        info_cpsc["error_reciente"] = f"Error al consultar CPSC API: {str(e)}"
        _registrar_consulta(info_cpsc, termino_busqueda, url)
        guardar_registro_fuentes(registro)
        return {
            "exito": False,
            "fuente": "CPSC",
            "error": str(e),
            "nuevos": 0,
            "modificados": 0,
            "sin_cambios": 0,
        }

    # Éxito de conexión y validación estructural
    info_cpsc["captura_respuesta"] = archivar_payload({"url": url, "contenido": contenido})
    info_cpsc["estado"] = "EXITOSA"
    info_cpsc["ultimo_exito"] = ahora_iso
    info_cpsc["error_reciente"] = None
    hashes = info_cpsc.setdefault("hashes_aviso", {})

    candidatos = cargar_candidatos()
    candidatos_map = {c["id"]: c for c in candidatos}

    nuevos = 0
    modificados = 0
    sin_cambios = 0

    for r in recalls:
        if not isinstance(r, dict):
            continue

        recall_num = str(r.get("RecallNumber") or r.get("RecallID") or "")
        if not recall_num:
            continue

        h = archivar_payload(r)
        anterior_hash = hashes.get(recall_num)

        titulo = str(r.get("Title") or "")
        descripcion = str(r.get("Description") or "")
        texto_evaluar = f"{titulo} {descripcion}"

        products_list = r.get("Products") or []
        coincidencias = _buscar_modelos_candidatos(texto_evaluar, productos=products_list)
        slug_principal = coincidencias[0][0] if coincidencias else None
        motivo_principal = coincidencias[0][1] if coincidencias else "Sin coincidencia automática con catálogo"
        todos_los_slugs = [c[0] for c in coincidencias]

        cand_id = f"cand-cpsc-{recall_num}"

        resumen_data = {
            "descripcion": (descripcion[:400] + "...") if len(descripcion) > 400 else descripcion,
            "productos": [str(p.get("Name") or "") for p in products_list if isinstance(p, dict)],
            "riesgos": [str(hz.get("Name") or "") for hz in (r.get("Hazards") or []) if isinstance(hz, dict)],
            "medidas": [str(rem.get("Name") or "") for rem in (r.get("Remedies") or []) if isinstance(rem, dict)],
        }

        if anterior_hash is None or cand_id not in candidatos_map:
            # Nuevo aviso o upsert de candidato ausente
            if anterior_hash is None:
                nuevos += 1
            hashes[recall_num] = h
            candidatos_map[cand_id] = {
                "id": cand_id,
                "fuente": "CPSC",
                "id_externo": recall_num,
                "titulo": titulo,
                "fecha_aviso": str(r.get("RecallDate") or ""),
                "fecha_deteccion": ahora_iso,
                "tipo_aviso": "Recall de seguridad EE. UU.",
                "coincidencia_modelo": slug_principal,
                "motivo_coincidencia": motivo_principal,
                "coincidencias_adicionales": todos_los_slugs,
                "estado_revision": "PENDIENTE",
                "enlace_original": str(r.get("URL") or ""),
                "resumen": resumen_data,
                "payload_original": r,
                "version_fuente": h,
                "consulta": {"url": url, "termino": termino_busqueda, "fecha": ahora_iso, "captura_sha256": info_cpsc["captura_respuesta"]},
            }
        elif anterior_hash != h:
            # Aviso modificado por la autoridad emisora: actualizar campos derivados
            modificados += 1
            hashes[recall_num] = h
            cand = candidatos_map[cand_id]
            cand["version_fuente"] = h
            cand["consulta"] = {"url": url, "termino": termino_busqueda, "fecha": ahora_iso, "captura_sha256": info_cpsc["captura_respuesta"]}
            cand["titulo"] = titulo
            cand["fecha_aviso"] = str(r.get("RecallDate") or "")
            cand["fecha_deteccion"] = ahora_iso
            cand["enlace_original"] = str(r.get("URL") or "")
            cand["resumen"] = resumen_data
            version_previa = archivar_payload(cand["payload_original"])
            cand["payload_original"] = r
            cand["coincidencia_modelo"] = slug_principal
            cand["motivo_coincidencia"] = motivo_principal
            cand["coincidencias_adicionales"] = todos_los_slugs
            cand["estado_revision"] = "MODIFICADO_PENDIENTE"
            cand.setdefault("historial_cambios", []).append({
                "fecha": ahora_iso,
                "hash_anterior": version_previa,
                "hash_nuevo": h,
                "tipo": "modificacion_fuente",
            })
        else:
            candidatos_map[cand_id]["consulta"] = {"url": url, "termino": termino_busqueda,
                "fecha": ahora_iso, "captura_sha256": info_cpsc["captura_respuesta"]}
            candidatos_map[cand_id].update(coincidencia_modelo=slug_principal,
                motivo_coincidencia=motivo_principal, coincidencias_adicionales=todos_los_slugs)
            aprobaciones = candidatos_map[cand_id].get('aprobaciones', {})
            pendientes = [slug for slug in todos_los_slugs if aprobaciones.get(slug, {}).get('version_fuente') != h]
            candidatos_map[cand_id]['modelos_pendientes'] = pendientes
            if pendientes and candidatos_map[cand_id].get('estado_revision') == 'APROBADO':
                candidatos_map[cand_id]['estado_revision'] = 'PENDIENTE'
            sin_cambios += 1

    info_cpsc["total_recibidos"] = len(recalls)
    info_cpsc["total_avisos_almacenados"] = len(hashes)
    info_cpsc["trazabilidad"] = "CAPTURAS_ARCHIVADAS"
    _registrar_consulta(info_cpsc, termino_busqueda, url)
    guardar_estado(registro=registro, candidatos=list(candidatos_map.values()))

    return {
        "exito": True,
        "fuente": "CPSC",
        "termino": termino_busqueda,
        "total_recibidos": len(recalls),
        "nuevos": nuevos,
        "modificados": modificados,
        "sin_cambios": sin_cambios,
    }


def _resolver_columnas_argentina(header_row: List[str]) -> Optional[Dict[str, int]]:
    """
    Inspecciona los encabezados del CSV de Defensa del Consumidor por nombre.
    Rechaza respuestas HTML o formatos no reconocidos.
    """
    headers_norm = [_normalizar_texto(h) for h in header_row]

    # Verificar si es una página HTML de error
    primera_celda = headers_norm[0] if headers_norm else ""
    if "<!doctype" in primera_celda or "<html" in primera_celda or "goog_auth" in primera_celda:
        return None

    indices: Dict[str, int] = {}
    for idx, h in enumerate(headers_norm):
        if "alerta" in h or "fecha" in h:
            indices.setdefault("fecha", idx)
        elif "marca" in h:
            indices.setdefault("marca", idx)
        elif "producto" in h or "descripcion_producto" in h or "modelo" in h:
            indices.setdefault("producto", idx)
        elif "defecto" in h:
            indices.setdefault("defecto", idx)
        elif "riesgo" in h:
            indices.setdefault("riesgos", idx)
        elif "categoria" in h or "filtro" in h:
            indices.setdefault("categoria", idx)

    # Validar presencia de columnas esenciales
    if "marca" not in indices or "producto" not in indices or "defecto" not in indices:
        return None

    return indices


@serializado
def sincronizar_defensa_consumidor(timeout: int = 15) -> Dict[str, Any]:
    """
    Consulta el dataset oficial de Defensa del Consumidor (Argentina) publicado en Google Sheets.
    Valida encabezados por nombre y genera identidades estables independientes de la fila.
    """
    registro = cargar_registro_fuentes()
    info_arg = registro.setdefault("defensa_consumidor_ar", {
        "nombre": "Defensa del Consumidor - Argentina",
        "endpoint": ARGENTINA_CSV_URL,
        "portal": "https://www.argentina.gob.ar/produccion/defensadelconsumidor/alertas-de-productos",
        "ultima_consulta": None,
        "ultimo_exito": None,
        "estado": "PENDIENTE",
        "error_reciente": None,
        "total_avisos_almacenados": 0,
        "hashes_aviso": {},
    })

    ahora_iso = datetime.now(timezone.utc).isoformat()
    info_arg["ultima_consulta"] = ahora_iso

    req = urllib.request.Request(ARGENTINA_CSV_URL, headers={"User-Agent": USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            contenido = res.read().decode("utf-8")
    except Exception as e:
        info_arg["estado"] = "FALLIDA"
        info_arg["error_reciente"] = f"Error al consultar dataset de Argentina: {str(e)}"
        guardar_registro_fuentes(registro)
        return {
            "exito": False,
            "fuente": "Defensa del Consumidor",
            "error": str(e),
            "nuevos": 0,
            "modificados": 0,
            "sin_cambios": 0,
        }

    if "<!doctype" in contenido.lower() or "<html" in contenido.lower():
        error_msg = "El contenido devuelto por Argentina es una página HTML de error o autenticación."
        info_arg["estado"] = "FALLIDA"
        info_arg["error_reciente"] = error_msg
        guardar_registro_fuentes(registro)
        return {
            "exito": False,
            "fuente": "Defensa del Consumidor",
            "error": error_msg,
            "nuevos": 0,
            "modificados": 0,
            "sin_cambios": 0,
        }

    reader = csv.reader(io.StringIO(contenido))
    rows = list(reader)


    if not rows or len(rows) < 2:
        error_msg = "Dataset de Argentina vacío o sin filas de datos."
        info_arg["estado"] = "FALLIDA"
        info_arg["error_reciente"] = error_msg
        guardar_registro_fuentes(registro)
        return {
            "exito": False,
            "fuente": "Defensa del Consumidor",
            "error": error_msg,
            "nuevos": 0,
            "modificados": 0,
            "sin_cambios": 0,
        }

    cols = _resolver_columnas_argentina(rows[0])
    if cols is None:
        error_msg = "El contenido devuelto por Argentina no contiene los encabezados esperados o es una página HTML de error."
        info_arg["estado"] = "FALLIDA"
        info_arg["error_reciente"] = error_msg
        guardar_registro_fuentes(registro)
        return {
            "exito": False,
            "fuente": "Defensa del Consumidor",
            "error": error_msg,
            "nuevos": 0,
            "modificados": 0,
            "sin_cambios": 0,
        }

    info_arg["captura_respuesta"] = archivar_payload({"url": ARGENTINA_CSV_URL, "contenido": contenido})
    info_arg["estado"] = "EXITOSA"
    info_arg["ultimo_exito"] = ahora_iso
    info_arg["error_reciente"] = None
    hashes = info_arg.setdefault("hashes_aviso", {})

    candidatos = cargar_candidatos()
    candidatos_map = {c["id"]: c for c in candidatos}

    nuevos = 0
    modificados = 0
    sin_cambios = 0

    palabras_herramientas = [
        "herramient", "dewalt", "bosch", "makita", "black", "decker",
        "stanley", "einhell", "lusqtoff", "sierra", "amoladora", "taladro", "ingletadora",
        'bateria', 'batería', 'cargador', 'compresor', 'generador', 'soldador', 'hidrolavadora',
        'lijadora', 'atornillador', 'esmeril', 'manguera', 'engrasadora', 'pistola de grasa'
    ]
    palabras_herramientas += [_normalizar_texto(e['marca']) for e in cargar_expedientes()]

    for idx, r in enumerate(rows[1:], start=2):
        fila_str = _normalizar_texto(" ".join(r))
        if not any(k in fila_str for k in palabras_herramientas):
            continue

        if _es_aviso_automotor(r, cols):
            continue

        fecha = r[cols["fecha"]] if "fecha" in cols and cols["fecha"] < len(r) else ""
        marca = r[cols["marca"]] if "marca" in cols and cols["marca"] < len(r) else ""
        descripcion_prod = r[cols["producto"]] if "producto" in cols and cols["producto"] < len(r) else ""
        defecto = r[cols["defecto"]] if "defecto" in cols and cols["defecto"] < len(r) else ""
        riesgos = r[cols["riesgos"]] if "riesgos" in cols and cols["riesgos"] < len(r) else ""

        # Identidad persistente y estable basada en contenido canónico (independiente de la posición de la fila)
        fecha = _fecha_canonica(fecha)
        marca = " ".join(marca.split())
        descripcion_prod = " ".join(descripcion_prod.split())
        defecto = " ".join(defecto.split())
        riesgos = " ".join(riesgos.split())
        clave_estable = f"{fecha.lower()}|{marca.lower()}|{descripcion_prod.lower()}"
        id_estable = f"arg-dnc-{hashlib.sha256(clave_estable.encode('utf-8')).hexdigest()[:12]}"

        payload = {
            "id_estable": id_estable,
            
            "fecha": fecha,
            "marca": marca,
            "descripcion": descripcion_prod,
            "defecto": defecto,
            "riesgos": riesgos,
        }

        h = archivar_payload(payload)
        anterior_hash = hashes.get(id_estable)

        texto_evaluar = f"{marca} {descripcion_prod} {defecto}"
        coincidencias = _buscar_modelos_candidatos(texto_evaluar)
        slug_principal = coincidencias[0][0] if coincidencias else None
        motivo_principal = coincidencias[0][1] if coincidencias else "Alerta de herramienta sin asignación a modelo"
        todos_los_slugs = [c[0] for c in coincidencias]

        cand_id = f"cand-{id_estable}"

        resumen_data = {
            "marca": marca,
            "producto": descripcion_prod,
            "defecto": defecto,
            "riesgos": riesgos,
        }

        if anterior_hash is None or cand_id not in candidatos_map:
            if anterior_hash is None:
                nuevos += 1
            hashes[id_estable] = h
            candidatos_map[cand_id] = {
                "id": cand_id,
                "fuente": "Defensa del Consumidor (Argentina)",
                "id_externo": id_estable,
                "titulo": f"{marca}: {descripcion_prod}".strip(),
                "fecha_aviso": fecha,
                "fecha_deteccion": ahora_iso,
                "tipo_aviso": "Notificación oficial de alerta y retiro",
                "coincidencia_modelo": slug_principal,
                "motivo_coincidencia": motivo_principal,
                "coincidencias_adicionales": todos_los_slugs,
                "estado_revision": "PENDIENTE",
                "enlace_original": info_arg["portal"],
                "resumen": resumen_data,
                "payload_original": payload,
                "version_fuente": h,
                "consulta": {"url": ARGENTINA_CSV_URL, "fila": idx, "fecha": ahora_iso, "captura_sha256": info_arg["captura_respuesta"]},
            }
        elif anterior_hash != h:
            modificados += 1
            hashes[id_estable] = h
            cand = candidatos_map[cand_id]
            cand["version_fuente"] = h
            cand["consulta"] = {"url": ARGENTINA_CSV_URL, "fila": idx, "fecha": ahora_iso, "captura_sha256": info_arg["captura_respuesta"]}
            cand["titulo"] = f"{marca}: {descripcion_prod}".strip()
            cand["fecha_aviso"] = fecha
            cand["fecha_deteccion"] = ahora_iso
            cand["resumen"] = resumen_data
            version_previa = archivar_payload(cand["payload_original"])
            cand["payload_original"] = payload
            cand["coincidencia_modelo"] = slug_principal
            cand["motivo_coincidencia"] = motivo_principal
            cand["coincidencias_adicionales"] = todos_los_slugs
            cand["estado_revision"] = "MODIFICADO_PENDIENTE"
            cand.setdefault("historial_cambios", []).append({
                "fecha": ahora_iso,
                "hash_anterior": version_previa,
                "hash_nuevo": h,
                "tipo": "modificacion_fuente",
            })
        else:
            candidatos_map[cand_id]["consulta"] = {"url": ARGENTINA_CSV_URL, "fila": idx,
                "fecha": ahora_iso, "captura_sha256": info_arg["captura_respuesta"]}
            candidatos_map[cand_id].update(coincidencia_modelo=slug_principal,
                motivo_coincidencia=motivo_principal, coincidencias_adicionales=todos_los_slugs)
            sin_cambios += 1

    info_arg["total_avisos_almacenados"] = len(hashes)
    info_arg["trazabilidad"] = "CAPTURAS_ARCHIVADAS"
    info_arg["total_filas_recibidas"] = len(rows) - 1
    info_arg["modo"] = "AUTOMATICO_PROGRAMABLE"
    info_arg['cobertura'] = 'Planilla oficial filtrada por términos y marcas de herramientas; no todos los productos de consumo'
    guardar_estado(registro=registro, candidatos=list(candidatos_map.values()))

    return {
        "exito": True,
        "fuente": "Defensa del Consumidor",
        "total_filas_revisadas": len(rows) - 1,
        "nuevos": nuevos,
        "modificados": modificados,
        "sin_cambios": sin_cambios,
    }


def main() -> None:
    """Punto de entrada CLI directo para sincronización periódica de fuentes."""
    print("Sincronizando fuentes oficiales de alertas...")
    marcas = sorted({e["marca"] for e in cargar_expedientes(forzar_recarga=True)})
    resultados = [sincronizar_cpsc(marca) for marca in marcas]
    for marca, resultado in zip(marcas, resultados):
        print(f"CPSC ({marca}): {resultado}")

    res_arg = sincronizar_defensa_consumidor()
    print(f"Defensa del Consumidor: {'OK' if res_arg['exito'] else 'FALLO - ' + str(res_arg.get('error'))}")

    if any(not r["exito"] for r in resultados) or not res_arg["exito"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
