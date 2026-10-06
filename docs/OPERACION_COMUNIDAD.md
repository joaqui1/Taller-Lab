# Comunidad de TallerLab

Primera versión implementada el 4 de octubre de 2026. El objetivo es construir evidencia de uso y conversaciones útiles alrededor de modelos identificados, junto a las fuentes técnicas. La autoridad dependerá de aportes reales, revisión editorial consistente y resultados publicados con sus límites.

## Recorrido disponible

- `/comunidad/`: búsqueda por marca, modelo, código y categoría del catálogo técnico.
- `/comunidad/modelos/<slug>/`: experiencias con tarea, duración, frecuencia, reparaciones; preguntas y respuestas; votos de utilidad; respuesta elegida por quien preguntó; sondeo por modelo con base y conteos.
- Los relatos pasan a pendiente. No se publican hasta que el editor los aprueba. Las críticas se revisan con los mismos criterios que los elogios.
- «Mis aportes» permite retirar tanto pendientes como publicados desde la sesión que los creó. Retirar una pregunta oculta también sus respuestas. No se puede republicar un aporte retirado.
- `/comunidad/criterios/`: criterios, consentimiento y alcance de los datos.
- `/comunidad/contacto/`: buzón privado para correcciones, apelaciones y solicitudes relativas a datos.
- `/comunidad/admin/`: acceso con clave; revisión y motivos privados; atención del buzón. Marcar una solicitud como atendida borra correo y mensaje. La respuesta al solicitante es manual, por el correo que indicó.

Las 179 guías publicadas tienen un acceso visible al comienzo y un bloque de comunidad. Un enlace directo requiere una asociación editorial existente y una mención exacta del modelo o código en el contenido de la guía; se excluyen asociaciones antiguas sin esa evidencia. Las otras guías abren el selector por categoría cuando esa categoría está cubierta, o el catálogo general. Para equipos todavía no incluidos se ofrece pedir su incorporación. Los filtros nunca apuntan a una categoría vacía. Las conversaciones enlazan de regreso a las guías editoriales confirmadas con el mismo criterio. Las fichas técnicas conservan su acceso directo. No se infieren equivalencias de producto a partir de una marca.

El formulario no pregunta relación con marcas ni mayoría de edad, tanto en relatos como en sondeos. Se conserva el consentimiento para publicar o registrar la elección. Aviso de publicación versión `comunidad-2026-10-04-v2`; los registros anteriores conservan su versión original. El H1 de la conversación identifica modelo y propósito: «opiniones y experiencias».

Los formularios funcionan mediante POST normal sin JavaScript. JavaScript añade borradores por pestaña, descarte y apertura de formularios desde enlaces. Se usan protección CSRF, escape de texto, límite de tamaño, controles de consentimiento, campo antispam, límites de envíos y claves de idempotencia para evitar duplicados por reintento. Las páginas personalizadas no se almacenan en cachés compartidas.

## Configuración para producción

En desarrollo se usa SQLite en `datos_comunidad/comunidad.db`, ignorado por Git. No cargar experiencias inventadas como si fueran aportes reales.

En Vercel o `APP_ENV=production`, no se permite SQLite como reemplazo de almacenamiento persistente. No se solicita mayoría de edad ni relación con marcas. Se mantiene el consentimiento para publicar. La participación permanece cerrada si falta configuración. Variables:

| Variable | Uso |
| --- | --- |
| `COMUNIDAD_DATABASE_URL` | PostgreSQL persistente propio para estos datos. El runtime necesita `psycopg`, ya incluido en requirements. |
| `COMUNIDAD_SESSION_SECRET` | Secreto aleatorio estable de al menos 32 caracteres. Firma la sesión compartida con el relevamiento. También puede usarse el secreto estable ya configurado en `RELEVAMIENTO_SESSION_SECRET`. |
| `COMUNIDAD_ADMIN_KEY` | Clave privada de moderación, distinta de las claves de otros módulos. |
| `COMUNIDAD_HABILITADA` | `1` abre participación una vez comprobada la configuración. `0` la cierra; los aportes publicados siguen legibles y el retiro propio sigue permitido. |

