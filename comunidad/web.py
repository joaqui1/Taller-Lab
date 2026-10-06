"""Recorridos HTML completos; los formularios también funcionan sin JavaScript."""
import hashlib
import hmac
import os
import re
import secrets
import time
import uuid

from flask import Blueprint, Response, redirect, render_template, request, session, url_for, current_app
from comunidad import storage as db
from comunidad import components as cc
from comunidad import avisos
from tallerlab_data.storage import get_all_tools, get_tool_by_slug

bp = Blueprint('comunidad', __name__, template_folder='templates')
# Cierra al final de cada request la conexión PostgreSQL compartida (también la que usan fichas y guías).
bp.record_once(lambda state: state.app.teardown_appcontext(db.close_request_connection))
# Páginas iguales para todos (sin formularios ni datos de la sesión): se pueden cachear en el CDN de Vercel.
PUBLIC_CACHE = 'public, max-age=0, s-maxage=300, stale-while-revalidate=600'
CACHEABLE_ENDPOINTS = {'comunidad.hub', 'comunidad.criteria'}


def csrf():
    if 'comunidad_csrf' not in session:
        session.permanent = True
        session['comunidad_csrf'] = secrets.token_urlsafe(32)
    return session['comunidad_csrf']


def actor():
    # Sesión persistente (ver PERMANENT_SESSION_LIFETIME en app.py): quien pregunta hoy puede volver
    # en días o semanas a elegir la respuesta que le sirvió o retirar su aporte.
    if 'comunidad_actor' not in session:
        session.permanent = True
        session['comunidad_actor'] = str(uuid.uuid4())
    return session['comunidad_actor']


def current_actor():
    """Lectura sin crear sesión: las páginas públicas no necesitan cookie para leerse."""
    return session.get('comunidad_actor', '')


class LazyToken:
    """El token CSRF (y la cookie de sesión) solo se generan si la página incluye un formulario."""
    def __str__(self):
        return csrf()
    __html__ = __str__


FIELD_LABELS = {'alias': 'nombre público', 'body': 'texto', 'task': 'trabajo', 'advantages': 'lo mejor',
    'problems': 'limitaciones', 'repair': 'reparaciones', 'title': 'pregunta en una línea', 'email': 'correo',
    'reason': 'motivo', 'request_id': 'formulario', 'post_id': 'aporte', 'parent_id': 'pregunta',
    'answer_id': 'respuesta', 'action': 'acción', 'option': 'opción', 'rating': 'puntuación'}


def admin_key():
    return os.environ.get('COMUNIDAD_ADMIN_KEY', '')


def stamp():
    return hmac.new(current_app.secret_key.encode(), admin_key().encode(), hashlib.sha256).hexdigest()


def authenticated():
    return bool(admin_key() and session.get('comunidad_admin') == stamp() and session.get('comunidad_expires', 0) > time.time())


def text_field(name, minimum=0, maximum=2000):
    value = request.form.get(name, '').strip()
    if not minimum <= len(value) <= maximum or '\x00' in value:
        label = FIELD_LABELS.get(name, name)
        if minimum:
            raise ValueError(f'Revisá el campo «{label}»: debe tener entre {minimum} y {maximum} caracteres.')
        raise ValueError(f'Revisá el campo «{label}»: puede tener hasta {maximum} caracteres.')
    return value


def choice(name, options):
    value = text_field(name, maximum=40)
    if value not in options:
        raise ValueError('Completá el tipo, tiempo y frecuencia de uso de tu herramienta.')
    return value


def rate_key(prefix):
    # Do not trust arbitrary proxy headers or persist raw addresses.
    identity = request.remote_addr or 'unknown'
    if os.environ.get('VERCEL'):
        # Vercel reescribe estos encabezados con la IP del visitante; fuera de Vercel no se confía en ellos.
        identity = (request.headers.get('X-Real-IP') or
                    request.headers.get('X-Vercel-Forwarded-For', '').split(',')[0].strip() or identity)
    return prefix + ':' + hmac.new(current_app.secret_key.encode(), identity.encode(), hashlib.sha256).hexdigest()


def _contact_email():
    try:
        from paginas_institucionales import contact_email
        return contact_email()
    except Exception:
        return ''


