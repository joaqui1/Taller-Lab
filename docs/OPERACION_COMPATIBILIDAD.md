# Operación de compatibilidad

La versión revisada el 4 de octubre de 2026 contiene **107 referencias: 18 modelos verificados, 40 relaciones documentadas y 89 referencias pendientes**. Incluye baterías, cargadores y herramientas Bosch Professional 18V y Gamma Multienergy. El ejemplo ProCORE18V 4.0Ah → GWS 18V-10 responde “Compatible documentado” con identidad, pertenencia y declaración oficial, incluido el manual del GWS. La consulta por códigos evita atribuir evidencia de una variante a otra.

## Datos y cobertura

- `data/reference_catalog.json`: referencias para buscar; no constituye evidencia.
- `data/verified_seed.json`: captura privada inicial, con texto íntegro, hash, afirmaciones comprobadas, modelos y relaciones. No se sirve como descarga pública.
- `data/document_profiles.json` y `sources.py`: perfiles documentales revisados, especificaciones y documentos complementarios. Un perfil identifica SKU, pertenencia y afirmaciones exactas; no aprueba productos por apariencia/voltaje. Para agregar modelos, contrastar la ficha/manual y configurar identidad, valores eléctricos y condiciones documentadas.
- `catalog.py`: activa una versión completa y reconstruye el índice. Lecturas concurrentes usan el mismo bloqueo.
- JSON público: productos con estado, evidencias sin cuerpo completo del fabricante, relaciones, versión y fechas. CSV público: relaciones documentadas con códigos, condiciones, fuentes y fechas.
- `/assets/datos/` conserva un corte histórico identificado. `/datos/compatibilidad/` entrega la versión activa.

No atribuir revisión humana, homologación IRAM, stock ni certificación a una comprobación automática de texto. Las evidencias vencen para emitir veredictos luego de 30 días sin nueva comprobación. El caso desconocido permanece desconocido.

## Configuración

En local, estado SQLite en `.compatibilidad-state/state.sqlite3`, fuera del código fuente e ignorado por Git. Se puede configurar `COMPATIBILITY_STATE_PATH`. No se crea almacenamiento al importar el módulo ni al leer por primera vez.

En Vercel se exige `COMPATIBILITY_DATABASE_URL` (o `DATABASE_URL` existente) con PostgreSQL y permisos para crear las tablas `compatibility_versions`, `compatibility_current` y `compatibility_metrics`. Se requiere el driver `psycopg`, incluido en requirements. No se sustituye por SQLite efímero si falta configuración.

Configurar `CRON_SECRET` como variable privada de Vercel. El cron `30 10 * * *` invoca GET `/api/compatibilidad/ejecutar` a las 10:30 UTC, 07:30 Argentina, enviando Authorization. GET no acepta parámetros. POST manual usa `COMPATIBILITY_MAINTENANCE_TOKEN`, si existe, o `CRON_SECRET`; ambos fallan cerrado sin configuración. No existen credenciales fijas ni secretos en query strings. La configuración local no prueba que el cron haya sido desplegado.

Las respuestas públicas pueden usar el corte verificado incluido si no se consigue leer PostgreSQL; esa caída se registra y el monitor falla explícitamente. La caducidad de evidencia impide que el corte siga emitiendo síes indefinidamente. La telemetría es opcional y falla sin interrumpir páginas; registra únicamente contadores por evento, nunca consultas libres, IPs o cookies.

## Alertas

El workflow `.github/workflows/compatibilidad-operacion.yml` compara cada día el estado público con la ejecución anterior guardada en la caché de GitHub Actions. Avisa cuando bajan los productos publicados o las relaciones, cuando un producto pasa de publicado a suspendido/pendiente, aparece una nueva fuente fallida o la evidencia más antigua supera 20 días. El mensaje incluye el modelo, el motivo y la fecha cuando se suspende un producto; la alerta de antigüedad incluye la fecha de revisión más antigua. Se avisa al dueño por los canales existentes de Comunidad: correo mediante Resend a `COMUNIDAD_AVISO_EDITOR_EMAIL` y/o Telegram al chat configurado. No cambia el vencimiento documental de 30 días.

En GitHub, cargar como secretos del repositorio `RESEND_API_KEY`, `COMUNIDAD_AVISOS_REMITENTE` y `COMUNIDAD_AVISO_EDITOR_EMAIL` para correo; o `COMUNIDAD_TELEGRAM_BOT_TOKEN` y `COMUNIDAD_TELEGRAM_CHAT_ID` para Telegram. Se pueden habilitar ambos canales. Si no hay un canal configurado o falla la entrega, el workflow falla y queda sujeto a las notificaciones habituales de GitHub Actions. No se requieren variables nuevas en Vercel; el workflow consulta el endpoint público `/api/compatibilidad/estado`.

