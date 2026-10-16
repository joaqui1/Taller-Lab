"""Redacción pública sin notas administrativas de enlaces o tareas internas."""
import re
from html.parser import HTMLParser
from html import escape
from urllib.parse import urlsplit


def es_enlace_afiliado(url):
    """Los enlaces de afiliado recibidos usan el dominio corto de Mercado Libre."""
    try:
        parsed = urlsplit(url)
        return (parsed.scheme == 'https' and parsed.netloc.lower() == 'meli.la'
                and re.fullmatch(r'/[A-Za-z0-9]+', parsed.path) is not None)
    except ValueError:
        return False


def _antes_del_pie(html, fragmento):
    """Inserta en el pie del sitio: el último </footer>, no los <footer> internos del contenido."""
    inicio, separador, fin = html.rpartition('</footer>')
    if not separador:
        return html
    return f'{inicio}{fragmento}\n  </footer>{fin}'


class _AtributosEnlace(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.attrs = dict(attrs)


def quitar_enlaces_compra_sin_afiliacion(html):
    """Quita botones comerciales; conserva fuentes, manuales y navegación interna."""
    def filtrar(match):
        parser = _AtributosEnlace()
        parser.feed(match.group(1))
        attrs = getattr(parser, 'attrs', {})
        href = attrs.get('href') or ''
        clases = set((attrs.get('class') or '').split())
        comercial = clases.intersection({'offer-button', 'buying-link', 'btn-mercado-libre', 'catalog-link'})
        if comercial and href.startswith(('https://', 'http://', '//')) and not es_enlace_afiliado(href):
            return ''
        return match.group(0)
    html = re.sub(r'(<a\b[^>]*>).*?</a\s*>', filtrar, html, flags=re.S | re.I)
    return re.sub(r'<div\b[^>]*class="offer-actions"[^>]*>\s*</div>', '', html)

REPLACEMENTS = {
    'Afiliación y correcciones': 'Correcciones',
    'Dos publicaciones afiliadas: primero cerrar la potencia nominal': 'Dos opciones por potencia y uso',
    'Ofertas argentinas pendientes de verificación': 'Publicaciones comerciales en Argentina',
    'La publicación afiliada pendiente no identifica esta variante; este enlace es a la ficha del código exacto.': 'Ficha del código exacto 9.398-295.0.',
    'Se compara la referencia argentina RE020114544; no se utiliza la oferta pendiente que anuncia 60 Hz.': 'Referencia argentina RE020114544 de 50 Hz.',
    'Ofertas comerciales: no se usan como documentación de especificaciones; las de Kommberg, Daewoo y KLD quedan pendientes de verificar.': 'Publicaciones comerciales; consultá las prestaciones en la ficha del código exacto.',
    'Identidad pendiente: pedir aclaración al vendedor': 'Cotejá el código -8/-9 con la placa del equipo',
    'deja nominal pendiente': 'no informa potencia nominal',
    '20 V anunciados; condición pendiente': '20 V anunciados; condición no informada',
    '550 W anunciados; régimen pendiente': '550 W anunciados; régimen no informado',
    'Cinco; rango pendiente': 'Cinco; rango no informado',
    'capacidades por material pendientes': 'capacidades por material no informadas',
    'total pendiente de cotización': 'sumá la cotización de los tres componentes',
    'el cuerpo sin batería tiene costos pendientes': 'al precio del cuerpo sumá batería y cargador',
    'sin resolver una medida pendiente': 'sin garantizar la capacidad para tu pieza',
    'Un dato no publicado queda pendiente de confirmación.': 'Los datos que no publica el fabricante se indican como no informados.',
    'un dato ausente o no verificable figura como pendiente': 'un dato ausente o no verificable figura como no informado',
    'quedan pendientes de verificar': 'deben cotejarse por código y configuración',
    'el resumen de pendientes no se actualiza': 'el resumen de la lista no se actualiza',
    'Ficha y foto oficiales; enlace suministrado por el usuario': 'Ficha y foto oficiales',
    'Foto y ficha del fabricante; enlace suministrado por el usuario': 'Foto y ficha del fabricante',
    'Publicaciones con enlace de afiliado': 'Opciones de compra',
    'Opciones con enlace de afiliado': 'Opciones de compra',
    'Algunos enlaces comerciales son de afiliado y pueden atribuir una compra a TallerLab; el sitio no recibe tus datos de pago.': 'El servicio externo puede atribuir una compra a TallerLab mediante el enlace; el sitio no recibe tus datos de pago.',
    'Fuentes, variables de comparación, precios, opiniones, pruebas propias y afiliación de TallerLab.': 'Fuentes, variables de comparación, precios, opiniones y revisión documental de TallerLab.',
}

def limpiar_contenido_publico(html):
    html = quitar_enlaces_compra_sin_afiliacion(html)
    # Las tarjetas antiguas en Markdown también pueden incluir botones de fuente.
    html=re.sub(r'<a\b[^>]*class="[^"]*\boffer-source\b[^"]*"[^>]*>.*?</a>', '', html, flags=re.S)
    for before, after in REPLACEMENTS.items():
        html=html.replace(before,after)
    # Quitar avisos comerciales, conservando los enlaces y las condiciones técnicas.
    html=re.sub(r'<p\b[^>]*>\s*<strong>Aviso de afiliación:</strong>.*?</p>', '', html, flags=re.S)
    html=re.sub(r'(?:Enlaces? de afiliado:|Algunos enlaces son de afiliado:)\s*TallerLab puede recibir una comisión[^.]*\.', '', html)
    html=re.sub(r'(?:Algunos enlaces (?:(?:a|de) productos|comerciales|de compra)|En los enlaces de afiliado TallerLab)\s*(?:pueden generar|puede recibir) una comisión[^.]*\.', '', html)
    html=re.sub(r'TallerLab puede recibir una comisión por los enlaces de afiliado[^.]*\.', '', html)
    html=html.replace('Enlaces comerciales suministrados por el usuario.', '')
    html=html.replace('; no se verificó su contenido actual', '')
    # La página metodológica conserva su política de correcciones.
    html=re.sub(r'Cuando una opción encaja con el uso y tiene documentación suficiente, priorizamos ofrecer su enlace de afiliado\..*?las búsquedas generales no llevan esa etiqueta\.', '', html, flags=re.S)
    html=html.replace('publicación afiliada', 'publicación').replace('referencia afiliada', 'publicación')
    html=re.sub(r'<p\b[^>]*>\s*(?:<em>\s*</em>)?\s*</p>', '', html)
    return html


def apply_community_nav(html):
    """Muestra Comunidad en los menús solo cuando la participación está habilitada."""
    try:
        from comunidad import storage
        if not storage.enabled():
            return html
    except Exception:
        return html

    def add_link_to_menu(match):
        def with_community(anchor_match):
            attributes = anchor_match.group("attributes") or ""
            return anchor_match.group(0) + f'<a href="/comunidad/"{attributes}>Comunidad</a>'

        body = re.sub(
            r'<a href="/datos/precios-herramientas-argentina/"(?P<attributes>[^>]*)>Precios</a>',
            with_community,
            match.group("body"),
        )
        return match.group("opening") + body + match.group("closing")

    for menu_pattern in (
        r'(?P<opening><nav aria-label="Menú de navegación">)(?P<body>.*?)(?P<closing></nav>)',
        r'(?P<opening><nav class="nav-links">)(?P<body>.*?)(?P<closing></nav>)',
    ):
        html = re.sub(menu_pattern, add_link_to_menu, html, flags=re.S)
    return html


def _tiene_enlace_afiliado_publicado(html):
    """Detecta enlaces patrocinados de Mercado Libre en el HTML final de una página."""
    for match in re.finditer(r'<a\b[^>]*>', html, flags=re.I):
        parser = _AtributosEnlace()
        parser.feed(match.group(0))
        attrs = getattr(parser, 'attrs', {})
        href = attrs.get('href') or ''
        rel = set((attrs.get('rel') or '').lower().split())
        try:
            host = urlsplit(href).hostname or ''
        except ValueError:
            continue
        host = host.lower().rstrip('.')
        mercado_libre = host == 'meli.la' or host == 'mercadolibre.com.ar' or host.endswith('.mercadolibre.com.ar')
        if mercado_libre and 'sponsored' in rel:
            return True
    return False


class PublicTemplate(str):
    def format(self, *args, **kwargs):
        for key in ('CONTENT','PAGE_DESC'):
            if isinstance(kwargs.get(key),str):
                kwargs[key]=limpiar_contenido_publico(kwargs[key])
        html = super().format(*args,**kwargs)
        html = apply_community_nav(html)
        from publicaciones_autoridad import footer_authority_links
        authority_links = footer_authority_links()
        if authority_links:
            html = _antes_del_pie(html, f'<p class="footer-authority-links">{authority_links}</p>')
        from servidor_local import REVIEWERS_PATH, public_reviewers
        if public_reviewers():
            reviewer_link = f'<p class="footer-reviewer-link"><a href="{REVIEWERS_PATH}">Equipo de revisión</a></p>'
            html = _antes_del_pie(html, reviewer_link)
        from paginas_institucionales import contact_email
        email = contact_email()
        if email:
            address = escape(email)
            link = f'<p class="footer-email"><a href="mailto:{escape(email, quote=True)}">{address}</a></p>'
            html = _antes_del_pie(html, link)
        if _tiene_enlace_afiliado_publicado(html) and 'class="footer-affiliate-disclosure"' not in html:
            disclosure = ('<p class="footer-affiliate-disclosure">Podemos recibir una comisión si comprás desde estos enlaces. '
                          '<a href="/como-trabajamos/#afiliacion">Cómo funciona la afiliación</a>.</p>')
            html = _antes_del_pie(html, disclosure)
        return html