Si el relevamiento ya usa sesiones activas, conservar su secreto estable evita invalidarlas; si se configura un nuevo secreto prioritario se invalidan las cookies anteriores. La administración vence después de una hora. Rotar clave administrativa revoca sesiones administrativas; rotar el secreto de sesión también afecta el acceso a «Mis aportes».

Antes de abrir: configurar estas variables en el entorno de destino, preparar copias de seguridad y sus plazos de retención, comprobar acceso PostgreSQL, probar un envío y su moderación en un entorno de prueba y designar quien revisa aportes/buzón. No compartir secretos en capturas ni documentos del repositorio. No se realizó despliegue ni verificación contra PostgreSQL remoto en esta entrega.

La primera conexión crea tablas e índices idempotentemente. El usuario de base necesita esos permisos. Es posible ejecutar `with comunidad.storage.connection(): pass` en el entorno configurado para inicializar antes del primer envío. Mantener la base separada del estudio anual.

## Revisión editorial

Comprobar correspondencia con el modelo, contexto, datos privados, publicidad y abuso. No interpretar la clave de sesión como identidad, compra o profesión verificada. Para solicitudes recibidas sin sesión original, comprobar la relación con el aporte antes de revelar datos o retirarlo administrativamente. Las solicitudes se resuelven manualmente; el panel no automatiza verificaciones de identidad ni envía correos.

Evitar incluir datos personales en motivos de moderación. El retiro borra alias, texto y contexto del aporte y sus marcas de utilidad/respuesta elegida; el registro de decisión y los identificadores operativos permanecen. Las copias de seguridad requieren su propia política de eliminación.

Los límites de envío guardan una huella HMAC de la conexión y contador por hora; se limpian ventanas de más de 48 horas cuando hay nueva actividad. El código usa la dirección informada por el servidor y no acepta encabezados de proxy arbitrarios. Verificar el comportamiento del alojamiento antes de abrir para evitar que un proxy agrupe a toda la audiencia en un mismo límite.

## Alcance y siguientes mejoras

Una sesión por navegador no equivale a una persona única: borrar cookies permite votar nuevamente. El sondeo es exploratorio, no representativo de Argentina. Se muestran hasta 300 aportes públicos recientes y hasta 50 propios por modelo; el panel muestra 200 aportes y 200 solicitudes pendientes. Se deben ampliar paginación y cuentas/recuperación cuando el volumen lo requiera.

No hay fotos de comprobantes, insignias de compra verificada, notificaciones por correo ni perfiles profesionales públicos en esta versión. Son posibles siguientes etapas, junto al seguimiento a 6/12 meses y proyectos reales de taller. El estudio anual conserva metodología y consentimiento independientes: no convertir automáticamente opiniones o votos en datos del estudio.

## Verificación

`tests/test_comunidad.py` usa bases temporales dentro de `tmp`, sin modificar aportes reales. Cubre rutas, permisos, publicación, escape de HTML, duplicados, consentimiento, respuestas elegidas, retiro, utilidad, reemplazo de voto, buzón privado, límites concurrentes, claves por formulario y cierre en producción sin almacenamiento.

La prueba `tests/test_comunidad_browser.cjs` usa Edge a 390 y 1440 px. Las solicitudes pasan al cliente real de Flask por `tests/comunidad_browser_bridge.py`, un puente stdio debido a las restricciones de localhost del entorno; no simula la lógica de guardado. Comprueba ausencia de desborde horizontal, borrador al recargar, envío pendiente, limpieza del borrador y retiro. Capturas de revisión en `tmp/community-model-390.png` y `tmp/community-model-1440.png`. Este recorrido local no certifica despliegue ni persistencia remota.

