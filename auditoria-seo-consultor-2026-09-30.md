# Auditoría SEO de publicación de TallerLab

> Diagnóstico inicial anterior a las correcciones. Consultá el estado actualizado en [cierre-seo-produccion-2026-09-30.md](cierre-seo-produccion-2026-09-30.md).

Fecha: 30/09/2026. Dominio: https://www.tallerlab.com.ar.

## Veredicto

**Todavía no está todo listo para dar por publicada la colección completa.** La versión pública funciona y tiene una base técnica correcta para ser rastreada. El cierre pendiente se concentra en el alcance editorial de amoladoras, la diferencia entre local y producción, y la comprobación de los destinos comerciales. La validación de rendimiento e indexación real sigue pendiente.

Es razonable mantener online el subconjunto aprobado. Los 404 de borradores deliberadamente excluidos no constituyen por sí solos un defecto SEO del resto del sitio. El problema es que el estado `published: true` no coincide con lo que efectivamente se sirve y con la expectativa de publicar toda la colección.

No se desplegó el sitio ni se modificaron artículos, ofertas o filtros durante esta auditoría.

## Alcance y evidencia

- Inspección de las **169 rutas indexables locales**, correspondientes a **159 archivos de guía**, categorías, portada, metodología y autor.
- Solicitudes a las 169 rutas equivalentes en producción: **167 responden 200** y dos responden 404.
- Solicitudes a las rutas de archivos excluidos, robots, sitemap, buscador auxiliar, variantes del dominio, variantes de barra final, imágenes y rutas inexistentes de control.
- Control existente `verificar_enlaces_publicados.py`: **169 rutas y 5.816 enlaces HTML aprobados**.
- Análisis de títulos, descripciones, H1, canonicals, JSON-LD, enlaces, anclas, imágenes y accesibilidad mediante enlaces desde la portada.
- Inspección de navegador de portada y `/compresores/50-litros/`, incluyendo ancho de 390 px y JSON-LD después del renderizado en una guía.
- Lectura del filtro editorial, configuración comercial, metodología, autor, ejemplos de guías excluidas y mapa provisional de Semrush.

Evidencia detallada: `auditoria-seo-consultor-2026-09-30.json`. Redirecciones y resultado de PageSpeed: `seo-redirecciones-pagespeed-2026-09-30.json`. Scripts reproducibles: `auditoria_seo_consultor.py` y `comprobar_seo_externo.py`.

## Revisiones técnicas

| Control | Resultado | Alcance y consecuencia |
| --- | --- | --- |
| Respuesta de páginas previstas | Local 169/169; público 167/169 | Dos guías disponibles localmente siguen sin desplegarse. |
| Sitemap | HTTP 200; 167 URL públicas | Corresponde al conjunto público actual, pero difiere del local de 169. |
| Robots | HTTP 200; `Allow: /`; sitemap absoluto correcto | No se observó bloqueo general de rastreo. |
| Canonical | Correcto en todas las páginas locales y las 167 públicas recuperadas | Dominio HTTPS con www y barra final. |
| Noindex accidental | No encontrado en esas páginas | El fragmento `/search-cards.html` sí tiene `X-Robots-Tag: noindex`, correctamente. |
| HTTPS | Respuestas válidas y HSTS observado | No se realizó una auditoría completa de configuración TLS. |
| Redirecciones | Permanentes; destinos correctos | HTTP sin www realiza dos saltos 308; HTTP con www y HTTPS sin www, uno. La guía sin barra final redirige 301. |
| 404 real | Aprobado en ruta inexistente de control | No devuelve 200 para ese error. |
| HTML inicial | Contenido y metadatos presentes | La lectura del contenido principal no depende de JavaScript. |
| Enlaces internos | Control existente aprobado; sin enlaces hacia 404 conocidos en HTML público analizado | El rastreo de estructura local no detectó destinos internos inexistentes. |
| Anclas | Sin destinos inexistentes en HTML local | Incluye navegación a fuentes. |
| Profundidad | Todas las rutas locales alcanzables en hasta dos enlaces desde portada | Es una medida técnica: el enlace desde listados no garantiza prioridad editorial. |
| Imágenes | Sin `alt` ausente ni dimensiones ausentes en HTML local | Las seis URL de imagen distintas solicitaron correctamente; la muestra de navegador no mostró imágenes rotas. No acredita permiso de uso ni exactitud de cada foto. |
| Móvil | Sin desbordamiento horizontal observado en portada y guía de 50 L a 390 px | Muestra de dos páginas; no certifica todas las calculadoras, tablas y páginas. |
| Rendimiento | No medido | PageSpeed API respondió 429 por cuota. No hay puntuación Lighthouse ni certificación de Core Web Vitals. |

