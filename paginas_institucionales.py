"""Contenido de contacto y privacidad acorde al funcionamiento del sitio."""
import json
import os
import re
from pathlib import Path

_EMAIL = re.compile(r"[^\s<>@]+@[^\s<>@]+\.[^\s<>@]+")


def contact_email():
    """Correo editorial que realmente recibe: CONTACT_EMAIL (entorno) o email_publico de perfil_autor.json."""
    email = os.environ.get("CONTACT_EMAIL", "").strip()
    if not _EMAIL.fullmatch(email):
        try:
            data = json.loads(Path(__file__).with_name("perfil_autor.json").read_text(encoding="utf-8"))
            email = str(data.get("email_publico", "")).strip()
        except (OSError, ValueError):
            email = ""
    return email if _EMAIL.fullmatch(email) else ""


def private_mailbox_available():
    """El buzón privado solo se anuncia si puede guardar mensajes (misma condición que su formulario)."""
    try:
        from comunidad import storage
        return bool(storage.readable())
    except Exception:
        return False


CONTACT_INTRO = '''
TallerLab es editado por [Joaquín Vallasciani](/autor/joaquin-vallasciani/). Podés reportar un dato incorrecto, una fuente que dejó de funcionar o una oferta cuyo modelo no coincide con la guía.
'''

CONTACT_PUBLIC = '''
## Enviar una corrección pública

[Abrir un reporte en el repositorio de TallerLab](https://github.com/joaqui1/Taller-Lab/issues/new).

Indicá la URL de la guía, el dato que querés corregir y, si la tenés, una ficha o manual del fabricante. GitHub requiere una cuenta y los reportes son públicos: no incluyas datos personales, comprobantes de compra ni información privada.
'''

CONTACT_SCOPE = '''
## Alcance de las consultas

TallerLab publica investigación documental y no vende las herramientas enlazadas. Para envíos, pagos, devoluciones o garantías de una compra, contactá al vendedor o fabricante. Una guía no reemplaza el manual de la unidad ni una evaluación profesional de la instalación.
'''


def contact_markdown(email=None, mailbox=None):
    """Arma Contacto solo con canales que funcionan hoy; nunca promete un buzón deshabilitado."""
    email = contact_email() if email is None else email
    mailbox = private_mailbox_available() if mailbox is None else mailbox
    parts = [CONTACT_INTRO]
    if email:
        parts.append(f"""
## Escribir al editor

Para correcciones, consultas privadas, solicitudes de retiro o sobre tus datos: [{email}](mailto:{email}). La atención es manual; usamos tu correo solo para responder y no te suscribe a comunicaciones.
""")
    parts.append(CONTACT_PUBLIC)
    if mailbox:
        parts.append("""
## Comunidad y consultas privadas

Para reportar un aporte de la comunidad, solicitar su retiro o enviar información que no querés publicar, usá el [buzón privado de comunidad](/comunidad/contacto/). La atención es manual y no te suscribe a comunicaciones.
""")
    elif not email:
        parts.append("""
## Consultas privadas

Por ahora no hay un canal privado habilitado. Si necesitás enviar información que no querés publicar, abrí un reporte sin datos personales indicando que preferís contacto privado y te indicaremos cómo seguir.
""")
    parts.append(CONTACT_SCOPE)
    return "\n".join(p.strip("\n") + "\n" for p in parts)


# Compatibilidad: texto estático con los canales disponibles al importar.
CONTACT = contact_markdown(email="", mailbox=False)

PRIVACY = '''
TallerLab es un sitio de guías documentales editado por [Joaquín Vallasciani](/autor/joaquin-vallasciani/). Esta página describe el funcionamiento del sitio; no asegura que los servicios externos tengan la misma política.

## Navegación y clics comerciales

El código del sitio no instala Google Analytics ni píxeles publicitarios. Al hacer clic en un enlace comercial registramos la fecha y hora, la URL del producto, la ruta de la guía y la ubicación del enlace. Ese evento no incluye nombre, correo ni un identificador personal generado por TallerLab.

El proveedor de alojamiento, Vercel, puede procesar datos técnicos de las solicitudes, como dirección IP, navegador y URL, para prestar y proteger el servicio. Los eventos de clic quedan en registros del alojamiento. No hay una base de datos de cuentas de lectores ni un formulario que recolecte datos de compra. No prometemos anonimato ni un plazo de borrado que el servicio no tenga configurado.

## Participación en la comunidad

Las experiencias, preguntas y respuestas se guardan para revisión antes de publicar el alias, el texto y el contexto de uso autorizado. Una cookie de sesión permite reconocer tus aportes desde ese navegador y retirarlos; no es una cuenta ni verifica identidad o compra. Los sondeos registran una elección por navegador y pueden reemplazarse. Se conserva un identificador derivado de la conexión para limitar envíos; no se guarda la dirección IP en esas tablas. El alojamiento puede mantener sus propios registros técnicos.

Los borradores se guardan en el almacenamiento de sesión del navegador y pueden descartarse desde el formulario. Cuando está habilitado, el buzón privado recibe correo y mensaje para atención manual, y permite al editor borrarlos al dar la solicitud por atendida. Consultá los [criterios de publicación y datos de comunidad](/comunidad/criterios/) para conocer el alcance y solicitar el retiro cuando ya no conservás la sesión. Los motivos de moderación son privados.

## Recursos y enlaces de terceros

Las tipografías se sirven desde el alojamiento de TallerLab. Algunas imágenes se cargan desde servidores de fabricantes o comercios: esos servidores reciben una solicitud de tu navegador y pueden tratar datos técnicos conforme a sus propias políticas.

Cuando abrís un enlace a Mercado Libre, GitHub o una fuente externa, rigen las políticas de ese servicio. Algunos enlaces comerciales son de afiliado y pueden atribuir una compra a TallerLab; el sitio no recibe tus datos de pago. Consultá la [privacidad de Mercado Libre](https://www.mercadolibre.com.ar/privacidad), la [privacidad de Vercel](https://vercel.com/legal/privacy-policy) y la [privacidad de Google](https://policies.google.com/privacy).

## Consultas y correcciones

Los reportes enviados por GitHub son públicos. No incluyas información personal o privada en ellos. Consultá los canales disponibles en [Contacto](/contacto/).
'''
