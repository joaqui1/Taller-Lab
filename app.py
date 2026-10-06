"""Entrada Flask para Vercel; reutiliza las mismas páginas del servidor local."""

import json
from datetime import timedelta
import os
import secrets
from pathlib import Path

from flask import Flask, Response, redirect, request, send_from_directory

from servidor_local import (
    ALL_ARTICLES,
    AUTHOR_PATH,
    ASSETS_DIR,
    CATEGORY_META,
    ALERTAS_PATHS,
    COMPATIBILITY_PATHS,
    COMPATIBILITY_SEARCH_PATH,
    COMPATIBILITY_DOWNLOAD_PATHS,
    TALLERLAB_DATA_PATHS,
    INDEXABLE_PATH_SET,
    OBSERVATORY_PATHS,
    export_compatibility_to_csv,
    export_compatibility_to_json,
    generate_study_csv,
    render_alertas_page,
    render_article_page,
    render_category_page,
    render_compatibility_page,
    render_tallerlab_data_page,
    render_home_page,
    render_editorial_page,
    render_feed,
    render_llms,
    render_not_found,
    render_observatory_page,
    render_relevamiento_view,
    render_robots,
    render_search_cards,
    render_sitemap,
    track_event,
    validate_affiliate_click,
    MaintenancePipeline,
    FAVICON_ICO,
)
from relevamiento_piloto import (
    ADMIN_KEY as RELEVAMIENTO_ADMIN_KEY,
    actualizar_estado_moderacion,
    exportar_dataset,
    get_admin_key,
    registrar_abandono,
    validar_y_procesar_formulario,
)
from observatorio.collector import CollectorLockError, run_collection_batch
from observatorio.config import OBSERVATORY_SECRET
from observatorio.db import query_all, query_one
from observatorio.export_csv import export_observations_to_csv

app = Flask(__name__, static_folder=None)
from alertas_web import bp as alertas_blueprint
app.register_blueprint(alertas_blueprint)


@app.route('/alertas/<slug>/', methods=['GET', 'HEAD'])
def alerts_dynamic_dossier(slug):
    from alertas_datos import obtener_expediente
    if obtener_expediente(slug) is None:
        return Response(render_not_found(request.path), status=404, content_type='text/html; charset=utf-8')
    # Caché corta en el CDN: las aprobaciones editoriales se ven en minutos sin consultar la base en cada visita.
    return Response(render_alertas_page(request.path), content_type='text/html; charset=utf-8',
                    headers={'Cache-Control': 'public, max-age=0, s-maxage=300, stale-while-revalidate=600'})

@app.before_request
def serve_free_observatory():
    from observatorio.estatico import static_observatory_file
    target = static_observatory_file(request.path)
    if request.method in ('GET', 'HEAD') and target:
        response = send_from_directory(target.parent, target.name)
        response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'
        if target.name in ('descargar-csv', 'historial.csv'):
            response.headers['Content-Type'] = 'text/csv; charset=utf-8'
            response.headers['Content-Disposition'] = 'attachment; filename="precios-herramientas.csv"'
        return response

@app.before_request
def load_compatibility_version():
    if request.path.startswith(('/compatibilidad/', '/plataformas/', '/baterias/', '/cargadores/', '/herramientas-bateria/', '/datos/compatibilidad/')):
        from compatibilidad.catalog import refresh_published_state
        refresh_published_state()

@app.after_request
def compatibility_pending_noindex(response):
    from compatibilidad.catalog import PRODUCTS_BY_SLUG, CATALOG_PRODUCTS
    if request.path.startswith(('/baterias/', '/cargadores/', '/herramientas-bateria/')):
        product = PRODUCTS_BY_SLUG.get(request.path.rstrip('/').split('/')[-1])
        if product and product.status != 'publicado':
            response.headers['X-Robots-Tag']='noindex, follow'
    elif request.path.startswith('/plataformas/'):
        platform=request.path.rstrip('/').split('/')[-1]
        if not any(p.platform_id==platform and p.status=='publicado' for p in CATALOG_PRODUCTS):
            response.headers['X-Robots-Tag']='noindex, follow'
    return response
app.config.update(SECRET_KEY=os.environ.get('COMUNIDAD_SESSION_SECRET') or os.environ.get('RELEVAMIENTO_SESSION_SECRET') or secrets.token_hex(32), SESSION_COOKIE_NAME='tallerlab_relevamiento', SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', PERMANENT_SESSION_LIFETIME=timedelta(days=365), SESSION_COOKIE_SECURE=bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV') or os.environ.get('APP_ENV') == 'production'))
from relevamiento_web import bp as relevamiento_blueprint
app.register_blueprint(relevamiento_blueprint)
from comunidad.web import bp as comunidad_blueprint
app.register_blueprint(comunidad_blueprint)