def page(template, title, path, **context):
    from servidor_local import HTML_SHELL, LOGO_SRC, PORT, absolute_url
    from html import escape
    notice = session.pop('comunidad_notice', '')
    clear_draft = session.pop('comunidad_clear_draft', '')
    error = context.pop('error', '')
    description = context.pop('description', 'Herramientas en uso: experiencias, preguntas y sondeos de lectores de TallerLab.')
    body = render_template(template, csrf=LazyToken(), notice=notice, error=error, clear_draft=clear_draft,
        opened=db.enabled(), readable=db.readable(), new_id=lambda: str(uuid.uuid4()),
        usages=db.USAGES, durations=db.DURATIONS, frequencies=db.FREQUENCIES,
        poll_options=db.POLL_OPTIONS, ratings=db.RATINGS, poll_min=cc.POLL_MIN,
        notify_available=avisos.email_ready(), contact_email=_contact_email(), **context)
    canonical = '<link rel="canonical" href="' + escape(absolute_url(path), quote=True) + '">'
    # Personalized pages and empty model discussions do not enter the index.
    if context.get('noindex') or request.query_string:
        canonical += '<meta name="robots" content="noindex, follow">'
    canonical += context.get('head_extra', '')
    from contenido_publico import apply_community_nav
    html = apply_community_nav(str(HTML_SHELL).format(PAGE_TITLE=escape(title), PAGE_DESC=escape(description, quote=True),
        CANONICAL_TAG=canonical, PORT=PORT, CONTENT=body, LOGO_SRC=LOGO_SRC))
    response = Response(html, content_type='text/html; charset=utf-8', status=context.get('status', 200))
    if response.status_code == 503:
        # Una caída temporal nunca debe parecer una página sin contenido (evita desindexar).
        response.headers['Retry-After'] = '600'
    return response


@bp.before_request
def guard():
    if request.content_length and request.content_length > 16000:
        return Response('El envío supera el tamaño permitido.', 413)
    if request.method == 'POST':
        supplied = request.form.get('csrf_token', '')
        expected = session.get('comunidad_csrf', '')
        if not expected or not hmac.compare_digest(expected, supplied):
            return page('message.html', 'Reabrí el formulario', '/comunidad/', noindex=True, status=403,
                error='El formulario venció. Volvé a abrir la página e intentá nuevamente.')


@bp.after_request
def headers(response):
    shared = (request.method in ('GET', 'HEAD') and request.endpoint in CACHEABLE_ENDPOINTS
              and not request.query_string and response.status_code == 200 and 'Set-Cookie' not in response.headers)
    # El CDN de Vercel no usa la cookie en la clave de caché: solo se cachean páginas sin contenido personal.
    response.headers['Cache-Control'] = PUBLIC_CACHE if shared else 'no-store, private'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    if '/admin' in request.path or request.method == 'POST':
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    return response


@bp.get('/comunidad/')
def hub():
    tools = get_all_tools()
    overview = db.overview_or_none()
    if overview is None:
        # Sin datos ni resumen previo no sabemos si la portada es indexable: 503 temporal, nunca noindex por error.
        return page('message.html', 'Comunidad temporalmente no disponible', '/comunidad/', status=503,
                    error='No pudimos cargar la comunidad. Intentá nuevamente en unos minutos.')
    indexable = cc.hub_indexable(overview)
    query = request.args.get('q', '').strip()[:100]
    category = request.args.get('categoria', '')
    categories = sorted({t.category for t in tools})
    selected = [t for t in tools if (not category or category == t.category)
        and (not query or query.casefold() in (t.brand + ' ' + t.model_name + ' ' + t.mpn).casefold())]
    selected.sort(key=lambda t: -(overview.get(t.slug, {}).get('reviews', 0) + overview.get(t.slug, {}).get('questions', 0)))
    polls = cc.category_polls(categories) if db.readable() else {}
    return page('hub.html', 'Opiniones de herramientas eléctricas en Argentina: experiencias de usuarios', '/comunidad/',
                tools=selected, query=query, category=category, categories=categories, overview=overview, polls=polls,
                noindex=not indexable,
                description=('Opiniones y experiencias reales de quienes usan taladros, amoladoras, compresores, hidrolavadoras, '
                             'soldadoras y generadores en Argentina. Preguntá por un modelo y compartí cómo te funcionó.')
                            if indexable else
                            ('Contá cómo te funciona tu taladro, amoladora, compresor, hidrolavadora, soldadora o generador, '
                             'y preguntá por un modelo a otros usuarios en Argentina.'),
                head_extra=cc.breadcrumb_jsonld([('Comunidad', '/comunidad/')]))


