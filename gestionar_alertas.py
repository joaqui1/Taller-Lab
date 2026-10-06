"""
Herramienta de línea de comandos para la gestión editorial de alertas y expedientes técnicos.
Permite sincronizar fuentes oficiales, revisar candidatos pendientes, aprobar alertas
con alcance delimitado y auditar la integridad de la base.
"""

from __future__ import annotations

import argparse
import json
import copy
from alertas_almacen import serializado, guardar_estado, archivar_payload
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import alertas_datos
from alertas_almacen import captura_verificable, leer_captura

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from alertas_datos import (
    ESTADOS_ALERTA,
    identidad_alerta,
    fuente_clave,
    cargar_candidatos,
    cargar_expedientes,
    cargar_registro_fuentes,
    derivar_estado_expediente,
    guardar_candidatos,
    guardar_expedientes,
    obtener_expediente,
    validar_expediente,
)
from sincronizador_alertas import (
    sincronizar_cpsc,
    sincronizar_defensa_consumidor,
)


def cmd_estado(args: argparse.Namespace) -> None:
    """Muestra el estado general del subsistema de alertas."""
    expedientes = cargar_expedientes()
    candidatos = cargar_candidatos()
    fuentes = cargar_registro_fuentes()

    print("=" * 60)
    print("TALLERLAB — ESTADO DE EXPEDIENTES TÉCNICOS Y ALERTAS")
    print("=" * 60)
    print(f"Total de modelos con expediente técnico: {len(expedientes)}")
    conteo_estados = {}
    for exp in expedientes:
        est = exp["estado_general"]
        conteo_estados[est] = conteo_estados.get(est, 0) + 1

    for est_k, info in ESTADOS_ALERTA.items():
        n = conteo_estados.get(est_k, 0)
        print(f"  {info['icono']} {info['etiqueta']}: {n}")

    print("\nModelos disponibles:")
    for exp in expedientes:
        print(f"  • [{exp['slug']}] {exp['marca']} {exp['modelo_base']} — Estado: {exp['estado_general']} (Variantes: {len(exp['variantes'])}, Alertas: {len(exp['alertas'])})")

    pendientes = [c for c in candidatos if c.get("estado_revision") in ("PENDIENTE", "MODIFICADO_PENDIENTE")]
    print(f"\nCola de candidatos para revisión editorial: {len(pendientes)} pendientes de {len(candidatos)} totales.")

    print("\nEstado de fuentes de información:")
    for fk, finfo in fuentes.items():
        print(f"  • {finfo.get('nombre', fk)}:")
        print(f"    Estado: {finfo.get('estado')} | Última consulta: {finfo.get('ultima_consulta')}")
        if finfo.get("error_reciente"):
            print(f"    ⚠️ Error reciente: {finfo.get('error_reciente')}")
    print("=" * 60)


def cmd_sync_cpsc(args: argparse.Namespace) -> None:
    """Ejecuta la sincronización con la API de CPSC."""
    query = args.query or "DeWalt"
    print(f"Consultando CPSC API (término: '{query}')...")
    res = sincronizar_cpsc(termino_busqueda=query)
    if res["exito"]:
        print(f"✓ Éxito. Recibidos: {res['total_recibidos']} | Nuevos: {res['nuevos']} | Modificados: {res['modificados']} | Sin cambios: {res['sin_cambios']}")
    else:
        print(f"✗ Error al consultar CPSC: {res['error']}")
        print("  (Los datos previos se conservaron y la fuente quedó marcada como contingente)")
        sys.exit(1)


def cmd_sync_argentina(args: argparse.Namespace) -> None:
    """Ejecuta la sincronización con el dataset de Defensa del Consumidor Argentina."""
    print("Consultando dataset oficial de Defensa del Consumidor (Argentina)...")
    res = sincronizar_defensa_consumidor()
    if res["exito"]:
        print(f"✓ Éxito. Filas analizadas: {res['total_filas_revisadas']} | Nuevas alertas detectadas: {res['nuevos']} | Modificadas: {res['modificados']}")
    else:
        print(f"✗ Error al consultar dataset argentino: {res['error']}")
        print("  (Los datos previos se conservaron y la fuente quedó marcada como contingente)")
        sys.exit(1)