ANALYTICS_SNIPPET = (b'<script>window.va=window.va||function(){(window.vaq=window.vaq||[]).push(arguments)};</script>'
                     b'<script defer src="/_vercel/insights/script.js"></script>')


@app.after_request
def vercel_web_analytics(response):
    """Vercel Web Analytics (sin cookies). Activar en el panel de Vercel y definir VERCEL_WEB_ANALYTICS=1."""
    if (os.environ.get('VERCEL_WEB_ANALYTICS') == '1' and response.status_code == 200 and response.mimetype == 'text/html'
            and not response.direct_passthrough and not request.path.startswith(('/comunidad/admin', '/api/'))):
        body = response.get_data()
        if b'/_vercel/insights/script.js' not in body and b'</body>' in body:
            response.set_data(body.replace(b'</body>', ANALYTICS_SNIPPET + b'</body>', 1))
    return response
ARTICLES_BY_URL = {article["url"]: article for article in ALL_ARTICLES}
FAVICON = (ASSETS_DIR / "favicon.svg").read_bytes()


@app.route("/assets/<path:filename>", methods=["GET", "HEAD"])
def asset(filename):
    from werkzeug.utils import safe_join
    generated_assets = ASSETS_DIR.parent / 'public' / 'assets'
    generated = safe_join(str(generated_assets), filename)
    directory = generated_assets if generated and Path(generated).is_file() else ASSETS_DIR
    response = send_from_directory(directory, filename)
    versioned = filename.endswith(".woff2") or (filename.startswith(("productos/", "portadas/")) and filename.endswith(".webp"))
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable" if versioned else "public, max-age=86400"
    return response


@app.route("/api/affiliate-click", methods=["POST"])
def affiliate_click():
    payload = request.get_data(cache=False)
    if not 0 < len(payload) <= 2048:
        return Response(status=400)
    try:
        event = validate_affiliate_click(json.loads(payload))
    except (ValueError, TypeError):
        return Response(status=400)

    # El sistema de archivos de la función no es almacenamiento persistente.
    # Los eventos quedan en los logs de la función hasta conectar una base externa.
    print(json.dumps({"type": "affiliate_click", **event}, ensure_ascii=False), flush=True)
    return Response(status=204, headers={"Cache-Control": "no-store"})


@app.route("/datos/precios/<category>/descargar-csv", methods=["GET"])
def observatory_csv(category):
    if category not in ("compresores", "hidrolavadoras", "generadores"):
        return Response('Categoría desconocida',status=404,content_type='text/plain; charset=utf-8')
    csv_data = export_observations_to_csv(category=category)
    return Response(
        csv_data,
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="tallerlab-precios-{category}.csv"'},
    )


@app.route("/datos/compatibilidad/baterias.csv", methods=["GET"])
def compatibility_csv():
    csv_data = export_compatibility_to_csv()
    return Response(
        csv_data,
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="tallerlab-compatibilidad-baterias.csv"'},
    )


@app.route("/datos/compatibilidad/baterias.json", methods=["GET"])
def compatibility_json():
    json_data = export_compatibility_to_json()
    return Response(
        json_data,
        content_type="application/json; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="tallerlab-compatibilidad-baterias.json"'},
    )


@app.route("/herramientas/investigacion/descargar-datos.csv", methods=["GET"])
def tallerlab_data_csv():
    csv_data = generate_study_csv()
    return Response(
        csv_data,
        content_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="tallerlab-datos-investigacion-herramientas.csv"'},
    )


@app.route('/herramientas/investigacion/descargar-datos.json', methods=['GET'])
def tallerlab_data_json():
    from tallerlab_data.documentary import export_snapshot
    payload = export_snapshot()
    payload.pop('candidates', None)
    return Response(json.dumps(payload, ensure_ascii=False), content_type='application/json; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="tallerlab-data.json"'})


@app.route('/herramientas/investigacion/fuentes.json', methods=['GET'])
def tallerlab_data_sources():
    from tallerlab_data.documentary import sources
    fields = {'url', 'checked_at', 'http_status', 'final_url', 'status', 'sha256', 'text_sha256', 'title', 'format', 'pages', 'reason', 'publisher_url'}
    payload = {'scope': 'Recuperación documental; no acredita ensayo ni validación automática de todas las especificaciones', 'sources': [{k: v for k, v in r.items() if k in fields} for r in sources().values()]}
    return Response(json.dumps(payload, ensure_ascii=False), content_type='application/json; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="tallerlab-fuentes.json"'})


