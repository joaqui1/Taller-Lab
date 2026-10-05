"""API operativa, mesa editorial y recursos públicos de alertas."""
import argparse
import csv
import hmac
import io
import json
import os
from html import escape
from flask import Blueprint, Response, request

from alertas_almacen import serializado, leer_captura
from alertas_datos import cargar_candidatos, cargar_expedientes, EDITOR_RESPONSABLE
from alertas_operacion import ejecutar, estado_publico
from alertas_persistencia import AlmacenOcupado

bp = Blueprint('alertas_operacion', __name__)


def json_response(data, status=200):
    return Response(json.dumps(data, ensure_ascii=False), status=status,
                    content_type='application/json; charset=utf-8', headers={'Cache-Control': 'no-store'})


def autorizado(editor=False):
    secret = os.getenv('ALERTAS_EDITOR_TOKEN') if editor else os.getenv('CRON_SECRET') or os.getenv('ALERTAS_MAINTENANCE_TOKEN')
    header = request.headers.get('Authorization', '')
    return bool(secret and header.startswith('Bearer ') and hmac.compare_digest(header[7:].encode('utf-8'), secret.encode('utf-8')))


def documento(title, content, noindex=False):
    from servidor_local import HTML_SHELL, canonical_tag, LOGO_SRC, PORT
    html = HTML_SHELL.format(PAGE_TITLE=escape(title.removesuffix(' · TallerLab')), PAGE_DESC=escape(title),
        CANONICAL_TAG=canonical_tag(request.path), PORT=PORT, LOGO_SRC=LOGO_SRC, CONTENT=content)
    return Response(html, content_type='text/html; charset=utf-8', headers={
        'X-Robots-Tag': 'noindex, follow' if noindex else 'index, follow', 'Cache-Control': 'no-store'})


@bp.route('/api/alertas/ejecutar', methods=['GET', 'POST'])
@bp.route('/api/alertas/historico', methods=['GET', 'POST'])
def cron():
    if not autorizado():
        return json_response({'error': 'No autorizado'}, 401)
    if request.args or request.get_data():
        return json_response({'error': 'La recolección no admite parámetros ni fuentes suministradas por el cliente'}, 400)
    try:
        result = ejecutar(historico=request.path.endswith('/historico'))
        return json_response(result, 200 if result['estado'] == 'correcto' else 503)
    except AlmacenOcupado:
        return json_response({'error': 'Recolección en curso'}, 409)
    except Exception:
        return json_response({'error': 'Revisar persistencia y registros de la recolección'}, 503)


@bp.route('/api/alertas/estado')
def status():
    try:
        return json_response(estado_publico())
    except Exception:
        return json_response({'estado': 'fuente_inaccesible', 'error': 'Estado del servicio temporalmente no disponible'}, 503)


@bp.route('/api/alertas/respaldos')
@bp.route('/api/alertas/respaldos/<fecha>')
def automatic_backups(fecha=None):
    if not autorizado(editor=True):
        return json_response({'error': 'No autorizado'}, 401)
    from alertas_respaldo import anteriores
    try:
        data = anteriores(fecha)
        if fecha is None:
            return json_response({'respaldos': data, 'ubicacion': 'misma_base', 'retencion_dias': 14})
        if data is None:
            return json_response({'error': 'Respaldo no encontrado'}, 404)
        return Response(data, content_type='application/zip', headers={'Cache-Control': 'no-store',
            'Content-Disposition': 'attachment; filename="tallerlab-alertas-'+fecha+'.zip"'})
    except ValueError:
        return json_response({'error': 'Fecha o integridad de respaldo inválida'}, 400)


@bp.route('/api/alertas/editorial')
def queue():
    if not autorizado(editor=True):
        return json_response({'error': 'No autorizado'}, 401)
    return json_response({'editor': EDITOR_RESPONSABLE, 'expedientes': [{'slug': e['slug'], 'modelo': e['modelo_base']} for e in cargar_expedientes()],
                          'candidatos': cargar_candidatos()})


@bp.route('/api/alertas/capturas/<digest>')
def snapshot(digest):
    if not autorizado(editor=True):
        return json_response({'error': 'No autorizado'}, 401)
    try:
        return json_response(leer_captura(digest))
    except (ValueError, OSError):
        return json_response({'error': 'Captura ausente o inválida'}, 404)