## Comandos

Desde el proyecto, con requirements instalados:

```powershell
python -m compatibilidad.cli sync --dry-run
python -m compatibilidad.cli sync
python -m compatibilidad.cli sync --offline
python -m compatibilidad.cli check-pair 1600A016GB 06019J40E0
python -m compatibilidad.cli rollback VERSION
python -m compatibilidad.cli export
python -m compatibilidad.operations health
python -m compatibilidad.operations monitor
python preparar_compatibilidad.py
python -m unittest discover -s tests -p test_compatibilidad.py -v
```

Dry-run obtiene y compara fuentes, pero no escribe estado ni modifica la versión activa. Offline no consulta ni publica y responde `NO_EJECUTADO_OFFLINE`. El ciclo real descarga documentos completos con límite de tamaño y redirecciones oficiales; verifica afirmaciones, fecha, dominio y extractos; publica aprobaciones y suspensiones juntas en una transacción.

Cada publicación conserva un snapshot íntegro e inmutable con identificador único, versión del motor, documentos/evidencias, modelos, relaciones y changelog. La actualización compara la versión anterior para impedir sobrescrituras de otro proceso. SQLite usa transacción exclusiva; PostgreSQL usa bloqueo transaccional y control de versión. Rollback restaura el puntero persistido y las estructuras activas: modifica las respuestas, páginas y descargas efectivamente.

Los antiguos archivos `data/snapshots/snapshot_1.0.0*` son artefactos previos de auditoría; no son restaurables con el nuevo motor ni deben tratarse como versiones verificadas.

## Revisar un cambio de fuente

Un cambio en el bloque técnico conserva el documento observado y suspende el modelo, aunque las palabras antiguas todavía estén presentes. Los cambios de navegación y pie de página fuera del bloque no suspenden modelos. Consultar el informe del ciclo y el snapshot privado, comparar documento previo/observado y verificar que no cambió la compatibilidad. El informe da `text_hash` de la captura nueva.

Si la identidad, pertenencia y regla siguen siendo ciertas, un operador puede aprobar explícitamente el hash revisado:

```powershell
python -m compatibilidad.cli approve-source PRODUCT_ID TEXT_HASH --reviewer "Nombre del revisor real" --note "Motivo documentado de la aprobación"
```

El comando vuelve a obtener la fuente, exige que coincida con ese hash y con las afirmaciones del perfil, publica una nueva versión y registra la aprobación. No usar nombres ficticios. Si faltan afirmaciones o cambian capacidad/SKU/requisitos, primero corregir el perfil y los datos contra el documento; no aprobar el cambio para mantener una respuesta anterior.

Una fuente inaccesible pasa a pendiente y deja de sostener un sí; un contenido cambiado entra en conflicto. `REVISION_REQUERIDA` aparece en el informe y en los registros de ejecución. Monitorizar fallos del cron y versiones sin actualización; no interpretar un HTTP 200 de acceso como revisión técnica exitosa.

## Validación realizada y límite de entrega

Se ejecutó un mantenimiento real el 4 de octubre de 2026: las 18 fichas Bosch/Gamma estuvieron accesibles, se comprobó el manual complementario y se publicó una versión en SQLite aislado para verificar la persistencia. Las 32 pruebas cubren ambigüedad independiente de ambos campos, colisiones, falsos dominios, fuente retirada/modificada, aprobación explícita, caducidad en procesos calientes, especificaciones adulteradas, publicación persistida, concurrencia, rollback, exportaciones, autenticación, fallos HTTP 503, noindex de pendientes y lectura pública ante fallo de SQLite.

`/api/compatibilidad/estado` devuelve HTTP 200 únicamente con almacenamiento persistido, comprobación de menos de 26 horas, fuentes accesibles y modelos verificados. Devuelve 503 si se degrada. El cron también devuelve 503 si el ciclo requiere revisión. `.github/workflows/compatibilidad-operacion.yml` prepara una comprobación externa diaria a las 08:30 Argentina; solo se activa al publicar el workflow en la rama predeterminada. Las alertas al dueño requieren configurar los secretos indicados en la sección Alertas.

## Despliegue preparado, publicación diferida

