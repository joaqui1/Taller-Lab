"""Entrada contextual sin cookies ni acceso a respuestas privadas en fichas técnicas.

También concentra las reglas SEO de la comunidad: umbrales de indexación, URLs de preguntas,
datos estructurados (QAPage, Review, AggregateRating) y rutas del sitemap.
"""
from html import escape
from urllib.parse import urlencode
import json
import re
import unicodedata

from comunidad import storage as db

# Una página de modelo se indexa con al menos 3 aportes útiles (experiencias o preguntas respondidas)
# y 150 palabras publicadas. Una pregunta se indexa en su propia URL cuando tiene una respuesta publicada.
MIN_CONTRIBUTIONS = 3
MIN_WORDS = 150
# El sondeo es por categoría y muestra porcentajes recién con 30 respuestas.
POLL_MIN = 30
# Resumen agregado (porcentajes) solo con 3 experiencias o más; promedio con 3 puntuaciones o más.
SUMMARY_MIN = 3
AUTHOR_PATH = '/autor/joaquin-vallasciani/'
# La portada /comunidad/ se indexa recién cuando enlaza a contenido real: al menos 3 páginas de modelo indexables.
# Mientras tanto queda «noindex, follow»: se puede visitar, compartir y enlazar, pero no compite como página vacía.
HUB_MIN_MODELS = 3


def hub_indexable(overview):
    return sum(1 for stats in (overview or {}).values() if model_indexable(stats)) >= HUB_MIN_MODELS


def absolute(path):
    from servidor_local import absolute_url
    return absolute_url(path)


def ascii_slug(text, limit=70):
    value = unicodedata.normalize('NFKD', (text or '').casefold()).encode('ascii', 'ignore').decode()
    value = re.sub('[^a-z0-9]+', '-', value).strip('-')
    if len(value) > limit:
        value = value[:limit].rsplit('-', 1)[0]
    return value or 'pregunta'


def excerpt(text, limit=160):
    text = ' '.join((text or '').split())
    return text if len(text) <= limit else text[:limit - 1].rsplit(' ', 1)[0] + '…'


def poll_scope(tool):
    return 'categoria:' + tool.category


def question_title(post):
    title = (post.get('context') or {}).get('title', '').strip()
    return title or excerpt(re.split(r'(?<=[?.!])\s', post.get('body', ''), maxsplit=1)[0], 110)


def question_path(slug, post):
    return f'/comunidad/modelos/{slug}/preguntas/{ascii_slug(question_title(post))}-{post["id"][:8]}/'


def stats_from_posts(posts):
    """Mismas claves que storage.overview(), calculadas sobre aportes ya publicados."""
    stats = {'reviews': 0, 'questions': 0, 'answers': 0, 'words': 0, 'ratings': [], 'repurchase': {},
             'usage': {}, 'answered_questions': [], 'last': ''}
    answered = {p['parent_id'] for p in posts if p['kind'] == 'answer'}
    for p in posts:
        ctx = p.get('context') or {}
        stats['words'] += db.word_count(p['body']) + sum(db.word_count(ctx.get(k, '')) for k in
                                                        ('task', 'advantages', 'problems', 'repair', 'title'))
        stats['last'] = max(stats['last'], p['created_at'])
        if p['kind'] == 'review':
            stats['reviews'] += 1
            if ctx.get('rating') in db.RATINGS:
                stats['ratings'].append(int(ctx['rating']))
            for key in ('repurchase', 'usage'):
                if ctx.get(key):
                    stats[key][ctx[key]] = stats[key].get(ctx[key], 0) + 1
        elif p['kind'] == 'question':
            stats['questions'] += 1
            if p['id'] in answered:
                stats['answered_questions'].append(p)
        else:
            stats['answers'] += 1
    return stats


def model_indexable(stats):
    if not stats:
        return False
    useful = stats['reviews'] + len(stats['answered_questions'])
    return useful >= MIN_CONTRIBUTIONS and stats['words'] >= MIN_WORDS


def review_summary(stats):
    """Datos agregados visibles; nunca se presentan como muestra representativa."""
    if not stats or stats['reviews'] < SUMMARY_MIN:
        return None
    total = stats['reviews']
    summary = {'count': total, 'repurchase_yes': stats['repurchase'].get('si', 0),
               'usage': [(db.USAGES[k], v) for k, v in sorted(stats['usage'].items(), key=lambda kv: -kv[1]) if k in db.USAGES]}
    ratings = stats['ratings']
    if len(ratings) >= SUMMARY_MIN:
        summary['rating'] = round(sum(ratings) / len(ratings), 1)
        summary['rating_count'] = len(ratings)
    return summary