def cmd_listar_candidatos(args: argparse.Namespace) -> None:
    """Lista los candidatos en la cola de revisión."""
    candidatos = cargar_candidatos()
    estado_filtro = args.estado.upper() if args.estado else None
    filtrados = [c for c in candidatos if (estado_filtro is None or c.get("estado_revision") == estado_filtro)]

    print(f"Candidatos encontrados ({len(filtrados)}):")
    for c in filtrados:
        print("-" * 50)
        print(f"ID: {c['id']} | Fuente: {c['fuente']} | Estado: {c['estado_revision']}")
        print(f"Título: {c.get('titulo')}")
        print(f"Fecha del aviso: {c.get('fecha_aviso')} | Detectado: {c.get('fecha_deteccion')}")
        print(f"Modelo sugerido: {c.get('coincidencia_modelo')} ({c.get('motivo_coincidencia')})")
        if c.get("coincidencias_adicionales"):
            print(f"Otros modelos coincidentes: {', '.join(c['coincidencias_adicionales'])}")
        print(f"Enlace: {c.get('enlace_original')}")
        resumen = c.get("resumen", {})
        if isinstance(resumen, dict):
            for rk, rv in resumen.items():
                if rv:
                    print(f"  {rk}: {rv}")


@serializado
def cmd_aprobar_candidato(args: argparse.Namespace) -> None:
    """
    Aprueba un candidato y lo incorpora como alerta en el expediente de un modelo.
    Exige mercado real, valida riesgos documentados, no inventa acciones oficiales,
    evita duplicados y deriva el estado general a partir de las alertas aprobadas.
    """
    candidatos = cargar_candidatos()
    cand = next((c for c in candidatos if c["id"] == args.cand_id), None)
    if not cand:
        print(f"Error: No se encontró candidato con ID '{args.cand_id}'")
        sys.exit(1)

    slug = args.slug or cand.get("coincidencia_modelo")
    if not slug:
        print("Error: Debe especificar --slug para asociar el candidato a un modelo.")
        sys.exit(1)

    expediente = copy.deepcopy(obtener_expediente(slug))
    if not expediente:
        print(f"Error: No existe el expediente con slug '{slug}'")
        sys.exit(1)

    # Cada afirmación de alcance exige una decisión expresa del revisor.
    requeridos = {"modelos": args.modelos, "lotes": args.lotes,
                  "excepciones": args.excepciones, "revisado-por": args.revisado_por}
    faltantes = [key for key, value in requeridos.items() if not value or not value.strip()]
    if faltantes:
        print("Error: Cotejo incompleto. Complete " + ", ".join("--" + key for key in faltantes)
              + ". Si la fuente no informa un campo, indíquelo expresamente tras revisarla.")
        sys.exit(1)
    permitidos = {"ALERTA_OFICIAL", "POSIBLE_COINCIDENCIA", "ALCANCE_NO_CONFIRMADO", "EXCLUIDO"}
    if args.alcance and args.alcance not in permitidos:
        print("Error: El estado de una consulta no es un alcance de alerta.")
        sys.exit(1)
    if not cand.get("payload_original") or not cand.get("enlace_original"):
        print("Error: Falta el registro original o la URL para documentar la aprobación.")
        sys.exit(1)

    # 1. Determinación de país / mercado (nunca asumir Argentina por defecto)
    pais_mercado = args.pais_mercado
    if not pais_mercado:
        fuente_raw = cand.get("fuente", "").lower()
        if "cpsc" in fuente_raw:
            pais_mercado = "Estados Unidos"
        elif "sernac" in fuente_raw:
            pais_mercado = "Chile"
        elif "defensa" in fuente_raw or "argentina" in fuente_raw:
            pais_mercado = "Argentina"
        else:
            print("Error: Debe especificar el mercado geográfico mediante --pais-mercado (ej. 'Estados Unidos', 'Argentina', 'Chile').")
            sys.exit(1)

    origen = fuente_clave(cand.get('fuente', ''))
    mercado_origen = {'cpsc': 'Estados Unidos', 'sernac_cl': 'Chile',
                      'defensa_consumidor_ar': 'Argentina'}.get(origen)
    if mercado_origen and pais_mercado != mercado_origen:
        print('Error: No se puede cambiar el mercado de la fuente. Documente el alcance argentino en una campaña local separada.')
        sys.exit(1)
    parsed_source = urlparse(cand['enlace_original'])
    official = {'cpsc': {'www.cpsc.gov', 'www.saferproducts.gov'}, 'sernac_cl': {'www.sernac.cl'},
                'defensa_consumidor_ar': {'www.argentina.gob.ar', 'docs.google.com'}}
    source_key = fuente_clave(cand.get('fuente', ''))
    if source_key in official and (parsed_source.scheme != 'https' or parsed_source.hostname not in official[source_key]):
        print('Error: La publicación debe tener una URL HTTPS de la fuente oficial.')
        sys.exit(1)

    # 2. Determinación de alcance territorial
    if args.alcance:
        estado_alcance = args.alcance
    else:
        # Avisos extranjeros sin confirmación expresa de canal local en Argentina se catalogan como POSIBLE_COINCIDENCIA
        if pais_mercado in ("Estados Unidos", "Chile"):
            estado_alcance = "POSIBLE_COINCIDENCIA"
        else:
            estado_alcance = "ALERTA_OFICIAL"

    # 3. Extracción y validación estricta de defectos y riesgos
    defecto_riesgo = args.defecto
    if not defecto_riesgo:
        resumen = cand.get("resumen") or {}
        riesgos = resumen.get("riesgos")
        defecto = resumen.get("defecto") or (cand.get("payload_original") or {}).get("Description")

        partes_riesgo = []
        if defecto and isinstance(defecto, str) and defecto.strip():
            partes_riesgo.append(defecto.strip())
        if isinstance(riesgos, list):
            partes_riesgo.extend(r.strip() for r in riesgos if r and isinstance(r, str) and r.strip())
        elif isinstance(riesgos, str) and riesgos.strip():
            partes_riesgo.append(riesgos.strip())

        defecto_riesgo = ". ".join(partes_riesgo)

    if not defecto_riesgo or not defecto_riesgo.strip():
        print("Error: No se puede aprobar una alerta sin descripción de defecto/riesgo documentada en la fuente oficial. Especifique --defecto.")
        sys.exit(1)

    # 4. Extracción honesta de acción oficial (no inventar 'Consultar al servicio oficial')
    accion_oficial = args.accion
    if not accion_oficial:
        resumen = cand.get("resumen") or {}
        medidas = resumen.get("medidas")
        if isinstance(medidas, list) and medidas:
            accion_oficial = " ".join(m.strip() for m in medidas if m and isinstance(m, str) and m.strip())
        elif isinstance(medidas, str) and medidas.strip():
            accion_oficial = medidas.strip()
        elif "Defensa" in cand.get("fuente", ""):
            accion_oficial = "No informada en la planilla oficial de Defensa del Consumidor; verificar con servicio técnico oficial."
        else:
            print("Error: No se cotejó la acción oficial. Especifique --accion tras consultar la fuente.")
            sys.exit(1)

    if origen in ('cpsc', 'sernac_cl') and estado_alcance == 'ALERTA_OFICIAL':
        # Confirmación del aviso en su mercado, sin extrapolar el alcance argentino.
        pais_mercado = mercado_origen

    # 5. Construir alerta estructurada con campos completos de trazabilidad
    id_aviso = cand["id_externo"]
    revisado_por = args.revisado_por
    version = archivar_payload(cand["payload_original"])

    nueva_alerta = {
        "id_aviso": id_aviso,
        "organismo": cand["fuente"],
        "pais_mercado": pais_mercado,
        "fecha": str(cand.get("fecha_aviso", ""))[:10],
        "estado_alcance": estado_alcance,
        "tipo_aviso": cand.get("tipo_aviso", "Aviso de seguridad"),
        "modelos_afectados": args.modelos,
        "identificacion_lotes_series": args.lotes,
        "periodo_comercializacion": args.periodo or "Período pendiente de cotejo documental.",
        "ubicacion_identificador": args.ubicacion or "Ubicación del identificador pendiente de cotejo documental.",
        "unidades_involucradas": args.unidades or "Cantidad pendiente de cotejo documental.",
        "excepciones_expresas": args.excepciones,
        "defecto_riesgo": defecto_riesgo.strip(),
        "accion_oficial": accion_oficial.strip(),
        "enlace_original": cand.get("enlace_original", ""),
        "evidencia_fuente": {
            "url": cand.get("enlace_original", ""),
            "version_fuente": version,
            "consulta": cand.get("consulta", {}),
            "revisado_por": revisado_por,
            "cotejo_contra_registro": f"Aprobado desde candidato {cand['id']} ({cand['fuente']})",
            "fecha_extraccion": cand.get("fecha_deteccion", datetime.now(timezone.utc).isoformat()),
        },
    }

    # 6. Idempotencia: actualizar alerta existente si ya fue aprobada antes
    alertas = expediente.setdefault("alertas", [])
    actualizada = False
    for i_al, al in enumerate(alertas):
        if identidad_alerta(al) == (fuente_clave(cand["fuente"]), str(id_aviso)):
            alertas[i_al] = nueva_alerta
            actualizada = True
            break
    if not actualizada:
        alertas.append(nueva_alerta)

    # 7. Derivar estado general del expediente rigurosamente
    expediente["estado_general"] = derivar_estado_expediente(
        expediente["alertas"],
        expediente.get("fuentes_consultadas", []),
    )
    expediente["fecha_revision"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expediente["revisado_por"] = revisado_por
    expediente['editor_responsable'] = alertas_datos.EDITOR_RESPONSABLE
    expediente.setdefault('historial_editorial', []).append({
        'fecha': datetime.now(timezone.utc).isoformat(), 'revisado_por': revisado_por,
        'aviso': id_aviso, 'version_fuente': version, 'accion': 'actualizacion' if actualizada else 'incorporacion'})

    # Validar que cumpla la especificación técnica completa
    validar_expediente(expediente)

    cand.setdefault("aprobaciones", {})[slug] = {
        "version_fuente": version, "revisado_por": revisado_por,
        "fecha": datetime.now(timezone.utc).isoformat(),
    }
    modelos = set(cand.get("coincidencias_adicionales") or [])
    modelos.add(cand.get("coincidencia_modelo") or slug)
    cand["modelos_pendientes"] = sorted(m for m in modelos
        if cand["aprobaciones"].get(m, {}).get("version_fuente") != version)
    cand["estado_revision"] = "PENDIENTE" if cand["modelos_pendientes"] else "APROBADO"
    cand["notas_editoriales"] = f"{'Re-aprobado' if actualizada else 'Aprobado'} e incorporado a {slug} el {expediente['fecha_revision']}"

    expedientes = cargar_expedientes()
    for idx, e in enumerate(expedientes):
        if e["slug"] == slug:
            expedientes[idx] = expediente
            break

    guardar_estado(expedientes=expedientes, candidatos=candidatos)
    accion_txt = "actualizado" if actualizada else "incorporado"
    print(f"✓ Candidato '{args.cand_id}' aprobado y {accion_txt} con éxito en '{slug}' (Estado derivado: {expediente['estado_general']}).")


@serializado
def cmd_descartar_candidato(args: argparse.Namespace) -> None:
    """Descarta un candidato con justificación editorial."""
    candidatos = cargar_candidatos()
    cand = next((c for c in candidatos if c["id"] == args.cand_id), None)
    if not cand:
        print(f"Error: No se encontró candidato con ID '{args.cand_id}'")
        sys.exit(1)

    cand["estado_revision"] = "DESCARTADO"
    cand["notas_editoriales"] = args.motivo or "Descartado tras revisión editorial por no corresponder al alcance."
    guardar_candidatos(candidatos)
    print(f"✓ Candidato '{args.cand_id}' marcado como descartado.")


@serializado
def cmd_registrar_consulta(args):
    """Registra una conclusión negativa editorial con captura y alcance explícitos."""
    expediente = obtener_expediente(args.slug)
    if not expediente or not captura_verificable(args.captura):
        raise SystemExit("Expediente inexistente o captura ausente/corrupta")
    captura = leer_captura(args.captura)
    dominios = {"cpsc": {"www.cpsc.gov", "www.saferproducts.gov"},
                "sernac_cl": {"www.sernac.cl"},
                "defensa_consumidor_ar": {"docs.google.com", "www.argentina.gob.ar"}}
    url = captura.get("url", "")
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in dominios[args.fuente] or not captura.get("contenido"):
        raise SystemExit("La captura debe contener la respuesta y URL HTTPS de la fuente oficial seleccionada")
    if not args.revisado_por.strip() or not args.metodo.strip():
        raise SystemExit("Debe identificar al revisor y describir método, filtros y límites del relevamiento")
    codigos = {v["codigo"] for v in expediente["variantes"]} | {expediente["modelo_base"]}
    if not codigos.issubset(set(args.modelos)):
        raise SystemExit("La conclusión de esta ficha requiere cotejar el modelo base y todas sus variantes registradas")
    if any(identidad_alerta(a)[0] == args.fuente and a["estado_alcance"] != "EXCLUIDO"
           for a in expediente.get("alertas", [])):
        raise SystemExit("Hay una alerta publicada de esa fuente: no puede registrarse una conclusión negativa")
    ahora = datetime.now(timezone.utc).isoformat()
    ev = {"captura_sha256": args.captura, "url": url, "metodo": args.metodo,
          "modelos_consultados": args.modelos, "revisado_por": args.revisado_por,
          "resultado": "SIN_COINCIDENCIAS", "fecha_revision": ahora}
    fuente = next((f for f in expediente["fuentes_consultadas"]
                   if fuente_clave(f["fuente"]) == args.fuente), None)
    if fuente is None:
        raise SystemExit("La fuente no está configurada en este expediente")
    fuente.update(estado="EXITOSA", fecha_consulta=ahora, evidencia_consulta=ev,
                  resultado=f"Sin coincidencias para {', '.join(args.modelos)} según el relevamiento descrito: {args.metodo}")
    expediente["estado_general"] = derivar_estado_expediente(expediente["alertas"], expediente["fuentes_consultadas"])
    expediente["fecha_revision"] = ahora[:10]
    expediente["revisado_por"] = args.revisado_por
    expedientes = cargar_expedientes()
    expedientes = [expediente if e["slug"] == expediente["slug"] else e for e in expedientes]
    guardar_estado(expedientes=expedientes)
    print("Consulta editorial registrada; la captura no demuestra cobertura fuera del método declarado.")


def cmd_auditar(args: argparse.Namespace) -> None:
    """Audita todos los expedientes técnicos y valida coherencia editorial."""
    expedientes = cargar_expedientes(forzar_recarga=True)
    errores = []

    print(f"Auditando {len(expedientes)} expedientes técnicos...")

    for exp in expedientes:
        try:
            validar_expediente(exp)
        except Exception as e:
            errores.append(f"[{exp.get('slug')}] Estructura inválida: {e}")

        # Reglas de exactitud
        slug = exp["slug"]
        for v in exp.get("variantes", []):
            if not v.get("codigo"):
                errores.append(f"[{slug}] Variante sin código")
            if not v.get("mercado"):
                errores.append(f"[{slug}] Variante {v.get('codigo')} sin mercado especificado")

        # Comprobar caso específico DW8307
        if slug == "dewalt-dw8307":
            exclusiones = [a.get("excepciones_expresas", "") for a in exp.get("alertas", [])]
            if not any("DW8307-AR" in exc for exc in exclusiones):
                errores.append("[dewalt-dw8307] DEBE documentar la exclusión expresa de DW8307-AR")

        # Comprobar caso específico DWS780
        if slug == "dewalt-dws780":
            organismos = {a.get("organismo") for a in exp.get("alertas", [])}
            if not {"SERNAC", "Defensa del Consumidor", "CPSC"}.issubset(organismos):
                errores.append("[dewalt-dws780] Debe incluir alertas de SERNAC, Defensa del Consumidor y CPSC")

        # Comprobar que SIN_ALERTAS no tenga alertas activas incompatibles
        if exp["estado_general"] == "SIN_ALERTAS":
            alertas_activas = [a for a in exp.get("alertas", []) if a.get("estado_alcance") == "ALERTA_OFICIAL"]
            if alertas_activas:
                errores.append(f"[{slug}] Estado marcado como SIN_ALERTAS pero contiene alertas oficiales activas")

    if errores:
        print(f"✗ Se encontraron {len(errores)} inconsistencias:")
        for err in errores:
            print(f"  • {err}")
        sys.exit(1)
    else:
        print(f"✓ Todos los {len(expedientes)} expedientes pasaron la auditoría editorial rigurosa.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gestor editorial de alertas y expedientes de TallerLab")
    subparsers = parser.add_subparsers(dest="comando", help="Comando a ejecutar")

    # estado
    subparsers.add_parser("estado", help="Resumen del estado de expedientes y fuentes")

    # sync-cpsc
    p_cpsc = subparsers.add_parser("sync-cpsc", help="Sincronizar avisos desde la API de CPSC")
    p_cpsc.add_argument("--query", "-q", default="DeWalt", help="Término o marca a buscar")

    # sync-argentina
    subparsers.add_parser("sync-argentina", help="Sincronizar dataset de Defensa del Consumidor Argentina")

    # listar-candidatos
    p_list = subparsers.add_parser("listar-candidatos", help="Listar candidatos de alerta pendientes")
    p_list.add_argument("--estado", "-e", choices=["PENDIENTE", "MODIFICADO_PENDIENTE", "APROBADO", "DESCARTADO"], help="Filtrar por estado")

    # aprobar-candidato
    p_aprob = subparsers.add_parser("aprobar-candidato", help="Aprobar candidato e incorporarlo a un expediente")
    p_aprob.add_argument("cand_id", help="ID del candidato")
    p_aprob.add_argument("--slug", "-s", help="Slug del modelo objetivo")
    p_aprob.add_argument("--alcance", "-a", choices=["ALERTA_OFICIAL", "POSIBLE_COINCIDENCIA", "ALCANCE_NO_CONFIRMADO", "EXCLUIDO"], help="Estado de alcance (por defecto infiere según origen)")
    p_aprob.add_argument("--pais-mercado", "-p", help="País o mercado afectado (por defecto infiere según origen)")
    p_aprob.add_argument("--modelos", "-m", help="Texto de modelos afectados")
    p_aprob.add_argument("--lotes", "-l", help="Texto de lotes o códigos")
    p_aprob.add_argument("--periodo", help="Período de comercialización")
    p_aprob.add_argument("--ubicacion", help="Ubicación del identificador o etiqueta")
    p_aprob.add_argument("--unidades", help="Número de unidades involucradas")
    p_aprob.add_argument("--excepciones", "-x", help="Excepciones expresas")
    p_aprob.add_argument("--defecto", "-d", help="Descripción del defecto y riesgos")
    p_aprob.add_argument("--accion", help="Acción oficial recomendada")
    p_aprob.add_argument("--revisado-por", help="Nombre del revisor editorial")

    # descartar-candidato
    p_desc = subparsers.add_parser("descartar-candidato", help="Descartar un candidato")
    p_desc.add_argument("cand_id", help="ID del candidato")
    p_desc.add_argument("--motivo", "-m", default="No aplica al alcance", help="Motivo del descarte")

    # auditar
    subparsers.add_parser("auditar", help="Auditar consistencia de expedientes técnicos")
    p_consulta = subparsers.add_parser("registrar-consulta", help="Registrar revisión editorial sin coincidencias con captura verificable")
    p_consulta.add_argument("--slug", required=True)
    p_consulta.add_argument("--fuente", choices=["cpsc", "sernac_cl", "defensa_consumidor_ar"], required=True)
    p_consulta.add_argument("--captura", required=True, help="SHA-256 de la respuesta oficial archivada")
    p_consulta.add_argument("--modelos", nargs="+", required=True)
    p_consulta.add_argument("--metodo", required=True, help="Método, filtros, período y límites de la consulta")
    p_consulta.add_argument("--revisado-por", required=True)

    args = parser.parse_args()
    if not args.comando:
        parser.print_help()
        sys.exit(0)

    comandos = {
        "registrar-consulta": cmd_registrar_consulta,
        "estado": cmd_estado,
        "sync-cpsc": cmd_sync_cpsc,
        "sync-argentina": cmd_sync_argentina,
        "listar-candidatos": cmd_listar_candidatos,
        "aprobar-candidato": cmd_aprobar_candidato,
        "descartar-candidato": cmd_descartar_candidato,
        "auditar": cmd_auditar,
    }

    comandos[args.comando](args)


if __name__ == "__main__":
    main()