El usuario pidió dejar el despliegue para después. No se publicó ni se renovó la sesión de Vercel.

1. Instalar `requirements.txt` y ejecutar `python preparar_compatibilidad.py`: verifica las pruebas, vigencia documental, exportaciones y assets del CDN. Si transcurrieron más de 30 días, renovar la evidencia con `python -m compatibilidad.cli sync` y resolver alertas antes de preparar.
2. En Vercel configurar `COMPATIBILITY_DATABASE_URL` con PostgreSQL persistente y `CRON_SECRET` privado. No usar SQLite en producción. Revisar variables y duración de funciones de `vercel.json`; el plan contratado debe permitir los cron configurados.
3. Renovar la sesión con `npx vercel login`. Verificar el proyecto y dominio de destino con la CLI. Publicar con `npx vercel --prod` cuando se retome el despliegue autorizado.
4. Ejecutar una vez el mantenimiento autenticado de `/api/compatibilidad/ejecutar`, sin secretos en URL. Comprobar `/api/compatibilidad/estado` con HTTP 200, 18 modelos y 40 relaciones, y una consulta exacta, las descargas y el sitemap. Una fuente modificada puede reducir legítimamente la cobertura y requerir revisión.
5. Confirmar la siguiente ejecución programada en Vercel. Publicar el workflow de supervisión en la rama predeterminada y probarlo manualmente. Verificar el estado en producción antes de anunciar actualización automática.

Las páginas de combinaciones incluyen respuesta explícita, SKU, condiciones, fechas, fuentes, autor y combinaciones relacionadas; el Dataset tiene versión, metodología y citas. El inicio permite explorar los modelos verificados, seleccionar sugerencias de códigos y filtrar la tabla sin ocultar los datos si JavaScript no está disponible. El CSV incluye también los manuales complementarios. La matriz imprimible y las descargas permiten reutilizar y verificar el trabajo. Son fundamentos de autoridad editorial; no garantizan rankings ni citas en buscadores.

## Próximas mejoras editoriales

### Afiliación contextual

`compatibilidad/commercial.py` muestra el referido existente `https://meli.la/1aD8WYE` como kit complementario Bosch 1600A015TD. Aparece en la plataforma Bosch Professional 18V, en la ficha GBA 4 Ah, en las herramientas con una relación documental vigente con esa batería y en las consultas afirmativas GBA 4 Ah → herramienta. Se identifica como kit diferente y exige confirmar códigos de componentes y tensión del cargador. No es una oferta exacta del SKU individual ni una aprobación documental del kit. El título comercial se conserva en `destinos-produccion-2026-09-30.json`; el acceso web actual a Mercado Libre no permitió verificar disponibilidad. No se anuncia precio, stock, descuento ni garantía.

El CTA dice “Consultar precio y contenido del kit Bosch 1600A015TD” y conserva `rel="sponsored nofollow noopener noreferrer"`. Por pedido del usuario, las tarjetas de compatibilidad no muestran el aviso de comisión. La telemetría registra únicamente el contador `clic_comercial`. El bloque se omite en impresión, referencias pendientes, Gamma y combinaciones desconocidas.

Las ofertas exactas se incorporan en `data/commercial_offers.json`, bajo `exact_offers`, usando como clave el ID del producto. Cada registro necesita `brand`, `mpn`, `url`, `identity_confirmed`, `reviewed_at` con zona horaria y `contents_note`. Revisar el destino y confirmar SKU antes de marcar `identity_confirmed: true`; comprobar kit, variante y tensión. Solo se aceptan enlaces de referido `https://meli.la/`, con identidad coincidente y revisión de menos de 30 días. La fecha es de la revisión real del aviso, no de la edición del JSON. Actualmente no hay ofertas exactas recibidas para los 18 modelos: no se inventaron enlaces ni se reutilizó el de la amoladora GWS 10 sin código completo.

### Plantilla editorial de las fichas de producto

`data/fichas_editorial.json` reserva una clave de primer nivel por ID de producto para el render enriquecido. Los registros nuevos llevan `publicado: false`; solo el dueño activa el render cambiándolo expresamente a `true`. Las investigaciones preexistentes del mismo archivo se conservan en sus campos actuales y no se leen para renderizar. Las nuevas claves por ID no incorporan especificaciones, respuestas ni imágenes. Los bloques sin datos no se renderizan.