@app.route("/api/compatibilidad/evento", methods=["POST"])
def compatibility_event():
    payload = request.get_data(cache=False)
    if not 0 < len(payload) <= 4096:
        return Response(status=400)
    try:
        data = json.loads(payload)
        track_event(
            event_type=data.get("event_type", ""),
            query_text=data.get("query_text"),
            model_a=data.get("model_a"),
            model_b=data.get("model_b"),
            verdict=data.get("verdict"),
        )
        return Response(status=204, headers={"Cache-Control": "no-store"})
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=400, content_type="application/json")


@app.route("/api/compatibilidad/ejecutar", methods=["POST", "GET"])
def compatibility_pipeline_execute():
    import hmac
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "").strip() if "Bearer " in auth_header else ""
    expected_token = os.environ.get("CRON_SECRET") if request.method=='GET' else os.environ.get("COMPATIBILITY_MAINTENANCE_TOKEN") or os.environ.get("CRON_SECRET")
    valid = bool(expected_token and token and hmac.compare_digest(token, expected_token))
    if not valid:
        return Response(json.dumps({"error": "No autorizado"}), status=401, content_type="application/json")
    try:
        body = request.get_json(silent=True) or {}
        if not isinstance(body, dict) or not isinstance(body.get("dry_run", False), bool):
            return Response(json.dumps({"error":"dry_run debe ser booleano"}), status=400, content_type="application/json")
        if request.method == 'GET' and request.args:
            return Response(json.dumps({"error":"El disparador cron no admite parámetros"}),status=400,content_type="application/json")
        dry_run = body.get("dry_run", False)
        pipeline = MaintenancePipeline()
        summary = pipeline.execute_maintenance(dry_run=dry_run)
        return Response(json.dumps(summary, ensure_ascii=False), status=200 if summary['status']=='OK' else 503, content_type="application/json",headers={'Cache-Control':'no-store'})
    except Exception as exc:
        app.logger.exception('Falló el mantenimiento de compatibilidad')
        return Response(json.dumps({"error": "No se pudo ejecutar el mantenimiento. Revisar los registros."}), status=500, content_type="application/json")


@app.route('/api/compatibilidad/estado',methods=['GET'])
def compatibility_health():
    from compatibilidad.operations import capture_health
    health=capture_health()
    return Response(json.dumps(health,ensure_ascii=False),status=200 if health['status']=='ok' else 503,
                    content_type='application/json',headers={'Cache-Control':'no-store'})

@app.route("/api/observatorio/ejecutar", methods=["POST", "GET"])
def observatory_cron_execute():
    auth_header = request.headers.get("Authorization", "")
    secret = os.environ.get("CRON_SECRET", "") or OBSERVATORY_SECRET
    token = auth_header.replace("Bearer ", "").strip() if "Bearer " in auth_header else ""
    import hmac
    if not secret or not token or not hmac.compare_digest(token, secret):
        return Response(json.dumps({"error": "No autorizado"}), status=401, content_type="application/json")

    # Rechazar solicitud de modo demo/fixtures en el endpoint productivo
    if request.args.get("fixtures"):
        return Response(
            json.dumps({"error": "Modo de prueba (fixtures) no admitido en el endpoint productivo."}),
            status=400,
            content_type="application/json",
        )

    batch_size = request.args.get("batch_size", type=int)
    try:
        summary = run_collection_batch(batch_size=batch_size, use_fixtures=False)
        return Response(json.dumps(summary, ensure_ascii=False), status=200, content_type="application/json")
    except CollectorLockError as exc:
        return Response(json.dumps({"error": str(exc)}), status=409, content_type="application/json")
    except Exception as exc:
        app.logger.exception('Falló la captura del observatorio')
        return Response(json.dumps({"error": "No se pudo ejecutar la captura. Revisar configuración y registros."}), status=500, content_type="application/json")


