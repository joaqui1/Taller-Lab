"""HTTP del relevamiento: sesión administrativa, CSRF y contratos compartidos."""
import hashlib
import hmac
import json
import os
import secrets
import time
from flask import Blueprint, Response, request, session, redirect, current_app
import relevamiento_piloto as rel

bp = Blueprint('relevamiento', __name__)
ADMIN_PATH = '/relevamiento-2027/admin/'
MAX_BODY = 65536

def credential_stamp():
    key = rel.get_admin_key()
    return hmac.new(current_app.config['SECRET_KEY'].encode(), key.encode(), hashlib.sha256).hexdigest() if key else ''

def authenticated():
    return bool(rel.get_admin_key() and session.get('rel_auth') == credential_stamp()
                and session.get('rel_expires', 0) > time.time())

def csrf_token():
    if 'rel_csrf' not in session:
        session['rel_csrf'] = secrets.token_urlsafe(32)
    return session['rel_csrf']

def csrf_valid():
    supplied = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token', '')
    expected = session.get('rel_csrf', '')
    return bool(isinstance(supplied, str) and expected and hmac.compare_digest(supplied, expected))

def reply(data, status=200):
    return Response(json.dumps(data, ensure_ascii=False), status=status, content_type='application/json; charset=utf-8')

def payload():
    if request.content_length is None or not 0 < request.content_length <= MAX_BODY:
        raise ValueError('La solicitud está vacía o supera el tamaño permitido.')
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('La solicitud debe ser un objeto JSON.')
    return data

@bp.before_request
def body_limit():
    if request.content_length and request.content_length > MAX_BODY:
        return reply({'ok': False, 'error': 'La solicitud supera el tamaño permitido.'}, 413)

@bp.after_request
def private_headers(response):
    response.headers['Cache-Control'] = 'no-store, private'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    if '/admin' in request.path or '/api/' in request.path:
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response

@bp.route('/relevamiento-2027/', methods=['GET'])
def landing():
    from servidor_local import render_relevamiento_view
    return Response(render_relevamiento_view('formulario', request.args), content_type='text/html; charset=utf-8')

@bp.route('/relevamiento-2027/metodologia/')
def methodology():
    from servidor_local import render_relevamiento_view
    return Response(render_relevamiento_view('metodologia'), content_type='text/html; charset=utf-8')

@bp.route(ADMIN_PATH, methods=['GET'])
@bp.route('/relevamiento-2027/admin', methods=['GET'])
def admin():
    from servidor_local import render_relevamiento_view
    # Query parameters never grant authorization; an old URL cannot leak a key.
    if 'key' in request.args:
        return redirect(ADMIN_PATH, code=303)
    params = {'demo': request.args.get('demo', ''), '_authenticated': authenticated(), '_csrf': csrf_token()}
    if authenticated() and rel.es_produccion() and not os.environ.get('RELEVAMIENTO_DATABASE_URL'):
        return Response('Relevamiento cerrado. Revisá la configuración de almacenamiento y sesión antes de abrirlo.', status=503)
    try:
        return Response(render_relevamiento_view('admin', params), content_type='text/html; charset=utf-8')
    except Exception:
        return Response('Panel temporalmente no disponible. Revisá la conexión de almacenamiento.', status=503)

@bp.route(ADMIN_PATH + 'login', methods=['POST'])
def login():
    if not rel.get_admin_key() or not csrf_valid():
        return reply({'ok': False, 'error': 'Acceso no autorizado.'}, 403)
    try:
        if rel.check_ip_rate_limit('login:' + (request.remote_addr or 'unknown')):
            return reply({'ok': False, 'error': 'Demasiados intentos. Intentá más tarde.'}, 429)
    except Exception:
        return reply({'ok': False, 'error': 'Acceso temporalmente no disponible.'}, 503)
    key = request.form.get('key', '')
    if not hmac.compare_digest(key, rel.get_admin_key()):
        return reply({'ok': False, 'error': 'Clave incorrecta.'}, 403)
    session.clear()
    session['rel_auth'] = credential_stamp()
    session['rel_expires'] = time.time() + 3600
    session['rel_csrf'] = secrets.token_urlsafe(32)
    return redirect(ADMIN_PATH, code=303)

