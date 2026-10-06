"""
Módulo de datos y dominio para el sistema de expedientes técnicos y alertas de herramientas.
Garantiza el cumplimiento de las reglas editoriales: conservación de sufijos regionales,
delimitación de alcance geográfico, registro de exclusiones y descargos de independencia.
"""

from __future__ import annotations

import json
import os
import copy
from alertas_almacen import serializado, lectura_serializada, guardar_estado, captura_verificable, leer_documento
from pathlib import Path
from typing import Any, Dict, List, Optional

DATOS_DIR = Path(os.environ.get("ALERTAS_DATA_DIR", str(Path(__file__).parent / "datos_alertas")))
MODELOS_FILE = DATOS_DIR / "modelos_expedientes.json"
CANDIDATOS_FILE = DATOS_DIR / "candidatos_revision.json"
FUENTES_FILE = DATOS_DIR / "registro_fuentes.json"
EDITOR_RESPONSABLE = 'Joaquín Vallasciani'

# Textos de transparencia y descargos exigidos
DESCARGO_INDEPENDENCIA = (
    "TallerLab es un proyecto independiente de investigación documental. "
    "No representa a organismos oficiales, agencias regulatorias ni a fabricantes de herramientas."
)
DESCARGO_NO_GARANTIA_SEGURIDAD = (
    "La ausencia de alertas en una consulta no certifica la seguridad del producto "
    "ni reemplaza la inspección técnica o las instrucciones del manual del fabricante."
)
DESCARGO_CAMPANA_EXTRANJERA = (
    "Una campaña de retiro o advertencia dispuesta en el extranjero no acredita por sí sola "
    "campaña activa ni reparación gratuita en Argentina sin confirmación del canal oficial local."
)

ESTADOS_ALERTA = {
    "ALERTA_OFICIAL": {
        "etiqueta": "Alerta oficial confirmada",
        "badge_class": "badge-alerta",
        "bg": "#7f1d1d",
        "color": "#fecaca",
        "icono": "⚠️",
        "descripcion": "Existe una campaña oficial de retiro, advertencia o modificación técnica confirmada con alcance identificado.",
    },
    "POSIBLE_COINCIDENCIA": {
        "etiqueta": "Posible coincidencia",
        "badge_class": "badge-posible",
        "bg": "#78350f",
        "color": "#fef3c7",
        "icono": "🔍",
        "descripcion": "Existe un aviso para una plataforma afín o modelo del exterior; requiere verificación adicional del código exacto.",
    },
    "SIN_ALERTAS": {
        "etiqueta": "Sin alertas coincidentes en fuentes consultadas",
        "badge_class": "badge-sin-alertas",
        "bg": "#1e293b",
        "color": "#94a3b8",
        "icono": "ℹ️",
        "descripcion": "No se encontraron llamados a revisión en las fuentes consultadas a la fecha de verificación. Esto no certifica seguridad absoluta ni sustituye la inspección técnica.",
    },
    "NO_REVISADO": {
        "etiqueta": "Modelo todavía no revisado",
        "badge_class": "badge-no-revisado",
        "bg": "#0f172a",
        "color": "#64748b",
        "icono": "⏳",
        "descripcion": "El expediente técnico de este modelo está en proceso de recopilación y verificación documental.",
    },
    "FUENTE_INACCESIBLE": {
        "etiqueta": "Fuente temporalmente inaccesible",
        "badge_class": "badge-inaccesible",
        "bg": "#831843",
        "color": "#fbcfe8",
        "icono": "📡",
        "descripcion": "Una o más fuentes oficiales no pudieron ser consultadas en la última actualización; se conservan los datos anteriores.",
    },
    "ALCANCE_NO_CONFIRMADO": {
        "etiqueta": "Alcance en Argentina no confirmado",
        "badge_class": "badge-alcance-pendiente",
        "bg": "#431407",
        "color": "#fed7aa",
        "icono": "📍",
        "descripcion": "Existe un aviso en otro mercado cuyo alcance o vigencia en Argentina no fue confirmado por el canal local.",
    },
    "EXCLUIDO": {
        "etiqueta": "Variante excluida expresamente",
        "badge_class": "badge-excluido",
        "bg": "#1e293b",
        "color": "#38bdf8",
        "icono": "—",
        "descripcion": "El aviso oficial exceptúa de manera explícita esta variante o código regional específico.",
    },
}

