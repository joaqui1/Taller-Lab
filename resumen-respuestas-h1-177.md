# Respuestas directas según H1: 177 borradores

Fecha: 27/09/2026. Alcance: 177 artículos sin `published: true`. La [matriz por URL](mapa-intencion-respuesta-177.csv) muestra keyword declarada, `title`, H1 y respuesta inicial nueva para cada archivo.

## Cambios

- Se reemplazó la introducción de cada borrador por una respuesta breve a la pregunta o decisión planteada en su H1. No se cambió ningún `title`, H1 ni H2.
- Las aperturas pasaron de 26.519 a 6.080 palabras en total (promedio aproximado de 150 a 34 por página). Se quitaron presentaciones genéricas y promesas de lo que «analizaremos» antes de responder.
- Se conservaron enlaces internos útiles en párrafos compactos al final de las guías. Las 177 siguen teniendo al menos un enlace interno en el Markdown; al publicarse, el servidor solo mostrará enlaces a destinos ya públicos.
- Los 177 archivos continúan como borradores. La reescritura de la respuesta inicial no constituye verificación de todas las cifras, opiniones o recomendaciones del cuerpo.

## Control realizado

| Control | Resultado |
| --- | ---: |
| URL con respuesta inicial definida | 177/177 |
| `title` idéntico al original | 177/177 |
| H1 y H2 idénticos al original | 177/177 |
| Respuesta situada antes del primer H2 | 177/177 |
| Markdown procesado sin error | 177/177 |
| Páginas sin enlaces internos en el archivo | 0/177 |

La comparación de encabezados y `title` se hizo contra `HEAD` de Git. `aplicar_respuestas_h1.py --check` comprueba que todas las respuestas sigan en su lugar.

## Límites editoriales detectados

La frase principal de `keywords` es una hipótesis existente en el frontmatter. No se validó la intención real de cada consulta con resultados de búsqueda y Search Console; por eso la matriz la llama «keyword declarada». El H1 existente guió cada respuesta.

Hay borradores cuyo cuerpo todavía contradice o no documenta la respuesta inicial. Por ejemplo, `/hidrolavadoras/lusqtoff-hl-120/` usa 100 bar máximos en una tabla mientras la ficha oficial indica 105; `/compresores/lusqtoff-50-litros/` estima caudal útil sin fuente y mezcla variantes. `/generadores/precios/` no puede ofrecer una cifra actual sin oferta y fecha verificadas. Permanecen fuera de publicación hasta corregir y documentar esos puntos. Ver [auditoría de evidencia](auditoria-contenido-177-2026-09-27.md).

Google recomienda usar términos de búsqueda en lugares prominentes como el título y encabezado principal, y crear contenido útil para personas; no establece una fórmula de coincidencia exacta entre keyword, title y H1. [Google Search Essentials](https://developers.google.com/search/docs/essentials).