def model_description(tool, stats):
    name = f'{tool.brand} {tool.model_name}'
    if stats and stats['reviews']:
        n = stats['reviews']
        return (f'{n} {"experiencia" if n == 1 else "experiencias"} de uso de {name} contadas por usuarios en Argentina: '
                'para qué la usan, cuánto tiempo, problemas y si la volverían a comprar. Preguntá por el modelo.')
    return f'Opiniones y experiencias de uso de {name}. Compartí para qué la usás y preguntá por el modelo a otros usuarios.'


def sort_answers(answers):
    return sorted(answers, key=lambda a: (not a.get('accepted'), not a.get('editor'), -a.get('helpful', 0), a['created_at']))


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + '</script>'


def breadcrumb_jsonld(items):
    return ld({'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': name, 'item': absolute(path)} for i, (name, path) in enumerate(items, 1)]})


def person(post):
    if post.get('editor'):
        return {'@type': 'Person', 'name': db.EDITOR_ALIAS, 'url': absolute(AUTHOR_PATH)}
    return {'@type': 'Person', 'name': post['alias']}


def product_ref(tool):
    return {'@type': 'Product', 'name': f'{tool.brand} {tool.model_name}', 'url': absolute(f'/herramientas/{tool.slug}/'),
            'brand': {'@type': 'Brand', 'name': tool.brand}}


def model_page_jsonld(tool, path, stats):
    data = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': f'{tool.brand} {tool.model_name}: opiniones y experiencias de usuarios',
            'url': absolute(path), 'inLanguage': 'es-AR', 'about': product_ref(tool),
            'isPartOf': {'@type': 'WebSite', 'name': 'TallerLab', 'url': absolute('/')}}
    if stats.get('last'):
        data['dateModified'] = stats['last']
    return ld(data)


def qapage_jsonld(tool, question, answers, path):
    url = absolute(path)
    def answer(a):
        return {'@type': 'Answer', 'text': a['body'], 'datePublished': a['created_at'], 'url': url + '#aporte-' + a['id'],
                'upvoteCount': a.get('helpful', 0), 'author': person(a)}
    entity = {'@type': 'Question', 'name': question['title'], 'text': question['body'], 'answerCount': len(answers),
              'datePublished': question['created_at'], 'author': person(question), 'about': product_ref(tool)}
    accepted = [a for a in answers if a.get('accepted')]
    if accepted:
        entity['acceptedAnswer'] = answer(accepted[0])
    others = [answer(a) for a in answers if not a.get('accepted')]
    if others:
        entity['suggestedAnswer'] = others
    return ld({'@context': 'https://schema.org', '@type': 'QAPage', 'mainEntity': entity})


def product_review_markup(slug):
    """Review/AggregateRating para el Product de la ficha: solo lo que la ficha muestra."""
    stats = db.safe_overview().get(slug)
    if not stats:
        return {}
    markup = {}
    reviews = [{'@type': 'Review', 'author': {'@type': 'Person', 'name': r['alias']}, 'datePublished': r['created_at'][:10],
                'reviewBody': r['body'], 'reviewRating': {'@type': 'Rating', 'ratingValue': int(r['context']['rating']),
                'bestRating': 5, 'worstRating': 1}} for r in stats['latest_reviews'] if r['context'].get('rating') in db.RATINGS]
    if reviews:
        markup['review'] = reviews
    summary = review_summary(stats)
    if summary and summary.get('rating'):
        markup['aggregateRating'] = {'@type': 'AggregateRating', 'ratingValue': summary['rating'],
                                     'ratingCount': summary['rating_count'], 'bestRating': 5, 'worstRating': 1}
    return markup


def community_sitemap_lastmod():
    """{ruta: fecha} solo de páginas con contenido suficiente; si la base no responde, devuelve {}."""
    from tallerlab_data.storage import get_tool_by_slug
    entries = {}
    for slug, stats in sorted(db.safe_overview().items()):
        if not get_tool_by_slug(slug):
            continue
        if model_indexable(stats):
            entries[f'/comunidad/modelos/{slug}/'] = stats['last'][:10]
        for question in stats['answered_questions']:
            entries[question_path(slug, question)] = question.get('last_answer', question['created_at'])[:10]
    return entries


