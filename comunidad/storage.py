"""Almacenamiento comunitario separado del catálogo y del estudio anual."""
import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'datos_comunidad' / 'comunidad.db'
POLL_ID = 'prioridad-compra-v1'
POLL_OPTIONS = {'tarea': 'Que resuelva mi trabajo', 'precio': 'Precio y costo completo',
                'repuestos': 'Repuestos y servicio', 'bateria': 'Mi plataforma de batería'}
USAGES = {'profesional': 'Trabajo remunerado', 'mixto': 'Uso mixto', 'domestico': 'Uso personal'}
DURATIONS = {'menos_3': 'Menos de 3 meses', '3_12': 'De 3 a 12 meses',
             '1_3': 'De 1 a 3 años', 'mas_3': 'Más de 3 años'}
FREQUENCIES = {'diario': 'A diario', 'semanal': 'Semanal', 'ocasional': 'Ocasional'}
NOTICE_VERSION = 'comunidad-2026-10-05-v4'
RATINGS = {'5': 'Excelente', '4': 'Buena', '3': 'Correcta', '2': 'Floja', '1': 'Mala'}
EDITOR_ACTOR = 'editor:tallerlab'
EDITOR_ALIAS = 'Joaquín Vallasciani'
# Las tablas se crean una sola vez por proceso y base, no en cada lectura.
_READY = set()
_CACHE = {}
CACHE_SECONDS = 120


def production():
    return bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV') or os.environ.get('APP_ENV') == 'production')


def readable():
    return not production() or bool(os.environ.get('COMUNIDAD_DATABASE_URL'))


def enabled():
    flag = os.environ.get('COMUNIDAD_HABILITADA', '0' if production() else '1')
    secret = os.environ.get('COMUNIDAD_SESSION_SECRET') or os.environ.get('RELEVAMIENTO_SESSION_SECRET', '')
    return flag.lower() in ('1', 'true') and readable() and (
        not production() or (len(secret) >= 32 and bool(os.environ.get('COMUNIDAD_ADMIN_KEY'))))


def _request_scope():
    """Contexto de Flask donde guardar la conexión compartida del request, o None fuera de un request."""
    try:
        from flask import g, has_app_context
    except ImportError:
        return None
    return g if has_app_context() else None


def close_request_connection(_exc=None):
    """Se registra como teardown de la app: cierra la conexión PostgreSQL compartida del request."""
    scope = _request_scope()
    conn = scope.pop('_comunidad_pg', None) if scope is not None else None
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass


def _open_postgres(dsn):
    from psycopg import connect
    from psycopg.rows import dict_row
    from relevamiento_piloto import PostgresConnection
    return PostgresConnection(connect(dsn, row_factory=dict_row, connect_timeout=10))


def _ensure_schema(conn, key):
    if key not in _READY:
        with conn:
            for sql in SCHEMA:
                conn.execute(sql)
        _READY.add(key)


@contextmanager
def connection():
    dsn = os.environ.get('COMUNIDAD_DATABASE_URL', '')
    scope = _request_scope() if dsn else None
    if scope is not None:
        # PostgreSQL: una sola conexión por request (antes, un envío abría 4 o 5 conexiones TLS nuevas).
        shared = scope.get('_comunidad_pg')
        if shared is not None and getattr(shared, '_comunidad_dsn', None) != dsn:
            close_request_connection()
            shared = None
        if shared is None:
            shared = _open_postgres(dsn)
            shared._comunidad_dsn = dsn
            scope._comunidad_pg = shared
        try:
            _ensure_schema(shared, dsn)
            yield shared
        except BaseException:
            # Una transacción abortada no debe contaminar las consultas siguientes del mismo request.
            try:
                shared.raw.rollback()
            except Exception:
                close_request_connection()
            raise
        return
    if dsn:
        conn = _open_postgres(dsn)
    else:
        if production():
            raise RuntimeError('La comunidad necesita almacenamiento persistente.')
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
    key = dsn or str(DB_PATH)
    try:
        _ensure_schema(conn, key)
        yield conn
    finally:
        conn.close()


def storage_key():
    return os.environ.get('COMUNIDAD_DATABASE_URL', '') or str(DB_PATH)


def clear_cache():
    _CACHE.clear()


def word_count(text):
    return len((text or '').split())