@app.route("/api/observatorio/estado", methods=["GET"])
def observatory_status():
    auth_header = request.headers.get("Authorization", "")
    secret = os.environ.get("CRON_SECRET", "") or OBSERVATORY_SECRET
    token = auth_header.replace("Bearer ", "").strip() if "Bearer " in auth_header else ""
    import hmac
    if not secret or not token or not hmac.compare_digest(token, secret):
        return Response(json.dumps({"error": "No autorizado"}), status=401, content_type="application/json")

    try:
        last_run = query_one("SELECT * FROM collector_runs ORDER BY started_at DESC LIMIT 1;")
        open_incidents = query_all("SELECT COUNT(*) AS count FROM incidents WHERE resolved = 0;")
        incidents_count = open_incidents[0]["count"] if open_incidents else 0

        health = "ok"
        if not last_run:
            health = "critico"
        else:
            status = last_run.get("status")
            started_at_str = last_run.get("started_at")
            is_stale = False
            if started_at_str:
                from datetime import datetime, timezone
                try:
                    s_dt = datetime.fromisoformat(started_at_str)
                    if s_dt.tzinfo is None:
                        s_dt = s_dt.replace(tzinfo=timezone.utc)
                    age_hours = (datetime.now(timezone.utc) - s_dt).total_seconds() / 3600.0
                    if age_hours > 26:
                        is_stale = True
                except Exception:
                    pass

            if status in ('failed','no_sources') or is_stale:
                health = "degradado" if status != "failed" else "critico"
            elif status == "partial_failure":
                health = 'degradado'
                total = last_run.get("total_offers", 0) or 1
                failed = last_run.get("failed_offers", 0) or 0
                if failed / total > 0.3:
                    health = "degradado"

        from observatorio.operations import capture_health
        coverage = capture_health()
        if coverage['status'] != 'ok':
            health = 'degradado'
        return Response(
            json.dumps({
                "status": health,
                "last_run": last_run,
                "open_incidents_count": incidents_count,
                "coverage": coverage,
            }, ensure_ascii=False),
            status=200,
            content_type="application/json",
        )
    except Exception:
        return Response(
            json.dumps({"status": "error", "error": "Error al verificar estado"}),
            status=500,
            content_type="application/json",
        )


@app.route("/", defaults={"path": ""}, methods=["GET", "HEAD"])
@app.route("/<path:path>", methods=["GET", "HEAD"], strict_slashes=False)
def page(path):
    url_path = "/" + path

    if url_path == "/robots.txt":
        return Response(render_robots(), content_type="text/plain; charset=utf-8")
    if url_path == "/sitemap.xml":
        return Response(render_sitemap(), content_type="application/xml; charset=utf-8")
    if url_path == "/feed.xml":
        return Response(render_feed(), content_type="application/rss+xml; charset=utf-8")
    if url_path == "/llms.txt":
        return Response(render_llms(), content_type="text/plain; charset=utf-8")
    if url_path == "/search-cards.html":
        return Response(render_search_cards(), content_type="text/html; charset=utf-8", headers={"X-Robots-Tag": "noindex"})
    if url_path == "/favicon.ico":
        return Response(FAVICON_ICO, content_type="image/x-icon", headers={"Cache-Control": "public, max-age=86400"})
    if url_path == "/favicon.svg":
        return Response(FAVICON, content_type="image/svg+xml")

    if url_path in ("/equipo-editorial", "/equipo-editorial/"):
        destination = AUTHOR_PATH
        if request.query_string:
            destination += "?" + request.query_string.decode("ascii")
        return redirect(destination, code=301)

    if not url_path.endswith("/") and url_path + "/" in INDEXABLE_PATH_SET:
        destination = url_path + "/"
        if request.query_string:
            destination += "?" + request.query_string.decode("ascii")
        return redirect(destination, code=301)

    if url_path == "/":
        html = render_home_page()

    elif url_path in ALERTAS_PATHS:
        html = render_alertas_page(url_path)
    elif url_path == COMPATIBILITY_SEARCH_PATH:
        return Response(
            render_compatibility_page(url_path, request.args),
            headers={"X-Robots-Tag": "noindex, follow"},
            content_type="text/html; charset=utf-8",
        )
    elif url_path in COMPATIBILITY_PATHS or (url_path.startswith('/compatibilidad/') and '-con-' in url_path):
        from compatibilidad.presentation import resolve_relationship
        if url_path not in COMPATIBILITY_PATHS and resolve_relationship(url_path) is None:
            return Response(render_not_found(url_path),status=404,content_type='text/html; charset=utf-8')
        html = render_compatibility_page(url_path)
    elif url_path in TALLERLAB_DATA_PATHS:
        html = render_tallerlab_data_page(url_path, request.args)
    elif url_path in OBSERVATORY_PATHS:
        html = render_observatory_page(url_path)
    elif url_path == "/como-trabajamos/":
        html = render_editorial_page("metodologia")
    elif url_path == AUTHOR_PATH:
        html = render_editorial_page("equipo")
    elif url_path in ("/contacto/", "/privacidad/"):
        html = render_editorial_page(url_path.strip("/"))
    elif url_path.endswith("/") and url_path in INDEXABLE_PATH_SET and url_path[1:-1] in CATEGORY_META:
        html = render_category_page(url_path[1:-1])
    elif url_path in ARTICLES_BY_URL:
        html = render_article_page(ARTICLES_BY_URL[url_path])
    else:
        return Response(render_not_found(url_path), status=404, content_type="text/html; charset=utf-8")

    return Response(html, content_type="text/html; charset=utf-8")