@bp.get('/comunidad/criterios/')
def criteria():
    return page('criteria.html', 'Cómo participa la comunidad', '/comunidad/criterios/')


@bp.route('/comunidad/contacto/', methods=['GET', 'POST'])
def contact():
    identity = actor()
    if request.method == 'POST':
        if not db.readable():
            return page('contact.html', 'Contacto privado de comunidad', '/comunidad/contacto/', noindex=True,
                error='El contacto está temporalmente no disponible. Intentá más tarde.', status=503)
        try:
            if not db.rate_allowed(rate_key('contact'), 5):
                return Response('Hubo muchos intentos. Intentá más tarde.', 429)
            if request.form.get('contact_consent') != 'yes' or request.form.get('website'):
                raise ValueError('Confirmá el uso de tus datos para atender esta solicitud.')
            email = text_field('email', 5, 254)
            if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
                raise ValueError('Indicá un correo válido para atender tu consulta.')
            body = text_field('body', 15, 2000)
            request_id = text_field('request_id', maximum=36)
            if not db.valid_uuid(request_id):
                raise ValueError('Reabrí el formulario antes de enviar.')
            db.save_request(request_id, identity, email, body)
            avisos.new_contribution('contact', '')
            session['comunidad_notice'] = 'Solicitud privada recibida. Referencia: ' + request_id + '. El equipo editorial la atenderá; no se publica en la comunidad.'
            return redirect(url_for('comunidad.contact'), 303)
        except ValueError as exc:
            return page('contact.html', 'Contacto privado de comunidad', '/comunidad/contacto/', noindex=True, error=str(exc), status=400)
        except Exception:
            current_app.logger.exception('Solicitud de comunidad no disponible')
            return page('contact.html', 'Contacto privado de comunidad', '/comunidad/contacto/', noindex=True,
                error='No pudimos guardar tu solicitud. Intentá nuevamente.', status=503)
    return page('contact.html', 'Contacto privado de comunidad', '/comunidad/contacto/', noindex=True)


def related_guides_for(tool):
    from servidor_local import ALL_ARTICLES
    from tallerlab_data.guide_links import GUIDE_TOOL_MAPPINGS
    related_paths = {path for path, slugs in GUIDE_TOOL_MAPPINGS.items() if tool.slug in slugs}
    return [article for article in ALL_ARTICLES if article['url'] in related_paths
        and any(candidate.slug == tool.slug for candidate in cc.guide_community_tools(article))]


def load(tool):
    """Lee todo en una conexión. Devuelve None si el almacenamiento no está disponible."""
    if not db.readable():
        return None
    try:
        return db.snapshot(tool.slug, current_actor(), cc.poll_scope(tool))
    except Exception:
        current_app.logger.exception('No se pudo leer la comunidad')
        return None


def model_view(tool, error='', status=200):
    related_guides = related_guides_for(tool)
    data = load(tool)
    unavailable = data is None
    posts, mine, counts, selected = data or ([], [], {}, '')
    if unavailable and status < 400:
        status = 503
    usage = request.args.get('uso', '')
    duration = request.args.get('tiempo', '')
    reviews = [p for p in posts if p['kind'] == 'review']
    filtered = [p for p in reviews if (not usage or p['context'].get('usage') == usage)
                and (not duration or p['context'].get('duration') == duration)]
    questions = [p for p in posts if p['kind'] == 'question']
    answer_counts = {}
    for p in posts:
        if p['kind'] == 'answer':
            answer_counts[p['parent_id']] = answer_counts.get(p['parent_id'], 0) + 1
    for q in questions:
        q['title'] = cc.question_title(q)
        q['path'] = cc.question_path(tool.slug, q)
        q['answer_count'] = answer_counts.get(q['id'], 0)
    stats = cc.stats_from_posts(posts)
    indexable = cc.model_indexable(stats) and not unavailable
    path = f'/comunidad/modelos/{tool.slug}/'
    total = sum(counts.values())
    head = cc.breadcrumb_jsonld([('Comunidad', '/comunidad/'), (tool.brand + ' ' + tool.model_name, path)])
    if indexable:
        head += cc.model_page_jsonld(tool, path, stats)
    return page('model.html', f'{tool.brand} {tool.model_name}: opiniones y experiencias de usuarios', path,
        tool=tool, reviews=filtered, review_count=len(reviews),
        questions=questions, mine=mine, counts=counts, selected=selected, related_guides=related_guides,
        total=total, usage=usage, duration=duration, unavailable=unavailable, summary=cc.review_summary(stats),
        description=cc.model_description(tool, stats),
        noindex=not indexable, head_extra=head, error=error, status=status)