SCHEMA = [
    '''CREATE TABLE IF NOT EXISTS comunidad_posts (
      id TEXT PRIMARY KEY, actor TEXT NOT NULL, tool_slug TEXT NOT NULL,
      kind TEXT NOT NULL, parent_id TEXT REFERENCES comunidad_posts(id),
      state TEXT NOT NULL DEFAULT 'pending', alias TEXT NOT NULL, body TEXT NOT NULL,
      context_json TEXT NOT NULL, created_at TEXT NOT NULL, notice_version TEXT NOT NULL)''',
    'CREATE INDEX IF NOT EXISTS comunidad_tool_state ON comunidad_posts(tool_slug, state, created_at)',
    '''CREATE TABLE IF NOT EXISTS comunidad_helpful (
      post_id TEXT NOT NULL REFERENCES comunidad_posts(id), actor TEXT NOT NULL,
      PRIMARY KEY(post_id, actor))''',
    '''CREATE TABLE IF NOT EXISTS comunidad_accepted (
      question_id TEXT PRIMARY KEY REFERENCES comunidad_posts(id),
      answer_id TEXT NOT NULL REFERENCES comunidad_posts(id))''',
    '''CREATE TABLE IF NOT EXISTS comunidad_polls (
      tool_slug TEXT NOT NULL, poll_id TEXT NOT NULL, actor TEXT NOT NULL, option_id TEXT NOT NULL,
      created_at TEXT NOT NULL, PRIMARY KEY(tool_slug, poll_id, actor))''',
    # «window» es palabra reservada en PostgreSQL: va siempre entre comillas.
    '''CREATE TABLE IF NOT EXISTS comunidad_limits (
      key TEXT NOT NULL, "window" INTEGER NOT NULL, count INTEGER NOT NULL,
      PRIMARY KEY(key, "window"))''',
    '''CREATE TABLE IF NOT EXISTS comunidad_audit (
      id TEXT PRIMARY KEY, post_id TEXT NOT NULL REFERENCES comunidad_posts(id),
      state TEXT NOT NULL, reason TEXT NOT NULL, created_at TEXT NOT NULL)''',
    # Avisos de respuesta: correo opcional de quien pregunta. Se borra al enviarse o a los 180 días.
    '''CREATE TABLE IF NOT EXISTS comunidad_avisos (
      id TEXT PRIMARY KEY, question_id TEXT NOT NULL REFERENCES comunidad_posts(id),
      email TEXT NOT NULL, created_at TEXT NOT NULL)''',
    '''CREATE TABLE IF NOT EXISTS comunidad_requests (
      id TEXT PRIMARY KEY, actor TEXT NOT NULL, email TEXT NOT NULL, body TEXT NOT NULL,
      state TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL)''',
]


def now():
    return datetime.now(timezone.utc).isoformat()


def valid_uuid(value):
    try:
        return isinstance(value, str) and str(uuid.UUID(value)) == value
    except (ValueError, AttributeError):
        return False