def evidencia_negativa_completa(fc):
    ev = fc.get("evidencia_consulta")
    if not isinstance(ev, dict):
        return False
    digest = ev.get("captura_sha256", "")
    return (isinstance(digest, str) and len(digest) == 64
            and all(c in "0123456789abcdef" for c in digest) and captura_verificable(digest)
            and bool(ev.get("url")) and bool(ev.get("modelos_consultados"))
            and bool(ev.get("metodo")) and bool(ev.get("revisado_por"))
            and ev.get("resultado") == "SIN_COINCIDENCIAS")


def derivar_estado_expediente(alertas: List[Dict[str, Any]], fuentes_consultadas: List[Dict[str, Any]]) -> str:
    """
    Deriva el estado general del expediente a partir de sus alertas aprobadas y fuentes.
    Nunca fuerza ciegamente ALERTA_OFICIAL si solo hay coincidencias potenciales o alcance no confirmado.
    """
    if not fuentes_consultadas and not alertas:
        return "NO_REVISADO"

    alcances = [a.get("estado_alcance") for a in alertas]
    if "ALERTA_OFICIAL" in alcances:
        return "ALERTA_OFICIAL"
    if "ALCANCE_NO_CONFIRMADO" in alcances:
        return "ALCANCE_NO_CONFIRMADO"
    if "POSIBLE_COINCIDENCIA" in alcances:
        return "POSIBLE_COINCIDENCIA"
    if alcances and all(a == "EXCLUIDO" for a in alcances):
        return "EXCLUIDO"

    # Verificar si alguna fuente de la ficha falló
    if any(fc.get("estado") == "FALLIDA" for fc in fuentes_consultadas):
        return "FUENTE_INACCESIBLE"

    fuentes_seguridad = [fc for fc in fuentes_consultadas if fuente_clave(fc.get("fuente", ""))]
    if not fuentes_seguridad or any(
        fc.get("estado") != "EXITOSA" or not fc.get("fecha_consulta")
        or not fc.get("resultado") or not evidencia_negativa_completa(fc)
        for fc in fuentes_seguridad
    ):
        return "NO_REVISADO"
    return "SIN_ALERTAS"


@lectura_serializada
def cargar_expedientes(forzar_recarga: bool = False) -> List[Dict[str, Any]]:
    """Lee el snapshot actual, observando cambios de otros procesos."""

    data = leer_documento('modelos_expedientes.json', [])

    for exp in data:
        exp['editor_responsable'] = EDITOR_RESPONSABLE
        # Un código por entidad: las listas con barras no son códigos comerciales.
        variantes = []
        for variante in exp.get('variantes', []):
            for codigo in variante['codigo'].split(' / '):
                item = dict(variante, codigo=codigo)
                variantes.append(item)
        exp['variantes'] = variantes
        validar_expediente(exp)

    return data


@serializado
def guardar_expedientes(expedientes: List[Dict[str, Any]]) -> None:
    guardar_estado(expedientes=expedientes)


def obtener_expediente(slug: str) -> Optional[Dict[str, Any]]:
    """Busca un expediente por su slug canónico."""
    for exp in cargar_expedientes():
        if exp["slug"] == slug:
            return exp
    return None


def obtener_todos_los_slugs() -> List[str]:
    """Retorna la lista ordenada de slugs de expedientes disponibles."""
    return sorted(exp["slug"] for exp in cargar_expedientes())