Resultado local actualizado: 18 pruebas de comunidad y 8 pruebas existentes del catálogo aprobadas; recorrido de navegador aprobado e interfaces inspeccionadas en celular y escritorio. La comprobación de guías recorre las 179 publicadas, sus enlaces, destinos y anclas, además de verificar los filtros de categoría y excluir códigos parciales o modelos ajenos.

Investigación y prioridades: `investigacion-autoridad/producto-comunidad-referentes-2026-10-04.md` y `investigacion-autoridad/estrategia-relevamiento-comunidad-2026-10-04.md`.

## Mejoras SEO y de autoridad (5 de octubre de 2026)

Respaldo previo: `respaldos/respaldo-comunidad-antes-seo-2026-10-05.zip`.

- **PostgreSQL:** la columna `window` de `comunidad_limits` es palabra reservada en PostgreSQL y rompía la creación de tablas. Ahora va entre comillas (compatible con la base SQLite existente). Verificado contra PostgreSQL 16: límites, envíos, moderación, respuestas del editor, sondeos, retiro y buzón.
- **Caídas sin desindexar:** si la base no responde, las páginas de modelo y pregunta devuelven `503` con `Retry-After: 600`, nunca `200 + noindex`.
- **Rendimiento:** las tablas se crean una vez por proceso; la página de modelo lee todo en una conexión (antes tres, cada una con 9 sentencias `CREATE`). Las páginas sin formulario (portada, criterios, fichas, guías) ya no crean cookie de sesión. Fichas y guías usan un resumen en memoria de 120 s y nunca fallan si la comunidad no responde.
- **Límites en Vercel:** en Vercel se usa `X-Real-IP` / `X-Vercel-Forwarded-For` (los reescribe Vercel); fuera de Vercel se sigue usando la dirección del servidor.
- **Preguntas con URL propia:** `/comunidad/modelos/<slug>/preguntas/<titulo>-<id8>/`. La pregunta exige un título de una línea (10–140 caracteres) que es el H1. Se indexa con al menos una respuesta publicada y lleva datos estructurados `QAPage` (respuesta aceptada / sugeridas, autor, fecha, votos). Sin respuestas: `noindex`. Un título viejo en la URL redirige con 301 a la canónica.
- **Respuestas del editor:** desde `/comunidad/admin/`, en cada pregunta publicada, «Responder como editor». Se publica de inmediato, queda auditada y se muestra como «Respuesta del editor de TallerLab» con enlace a la página de autor (también en el JSON-LD). Es la herramienta principal para arrancar: responder cada pregunta en menos de 48 h.
- **Umbral de indexación del modelo:** 3 aportes útiles (experiencias o preguntas respondidas) y 150 palabras publicadas (`MIN_CONTRIBUTIONS` / `MIN_WORDS` en `comunidad/components.py`). Con contenido suficiente lleva `CollectionPage` + `BreadcrumbList`.
- **Sitemap:** incluye automáticamente modelos y preguntas indexables con `lastmod` de su última actividad.
- **Ficha técnica:** muestra las 3 experiencias más recientes, el resumen y las preguntas recientes, renderizado en servidor. El `Product` de la ficha suma `review` (las experiencias visibles con puntuación) y `aggregateRating` con 3 o más puntuaciones. Nota: solo 43 de 100 fichas son indexables por la regla de calidad documental; en las demás, la página de comunidad es la que posiciona las opiniones.
- **Puntuación opcional 1–5** en experiencias. Resumen visible (cantidad, «la volverían a comprar», puntuación media, uso más frecuente) a partir de 3 experiencias, con aviso de que no es muestra representativa.
- **Sondeo por categoría** (`categoria:<categoría>`), no por modelo; los porcentajes se publican desde 30 respuestas. La portada muestra los sondeos que alcanzaron la base.
- **Guías:** el acceso superior «Leer N opiniones y preguntas» aparece solo si los modelos de la guía tienen aportes publicados; el bloque inferior muestra la actividad por modelo.
- **Portada:** título «Opiniones de herramientas eléctricas en Argentina: experiencias de usuarios», H1 con palabras de búsqueda, modelos con actividad primero.
- **Errores en castellano:** los mensajes de validación muestran etiquetas («pregunta en una línea», «nombre público») en vez de nombres internos.