Cada dato documentado usa `value`, `unit`, `source` (URL oficial HTTPS), `section` (sección de la ficha o manual) y `date_consulted` en formato `dd/mm/aaaa`. Se admiten unidades conocidas; para especificaciones: tensión `V`, capacidad `Ah`, energía `Wh`, peso `kg` o `g`, dimensiones `mm` o `cm` y tecnología de celdas como texto. La energía debe ser el producto numérico de tensión por capacidad y se muestra como cálculo de TallerLab. Los tiempos usan `min` o `h`.

Este JSONC ilustra la forma, no es un registro para copiar ni contiene datos de un producto:

```jsonc
{
  "ID_PRODUCTO": { // Reemplazar por un ID ya existente en el catálogo.
    "publicado": false, // Mantenerlo así hasta la activación editorial del dueño.
    "compatibility": [
      {
        "counterpart_id": "ID_CONTRAPARTE", // El nombre, código y enlace salen del catálogo.
        "type": { "value": "DATO_DOCUMENTADO", "unit": "tipo de relación", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
        "conditions": { "value": "CONDICION_DOCUMENTADA", "unit": "condición", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" } // Omitir si no existe una condición.
      }
    ],
    "specifications": {
      "voltage": { "value": 0, "unit": "V", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "capacity_ah": { "value": 0, "unit": "Ah", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "energy_wh": { "value": 0, "unit": "Wh", "source": "URL_OFICIAL_HTTPS", "section": "CALCULO_TALLERLAB_V_POR_AH", "date_consulted": "dd/mm/aaaa" }
    },
    "charge_times": [{ "counterpart_id": "ID_CONTRAPARTE", "time": { "value": 0, "unit": "min", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" } }],
    "tool": { "packages": [{
      "code": { "value": "CODIGO_EXACTO", "unit": "texto", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "package_type": { "value": "DATO_DOCUMENTADO", "unit": "presentación", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "box_contents": [{ "value": "ELEMENTO_DOCUMENTADO", "unit": "elemento", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" }]
    }] },
    "identification": { "text": { "value": "INSTRUCCION_DOCUMENTADA", "unit": "texto", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" } },
    "common_errors": [{ "value": "ERROR_DOCUMENTADO", "unit": "texto", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" }],
    "faqs": [{
      "question": { "value": "PREGUNTA", "unit": "pregunta", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "answer": { "value": "RESPUESTA_DOCUMENTADA", "unit": "respuesta", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" }
    }],
    "image": { // Opcional; solo se renderiza con archivo, texto alternativo y crédito.
      "file": { "value": "/assets/ARCHIVO", "unit": "archivo", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "alt": { "value": "DESCRIPCION_DE_LA_IMAGEN", "unit": "texto alternativo", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "author_or_license": { "value": "AUTOR_O_LICENCIA", "unit": "autor o licencia", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" },
      "credit": { "value": "CREDITO_VISIBLE", "unit": "crédito visible", "source": "URL_OFICIAL_HTTPS", "section": "SECCION_DEL_DOCUMENTO", "date_consulted": "dd/mm/aaaa" }
    }
  }
}
```

El bloque de herramienta registra la presentación y el contenido por código exacto. El kit Bosch 1600A015TD solo puede acompañar a una herramienta publicada cuya ficha indique `package_type.value` igual a `Solo cuerpo` y cuyo código coincida; no aparece en fichas de baterías, cargadores ni herramientas sin esa documentación. Una imagen se atribuye visiblemente y se incorpora al JSON-LD de la página; no se genera marcado `FAQPage`.

- Ampliar la cobertura con fichas y manuales oficiales de las referencias pendientes. Priorizar los modelos que consultan los lectores; documentar SKU exacto, plataforma, especificaciones, condiciones y relación antes de habilitar respuestas afirmativas. La cobertura verificada actual solo corresponde a Bosch y Gamma.
- Añadir ensayos propios reproducibles y fotografías originales si se pretende acreditar experiencia práctica: identificar unidades, procedimiento, resultado y autor de cada ensayo. La verificación documental existente no equivale a un ensayo físico.
- Cerrar la revisión visual en escritorio y móvil con un navegador que pueda acceder al servidor local o al futuro preview de Vercel. La plantilla de TAREA 6 se revisó en escritorio con un fixture sintético; todavía falta la comprobación en viewport móvil.

No se aprovisionó PostgreSQL ni se desplegó el sitio: faltan esas acciones y comprobar una ejecución real de Vercel para certificar operación programada en producción. Esta entrega habilita ese camino con código y configuración verificables; no promete autoridad SEO ni ampliación automática de cualquier fabricante.