def question_view(tool, question_id, requested_path=None, error='', status=200):
    data = load(tool)
    if data is None:
        return page('message.html', 'Comunidad temporalmente no disponible', f'/comunidad/modelos/{tool.slug}/',
                    noindex=True, status=503, error='No pudimos leer esta conversación. Intentá nuevamente en unos minutos.')
    posts, mine, counts, selected = data
    question = next((p for p in posts if p['id'] == question_id and p['kind'] == 'question'), None)
    if not question:
        return page('message.html', 'Pregunta no disponible', f'/comunidad/modelos/{tool.slug}/', noindex=True, status=404,
                    error='Esta pregunta ya no está publicada.')
    question['title'] = cc.question_title(question)
    path = cc.question_path(tool.slug, question)
    if requested_path is not None and requested_path != path:
        return redirect(path, 301)
    answers = cc.sort_answers([p for p in posts if p['kind'] == 'answer' and p['parent_id'] == question_id])
    others = []
    for q in posts:
        if q['kind'] == 'question' and q['id'] != question_id and len(others) < 6:
            q['title'] = cc.question_title(q)
            q['path'] = cc.question_path(tool.slug, q)
            others.append(q)
    head = cc.breadcrumb_jsonld([('Comunidad', '/comunidad/'), (tool.brand + ' ' + tool.model_name, f'/comunidad/modelos/{tool.slug}/'),
                                 (question['title'], path)])
    if answers:
        head += cc.qapage_jsonld(tool, question, answers, path)
    return page('question.html', f'{question["title"]} · {tool.brand} {tool.model_name}', path,
        tool=tool, question=question, answers=answers, others=others, related_guides=related_guides_for(tool),
        unavailable=False, description=cc.excerpt(question['body'], 155),
        noindex=not answers, head_extra=head, error=error, status=status)


@bp.get('/comunidad/modelos/<slug>/')
def model(slug):
    tool = get_tool_by_slug(slug)
    if not tool:
        return page('message.html', 'Modelo no encontrado', '/comunidad/', noindex=True, status=404,
                    error='Ese modelo no está en el catálogo. Buscá una herramienta para participar.')
    return model_view(tool)


@bp.get('/comunidad/modelos/<slug>/preguntas/<path:qpath>/')
def question(slug, qpath):
    tool = get_tool_by_slug(slug)
    if not tool:
        return page('message.html', 'Modelo no encontrado', '/comunidad/', noindex=True, status=404,
                    error='Ese modelo no está en el catálogo. Buscá una herramienta para participar.')
    if not db.readable():
        return question_view(tool, '')
    try:
        question_id = db.find_question(slug, qpath.rsplit('-', 1)[-1])
    except Exception:
        current_app.logger.exception('No se pudo leer la pregunta')
        return page('message.html', 'Comunidad temporalmente no disponible', f'/comunidad/modelos/{slug}/', noindex=True,
                    status=503, error='No pudimos leer esta conversación. Intentá nuevamente en unos minutos.')
    if not question_id:
        return page('message.html', 'Pregunta no encontrada', f'/comunidad/modelos/{slug}/', noindex=True, status=404,
                    error='No encontramos esa pregunta. Puede haber sido retirada.')
    return question_view(tool, question_id, f'/comunidad/modelos/{slug}/preguntas/{qpath}/')


