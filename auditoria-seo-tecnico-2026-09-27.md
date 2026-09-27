# Auditoría SEO técnica de TallerLab (local)

**Fecha:** 27/09/2026. **Alcance:** servidor Python en `http://localhost:8080/`, 178 artículos, 5 páginas de categoría independientes y la portada: 184 URLs distintas. No existe aún un dominio publicado; por eso no se verificaron HTTPS, indexación real, Search Console ni Core Web Vitals de usuarios.

## Resultado

El contenido es legible en el HTML inicial y la estructura básica de cada página está bien: las 184 URLs tienen un `title`, una meta descripción y un H1; no se encontraron duplicados exactos de esos tres elementos. Hay enlaces internos hacia las 184 URLs. Las 442 apariciones de `<img>` tienen atributo `alt` con texto. Una prueba a 375 px de ancho no mostró desplazamiento horizontal en portada, categoría de compresores ni guía de 50 litros.

**No está listo para publicarse con una configuración SEO completa.** Los problemas prioritarios son los siguientes.

| Prioridad | Hallazgo comprobado | Efecto y corrección |
| --- | --- | --- |
| Alta | `/sitemap.xml` devuelve 404. | Crear un sitemap con las 184 URLs canónicas y absolutas una vez elegido el dominio. Incluir `lastmod` solo si representa una modificación significativa comprobable. Publicarlo en la raíz y declararlo en Search Console y, si se crea, en `robots.txt`. |
| Alta | Las 184 páginas carecen de `rel="canonical"`. Además, `/compresores/50-litros` y `/compresores/50-litros/` devuelven 200 con el mismo HTML y sin redirección; el patrón se aplica a rutas sin extensión. | Elegir la barra final como formato único, redirigir las variantes a la URL preferida y usar canonical absoluto y autorreferente en las páginas indexables. El dominio deberá ser configurable; nunca publicar `localhost` como canonical. |
| Alta | `/soldadura-electronica/` se enlaza desde artículos, pero devuelve 404. | Crear la página de categoría o cambiar los enlaces a un destino existente. Volver a rastrear las rutas después. |
| Media | La portada entrega 280.529 bytes de HTML sin compresión HTTP observada. Incluye tarjetas para todos los artículos dentro de resultados de búsqueda ocultos. | Renderizar los resultados del buscador cuando se usan, reducir el HTML inicial y habilitar compresión en el servidor de producción. Medir LCP, INP y CLS al publicar. |
| Media | Las 442 apariciones de `<img>` carecen de atributos `width` y `height`. | Declarar dimensiones intrínsecas o `aspect-ratio` para reservar espacio. Ya hay contenedores CSS de tamaño fijo para varias imágenes, así que esto es un riesgo de desplazamiento visual, no una prueba de CLS malo. |
| Media | Hay 22 fuentes de imagen externas distintas en las tarjetas. | Comprobar disponibilidad, permiso de uso y coincidencia de modelo; considerar servir versiones optimizadas propias. El `alt` existe, pero una foto de variante equivocada seguiría siendo engañosa. |
| Baja | Las 184 páginas carecen de JSON-LD; tampoco hay `<link rel="icon">`. `/favicon.ico` devuelve SVG con MIME `image/svg+xml`. | Añadir datos `Article`/`BreadcrumbList` solo cuando coincidan con el contenido visible y fechas verificadas. Preparar un favicon PNG/ICO cuadrado y enlazarlo en el `<head>`. El marcado estructurado no es requisito para indexar. |

## Robots e indexación

`/robots.txt` devuelve 404. Esto **no bloquea** el rastreo de Google: un 404 en ese archivo se interpreta como ausencia de restricciones. Al publicar, conviene añadir un archivo simple que declare el sitemap. El sitio local tampoco declara `noindex`; actualmente `localhost` no es accesible para Google. Las URLs inexistentes sí devuelven un HTTP 404 real, lo cual es correcto.

No se puede comprobar qué páginas elegiría Google como canónicas ni cuáles indexaría hasta que exista una versión pública y datos de Search Console.

## Imágenes y metadatos

No se encontraron imágenes sin `alt` ni enlaces sin texto accesible en el HTML generado. El logo repetido aporta 368 de las 442 apariciones de imagen; por eso ese conteo no equivale a 442 fotos distintas. La imagen principal tiene un `alt` genérico ("Herramientas de taller"); puede describirse con más precisión. Las fotos de producto tienen marca y modelo en el `alt`.

Los `title`, descripciones y H1 son únicos. Hay 23 títulos de más de 65 caracteres y 48 descripciones de más de 165; no son errores técnicos ni existen límites fijos de Google. Conviene revisar cómo se recortan visualmente en los resultados de búsqueda cuando el sitio esté publicado.

## Comprobaciones y límites

- Páginas renderizadas y examinadas: 184.
- Enlaces internos: 3.805 apariciones. Destino interno inexistente detectado: `/soldadura-electronica/`.
- Imágenes con `alt` vacío o ausente: 0. Imágenes sin `width`/`height`: 442 apariciones.
- Canonicals: 0/184. JSON-LD: 0/184. Un navegador confirmó la ausencia de ambos en la guía de 50 litros después de cargar JavaScript.
- Una URL inexistente devuelve 404; la variante sin barra final de la guía de 50 litros devuelve 200 y el mismo HTML que la versión con barra.
- No se midieron rankings, cobertura de índice, HTTPS, redirecciones de dominio, enlaces externos, Core Web Vitals reales ni estado de las 22 imágenes alojadas por terceros.

## Orden recomendado antes de publicar

1. Definir dominio HTTPS y formato canónico; crear redirecciones y canonical consistente.
2. Corregir `/soldadura-electronica/` y generar sitemap con URL absolutas válidas.
3. Publicar `robots.txt` con referencia al sitemap; verificar ambos endpoints y enviar el sitemap a Search Console.
4. Reducir el HTML inicial de la portada y optimizar las imágenes; medir rendimiento móvil real.
5. Añadir favicon y, después de verificar datos editoriales, marcado estructurado apropiado.

## Referencias

- [Google: crear y enviar un sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [Google: canonicals y redirecciones](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [Google: interpretación de robots.txt](https://developers.google.com/crawling/docs/robots-txt/robots-txt-spec)
- [Google: buenas prácticas de imágenes](https://developers.google.com/search/docs/appearance/google-images)
- [Google: favicon en resultados](https://developers.google.com/search/docs/appearance/favicon-in-search)
- [Google: marcado Article](https://developers.google.com/search/docs/appearance/structured-data/article)