def rate_allowed(key, maximum=15):
    import time
    window = int(time.time() // 3600)
    with connection() as conn, conn:
        row = conn.execute('''INSERT INTO comunidad_limits(key,"window",count) VALUES(?,?,1)
          ON CONFLICT(key,"window") DO UPDATE SET count=comunidad_limits.count+1 RETURNING count''',
                           (key, window)).fetchone()
        conn.execute('DELETE FROM comunidad_limits WHERE "window" < ?', (window - 48,))
        return row['count'] <= maximum


def save_post(post_id, actor, slug, kind, alias, body, context, parent=None, notify_email=''):
    with connection() as conn, conn:
        if parent:
            row = conn.execute("SELECT * FROM comunidad_posts WHERE id=? AND state='published'", (parent,)).fetchone()
            if not row or row['kind'] != 'question' or row['tool_slug'] != slug:
                raise ValueError('La pregunta ya no está disponible para responder.')
        existing = conn.execute('SELECT * FROM comunidad_posts WHERE id=?', (post_id,)).fetchone()
        if existing:
            if (existing['actor'], existing['tool_slug'], existing['kind'], existing['parent_id'],
                existing['alias'], existing['body'], existing['context_json']) != (
                    actor, slug, kind, parent, alias, body, json.dumps(context, ensure_ascii=False, sort_keys=True)):
                raise ValueError('Este envío ya se utilizó. Abrí un formulario nuevo.')
            return post_id
        conn.execute('''INSERT INTO comunidad_posts
            (id,actor,tool_slug,kind,parent_id,alias,body,context_json,created_at,notice_version)
            VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO NOTHING''',
            (post_id, actor, slug, kind, parent, alias, body,
             json.dumps(context, ensure_ascii=False, sort_keys=True), now(), NOTICE_VERSION))
        if notify_email and kind == 'question':
            conn.execute('INSERT INTO comunidad_avisos(id,question_id,email,created_at) VALUES(?,?,?,?) ON CONFLICT(id) DO NOTHING',
                         (post_id, post_id, notify_email, now()))
        # Validate the winner of a concurrent insert with the same idempotency key.
        winner = conn.execute('SELECT * FROM comunidad_posts WHERE id=?', (post_id,)).fetchone()
        if (winner['actor'], winner['tool_slug'], winner['kind'], winner['parent_id'], winner['alias'],
            winner['body'], winner['context_json']) != (actor, slug, kind, parent, alias, body,
                    json.dumps(context, ensure_ascii=False, sort_keys=True)):
            raise ValueError('Este envío ya se utilizó. Abrí un formulario nuevo.')
    return post_id


def _visible(conn, slug, actor):
        rows = conn.execute('''SELECT p.*, (SELECT COUNT(*) FROM comunidad_helpful h WHERE h.post_id=p.id) AS helpful,
            (SELECT COUNT(*) FROM comunidad_helpful h WHERE h.post_id=p.id AND h.actor=?) AS voted,
            (SELECT COUNT(*) FROM comunidad_accepted a WHERE a.answer_id=p.id) AS accepted
            FROM comunidad_posts p WHERE p.tool_slug=? AND p.state='published'
            AND (p.parent_id IS NULL OR EXISTS (SELECT 1 FROM comunidad_posts q WHERE q.id=p.parent_id AND q.state='published'))
            ORDER BY p.created_at DESC LIMIT 300''', (actor, slug)).fetchall()
        return [dict(row, context=json.loads(row['context_json']), own=row['actor'] == actor,
                     editor=row['actor'] == EDITOR_ACTOR) for row in rows]


def visible_posts(slug, actor=''):
    with connection() as conn:
        return _visible(conn, slug, actor)


def snapshot(slug, actor, poll_scope):
    """Todo lo que necesita una página de modelo en una sola conexión."""
    with connection() as conn:
        posts = _visible(conn, slug, actor)
        mine = [dict(r) for r in conn.execute('''SELECT id,kind,state,body FROM comunidad_posts
            WHERE tool_slug=? AND actor=? ORDER BY created_at DESC LIMIT 50''', (slug, actor)).fetchall()] if actor else []
        counts, choice = _poll(conn, poll_scope, actor)
    return posts, mine, counts, choice


def find_question(slug, short_id):
    if not short_id or len(short_id) != 8 or any(c not in '0123456789abcdef' for c in short_id):
        return None
    with connection() as conn:
        rows = conn.execute('''SELECT id FROM comunidad_posts WHERE tool_slug=? AND kind='question'
            AND state='published' AND id LIKE ?''', (slug, short_id + '%')).fetchall()
    return rows[0]['id'] if len(rows) == 1 else None


def overview():
    """Resumen público por modelo (solo aportes publicados), con caché breve en memoria."""
    import time
    key = storage_key()
    hit = _CACHE.get(key)
    if hit and hit[0] > time.time():
        return hit[1]
    with connection() as conn:
        rows = conn.execute('''SELECT p.id,p.tool_slug,p.kind,p.parent_id,p.alias,p.body,p.context_json,p.created_at,p.actor,
            (SELECT COUNT(*) FROM comunidad_helpful h WHERE h.post_id=p.id) AS helpful
            FROM comunidad_posts p WHERE p.state='published'
            AND (p.parent_id IS NULL OR EXISTS (SELECT 1 FROM comunidad_posts q WHERE q.id=p.parent_id AND q.state='published'))
            ORDER BY p.created_at DESC''').fetchall()
    data = {}
    answered = {}
    last_answer = {}
    for row in rows:
        if row['kind'] == 'answer':
            answered[row['parent_id']] = answered.get(row['parent_id'], 0) + 1
            last_answer[row['parent_id']] = max(last_answer.get(row['parent_id'], ''), row['created_at'])
    for row in rows:
        item = dict(row, context=json.loads(row['context_json']), editor=row['actor'] == EDITOR_ACTOR)
        item.pop('actor', None)
        stats = data.setdefault(row['tool_slug'], {'reviews': 0, 'questions': 0, 'answers': 0, 'words': 0,
            'last': '', 'ratings': [], 'repurchase': {}, 'usage': {}, 'latest_reviews': [], 'latest_questions': [],
            'answered_questions': []})
        stats['words'] += word_count(row['body']) + sum(word_count(item['context'].get(k, ''))
            for k in ('task', 'advantages', 'problems', 'repair', 'title'))
        stats['last'] = max(stats['last'], row['created_at'])
        if row['kind'] == 'review':
            stats['reviews'] += 1
            ctx = item['context']
            if ctx.get('rating') in RATINGS:
                stats['ratings'].append(int(ctx['rating']))
            if ctx.get('repurchase'):
                stats['repurchase'][ctx['repurchase']] = stats['repurchase'].get(ctx['repurchase'], 0) + 1
            if ctx.get('usage'):
                stats['usage'][ctx['usage']] = stats['usage'].get(ctx['usage'], 0) + 1
            if len(stats['latest_reviews']) < 3:
                stats['latest_reviews'].append(item)
        elif row['kind'] == 'question':
            stats['questions'] += 1
            item['answers'] = answered.get(row['id'], 0)
            item['last_answer'] = last_answer.get(row['id'], row['created_at'])
            if item['answers']:
                stats['answered_questions'].append(item)
            if len(stats['latest_questions']) < 3:
                stats['latest_questions'].append(item)
        else:
            stats['answers'] += 1
    _CACHE[key] = (time.time() + CACHE_SECONDS, data)
    return data


def safe_overview():
    """Las fichas y guías nunca deben fallar por la comunidad."""
    if not readable():
        return {}
    try:
        return overview()
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Resumen de comunidad no disponible')
        # Mejor el último resumen conocido (aunque haya vencido) que vaciar fichas, guías y sitemap por una caída breve.
        stale = _CACHE.get(storage_key())
        return stale[1] if stale else {}


def overview_or_none():
    """Como safe_overview, pero devuelve None si no hay ni datos frescos ni un resumen anterior."""
    if not readable():
        return {}
    try:
        return overview()
    except Exception:
        import logging
        logging.getLogger(__name__).exception('Resumen de comunidad no disponible')
        stale = _CACHE.get(storage_key())
        return stale[1] if stale else None


def own_posts(slug, actor):
    with connection() as conn:
        return [dict(r) for r in conn.execute('''SELECT id,kind,state,body FROM comunidad_posts
            WHERE tool_slug=? AND actor=? ORDER BY created_at DESC LIMIT 50''', (slug, actor)).fetchall()]


def moderate(post_id, state, reason):
    if state not in ('published', 'rejected') or not valid_uuid(post_id) or not 3 <= len(reason) <= 500:
        raise ValueError('Indicá una decisión y un motivo de revisión.')
    with connection() as conn, conn:
        suffix = ' FOR UPDATE' if not isinstance(conn, sqlite3.Connection) else ''
        if isinstance(conn, sqlite3.Connection):
            conn.execute('BEGIN IMMEDIATE')
        row = conn.execute('SELECT * FROM comunidad_posts WHERE id=?' + suffix, (post_id,)).fetchone()
        if not row or row['state'] == 'withdrawn':
            raise ValueError('El aporte fue retirado o ya no está disponible.')
        if state == 'published' and row['parent_id']:
            parent = conn.execute("SELECT state FROM comunidad_posts WHERE id=?", (row['parent_id'],)).fetchone()
            if not parent or parent['state'] != 'published':
                raise ValueError('Publicá la pregunta antes de aprobar una respuesta.')
        conn.execute('UPDATE comunidad_posts SET state=? WHERE id=?', (state, post_id))
        conn.execute('INSERT INTO comunidad_audit VALUES(?,?,?,?,?)', (str(uuid.uuid4()), post_id, state, reason, now()))
    clear_cache()


def editor_answer(question_id, body):
    """Respuesta identificada del editor: se publica directamente y queda auditada."""
    if not valid_uuid(question_id) or not 20 <= len(body.strip()) <= 3000:
        raise ValueError('La respuesta del editor debe tener entre 20 y 3000 caracteres.')
    with connection() as conn, conn:
        q = conn.execute("SELECT * FROM comunidad_posts WHERE id=? AND state='published' AND kind='question'", (question_id,)).fetchone()
        if not q:
            raise ValueError('Publicá la pregunta antes de responderla como editor.')
        post_id = str(uuid.uuid4())
        conn.execute('''INSERT INTO comunidad_posts
            (id,actor,tool_slug,kind,parent_id,state,alias,body,context_json,created_at,notice_version)
            VALUES(?,?,?,?,?,?,?,?,?,?,?)''', (post_id, EDITOR_ACTOR, q['tool_slug'], 'answer', question_id, 'published',
            EDITOR_ALIAS, body.strip(), json.dumps({'role': 'editor'}), now(), NOTICE_VERSION))
        conn.execute('INSERT INTO comunidad_audit VALUES(?,?,?,?,?)', (str(uuid.uuid4()), post_id, 'published', 'Respuesta del editor', now()))
    clear_cache()
    return post_id


def queue():
    with connection() as conn:
        return [dict(r, context=json.loads(r['context_json'])) for r in conn.execute(
            "SELECT * FROM comunidad_posts WHERE state IN ('pending','published','rejected') ORDER BY CASE WHEN state='pending' THEN 0 ELSE 1 END,created_at DESC LIMIT 200").fetchall()]


def withdraw(post_id, actor):
    with connection() as conn, conn:
        changed = conn.execute("UPDATE comunidad_posts SET state='withdrawn',alias='Retirado',body='',context_json='{}' WHERE id=? AND actor=? AND state!='withdrawn'", (post_id, actor)).rowcount
        if not changed:
            raise ValueError('No pudimos retirar ese aporte desde este navegador.')
        conn.execute('DELETE FROM comunidad_accepted WHERE question_id=? OR answer_id=?', (post_id, post_id))
        conn.execute('DELETE FROM comunidad_helpful WHERE post_id=?', (post_id,))
        conn.execute('DELETE FROM comunidad_avisos WHERE question_id=?', (post_id,))
    clear_cache()


def helpful(post_id, actor):
    with connection() as conn, conn:
        post = conn.execute("SELECT * FROM comunidad_posts WHERE id=? AND state='published'", (post_id,)).fetchone()
        if not post or post['actor'] == actor:
            raise ValueError('Elegí un aporte publicado de otra persona.')
        if post['parent_id'] and not conn.execute("SELECT id FROM comunidad_posts WHERE id=? AND state='published'", (post['parent_id'],)).fetchone():
            raise ValueError('La pregunta ya no está publicada.')
        conn.execute('INSERT INTO comunidad_helpful(post_id,actor) VALUES(?,?) ON CONFLICT(post_id,actor) DO NOTHING', (post_id, actor))


def accept(question_id, answer_id, actor):
    with connection() as conn, conn:
        q = conn.execute("SELECT * FROM comunidad_posts WHERE id=? AND state='published'", (question_id,)).fetchone()
        a = conn.execute("SELECT * FROM comunidad_posts WHERE id=? AND state='published'", (answer_id,)).fetchone()
        if not q or not a or q['actor'] != actor or q['kind'] != 'question' or a['kind'] != 'answer' or a['parent_id'] != question_id:
            raise ValueError('Solo quien preguntó puede elegir una respuesta publicada de esa pregunta.')
        conn.execute('INSERT INTO comunidad_accepted VALUES(?,?) ON CONFLICT(question_id) DO UPDATE SET answer_id=excluded.answer_id', (question_id, answer_id))


def poll_vote(slug, actor, option):
    if option not in POLL_OPTIONS:
        raise ValueError('Elegí una opción de la encuesta.')
    with connection() as conn, conn:
        conn.execute('''INSERT INTO comunidad_polls VALUES(?,?,?,?,?)
            ON CONFLICT(tool_slug,poll_id,actor) DO UPDATE SET option_id=excluded.option_id,created_at=excluded.created_at''',
                     (slug, POLL_ID, actor, option, now()))


def _poll(conn, scope, actor=''):
    counts = {r['option_id']: r['n'] for r in conn.execute('''SELECT option_id,COUNT(*) AS n FROM comunidad_polls
        WHERE tool_slug=? AND poll_id=? GROUP BY option_id''', (scope, POLL_ID)).fetchall()}
    choice = conn.execute('SELECT option_id FROM comunidad_polls WHERE tool_slug=? AND poll_id=? AND actor=?', (scope, POLL_ID, actor)).fetchone()
    return counts, choice['option_id'] if choice else ''


def poll_results(scope, actor=''):
    """scope es «categoria:<categoría>»: el sondeo se agrega por categoría, no por modelo."""
    with connection() as conn:
        return _poll(conn, scope, actor)


def all_poll_results():
    with connection() as conn:
        rows = conn.execute('''SELECT tool_slug,option_id,COUNT(*) AS n FROM comunidad_polls WHERE poll_id=?
            GROUP BY tool_slug,option_id''', (POLL_ID,)).fetchall()
    result = {}
    for r in rows:
        result.setdefault(r['tool_slug'], {})[r['option_id']] = r['n']
    return result


def save_request(request_id, actor, email, body):
    with connection() as conn, conn:
        conn.execute('INSERT INTO comunidad_requests(id,actor,email,body,created_at) VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING',
                     (request_id, actor, email, body, now()))
        row = conn.execute('SELECT * FROM comunidad_requests WHERE id=?', (request_id,)).fetchone()
        if (row['actor'], row['email'], row['body']) != (actor, email, body):
            raise ValueError('Este envío ya se utilizó. Abrí un formulario nuevo.')


def private_requests():
    with connection() as conn:
        return [dict(r) for r in conn.execute("SELECT id,email,body,created_at FROM comunidad_requests WHERE state='pending' ORDER BY created_at LIMIT 200").fetchall()]


def resolve_request(request_id):
    with connection() as conn, conn:
        result = conn.execute("UPDATE comunidad_requests SET state='resolved',email='',body='' WHERE id=? AND state='pending'", (request_id,))
        if not result.rowcount:
            raise ValueError('La solicitud no está pendiente.')


def get_post(post_id):
    if not valid_uuid(post_id):
        return None
    with connection() as conn:
        row = conn.execute('SELECT * FROM comunidad_posts WHERE id=?', (post_id,)).fetchone()
    return dict(row, context=json.loads(row['context_json']), editor=row['actor'] == EDITOR_ACTOR) if row else None


def notifications_for(question_id):
    with connection() as conn:
        return [dict(r) for r in conn.execute('SELECT id,email FROM comunidad_avisos WHERE question_id=?', (question_id,)).fetchall()]


def delete_notification(notification_id):
    with connection() as conn, conn:
        conn.execute('DELETE FROM comunidad_avisos WHERE id=?', (notification_id,))


def purge_notifications(days=180):
    from datetime import timedelta
    limit = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    with connection() as conn, conn:
        return conn.execute('DELETE FROM comunidad_avisos WHERE created_at < ?', (limit,)).rowcount


def admin_stats():
    """Indicadores para operar la comunidad sin herramientas externas."""
    from datetime import timedelta
    week = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    with connection() as conn:
        by_state = {(r['state'], r['kind']): r['n'] for r in conn.execute(
            'SELECT state,kind,COUNT(*) AS n FROM comunidad_posts GROUP BY state,kind').fetchall()}
        oldest = conn.execute("SELECT MIN(created_at) AS t FROM comunidad_posts WHERE state='pending'").fetchone()['t']
        week_posts = conn.execute('SELECT COUNT(*) AS n FROM comunidad_posts WHERE created_at >= ? AND actor != ?',
                                  (week, EDITOR_ACTOR)).fetchone()['n']
        requests = conn.execute("SELECT COUNT(*) AS n FROM comunidad_requests WHERE state='pending'").fetchone()['n']
        unanswered = [dict(r, context=json.loads(r['context_json'])) for r in conn.execute('''SELECT q.id,q.tool_slug,q.alias,q.body,q.context_json,q.created_at
            FROM comunidad_posts q WHERE q.kind='question' AND q.state='published' AND NOT EXISTS (
              SELECT 1 FROM comunidad_posts a WHERE a.parent_id=q.id AND a.state='published')
            ORDER BY q.created_at LIMIT 100''').fetchall()]
        polls = conn.execute('SELECT COUNT(*) AS n FROM comunidad_polls').fetchone()['n']
        subscribers = conn.execute('SELECT COUNT(*) AS n FROM comunidad_avisos').fetchone()['n']
    def count(state, kind=None):
        return sum(n for (st, k), n in by_state.items() if st == state and (kind is None or k == kind))
    return {'pending': count('pending'), 'published_reviews': count('published', 'review'),
            'published_questions': count('published', 'question'), 'published_answers': count('published', 'answer'),
            'rejected': count('rejected'), 'withdrawn': count('withdrawn'), 'oldest_pending': oldest or '',
            'week_posts': week_posts, 'requests': requests, 'unanswered': unanswered, 'polls': polls,
            'subscribers': subscribers}