Pruebas: `tests/test_comunidad.py` pasa de 18 a 25 casos (503, cookies, preguntas/QAPage/editor/301, umbral + sitemap + Review/AggregateRating, acceso de guías, puntuación inválida, sondeo con base mínima). Con las pruebas de catálogo: 55 pruebas aprobadas. Revisión visual en 390 y 1280 px sin desborde horizontal.

### Arranque recomendado (sin inventar aportes)

1. Abrir la participación con 10–15 modelos de más tráfico/clics de afiliados y difundir esas URLs (grupos de oficio, Instagram, contactos).
2. Responder como editor cada pregunta, citando fuente o diciendo «no lo sé».
3. Invitar a quienes compraron por enlaces de afiliados a contar su experiencia a los 30–60 días.
4. Con unos 30+ votos por categoría o 50+ experiencias, publicar un informe («Qué pesa al elegir un compresor según 120 lectores») y difundirlo: eso genera enlaces y menciones, que es la autoridad que la comunidad sola no da.

## Operación y puesta en marcha (5 de octubre de 2026, tarde)

Cambios de código:

- **Sesión:** cookie `SameSite=Lax` (antes `Strict`, que descartaba la sesión al llegar desde Google, WhatsApp o Instagram y hacía perder «Mis aportes» y el voto) y persistente por 365 días cuando la comunidad la crea. Quien pregunta puede volver semanas después a elegir la respuesta o retirar su aporte.
- **Avisos al editor (`comunidad/avisos.py`):** Telegram inmediato por cada aporte o solicitud nueva (sin texto ni datos personales) y resumen diario por Telegram y/o correo desde el cron `/api/comunidad/resumen` (08:00 de Argentina, `Authorization: Bearer CRON_SECRET`). Solo se envía si hay algo para hacer.
- **Aviso a quien pregunta:** correo opcional con consentimiento en el formulario de pregunta (solo aparece si el correo está configurado). Un único aviso cuando se publica la primera respuesta (moderada o del editor); el correo se borra al enviarse, al retirar la pregunta o a los 180 días (tabla `comunidad_avisos`).
- **Panel:** indicadores (pendientes y antigüedad, preguntas sin respuesta, aportes de 7 días, publicados, votos, avisos en espera, canales activos) y lista de preguntas sin respuesta con formulario de respuesta del editor.
- **Términos de participación** y aviso por correo en `/comunidad/criterios/`. Versión de aviso `comunidad-2026-10-05-v4`.
- **Analítica:** Vercel Web Analytics (sin cookies) en todas las páginas HTML salvo el panel, cuando `VERCEL_WEB_ANALYTICS=1`.
- `.vercelignore` excluye `/respaldos/` y `/respaldo-*/`; `.env.example` documenta las nuevas variables.

Verificado: 31 pruebas de comunidad y 83 de catálogo, compatibilidad y alertas; almacenamiento probado contra PostgreSQL 16 (incluidos avisos, panel y limpieza).

### Pasos del editor para abrir