@bp.route('/api/alertas/respaldo')
def backup():
    if not autorizado(editor=True):
        return json_response({'error': 'No autorizado'}, 401)
    from alertas_respaldo import respaldo
    return Response(respaldo(), content_type='application/zip', headers={
        'Cache-Control': 'no-store', 'Content-Disposition': 'attachment; filename="tallerlab-alertas-respaldo.zip"'})


@serializado
def decidir(body):
    from gestionar_alertas import cmd_aprobar_candidato, cmd_descartar_candidato
    cand = next((c for c in cargar_candidatos() if c['id'] == body.get('id')), None)
    if not cand:
        return {'error': 'Candidato inexistente'}, 404
    if not body.get('version_fuente') or cand.get('version_fuente') != body['version_fuente']:
        return {'error': 'La fuente cambió. Vuelva a cargar y revisar la versión actual'}, 409
    if body.get('accion_editorial') == 'descartar':
        if not body.get('motivo', '').strip():
            return {'error': 'Explique el motivo del descarte'}, 400
        cmd_descartar_candidato(argparse.Namespace(cand_id=cand['id'], motivo=body['motivo']))
    elif body.get('accion_editorial') == 'aprobar':
        fields = ('slug', 'modelos', 'lotes', 'excepciones', 'periodo', 'ubicacion', 'unidades', 'defecto', 'accion', 'alcance', 'pais_mercado')
        values = {field: body.get(field) or None for field in fields}
        values.update(cand_id=cand['id'], revisado_por=EDITOR_RESPONSABLE)
        try:
            cmd_aprobar_candidato(argparse.Namespace(**values))
        except SystemExit:
            return {'error': 'Cotejo incompleto o mercado incompatible: revise modelos, lotes, excepciones, riesgo y acción oficial'}, 400
    else:
        return {'error': 'Decisión desconocida'}, 400
    return {'estado': 'guardado', 'editor': EDITOR_RESPONSABLE}, 200


@bp.route('/api/alertas/editorial/decision', methods=['POST'])
def decision():
    if not autorizado(editor=True):
        return json_response({'error': 'No autorizado'}, 401)
    if request.content_length is None or not 0 < request.content_length <= 32768:
        return json_response({'error': 'Solicitud demasiado grande o vacía'}, 400)
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or any(not isinstance(v, str) or len(v) > 8000 for v in body.values()):
        return json_response({'error': 'Los campos deben ser textos de hasta 8000 caracteres'}, 400)
    try:
        result, code = decidir(body)
        return json_response(result, code)
    except AlmacenOcupado:
        return json_response({'error': 'Otra operación está en curso; vuelva a intentar'}, 409)