La portada local entrega **29.131 bytes de HTML**. La advertencia histórica sobre una portada de 280 KB ya no describe este estado. El fragmento público de resultados del buscador sigue pesando aproximadamente 150 KB sin compresión solicitada; conviene medir su impacto al usar el buscador. Estas medidas de tamaño no prueban un problema de LCP, INP o CLS.

## Hallazgos prioritarios

### 1. Alta: reconciliar el estado de publicación de amoladoras

**Evidencia:** hay 179 archivos de guía y 159 admitidos por el filtro. Los 20 archivos excluidos tienen `published: true`. Uno corresponde a `/amoladoras/`, cuya ruta sigue funcionando como categoría; las otras **19 rutas de amoladoras devuelven 404**. La lista completa está en el campo `summary.excluded` del JSON.

Entre las exclusiones están DeWalt, Makita, Lüsqtoff, Gamma, inalámbricas, disco flap y disco de desbaste. Según el mapa provisional de Semrush guardado en el proyecto, disco flap y disco de desbaste tenían volumen 2.900 y 1.600, respectivamente. Son datos históricos del archivo, no mediciones actuales ni predicciones de tráfico.

El filtro requiere encabezado exacto de fuentes y las etiquetas «Dato documentado» y «Análisis TallerLab». Entre los 20 archivos excluidos, 19 carecen de la segunda etiqueta, 18 de la primera y tres del encabezado exacto. Algunas guías contienen documentación y análisis expresados con otras palabras; por eso exclusión automática no equivale a demostración de mala calidad.

**Impacto:** esas páginas no pueden posicionarse mientras respondan 404; queda incompleta la cobertura editorial prevista. No se observaron enlaces rotos a ellas desde el conjunto público inspeccionado.

**Corrección:** revisar evidencia y utilidad de cada guía; ajustar su contenido a la política editorial cuando corresponda o marcarla explícitamente como pendiente. Conservar el filtro hasta que cada decisión esté respaldada. No basta agregar etiquetas para habilitar archivos.

**Cierre:** inventario editorial y rutas servidas deben coincidir, con decisiones explícitas sobre qué se publica.

### 2. Alta para completar el lanzamiento: dos guías locales faltan en producción

**Evidencia:** `/sierras/caladoras-skil/` y `/sierras/disco-para-sierra-circular/` responden 200 localmente y 404 públicamente. El sitemap público contiene 167 URL; el local, 169. El informe anterior que excluía estas guías ya quedó desactualizado respecto del contenido local.

**Impacto:** esas dos guías no están disponibles para lectores ni Google. También demuestra que aprobar el repositorio local no basta para aprobar el sitio desplegado.

**Corrección:** publicar la versión revisada mediante el flujo de despliegue habitual y repetir las solicitudes sobre ambas guías y sitemap.

**Cierre:** las 169 URL previstas deben responder 200 y aparecer en el sitemap público, si se mantiene ese alcance.

### 3. Alta editorial/comercial: ofertas sin destino comprobado

**Evidencia:** **16 páginas locales de compresores** contienen «destino sin verificar». La guía pública de 50 L muestra esa declaración en una tarjeta de LC2550B-8. Se encontraron 207 URL únicas `meli.la` en todo el HTML local.

**Impacto:** riesgo de conducir a una variante distinta de la descrita y de reducir confianza y conversión. No se afirma que esos destinos estén equivocados: siguen sin certificación en esta revisión.

**Corrección:** comprobar destino final, código, tensión, kit, vendedor, imagen y disponibilidad, registrando fecha. Cuando no se pueda comprobar, retirar la recomendación de oferta concreta o mantener únicamente una búsqueda de modelo claramente identificada. No usar la mera presencia de `sponsored` como prueba de correspondencia de producto.

**Cierre:** ninguna recomendación de publicación concreta debe presentarse como verificada sin evidencia de su destino.

### 4. Media: completar señales de contacto y tratamiento de datos