1. **Commit único** con `comunidad/`, `assets/comunidad.*`, `tests/test_comunidad*`, `docs/OPERACION_COMUNIDAD.md`, `app.py`, `servidor_local.py`, `tallerlab_data/views.py`, `vercel.json`, `.vercelignore`, `.env.example`. Sin `comunidad/` el sitio entero falla al importar.
2. **Variables en Vercel (Production):** `COMUNIDAD_DATABASE_URL` (Neon, cadena *pooled* `-pooler`, `sslmode=require`; puede ser la misma base de alertas), `COMUNIDAD_SESSION_SECRET` (≥ 32 caracteres; si ya existe `RELEVAMIENTO_SESSION_SECRET`, reutilizarlo evita invalidar sesiones), `COMUNIDAD_ADMIN_KEY`, `COMUNIDAD_HABILITADA=1`. Ya existe `CRON_SECRET`.
3. **Telegram (5 min, gratis):** crear un bot con @BotFather → `COMUNIDAD_TELEGRAM_BOT_TOKEN`; escribirle al bot y obtener el chat id (`https://api.telegram.org/bot<TOKEN>/getUpdates`) → `COMUNIDAD_TELEGRAM_CHAT_ID`.
4. **Correo (opcional, recomendado):** cuenta en Resend, verificar el dominio `tallerlab.com.ar` (registros DNS), `RESEND_API_KEY`, `COMUNIDAD_AVISOS_REMITENTE="TallerLab <avisos@tallerlab.com.ar>"`, `COMUNIDAD_AVISO_EDITOR_EMAIL`.
5. **Analítica:** activar Web Analytics en el proyecto de Vercel y definir `VERCEL_WEB_ANALYTICS=1`.
6. **Desplegar y probar en privado:** enviar una experiencia, una pregunta con aviso por correo y una respuesta; moderar; responder como editor; comprobar Telegram, correo, retiro y que el límite de envíos no bloquee a otra conexión. Rechazar o retirar los aportes de prueba. Ejecutar el cron desde el panel de Vercel y revisar la respuesta JSON.
7. **Search Console:** reenviar el sitemap y validar una página de pregunta respondida con la prueba de resultados enriquecidos.
8. **Legal:** consultar con un profesional la inscripción de la base en el Registro Nacional de Bases de Datos (AAIP, Ley 25.326) y revisar los términos.
9. **Lanzamiento:** elegir 10–15 modelos con más impresiones en Search Console, difundir esas URLs, moderar en < 24 h y responder cada pregunta en < 48 h.

## Ajustes de rendimiento e indexación (5 de octubre de 2026, noche)

- **Una conexión PostgreSQL por request:** `comunidad.storage.connection()` reutiliza la conexión dentro del mismo request (`flask.g`) y la cierra al final (`teardown_appcontext`). Un envío pasaba de 4–5 conexiones TLS a 1. Si una consulta falla, se hace rollback y la conexión sigue sirviendo. Fuera de un request (scripts, cron sin contexto) se mantiene una conexión por llamada. SQLite local no cambia. Verificado contra PostgreSQL 16.
- **Resumen de respaldo:** si la base no responde, fichas, guías y sitemap usan el último resumen conocido de esa instancia en lugar de quedar vacíos. Límite: una instancia nueva de Vercel sin resumen previo sigue sin datos hasta que la base responda.
- **Portada `/comunidad/`:** queda `noindex, follow` hasta que haya al menos 3 páginas de modelo indexables (`HUB_MIN_MODELS` en `comunidad/components.py`). Se puede visitar, compartir y enlazar igual; solo no compite en Google mientras está vacía. La descripción ya no promete «opiniones reales» mientras no las hay. Si no hay datos ni resumen previo, responde `503` (nunca `noindex` por error). Mientras sea `noindex` tampoco figura en `sitemap.xml`; entra sola cuando pasa el umbral.
- **Caché CDN:** la portada (sin parámetros de búsqueda) y `/comunidad/criterios/` se sirven con `s-maxage=300, stale-while-revalidate=600`. Las páginas de modelo y pregunta siguen `no-store`: muestran «Mis aportes», votos propios y avisos, y el CDN de Vercel no usa la cookie en la clave de caché (con `Vary: Cookie` directamente no cachea). Cachearlas exige separar la parte personal (por ejemplo, cargarla aparte); conviene hacerlo cuando el tráfico lo justifique.

Pruebas: `tests/test_comunidad.py` pasa a 34 casos (portada noindex/503, resumen de respaldo, conexión única por request).
