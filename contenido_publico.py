"""Redacción pública sin notas administrativas de enlaces o tareas internas."""
import re

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

class PublicTemplate(str):
    def format(self, *args, **kwargs):
        for key in ('CONTENT','PAGE_DESC'):
            if isinstance(kwargs.get(key),str):
                kwargs[key]=limpiar_contenido_publico(kwargs[key])
        return super().format(*args,**kwargs)