def buscar_expedientes(
    query: Optional[str] = None,
    marca: Optional[str] = None,
    estado: Optional[str] = None,
    categoria: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Filtra los expedientes por búsqueda textual tokenizada (marca, modelo base,
    sufijos regionales, códigos de barras o EAN, categorías) y filtros estructurados.
    """
    resultados = []
    q_norm = (query or "").strip().lower()
    tokens = q_norm.split() if q_norm else []

    for exp in cargar_expedientes():
        if marca and exp["marca"].lower() != marca.lower():
            continue
        if estado and exp["estado_general"] != estado:
            continue
        if categoria and exp["categoria"].lower() != categoria.lower():
            continue

        if not tokens:
            resultados.append(exp)
            continue

        # Campos evaluados en el corpus
        textos = [
            exp["marca"],
            exp["modelo_base"],
            exp["nombre_comercial"],
            exp["categoria"],
            exp["slug"],
            exp.get("resumen_editorial", ""),
        ]
        for v in exp.get("variantes", []):
            textos.extend([
                v.get("codigo", ""),
                v.get("codigo_barras", ""),
                v.get("tipo_revision", ""),
                v.get("mercado", ""),
            ])
        for a in exp.get("alertas", []):
            textos.extend([
                a.get("id_aviso", ""),
                a.get("organismo", ""),
                a.get("modelos_afectados", ""),
                a.get("identificacion_lotes_series", ""),
            ])

        corpus = " ".join(t.lower() for t in textos if t)
        # Todos los tokens deben coincidir en el corpus
        if all(token in corpus for token in tokens):
            resultados.append(exp)

    return resultados


def validar_expediente(exp: Dict[str, Any]) -> None:
    """Verifica que el expediente cumpla con la estructura y rigurosidad obligatorias."""
    campos_obligatorios = [
        "slug",
        "marca",
        "modelo_base",
        "nombre_comercial",
        "categoria",
        "estado_general",
        "revisado_por",
        "fecha_revision",
        "variantes",
        "documentacion",
        "alertas",
        "fuentes_consultadas",
    ]
    for c in campos_obligatorios:
        if c not in exp:
            raise ValueError(f"Expediente '{exp.get('slug')}' carece del campo obligatorio '{c}'")

    if exp["estado_general"] not in ESTADOS_ALERTA:
        raise ValueError(
            f"Estado desconocido '{exp['estado_general']}' en expediente '{exp['slug']}'"
        )

    if not isinstance(exp["variantes"], list) or not exp["variantes"]:
        raise ValueError(f"Expediente '{exp['slug']}' debe tener al menos una variante identificada")

    for v in exp["variantes"]:
        if "codigo" not in v or "mercado" not in v:
            raise ValueError(f"Variante inválida en expediente '{exp['slug']}': falta codigo o mercado")

    for al in exp.get("alertas", []):
        if al.get("estado_alcance") not in {"ALERTA_OFICIAL", "POSIBLE_COINCIDENCIA", "ALCANCE_NO_CONFIRMADO", "EXCLUIDO"}:
            raise ValueError("Alcance de alerta inválido: no se admiten estados de consulta")
        # Rechazar falsas alertas generadas a partir de resultados negativos
        if "SIN-COINCIDENCIA" in al.get("id_aviso", ""):
            raise ValueError(
                f"Expediente '{exp['slug']}' contiene una falsa alerta negativa ({al.get('id_aviso')}). "
                "Los resultados negativos deben documentarse en fuentes_consultadas, no en la lista de alertas."
            )

        for ac in [
            "id_aviso",
            "organismo",
            "pais_mercado",
            "fecha",
            "estado_alcance",
            "modelos_afectados",
            "defecto_riesgo",
            "accion_oficial",
            "enlace_original",
            "identificacion_lotes_series",
            "excepciones_expresas",
            "evidencia_fuente",
        ]:
            if ac not in al:
                raise ValueError(f"Alerta en expediente '{exp['slug']}' carece de '{ac}'")

        ev = al.get("evidencia_fuente", {})
        if not isinstance(ev, dict) or not ev.get("url") or not ev.get("revisado_por"):
            raise ValueError(f"Alerta '{al.get('id_aviso')}' en '{exp['slug']}' carece de evidencia_fuente válida")

    for fc in exp.get("fuentes_consultadas", []):
        if "fuente" not in fc or "fecha_consulta" not in fc or "estado" not in fc:
            raise ValueError(f"Fuente consultada en '{exp['slug']}' incompleta")


@lectura_serializada
def cargar_candidatos() -> List[Dict[str, Any]]:
    """Carga los candidatos pendientes de revisión editorial."""
    return leer_documento('candidatos_revision.json', [])


@serializado
def guardar_candidatos(candidatos: List[Dict[str, Any]]) -> None:
    guardar_estado(candidatos=candidatos)


@lectura_serializada
def cargar_registro_fuentes() -> Dict[str, Any]:
    """Carga el estado e historial de consultas a fuentes externas."""
    return leer_documento('registro_fuentes.json', {})


@serializado
def guardar_registro_fuentes(registro: Dict[str, Any]) -> None:
    guardar_estado(registro=registro)


def fuente_clave(nombre):
    nombre = nombre.lower()
    if "cpsc" in nombre:
        return "cpsc"
    if "sernac" in nombre:
        return "sernac_cl"
    if "defensa" in nombre:
        return "defensa_consumidor_ar"
    return None


def expediente_publico(exp):
    """Combina antecedentes editoriales y salud de consultas sin inventar revisiones."""
    exp = copy.deepcopy(exp)
    registro = cargar_registro_fuentes()
    avisos = []
    from alertas_operacion import edad_horas
    antiguedad = edad_horas(exp.get('fecha_revision'))
    if antiguedad is not None and antiguedad > 90 * 24:
        avisos.append('La revisión editorial tiene más de 90 días y requiere revalidación. Los avisos históricos se conservan.')
    if registro.get('operacion', {}).get('estado') == 'parcial':
        avisos.append('La última recolección diaria quedó incompleta. Consulte el estado del servicio y la cobertura de cada fuente.')
    for fc in exp.get("fuentes_consultadas", []):
        key = fuente_clave(fc["fuente"])
        info = registro.get(key, {})
        if key == "cpsc":
            # Cada búsqueda tiene su propio alcance: un fallo DeWalt no revisa Makita.
            consultas = info.get("consultas", {})
            info = consultas.get(exp["marca"].lower(), info if not consultas else {})
        fc["ultimo_intento_automatico"] = info.get("ultima_consulta")
        fc["ultimo_exito_automatico"] = info.get("ultimo_exito")
        if info.get("estado") == "FALLIDA":
            avisos.append(f"{fc['fuente']}: último intento de actualización fallido ({info.get('ultima_consulta', 'fecha no disponible')}). Se conserva la consulta editorial del {fc['fecha_consulta']}.")
            fc["estado_actualizacion"] = "FALLIDA"
        antiguedad_consulta = edad_horas(info.get('ultimo_exito'))
        if antiguedad_consulta is not None and antiguedad_consulta > 48:
            avisos.append(f"{fc['fuente']}: han transcurrido más de 48 horas desde la última consulta automática exitosa; actualización pendiente.")
            fc['estado_actualizacion'] = 'VENCIDA'
        if info.get("trazabilidad") == "SIN_CAPTURA":
            avisos.append(f"{fc['fuente']}: antecedente editorial sin captura archivada; pendiente de revalidación documental.")
    candidatos = { (fuente_clave(c["fuente"]), str(c["id_externo"])): c for c in cargar_candidatos() }
    for al in exp.get("alertas", []):
        ev = al.get("evidencia_fuente", {})
        if ev.get("captura_estado") == "PENDIENTE":
            avisos.append(f"{al['organismo']}: no se pudo archivar la publicación del aviso {al['id_aviso']} en esta revisión. Se conserva el antecedente editorial y su enlace oficial; la captura está pendiente.")
        cand = candidatos.get(identidad_alerta(al))
        if cand and cand.get("version_fuente") != al.get("evidencia_fuente", {}).get("version_fuente"):
            avisos.append(f"{al['organismo']}: hay una captura del aviso {cand['id_externo']} pendiente de cotejo con la versión publicada. Se conserva el texto editorial anterior.")
    exp["avisos_actualizacion"] = list(dict.fromkeys(avisos))
    derivado = derivar_estado_expediente(exp.get("alertas", []), exp.get("fuentes_consultadas", []))
    if not exp.get("alertas"):
        exp["estado_general"] = derivado
        if any(fc.get("estado_actualizacion") == "FALLIDA" for fc in exp.get("fuentes_consultadas", [])):
            exp["estado_general"] = "FUENTE_INACCESIBLE"
    return exp


def identidad_alerta(al):
    ref = al.get("referencia_ingestion", {})
    key = ref.get("fuente") or fuente_clave(al.get("organismo", ""))
    identificador = str(ref.get("id_externo") or al.get("id_aviso", ""))
    if key == "cpsc":
        identificador = identificador.removeprefix("CPSC-")
    return key, identificador