**Evidencia:** las rutas probadas `/contacto/` y `/privacidad/` dan 404. La muestra de navegador no tiene enlaces de contacto, privacidad o correo. La búsqueda en el código del sitio no encontró un canal de contacto ni una integración de GA4/GTM. Sí hay metodología, autor y aviso de afiliación.

**Impacto:** falta un canal visible para consultas y correcciones; queda pendiente documentar el tratamiento de datos antes de incorporar medición más amplia. No son requisitos técnicos de indexación ni se evaluaron obligaciones legales.

**Corrección:** incorporar contacto real y una explicación de privacidad acorde al funcionamiento efectivo del sitio y al registro de clics. No inventar credenciales, dirección comercial ni información personal.

### 5. Media: reconciliar configuración de ofertas con decisiones editoriales

**Evidencia:** siguen existiendo cuatro ofertas configuradas ausentes del HTML de su guía: KGE/800 y LG950P en generadores portátiles; GSA18V24 y DCS380B en sierras sable.

**Impacto:** inconsistencia entre catálogo y página, con controles comerciales poco fiables. No demuestra que deba insertarse automáticamente cada oferta: puede ser correcto derivarla a otra guía.

**Corrección:** decidir ubicación y variantes correspondientes; actualizar catálogo y verificadores para reflejar esa decisión. El informe anterior registra siete verificadores fallidos; esos siete no se reejecutaron aquí y no se presentan como fallos actuales confirmados.

## Metadatos, marcado y presentación

- **Aprobado:** títulos y descripciones presentes y sin duplicados exactos; un H1 por página; idioma declarado; canonicals correctos. También se verificó la ausencia de duplicados exactos en las 167 páginas públicas recuperadas.
- **Revisión editorial:** 34 títulos locales superan 65 caracteres y 29 descripciones superan 165. Revisar claridad y posible recorte visual; esas longitudes no son límites obligatorios de Google ni justifican acortar todo automáticamente.
- **Mejora menor:** saltos H1 → H3 en `/hidrolavadoras/hidrolavadora-para-aire-acondicionado/` y `/taladros/rotomartillo-dewalt/`. Corregir la jerarquía cuando el encabezado sea una sección principal.
- **JSON-LD existente:** 169 `Organization`, 159 `Article`, un `WebSite` y un `ProfilePage` en HTML local; JSON parseable. Navegador confirmó `Organization` y `Article` en la guía pública de 50 L. No se hizo validación de elegibilidad con Rich Results Test.
- **Mejora de schema:** no se detectó `BreadcrumbList` en el HTML local, aunque hay migas visibles. Añadirlo con la jerarquía real. El `Article` de la muestra incluye fecha de modificación y autor, pero no `image` ni fecha de publicación; evaluar campos con evidencia auténtica. No inventar fechas ni puntuaciones de productos.
- **Compartir en redes:** ninguna de las 169 páginas locales tiene `og:title` ni `twitter:card`. Añadir Open Graph e imagen para compartir. Es una mejora de presentación y distribución, no un bloqueo de indexación.
- **Afiliación técnica:** los enlaces `meli.la` inspeccionados incluyen `sponsored`. La muestra pública también explica que puede existir comisión. Esto coincide con la [orientación de Google sobre enlaces patrocinados](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links).

## Contenido, intención de búsqueda y autoridad

La muestra de 50 L aporta valor propio: calcula con datos del lector, distingue aspiración de caudal de salida, cita documentación primaria, identifica una contradicción de potencia y explica límites. La metodología y la firma son visibles y no se declara una prueba física inexistente. Son buenas señales editoriales.

El control automático de todas las páginas verifica estructura; **no demuestra que todas las afirmaciones técnicas sean correctas o que cada guía supere a sus competidores**. Se identificaron 1.047 destinos HTTPS externos únicos en el HTML local, incluidos comerciales: no se cotejó nuevamente el contenido de cada fuente ni todos los destinos de afiliados.

Para cerrar la revisión editorial profesional:

1. Priorizar las páginas de mayor potencial comercial y las 19 excluidas; verificar dato → fuente → modelo → mercado → conclusión.
2. Mantener investigación documental claramente distinguida de pruebas físicas. Si se usan «mejor», «opiniones» o comparativas de rendimiento, aportar la evidencia que justifica esa promesa.
3. Revisar que cada consulta comercial reciba una respuesta útil temprana: para quién sirve, alternativa, limitación y qué revisar al comprar.
4. Convertir el mapa provisional de Semrush en un mapa de las URL canónicas efectivamente publicadas, con una intención principal por página y relaciones categoría/modelo/uso. Sus 288 URL propuestas son hipótesis; 232 no coinciden con las rutas locales actuales y **no deben tratarse como 232 errores 404 del sitio**.
5. Contrastar las SERP actuales de consultas prioritarias antes de separar páginas cercanas. No se comprobó canibalización mediante datos de consultas ni comparación de resultados en esta auditoría.
6. Fortalecer experiencia y autoridad mediante ejemplos originales, fotos propias cuando existan, cálculos explicados y referencias relevantes. No agregar testimonios, credenciales o reseñas ficticias.

Google recomienda reseñas con investigación y análisis sustanciales en su [documentación del sistema de reseñas](https://developers.google.com/search/docs/appearance/reviews-system). La afiliación puede ser compatible con contenido valioso; la [política sobre afiliación de poco valor](https://developers.google.com/search/docs/essentials/spam-policies) distingue el contenido que aporta utilidad de las descripciones copiadas sin valor añadido.

## Controles que todavía requieren datos o acceso externo

| Revisión profesional | Estado | Cómo cerrarla |
| --- | --- | --- |
| Search Console: indexación y canonical elegida por Google | Sin acceso confirmado | Inspeccionar portada, hubs y guías prioritarias; revisar exclusiones y enviar sitemap. |
| Acciones manuales y problemas de seguridad | No verificado | Consultar los informes correspondientes en Search Console. |
| Core Web Vitals y PageSpeed | API 429; sin medición | Ejecutar PageSpeed/Lighthouse móvil en portada, hub, comparativa y calculadora. Usar CrUX/Search Console cuando haya muestra. |
| Conversiones y clics comerciales | Endpoint de clics existente; sin análisis de datos persistentes | Revisar almacenamiento, privacidad y atribución. El endpoint usa logs de función, no una base persistente de analítica. |
| Destinos de afiliados | Sin validación completa de producto | Abrir y cotejar las 207 URL únicas, priorizando las que se recomiendan comercialmente. |
| Evidencia de cada afirmación y permisos de fotos | Sin certificación exhaustiva | Revisión documental y registro de derechos/modelo. |
| Canibalización y competidores | No demostrado | Consultas por URL en Search Console y comparación de SERP actuales. |
| Backlinks, menciones y autoridad | No medido | Revisar enlaces de Search Console y herramienta de backlinks con acceso real. |
| SEO local / hreflang | No se justifican por el alcance observado | El proyecto es un medio de guías para Argentina en español; no añadir sedes ni versiones internacionales ficticias. |

Los objetivos habituales de buena experiencia son LCP ≤ 2,5 s, INP ≤ 200 ms y CLS ≤ 0,1, evaluados con datos reales; ver [Core Web Vitals de Google](https://developers.google.com/search/docs/appearance/core-web-vitals). El tamaño del HTML y una captura móvil no sustituyen esa evaluación.

## Orden de cierre recomendado

1. Resolver la decisión editorial de las 19 guías de amoladoras y el archivo de categoría excluido.
2. Verificar los destinos de ofertas concretas, especialmente las 16 páginas con advertencia; reconciliar las cuatro ofertas ausentes.
3. Agregar canal de contacto y documentación de datos acorde al sitio real.
4. Desplegar la versión aprobada y repetir rutas, sitemap y canonical en producción. Las dos guías de sierras deben dejar de devolver 404 si forman parte del lanzamiento.
5. Medir rendimiento móvil y resolver cualquier problema material detectado.
6. Verificar Search Console y establecer medición de clics y consultas; esto se completa sobre el sitio público.
7. Incorporar Open Graph, breadcrumbs estructurados y ajustes puntuales de títulos y jerarquía.

**Criterio de aprobación:** conjunto editorial explícito, mismas URL aprobadas en local y producción, ofertas comprobadas, medición de rendimiento realizada y controles de Search Console iniciados. Publicar y cumplir los requisitos técnicos no garantiza indexación ni posiciones, según los [requisitos técnicos de Google](https://developers.google.com/search/docs/essentials/technical).
