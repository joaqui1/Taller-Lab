# Operación del relevamiento

Estado: cerrado por defecto. Implementación local corregida; apertura pública pendiente de configurar y probar almacenamiento persistente en el destino.

## Configuración

Copiar los nombres de `.env.example` al entorno del proceso; el servidor no carga ese archivo automáticamente. Definir `RELEVAMIENTO_ADMIN_KEY` y un `RELEVAMIENTO_SESSION_SECRET` aleatorio estable de al menos 32 caracteres. En producción definir `RELEVAMIENTO_DATABASE_URL` con PostgreSQL persistente y TLS según el proveedor. No reutilizar `DATABASE_URL` del observatorio. Instalar `requirements.txt`, que incluye psycopg.

Mantener `RELEVAMIENTO_HABILITADO=0` hasta verificar conexión, escritura, lectura, reinicio y exportación en el destino. Establecer `RELEVAMIENTO_HABILITADO=1` para abrir. En local usa `datos_relevamiento/relevamiento.db`. No trasladar SQLite al filesystem efímero de Vercel. La creación de tablas es idempotente; datos antiguos no reciben permisos nuevos retroactivamente.

El acceso administrativo es `/relevamiento-2027/admin/`: clave por POST, sesión de una hora y token CSRF para cambios. Usar HTTPS en producción. No compartir enlaces antiguos con `key`. Cambiar el secreto de sesión cierra las sesiones; cambiar la clave invalida las existentes. El panel permite salir. Evitar guardar respuestas o exportaciones privadas en Git.

El limitador es persistente y atómico: diez intentos de formulario por dirección y hora fija; los eventos admiten 120. Las redes compartidas pueden alcanzar el límite. No se confía en `X-Forwarded-For` arbitrario. Verificar que el despliegue entregue una dirección remota correcta; configurar proxies confiables en la infraestructura, nunca aceptar libremente ese header.

## Datos y revisión

Respuestas, contactos y reseñas se guardan en una sola transacción y tablas distintas vinculadas por UUID. La tabla `consentimientos` conserva versión del aviso, fecha de aceptación y permisos de cada nueva respuesta. No es anonimato completo.

La aprobación de reseña no cambia el estado analítico. Solo permite autorizar una reseña de respuesta válida con permiso explícito. Descartar una respuesta revoca la aprobación. Antes de publicar revisar texto libre y quitar identificadores. No se publican reseñas automáticamente.

Exportaciones autenticadas: `analitica` es privada, `informe` y `comercial` filtran por finalidad; `publica` contiene únicamente agregados con celdas de cinco o más. Esta última no incluye texto libre ni contactos. Verificar riesgo de identificación y grupos faltantes antes de publicar; no ofrecer el JSON analítico como dataset público.

## Solicitudes de baja

El responsable debe atender el canal editorial de contacto y comprobar que la solicitud corresponde al participante. Buscar internamente el UUID por correo o comprobante de respuesta, sin compartir otros datos. En el panel introducirlo en «Baja de contacto y permisos». La operación elimina el contacto, revoca los tres permisos registrados y retira autorización de reseña; conserva respuestas técnicas seudonimizadas. Registrar la atención en un registro privado mínimo.

También retirar el contacto de listas y archivos ya exportados, detener comunicaciones pendientes y quitar citas ya publicadas manualmente. La aplicación no controla servicios externos. Solicitudes de acceso, rectificación o eliminación integral necesitan tratamiento editorial adicional; no confundir revocación con eliminación de todos los datos. Establecer política de conservación y responsable antes de abrir.

## Verificación

Ejecutar `python verificar_relevamiento.py` con las dependencias instaladas. Usa una base temporal dentro de `tmp/`. Incluye validación, cierre, sesiones, CSRF, moderación atómica, selección múltiple, segmentación, eventos deduplicados, concurrencia y rate limit persistente. No toca respuestas reales.

Ejecutar también `python verificar_relevamiento_front.py` con Node disponible: verifica etiquetas, sintaxis de scripts del panel y el JavaScript real del formulario mediante controles simulados, incluyendo selección múltiple y serialización.

Las pruebas locales SQLite no certifican PostgreSQL, backups, correo ni infraestructura de producción. Verificar esos componentes en el destino antes del lanzamiento. La completitud del navegador es aproximada; los eventos bloqueados o perdidos pueden alterar el porcentaje. La comprobación visual en navegador quedó pendiente: el navegador no pudo acceder al servidor local y devolvió un timeout.
