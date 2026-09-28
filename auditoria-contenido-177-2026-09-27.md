# Auditoría preliminar de intención y evidencia (27/09/2026)

## Alcance y veredicto

Se inventariaron los 178 archivos Markdown del sitio: 1 guía publicada y 177 borradores. **No se puede afirmar que las 177 guías cumplan** la cadena `consulta → title → H1 → respuesta` ni el estándar de aporte original. El [inventario por URL](auditoria-intencion-y-evidencia-2026-09-27.csv) registra señales visibles en cada archivo y una acción preliminar. No certifica la intención de búsqueda real, la vigencia de especificaciones ni la veracidad de opiniones. Esos puntos necesitan revisión editorial con fuentes externas por modelo.

Google recomienda contenido útil y fiable, palabras usadas por las personas en lugares prominentes como title y encabezado principal, enlaces rastreables y dar a conocer el sitio. Estas son prácticas, no una fórmula que garantice tráfico. También pregunta si el contenido aporta investigación o análisis original y si añade valor sustancial a las fuentes usadas. [Search Essentials](https://developers.google.com/search/docs/essentials) · [Contenido útil](https://developers.google.com/search/docs/fundamentals/creating-helpful-content).

## Censo de los archivos

| Señal verificable en el repositorio | Resultado | Interpretación |
| --- | ---: | --- |
| Keyword principal declarada en frontmatter | 178/178 | Es una hipótesis editorial, no una intención validada con resultados de búsqueda. |
| Cobertura léxica completa de esa keyword en title | 155/178 | Comparación aproximada de palabras normalizadas; requiere lectura manual de los 23 restantes. |
| Cobertura léxica completa en H1 | 158/178 | Misma limitación; una coincidencia no prueba que el título responda bien. |
| Al menos un enlace externo no comercial en el cuerpo | 35/178 | Un enlace no demuestra que respalde una cifra concreta. |
| Ningún enlace externo no comercial en el cuerpo | 143/178 | Hay que localizar fuentes técnicas o quitar cifras no sustentadas. |
| Tabla Markdown | 174/178 | La presencia de tabla no equivale a comparación original ni a datos verificados. |
| Mención de opiniones/compradores/reseñas en el cuerpo | 9/178 | Las menciones detectadas no acreditan una muestra identificable de opiniones. |

Conteo de fuentes no comerciales por sección: amoladoras 21/25 sin enlace, compresores 12/23, generadores 18/21, hidrolavadoras 23/23, sierras 19/29, soldadoras 22/29, soldadura electrónica 5/5 y taladros 23/23. La búsqueda detecta enlaces Markdown `https://`; una revisión humana debe comprobar referencias con otro formato y si cada enlace sustenta el dato próximo.

## Contraste manual de casos de riesgo

1. **`/compresores/lusqtoff-50-litros/`**: la tabla atribuye al supuesto LC-2050 2 HP, 206 l/min y ~140 l/min útiles a 6 bar, enlazando solo a la portada de Lüsqtoff. El [catálogo oficial 2020–2021](https://lusqtoff.com.ar/files/Catalogo_Lusqtoff_2020.pdf) identifica LC-2050BK con **2,5 HP** y 206 l/min, sin el dato de caudal útil que la guía presenta como aproximación. La [ficha actual LC2550B-8](https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8) también usa 2,5 HP/206 l/min, pero corresponde a otro código. Hay mezcla de variantes y una conversión de caudal sin método comprobable. El borrador no debe publicarse así.
2. **`/hidrolavadoras/lusqtoff-hl-120/`**: promete patrones de «miles de usuarios», límites de uso y una tabla de presión sin mostrar muestra, enlaces a reseñas concretas ni método. La [ficha oficial HL-120](https://www.lusqtoff.com.ar/ver-producto/HL-120) informa 70 bar de trabajo y **105 bar máximos permitidos**; la tabla del borrador indica 100 bar máximos. El texto necesita verificar cifras y retirar o documentar las atribuciones a compradores.
3. **`/hidrolavadoras/para-autos/`**: title, H1 y primer párrafo sí enfocan el lavado de autos. Su tabla compara publicaciones de Mercado Libre, pero no identifica modelos exactos ni fichas oficiales para verificar presión, caudal y accesorios. Es un buen punto de partida de intención, aún insuficiente como comparación documentada.
4. **`/soldadura-electronica/yihua-898d/`**: el primer párrafo responde a qué incluye y para qué sirve, pero los datos técnicos salen de una publicación comercial y no de un manual identificado. Separar lo que declara el vendedor de lo que confirma el fabricante.
5. **`/compresores/50-litros/`**: la única guía publicada tiene una matriz de decisión y fuentes de los tres modelos. La [página comercial de Gamma](https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros/) muestra 2 HP para G2802AR, mientras el [manual de Gamma](https://www.gammaherramientas.com.ar/web/wp-content/uploads/compresores_compresor-de-50-litros_G2802AR-102-manual.pdf) muestra 2,5 HP; la guía deja visible esa discrepancia. Sigue siendo análisis documental, no una prueba propia. Su consulta objetivo y su respuesta inicial son coherentes; la validación de intención en resultados de búsqueda reales queda pendiente.

## Regla de publicación por URL

1. Elegir una consulta principal y documentar su intención con resultados reales, no solo con la lista de keywords. Resolver canibalización con otras URLs antes de escribir.
2. Redactar title, H1 y primer bloque para responder esa intención con precisión. Registrar el resultado esperado y verificar que el resto del texto no derive hacia otra búsqueda.
3. Identificar cada código de producto y enlazar la ficha o manual que respalda cada especificación decisiva. Mostrar contradicciones entre fuentes y datos no informados.
4. Si se citan opiniones, guardar URL, fecha, plataforma, variante y tamaño de muestra. Resumir 3–5 patrones solo si hay evidencia suficiente; si no, omitir el bloque. No convertir reseñas de terceros en experiencia de TallerLab.
5. Comparar productos en variables relevantes para la tarea, explicar compensaciones y cerrar con una conclusión que se desprenda de los datos. No usar ranking o puntuación inventada.
6. Hacer lectura final de seguridad, exactitud, enlaces y afiliación; entonces registrar revisor, fecha y `published: true`.

Google recomienda en las reseñas cuantificar diferencias, explicar ventajas y desventajas según investigación propia y respaldar con evidencia las afirmaciones de experiencia. No exige un número fijo de opiniones. [Guía de reseñas](https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews). Su política sobre abuso de contenido a escala depende del propósito de manipular rankings y del poco valor para usuarios; estas señales del repositorio **no prueban una infracción**, pero justifican mantener los borradores fuera de búsqueda mientras se investigan. [Políticas de spam](https://developers.google.com/search/docs/essentials/spam-policies).
