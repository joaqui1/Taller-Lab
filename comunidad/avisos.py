"""Avisos opcionales: Telegram para el editor y correo (Resend) para quien pregunta y el resumen diario.

Todo es de mejor esfuerzo: si no hay configuración o el servicio falla, la comunidad sigue funcionando.
Variables:
  COMUNIDAD_TELEGRAM_BOT_TOKEN, COMUNIDAD_TELEGRAM_CHAT_ID  -> aviso inmediato y resumen al editor.
  RESEND_API_KEY, COMUNIDAD_AVISOS_REMITENTE                -> correos (remitente de un dominio verificado).
  COMUNIDAD_AVISO_EDITOR_EMAIL                               -> destino del resumen diario por correo.
"""
import logging
import os

from comunidad import storage as db

log = logging.getLogger(__name__)
SITE = os.environ.get('SITE_URL', 'https://www.tallerlab.com.ar').rstrip('/')


def site_url(path):
    return os.environ.get('SITE_URL', SITE).rstrip('/') + path


def telegram_ready():
    return bool(os.environ.get('COMUNIDAD_TELEGRAM_BOT_TOKEN') and os.environ.get('COMUNIDAD_TELEGRAM_CHAT_ID'))


def email_ready():
    return bool(os.environ.get('RESEND_API_KEY') and os.environ.get('COMUNIDAD_AVISOS_REMITENTE'))


def send_telegram(text):
    if not telegram_ready():
        return False
    try:
        import requests
        token = os.environ['COMUNIDAD_TELEGRAM_BOT_TOKEN']
        res = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', timeout=5, json={
            'chat_id': os.environ['COMUNIDAD_TELEGRAM_CHAT_ID'], 'text': text[:3900], 'disable_web_page_preview': True})
        return res.ok
    except Exception:
        log.exception('No se pudo enviar el aviso de Telegram')
        return False


def send_email(to, subject, text):
    if not email_ready():
        return False
    try:
        import requests
        res = requests.post('https://api.resend.com/emails', timeout=8,
            headers={'Authorization': 'Bearer ' + os.environ['RESEND_API_KEY']},
            json={'from': os.environ['COMUNIDAD_AVISOS_REMITENTE'], 'to': [to], 'subject': subject, 'text': text})
        return res.ok
    except Exception:
        log.exception('No se pudo enviar el correo de la comunidad')
        return False


def new_contribution(kind, tool_slug):
    """Aviso inmediato al editor; no incluye el texto ni datos de la persona."""
    label = {'review': 'experiencia', 'question': 'pregunta', 'answer': 'respuesta', 'contact': 'solicitud privada'}.get(kind, kind)
    target = f' sobre {tool_slug}' if tool_slug else ''
    send_telegram(f'TallerLab: nueva {label}{target} para revisar.\n{site_url("/comunidad/admin/")}')


def answer_published(answer_id):
    """Avisa por correo, una sola vez, a quien pidió aviso para esa pregunta; luego borra el correo."""
    if not email_ready():
        return 0
    from comunidad.components import question_path
    from tallerlab_data.storage import get_tool_by_slug
    answer = db.get_post(answer_id)
    if not answer or answer['kind'] != 'answer' or answer['state'] != 'published':
        return 0
    question = db.get_post(answer['parent_id'])
    tool = get_tool_by_slug(question['tool_slug']) if question else None
    if not question or question['state'] != 'published' or not tool:
        return 0
    url = site_url(question_path(tool.slug, question))
    name = f'{tool.brand} {tool.model_name}'
    sent = 0
    for item in db.notifications_for(question['id']):
        text = (f'Hola. Publicamos una respuesta a tu pregunta sobre {name} en TallerLab:\n\n{url}\n\n'
                'Si te sirvió, podés marcarla como la respuesta que resolvió tu consulta desde el mismo navegador.\n\n'
                'Este es el único aviso: tu correo ya fue borrado de nuestra lista. No te suscribimos a nada.')
        if send_email(item['email'], f'Respondieron tu pregunta sobre {name}', text):
            db.delete_notification(item['id'])
            sent += 1
    return sent


def daily_digest():
    """Resumen diario para el editor. Devuelve el resumen aunque no haya canales configurados."""
    purged = db.purge_notifications()
    stats = db.admin_stats()
    lines = [f"Pendientes de moderar: {stats['pending']}" + (f" (el más antiguo: {stats['oldest_pending'][:10]})" if stats['oldest_pending'] else ''),
             f"Preguntas publicadas sin respuesta: {len(stats['unanswered'])}",
             f"Solicitudes privadas pendientes: {stats['requests']}",
             f"Aportes de usuarios en 7 días: {stats['week_posts']}",
             f"Publicado: {stats['published_reviews']} experiencias, {stats['published_questions']} preguntas, {stats['published_answers']} respuestas"]
    needs_action = stats['pending'] or stats['unanswered'] or stats['requests']
    text = 'TallerLab Comunidad · resumen diario\n\n' + '\n'.join(lines) + '\n\n' + site_url('/comunidad/admin/')
    channels = []
    if needs_action:
        if send_telegram(text):
            channels.append('telegram')
        editor = os.environ.get('COMUNIDAD_AVISO_EDITOR_EMAIL', '')
        if editor and send_email(editor, f"Comunidad: {stats['pending']} pendientes, {len(stats['unanswered'])} preguntas sin respuesta", text):
            channels.append('email')
    return {'pending': stats['pending'], 'unanswered': len(stats['unanswered']), 'requests': stats['requests'],
            'week_posts': stats['week_posts'], 'sent': channels, 'purged_notifications': purged}