@bp.post('/comunidad/modelos/<slug>/participar')
def participate(slug):
    tool = get_tool_by_slug(slug)
    if not tool:
        return Response('Modelo desconocido.', 404)
    action = request.form.get('action', '')
    back_id = request.form.get('pregunta', '')
    back_question = request.form.get('volver') == 'pregunta' and db.valid_uuid(back_id)

    def failed(message, code):
        if back_question:
            return question_view(tool, back_id, error=message, status=code)
        return model_view(tool, message, code)

    if not db.enabled() and not (action == 'withdraw' and db.readable()):
        return failed('La participación todavía no está abierta.', 503)
    try:
        if not db.rate_allowed(rate_key('participation')):
            return failed('Hubo muchos intentos desde esta conexión. Intentá más tarde.', 429)
        action = text_field('action', maximum=20)
        identity = actor()
        if action in ('review', 'question', 'answer'):
            if request.form.get('consent') != 'yes':
                raise ValueError('Confirmá que autorizás la publicación de tu aporte.')
            if request.form.get('website'):
                raise ValueError('No pudimos aceptar este envío. Revisá el formulario.')
            post_id = text_field('request_id', maximum=36)
            if not db.valid_uuid(post_id):
                raise ValueError('Reabrí el formulario antes de enviar.')
            alias = text_field('alias', 2, 40)
            body = text_field('body', 20, 2000)
            context = {}
            if action == 'review':
                context = {'usage': choice('usage', db.USAGES), 'duration': choice('duration', db.DURATIONS),
                    'frequency': choice('frequency', db.FREQUENCIES), 'task': text_field('task', 3, 160),
                    'advantages': text_field('advantages', maximum=500), 'problems': text_field('problems', maximum=500),
                    'repair': text_field('repair', maximum=500),
                    'repurchase': choice('repurchase', {'si', 'no', 'depende'})}
                rating = request.form.get('rating', '')
                if rating:
                    if rating not in db.RATINGS:
                        raise ValueError('Elegí una puntuación de 1 a 5 o dejala vacía.')
                    context['rating'] = rating
            notify_email = ''
            if action == 'question':
                context = {'title': text_field('title', 10, 140)}
                notify_email = request.form.get('aviso_email', '').strip()
                if notify_email:
                    if not avisos.email_ready():
                        notify_email = ''
                    elif len(notify_email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', notify_email):
                        raise ValueError('Revisá el correo para el aviso o dejalo vacío.')
                    elif request.form.get('aviso_consent') != 'yes':
                        raise ValueError('Confirmá que querés recibir un único aviso por correo, o dejá el correo vacío.')
            parent = text_field('parent_id', maximum=36) if action == 'answer' else None
            if parent and not db.valid_uuid(parent):
                raise ValueError('Elegí una pregunta publicada para responder.')
            if action == 'answer' and not parent:
                raise ValueError('Elegí la pregunta que querés responder.')
            db.save_post(post_id, identity, slug, action, alias, body, context, parent, notify_email)
            avisos.new_contribution(action, slug)
            session['comunidad_clear_draft'] = slug + ':' + action + (':' + parent if parent else '')
            message = 'Recibimos tu aporte. Lo revisaremos antes de publicarlo. Podés retirarlo en «Mis aportes».'
        elif action in ('helpful', 'withdraw', 'accept'):
            post_id = text_field('post_id', maximum=36)
            if not db.valid_uuid(post_id):
                raise ValueError('Elegí un aporte válido.')
            # Never let an action issued for one product modify another product.
            with db.connection() as conn:
                post = conn.execute('SELECT tool_slug FROM comunidad_posts WHERE id=?', (post_id,)).fetchone()
            if not post or post['tool_slug'] != slug:
                raise ValueError('Ese aporte no pertenece a este modelo.')
            if action == 'helpful':
                db.helpful(post_id, identity)
                message = 'Gracias. Registramos que este aporte te sirvió.'
            elif action == 'withdraw':
                db.withdraw(post_id, identity)
                message = 'Retiramos tu aporte de la publicación.'
            else:
                db.accept(post_id, text_field('answer_id', maximum=36), identity)
                message = 'Marcamos la respuesta que te ayudó.'
        elif action == 'poll':
            if request.form.get('poll_consent') != 'yes':
                raise ValueError('Confirmá la participación en el sondeo antes de votar.')
            db.poll_vote(cc.poll_scope(tool), identity, text_field('option', maximum=30))
            message = 'Guardamos tu elección. Si volvés a votar desde este navegador, la reemplazamos.'
        else:
            raise ValueError('Acción desconocida.')
        session['comunidad_notice'] = message
        if back_question:
            question = db.visible_posts(slug, identity)
            target = next((q for q in question if q['id'] == back_id and q['kind'] == 'question'), None)
            if target:
                return redirect(cc.question_path(slug, target) + '#participacion', code=303)
        return redirect(url_for('comunidad.model', slug=slug) + '#participacion', code=303)
    except ValueError as exc:
        return failed(str(exc), 400)
    except Exception:
        current_app.logger.exception('No se pudo guardar un aporte comunitario')
        return failed('No pudimos completar el envío. Intentá nuevamente.', 503)


@bp.route('/comunidad/admin/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        try:
            if not db.readable():
                return page('message.html', 'Panel temporalmente no disponible', '/comunidad/admin/', noindex=True, status=503,
                    error='El almacenamiento no está disponible.')
            action = request.form.get('action')
            limit_kind = 'admin-login' if action == 'login' else 'admin-actions'
            if not db.rate_allowed(rate_key(limit_kind), 20 if action == 'login' else 500):
                return Response('Demasiados intentos. Intentá más tarde.', 429)
            if action == 'login':
                if not admin_key() or not hmac.compare_digest(request.form.get('key', ''), admin_key()):
                    return page('admin.html', 'Panel de comunidad', '/comunidad/admin/', logged=False, rows=[], noindex=True,
                                error='No pudimos validar el acceso.', status=403)
                session['comunidad_admin'] = stamp()
                session['comunidad_expires'] = time.time() + 3600
                session['comunidad_csrf'] = secrets.token_urlsafe(32)
            elif not authenticated():
                return Response('Acceso no autorizado.', 403)
            elif action == 'logout':
                session.pop('comunidad_admin', None)
                session.pop('comunidad_expires', None)
            elif action == 'moderate':
                post_id, state = text_field('post_id', maximum=36), text_field('state', maximum=20)
                db.moderate(post_id, state, text_field('reason', 3, 500))
                sent = avisos.answer_published(post_id) if state == 'published' else 0
                session['comunidad_notice'] = 'Decisión de moderación guardada.' + (f' Se avisó por correo a {sent} persona(s).' if sent else '')
            elif action == 'editor_answer':
                answer_id = db.editor_answer(text_field('question_id', maximum=36), text_field('body', 20, 3000))
                sent = avisos.answer_published(answer_id)
                session['comunidad_notice'] = 'Respuesta del editor publicada.' + (f' Se avisó por correo a {sent} persona(s).' if sent else '')
            elif action == 'resolve_request':
                db.resolve_request(text_field('request_id', maximum=36))
                session['comunidad_notice'] = 'Solicitud marcada como atendida. Se retiraron el correo y el texto del buzón.'
            else:
                raise ValueError('Acción desconocida.')
            return redirect(url_for('comunidad.admin'), 303)
        except ValueError as exc:
            return page('admin.html', 'Panel de comunidad', '/comunidad/admin/', logged=authenticated(),
                        rows=db.queue() if authenticated() else [], noindex=True, error=str(exc), status=400)
        except Exception:
            current_app.logger.exception('Panel comunitario no disponible')
            return page('message.html', 'Panel temporalmente no disponible', '/comunidad/admin/', noindex=True, status=503,
                        error='No pudimos completar la operación. Intentá nuevamente.')
    try:
        logged = authenticated()
        return page('admin.html', 'Panel de comunidad', '/comunidad/admin/', logged=logged,
                    rows=db.queue() if logged else [], inbox=db.private_requests() if logged else [],
                    stats=db.admin_stats() if logged else {}, channels={'telegram': avisos.telegram_ready(), 'email': avisos.email_ready()},
                    question_path=cc.question_path, noindex=True)
    except Exception:
        return page('message.html', 'Panel temporalmente no disponible', '/comunidad/admin/', noindex=True, status=503,
                    error='No pudimos leer los aportes. Intentá nuevamente.')


@bp.get('/api/comunidad/resumen')
def daily_digest():
    """Cron diario de Vercel (Authorization: Bearer CRON_SECRET): resumen al editor y limpieza de avisos vencidos."""
    import json
    secret = os.environ.get('CRON_SECRET', '')
    header = request.headers.get('Authorization', '')
    token = header[7:].strip() if header.startswith('Bearer ') else ''
    if not secret or not token or not hmac.compare_digest(token, secret):
        return Response(json.dumps({'error': 'No autorizado'}), 401, content_type='application/json')
    if not db.readable():
        return Response(json.dumps({'error': 'Almacenamiento no disponible'}), 503, content_type='application/json')
    try:
        summary = avisos.daily_digest()
    except Exception:
        current_app.logger.exception('Falló el resumen diario de la comunidad')
        return Response(json.dumps({'error': 'Falló el resumen'}), 500, content_type='application/json')
    return Response(json.dumps(summary, ensure_ascii=False), 200, content_type='application/json')