def community_sitemap_excluded():
    """Rutas fijas de la comunidad que no deben ir al sitemap. Si la base no responde, no se excluye nada."""
    overview = db.overview_or_none()
    if overview is None or hub_indexable(overview):
        return set()
    return {'/comunidad/'}


def community_sitemap_paths():
    return list(community_sitemap_lastmod())


def category_polls(categories):
    try:
        results = db.all_poll_results()
    except Exception:
        return {}
    polls = {}
    for category in categories:
        counts = results.get('categoria:' + category, {})
        total = sum(counts.values())
        polls[category] = {'counts': counts, 'total': total, 'visible': total >= POLL_MIN}
    return polls


def stars(value):
    value = int(value)
    return '★' * value + '☆' * (5 - value)


def activity_label(stats):
    if not stats:
        return ''
    parts = []
    if stats['reviews']:
        parts.append(f"{stats['reviews']} {'experiencia' if stats['reviews'] == 1 else 'experiencias'}")
    if stats['questions']:
        parts.append(f"{stats['questions']} {'pregunta' if stats['questions'] == 1 else 'preguntas'}")
    return ' · '.join(parts)


def render_model_community(tool):
    """Bloque de la ficha técnica: muestra aportes publicados (renderizados en servidor) sin crear sesión."""
    slug = escape(tool.slug, quote=True)
    name = escape(tool.brand + ' ' + tool.model_name)
    base = f'/comunidad/modelos/{slug}/'
    stats = db.safe_overview().get(tool.slug)
    actions = f'''<div class="co-teaser-actions"><a href="{base}#contar">Contar mi experiencia</a>
      <a href="{base}#preguntas">Preguntar sobre este modelo</a>
      <a href="{base}#sondeo">Participar del sondeo</a></div>'''
    if not stats or not (stats['reviews'] or stats['questions']):
        return f'''<link rel="stylesheet" href="/assets/comunidad.css?v=3">
    <section class="co-teaser" id="comunidad-modelo" aria-label="Comunidad de este modelo">
      <p class="co-kicker">TallerLab Comunidad</p><h2>Opiniones de usuarios de {name}</h2>
      <p>Todavía no hay experiencias publicadas. ¿La usás? Contá para qué y cuánto tiempo: tu relato ayuda a otra persona a elegir.</p>
      {actions}
    </section>'''
    summary = review_summary(stats)
    lines = []
    if summary:
        line = f"{summary['count']} experiencias publicadas · {summary['repurchase_yes']} de {summary['count']} la volverían a comprar"
        if summary.get('rating'):
            line += f" · Puntuación media {str(summary['rating']).replace('.', ',')}/5 ({summary['rating_count']} valoraciones)"
        lines.append(f'<p class="co-summary-line">{escape(line)}</p>')
    cards = []
    for r in stats['latest_reviews']:
        ctx = r['context']
        meta = ' · '.join(x for x in [db.USAGES.get(ctx.get('usage'), ''), db.DURATIONS.get(ctx.get('duration'), ''),
                                      db.FREQUENCIES.get(ctx.get('frequency'), '')] if x)
        rating = f'<p class="co-rating" aria-label="Puntuación {ctx["rating"]} de 5">{stars(ctx["rating"])} <span>{ctx["rating"]}/5</span></p>' if ctx.get('rating') in db.RATINGS else ''
        task = f'<p><strong>Trabajo:</strong> {escape(ctx.get("task", ""))}</p>' if ctx.get('task') else ''
        cards.append(f'''<article class="co-post"><div class="co-post-head"><strong>{escape(r['alias'])}</strong>
        <time datetime="{escape(r['created_at'], quote=True)}">{escape(r['created_at'][:10])}</time></div>{rating}
        <p class="co-context">{escape(meta)}</p>{task}<p class="co-body">{escape(r['body'])}</p>
        <p class="co-badge">Experiencia declarada</p></article>''')
    questions = []
    for q in stats['latest_questions']:
        label = f"{q['answers']} {'respuesta' if q['answers'] == 1 else 'respuestas'}" if q['answers'] else 'Sin respuesta todavía'
        questions.append(f'<li><a href="{escape(question_path(tool.slug, q), quote=True)}">{escape(question_title(q))}</a> <span class="co-small">{label}</span></li>')
    questions_html = f'<h3>Preguntas recientes</h3><ul class="co-question-list">{"".join(questions)}</ul>' if questions else ''
    return f'''<link rel="stylesheet" href="/assets/comunidad.css?v=3">
    <section class="co-teaser co-model-reviews" id="comunidad-modelo" aria-label="Opiniones de usuarios">
      <p class="co-kicker">TallerLab Comunidad · experiencias declaradas</p><h2>Opiniones de usuarios de {name}</h2>
      {"".join(lines)}{"".join(cards)}{questions_html}
      <p><a href="{base}">Ver todas las opiniones y preguntas de {name} →</a></p>
      {actions}
    </section>'''