@bp.route(ADMIN_PATH + 'logout', methods=['POST'])
def logout():
    if not authenticated() or not csrf_valid():
        return reply({'ok': False}, 403)
    session.clear()
    return redirect(ADMIN_PATH, code=303)

@bp.route('/api/relevamiento/submit', methods=['POST'])
def submit():
    if not rel.relevamiento_abierto():
        return reply({'ok': False, 'errores': {'_global': 'El relevamiento todavía no está abierto.'}}, 503)
    try:
        data = payload()
        valid, result, status = rel.validar_y_procesar_formulario(
            data, client_ip=request.remote_addr or 'unknown', user_agent=request.headers.get('User-Agent', ''))
        return reply({'ok': valid, **result} if valid else {'ok': False, 'errores': result}, status)
    except ValueError as exc:
        return reply({'ok': False, 'errores': {'_global': str(exc)}}, 400)
    except Exception:
        return reply({'ok': False, 'errores': {'_global': 'No pudimos guardar la respuesta. Intentá nuevamente.'}}, 503)

@bp.route('/api/relevamiento/abandon', methods=['POST'])
def event():
    if not rel.relevamiento_abierto():
        return reply({'ok': False}, 503)
    try:
        data = payload()
        if rel.check_ip_rate_limit('event:' + (request.remote_addr or 'unknown'), maximum=120):
            return reply({'ok': False}, 429)
        result = rel.registrar_abandono(data.get('paso'), data.get('utm'), data.get('session_id'))
        return reply({'ok': True, 'id': result['id']})
    except (ValueError, TypeError):
        return reply({'ok': False, 'error': 'Evento inválido.'}, 400)
    except Exception:
        return reply({'ok': False, 'error': 'Registro temporalmente no disponible.'}, 503)

@bp.route('/api/relevamiento/moderar', methods=['POST'])
def moderate():
    if not authenticated() or not csrf_valid():
        return reply({'ok': False, 'error': 'Acceso no autorizado.'}, 403)
    try:
        data = payload()
        ok = rel.actualizar_estado_moderacion(data.get('response_id'), data.get('estado'),
                    notas=data.get('notas'), aprobar_resena=data.get('aprobar_resena'))
        return reply({'ok': ok}, 200 if ok else 400)
    except (ValueError, TypeError):
        return reply({'ok': False}, 400)
    except Exception:
        return reply({'ok': False, 'error': 'Moderación temporalmente no disponible.'}, 503)

@bp.route('/api/relevamiento/export')
def export():
    if not authenticated():
        return reply({'error': 'Acceso no autorizado.'}, 403)
    kind, fmt = request.args.get('tipo', 'analitica'), request.args.get('formato', 'csv')
    if kind not in ('analitica', 'informe', 'comercial', 'publica') or fmt not in ('csv', 'json'):
        return reply({'error': 'Exportación inválida.'}, 400)
    try:
        content, ctype, filename = rel.exportar_dataset(kind, fmt)
    except Exception:
        return reply({'error': 'Exportación temporalmente no disponible.'}, 503)
    return Response(content, content_type=ctype, headers={'Content-Disposition': f'attachment; filename="{filename}"'})

@bp.route('/api/relevamiento/revocar', methods=['POST'])
def revoke():
    if not authenticated() or not csrf_valid():
        return reply({'ok': False}, 403)
    try:
        ok = rel.revocar_contacto(payload().get('response_id'))
        return reply({'ok': ok}, 200 if ok else 400)
    except ValueError:
        return reply({'ok': False}, 400)
    except Exception:
        return reply({'ok': False}, 503)