@bp.route('/datos/alertas/avisos.json')
@bp.route('/datos/alertas/avisos.csv')
def export():
    rows = []
    for exp in cargar_expedientes():
        for al in exp['alertas']:
            rows.append({'modelo': exp['modelo_base'], 'slug': exp['slug'], 'aviso': al['id_aviso'],
                'mercado': al['pais_mercado'], 'alcance': al['estado_alcance'], 'fecha_aviso': al['fecha'],
                'modelos_afectados': al['modelos_afectados'], 'lotes': al['identificacion_lotes_series'],
                'excepciones': al['excepciones_expresas'], 'riesgo': al['defecto_riesgo'], 'accion': al['accion_oficial'],
                'fuente': al['enlace_original'], 'editor': EDITOR_RESPONSABLE,
                'version_fuente': al['evidencia_fuente'].get('version_fuente', ''),
                'revision_version': 'aprobada' if al['evidencia_fuente'].get('version_fuente') else 'cotejo_pendiente'})
    if request.path.endswith('.json'):
        return json_response({'editor': EDITOR_RESPONSABLE, 'metodologia': '/alertas/metodologia/',
            'alcance': 'Avisos publicados del catálogo de TallerLab; no registro exhaustivo ni certificación de seguridad', 'avisos': rows})
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader()
        # Neutralizar fórmulas al abrir el recurso en planillas.
        writer.writerows({k: "'"+str(v) if str(v).lstrip().startswith(('=', '+', '-', '@')) else v for k,v in row.items()} for row in rows)
    return Response(output.getvalue(), content_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="tallerlab-alertas.csv"'})


@bp.route('/alertas/estado/')
def estado_page():
    data = estado_publico()
    rows = ''.join(f"<tr><td>{escape(s['fuente'])}</td><td>{escape(s['estado'])}</td><td>{escape(s['ultimo_exito'] or 'Sin consulta registrada')}</td><td>{escape(s['cobertura'])}</td></tr>" for s in data['fuentes'])
    return documento('Estado de documentación y alertas · TallerLab', f'''<article class="markdown-body"><p><a href="/alertas/">← Documentación y alertas</a></p><h1>Estado del servicio</h1>
    <p>Editor responsable: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a>.</p><p>Estado: <strong>{escape(data['estado'])}</strong>. Última ejecución: {escape(data['ultima_ejecucion'] or 'Programación todavía no verificada')}.</p>
    <p>Almacenamiento: {escape(data['persistencia'])}. Origen de la última ejecución: {escape(data['entorno_ultima_ejecucion'])}.</p>
    <p>{data['expedientes']} expedientes · {data['pendientes_con_coincidencia']} candidatos relevantes pendientes de revisión.</p><table><thead><tr><th>Fuente</th><th>Consulta</th><th>Último éxito UTC</th><th>Cobertura</th></tr></thead><tbody>{rows}</tbody></table>
    <p>Una consulta automática no equivale a revisión humana. La ausencia de coincidencias no acredita seguridad.</p><p><a href="/alertas/metodologia/">Metodología y límites</a></p></article>''', noindex=True)


@bp.route('/alertas/metodologia/')
def metodologia():
    return documento('Metodología de documentación y alertas · TallerLab', '''<article class="markdown-body"><p><a href="/alertas/">← Expedientes</a></p><h1>Cómo investigamos documentación y alertas</h1>
    <p>Editor responsable: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a>. TallerLab es un servicio independiente de investigación documental.</p>
    <h2>Fuentes y cobertura</h2><p>Argentina: planilla enlazada por el registro nacional, filtrada por marcas y términos de herramientas. CPSC: novedades diarias por fecha de publicación y comprobación por número de las campañas conocidas; conciliación histórica de marcas en una tarea separada. SERNAC: seguimiento de las publicaciones citadas; no búsqueda de todas las alertas chilenas.</p>
    <h2>Actualización y publicación</h2><p>La tarea se programa diariamente en producción. Su activación y última consulta efectiva se muestran en el <a href="/alertas/estado/">estado del servicio</a>. Cada respuesta se archiva y los cambios se presentan como candidatos. Se conserva la versión publicada hasta revisar modelos, variantes, mercado, lotes, excepciones, riesgo y acción oficial.</p>
    <p>El editor aprueba una versión concreta. Una consulta fallida conserva el historial y deja una advertencia. Más de 48 horas sin consulta automática satisfactoria requiere atención; una revisión editorial de más de 90 días se señala para revalidación, sin eliminar avisos históricos.</p>
    <h2>Alcance argentino</h2><p>Los avisos conservan el mercado de su fuente. Una campaña extranjera no confirma alcance, garantía ni reparación gratuita en Argentina. Las equivalencias y exclusiones requieren evidencia explícita de la variante.</p>
    <h2>Recursos y correcciones</h2><p><a href="/datos/alertas/avisos.csv">Descargar CSV</a> · <a href="/datos/alertas/avisos.json">Consultar JSON</a>. Los recursos incluyen procedencia y estado de revisión. No son un registro completo de todos los productos ni una certificación. Cite la ficha, la fecha y la fuente original. Los derechos de documentos e imágenes originales corresponden a sus titulares.</p>
    <p><a href="/contacto/">Enviar una corrección</a>. Las correcciones sustantivas se registran con fecha, responsable y versión de la fuente. La fecha editorial no cambia por una descarga automática.</p></article>''')


@bp.route('/alertas/editorial/')
def mesa():
    from pathlib import Path
    return documento('Mesa editorial · TallerLab', Path(__file__).with_name('alertas_editorial.html').read_text(encoding='utf-8'), noindex=True)