def guide_community_tools(article):
    """Require both an editorial association and an exact model/code mention."""
    from tallerlab_data.guide_links import get_tools_for_guide
    def ascii_text(value):
        return unicodedata.normalize('NFKD', value.casefold()).encode('ascii', 'ignore').decode()
    body = ascii_text(article.get('h1', '') + ' ' + article.get('body', ''))
    verified = []
    for tool in get_tools_for_guide(article['url']):
        brand = re.sub('[^a-z0-9]', '', ascii_text(tool.brand))
        full_code = re.sub('[^a-z0-9]', '', tool.slug)
        model_code = full_code[len(brand):] if full_code.startswith(brand) else full_code
        if model_code[:1].isdigit():
            model_code = full_code
        identifiers = [re.sub('[^a-z0-9]', '', ascii_text(tool.mpn or '')), model_code]
        for identifier in identifiers:
            if len(identifier) < 5:
                continue
            pattern = r'(?<![a-z0-9])' + r'[\W_]*'.join(map(re.escape, identifier)) + r'(?![a-z0-9])'
            if re.search(pattern, body):
                verified.append(tool)
                break
    return verified


def guide_community_search(article):
    from tallerlab_data.storage import get_all_categories
    category = article.get('section', '')
    categories = get_all_categories()
    return '/comunidad/?' + urlencode({'categoria': category}) if category in categories else '/comunidad/'


def render_guide_community_entry(article):
    """Acceso superior solo cuando hay contenido real que leer; si no, la guía conserva su foco."""
    tools = guide_community_tools(article)
    overview = db.safe_overview()
    total = sum(overview.get(t.slug, {}).get('reviews', 0) + overview.get(t.slug, {}).get('questions', 0) for t in tools)
    if not total:
        return ''
    label = f"Leer {total} {'opinión y pregunta' if total == 1 else 'opiniones y preguntas'} de usuarios"
    return f'<p class="co-guide-entry"><a href="#comunidad-guia">{label} →</a></p>'


def render_guide_community(article):
    tools = guide_community_tools(article)
    overview = db.safe_overview()
    items = []
    for tool in tools:
        name = escape(tool.brand + ' ' + tool.model_name)
        href = '/comunidad/modelos/' + escape(tool.slug, quote=True) + '/'
        activity = activity_label(overview.get(tool.slug))
        activity_html = f'<p class="co-small">{escape(activity)}</p>' if activity else ''
        items.append(f'''<li><h3>Opiniones de {name}</h3>{activity_html}<div class="co-teaser-actions">
            <a href="{href}#experiencias">Leer opiniones</a>
            <a href="{href}#contar">Contar mi experiencia</a>
            <a href="{href}#preguntar">Preguntar</a></div></li>''')
    selection = '<ul class="co-guide-models">' + ''.join(items) + '</ul>' if items else ''
    text = 'Elegí el modelo exacto para leer experiencias, compartir la tuya o hacer una pregunta.' if tools else (
        'Buscá tu equipo en el catálogo de la comunidad para leer experiencias, compartir la tuya o hacer una pregunta. '
        'Si no aparece, podés pedir que lo incorporemos desde el contacto privado.')
    return f'''<link rel="stylesheet" href="/assets/comunidad.css?v=3">
        <section class="co-teaser co-guide-community" id="comunidad-guia" aria-label="Comunidad de esta guía">
        <p class="co-kicker">TallerLab Comunidad</p><h2>La experiencia de uso también cuenta</h2>
        <p>{text}</p>{selection}<div class="co-teaser-actions">
        <a href="{escape(guide_community_search(article), quote=True)}">Buscar otro modelo</a>
        <a href="/comunidad/contacto/">Pedir un modelo o enviar una consulta</a></div></section>'''
