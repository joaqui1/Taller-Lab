# Auditoría SEO de las 24 URLs de sierras

**Actualización posterior (26/09/2026):** El proyecto local ahora tiene 29 URLs de sierras. Se añadieron cinco páginas de marca y enlaces de afiliado a 12 publicaciones únicas, distribuidos en nueve guías. Las cifras y observaciones históricas de esta auditoría describen el estado anterior a esa ampliación.

**Fecha inicial:** 23/09/2026. **Actualización de implementación:** 24/09/2026. **Mercado:** Argentina. **Estado revisado:** archivos locales y servidor de vista previa. No equivale a una auditoría del sitio publicado ni a datos de Search Console.

**Cambios ya aplicados en el proyecto local (24/09):** `/sierras/` muestra las 24 guías; el cuerpo de estas guías se entrega como HTML desde el servidor; se retiró de su vista el botón de búsqueda genérico de Mercado Libre y la afirmación de ensayos de taller no acreditados. Quedan pendientes los enlaces de afiliado oficiales para productos concretos, la revisión editorial de especificaciones/fuentes y la verificación de indexación al publicar.

## Fuentes y criterio

- `C:/Users/joaqu/Desktop/keywords/Keywords_Sierra.csv`: 8.674 filas de Google Keyword Planner. Sus volúmenes aparecen agrupados y redondeados (muchas variantes muestran 5.000 o 500); no hay que sumarlos ni tratarlos como búsquedas independientes.
- `C:/Users/joaqu/Desktop/keywords/semrush/semrush_sierras.csv`: 40 consultas, más `semrush_consulta_adicional.csv` con 140 consultas de varias categorías. Son exports guardados, no una consulta en vivo a la cuenta de Semrush. Volumen y KD son señales relativas, no previsiones de tráfico.
- 24 Markdown de `paginas/sierras/` y la arquitectura/renderizado de `servidor_local.py`.
- La mención inicial de soldadoras se comprobó contra `keywords_soldadoras.csv` y `semrush_soldadoras.csv`, pero la última aclaración del encargo fija el análisis en las URLs de sierras. No conviene mezclar keywords de soldadura con la arquitectura de sierras salvo cruces editoriales muy concretos de corte de metal.

## Diagnóstico

**H1:** Los 24 archivos tienen un H1 único en el Markdown y un `h1` en frontmatter. El servidor elimina el H1 del cuerpo y pinta el del frontmatter, por lo que no hay doble H1 en la página renderizada. Los títulos y H1 contienen la entidad principal. Son adecuados en lo esencial; el trabajo prioritario es profundizar la utilidad de cada página, no reescribir todos los H1.

**Arquitectura:** Hay 24 URLs y 92 enlaces internos explícitos entre ellas, sin destinos inexistentes en el conjunto. El mapa de la categoría `/sierras/` ya enumera las 24, incluidas ingletadoras, caladoras Bosch, DeWalt DWE560 y Stanley SC16.

**Renderizado e indexación:** El cuerpo Markdown de las 24 guías de sierras se convierte a HTML en el servidor, de modo que el HTML inicial incluye contenido y enlaces contextuales. Comprobar la versión indexada en Search Console al publicar. En el código local tampoco aparece una canonical explícita ni rutas de sitemap/robots; verificar la implementación de producción antes de atribuirlo al sitio público.

**Confianza editorial:** El pie de las guías de sierras ya no afirma que hubo ensayos de taller. En fichas de marca/modelo aún conviene enlazar fichas o manuales oficiales de la variante argentina y diferenciar dato publicado, inferencia y prueba propia. Evitar tablas de prestaciones genéricas que parezcan mediciones propias.

**Enlazado:** Los bloques de enlaces actuales cumplen una base, pero algunos repiten el mismo destino y varias páginas de familia enlazan modelos sin una jerarquía clara. Priorizar enlaces contextuales desde la familia hacia sus marcas/modelos/accesorios y retorno a la familia, más un enlace lateral solo si resuelve una comparación real. No añadir todas las URLs a cada artículo.

## Priorización con los datos disponibles

| Prioridad | URL y keyword | Señal Semrush (vol./KD) | Acción |
|---|---:|---:|---|
| 1 | `/sierras/sierra-sin-fin-para-madera/` | 720 / 8 | Mantener. Añadir criterios comprobables de cinta, altura de corte y compra usada; enlazar desde el índice de sierras y desde banco. |
| 1 | `/sierras/sable/` | 1.900 / 10 | Mantener. Hacer visible la diferencia por material y batería; enlazar la variante inalámbrica. |
| 1 | `/sierras/sensitivas/` | 3.600 / 13 | Mantener. Separar corte de metal de ingletadora para madera y de sierra sin fin de metal. |
| 1 | `/sierras/sin-fin-metal/` | 480 / 7 | Mantener. Desarrollar decisión horizontal/vertical y capacidad para perfiles/tubos. |
| 1 | `/sierras/de-banco-einhell/` | 210 / 6 | Mantener y enlazar más desde la familia de banco. Confirmar modelos disponibles y datos oficiales. |
| 1 | `/sierras/ingletadoras-einhell/` y `/sierras/ingletadoras-total/` | 320 / 8 y 110 / 5 | Mantener. Diferenciar gama/modelos concretos, con fichas verificadas. |
| 1 | `/sierras/sierra-caladora-bosch/`, `/sierras/bosch-gks-150/`, `/sierras/sierra-sable-inalambrica/` | 140 / 9, 140 / 7, 90 / 5 | Mantener; buenas consultas de cola larga para un dominio nuevo. |
| 2 | `/sierras/circulares/`, `/sierras/caladoras/`, `/sierras/de-banco/`, `/sierras/ingletadoras/` | 8.100 / 23, 2.400 / 20, 1.300 / 18, “ingletadora” no medida en Semrush export | Son hubs necesarios. Competencia mayor; publicar como guías completas y puertas de entrada, sin esperar ranking rápido. |
| 2 | `/sierras/sierra-circular-dewalt-dwe560/`, `/sierras/stanley-sc16/`, `/sierras/disco-para-sierra-circular/` | 30 / 8, 30 / 6, 170 / 8 | Mantener; páginas específicas y complementarias. No crear otra página para la variante de nombre del mismo modelo. |
| 3 | Páginas de marca con KD 16–24 o volumen sin medir | variable | Mantener si la gama tiene modelos reales y diferencia editorial; reforzar fuentes y comparativa antes de expandir. |

## H1 y contenido: ajustes puntuales

1. **Conservar los 24 H1 como punto de partida.** Los de “Qué/ Cómo elegir...” encajan con intención informativa y comercial mixta. En `/sierras/ingletadoras/`, incluir también el singular “ingletadora” en el primer párrafo y en el title si se decide afinarlo. No crear `/sierras/ingletadora/` aparte.
2. **Evitar promesas de comparación sin comparación real.** Las páginas de marca deben mostrar una tabla de modelos concretos, código de variante, criterio diferenciador, limitación y fuente; “modelos y precios” genéricos no basta. Especialmente `caladoras-skil`, `caladoras-einhell`, `circulares-black-decker`, `circulares-lusqtoff`, `ingletadoras-dewalt`, `ingletadoras-total`.
3. **Separar intención de modelo e intención de familia.** GKS 150, DWE560 y SC16 responden a especificaciones/compatibilidad del modelo. `/sierras/circulares/` compara tipos y criterios. Enlazar en ambas direcciones, sin copiar la misma tabla general a las tres fichas.
4. **Aterrizar accesorios a compatibilidad.** `/sierras/disco-para-sierra-circular/` debe dejar claro diámetro, eje, RPM y material; `/sierras/guia-para-sierra-circular/` debe explicar cuándo un riel necesita adaptador. Evitar prometer compatibilidad universal.
5. **Revisar afirmaciones técnicas de las primeras 20 páginas.** Dieciocho de las 24 no enlazan una fuente externa distinta de Mercado Libre. Las guías generales pueden explicar criterios sin citar cada frase, pero cifras exactas, variantes y accesorios incluidos requieren fuente primaria.

## Propuesta de enlazado interno por URL

La columna “añadir” evita repetir enlaces ya presentes. Son enlaces editoriales en el cuerpo, con la frase indicada como anchor orientativo; no todos deben colocarse al comienzo. Las cuatro incorporaciones al índice de categoría son obligatorias para que la navegación refleje el inventario real.

| URL | Rol / keyword principal | Enlace contextual a añadir o mejorar |
|---|---|---|
| `/sierras/circulares/` | Hub sierra circular | Ya enlaza guía, disco, GKS 150, DWE560, SC16, Black+Decker y Lusqtoff. Añadir **sierra de banco** en el apartado sobre trabajo estacionario; evitar sumar más modelos en el bloque inicial. |
| `/sierras/sensitivas/` | Hub sensitiva | Añadir **ingletadora** hacia `/sierras/ingletadoras/` en la sección de diferencias. Mantener DeWalt y sin fin para metal. Reducir la repetición del enlace a DeWalt. |
| `/sierras/sable/` | Hub sierra sable | Mantener inalámbrica y caladora. Añadir **sensitiva para perfiles de metal** solo en la comparación de tareas donde corresponda. |
| `/sierras/caladoras/` | Hub sierra caladora | Mantener Bosch, Skil, Einhell y sable. Añadir **sierra circular** en cortes rectos largos y **sierra de banco** cuando se hable de placas repetidas. |
| `/sierras/sierra-sin-fin-para-madera/` | Sierra sin fin madera | Mantener banco y metal; quitar uno de los dos enlaces al mismo destino de metal. Añadir **ingletadora** para corte transversal repetido cuando se comparen usos. |
| `/sierras/de-banco/` | Hub sierra de banco | Ya enlaza Einhell, circular y sin fin madera. Añadir **disco para sierra circular** en melamina solo si se precisa compatibilidad de disco de mesa; añadir **ingletadora** en la comparación de herramientas. |
| `/sierras/sin-fin-metal/` | Sierra sin fin metal | Mantener madera y sensitiva. Añadir un enlace a `/sierras/sensitivas-dewalt/` al hablar de alternativa de corte abrasivo por modelo. |
| `/sierras/ingletadoras-einhell/` | Gama Einhell | Mantener hub ingletadoras y comparación con DeWalt/Total. Afinar el anchor de retorno a **cómo elegir una ingletadora**. No añadir más enlaces laterales sin necesidad. |
| `/sierras/de-banco-einhell/` | Gama banco Einhell | Mantener retorno a banco. Cambiar el enlace lateral a ingletadora Einhell por **disco para sierra circular** solo si el texto aborda dientes/compatibilidad de la hoja; si no, dejar solo el retorno. |
| `/sierras/caladoras-skil/` | Gama Skil | Mantener retorno a caladoras y comparación Bosch/Einhell. Enlazar **hojas para caladora** en la propia guía general por ahora; no hay URL específica. |
| `/sierras/guia-para-sierra-circular/` | Accesorio guía | Ya enlaza hub, GKS 150, DWE560, SC16 y disco. Reforzar tabla de compatibilidad de estos tres modelos antes de sumar destinos. |
| `/sierras/sensitivas-dewalt/` | Gama sensitiva DeWalt | Mantener retorno a sensitivas y alternativa sin fin metal. Evitar enlazar soldadoras desde aquí salvo contexto de preparación de perfiles. |
| `/sierras/ingletadoras-dewalt/` | Gama ingletadora DeWalt | Mantener retorno a ingletadoras y comparativas con Einhell/Total. Anclar el retorno en la sección de elección fija/telescópica. |
| `/sierras/ingletadoras-total/` | Gama ingletadora Total | Mantener retorno a ingletadoras y comparativas Einhell/DeWalt. No necesita más enlaces hasta que se añada un contenido sobre discos de ingletadora. |
| `/sierras/disco-para-sierra-circular/` | Accesorio disco | Ya enlaza hub circular, tres modelos y banco. Añadir **guía para sierra circular** solo si se explica cómo lograr precisión; no presentar discos de mano como intercambiables automáticamente con sierra de banco. |
| `/sierras/bosch-gks-150/` | Modelo GKS 150 | Ya enlaza hub, DWE560, SC16, guía y disco. Mantener este patrón; ubicar la comparación de modelos en una sola sección. |
| `/sierras/circulares-black-decker/` | Gama Black+Decker | Mantener hub, Lusqtoff y disco. Añadir **guía para sierra circular** en cortes largos si se verifica la compatibilidad de la base. |
| `/sierras/caladoras-einhell/` | Gama Einhell | Mantener hub y Bosch/Skil. Añadir un enlace desde la sección a batería a `/sierras/sierra-sable-inalambrica/` únicamente como alternativa de herramienta para demolición/poda, no como reemplazo equivalente. |
| `/sierras/sierra-sable-inalambrica/` | Variante de alimentación | Actualmente solo vuelve al hub sable. Añadir **sierra caladora** en el apartado sobre precisión y **sierra sin fin para metal** solo al comparar cortes repetidos de perfiles. Priorizar al menos el primero. |
| `/sierras/circulares-lusqtoff/` | Gama Lusqtoff | Mantener hub, Black+Decker y disco. Añadir **guía para sierra circular** si la página identifica compatibilidad real de los modelos citados. |
| `/sierras/ingletadoras/` | Hub ingletadora | Incluirla en `/sierras/` como guía de tipo. Ya enlaza Einhell, DeWalt y Total. Añadir **sensitiva** en la explicación de corte de metal; evitar que DWE560 y SC16 ocupen más espacio que las ingletadoras en esta página. |
| `/sierras/sierra-caladora-bosch/` | Gama Bosch | Incluirla en `/sierras/` como marca. Mantener retorno a caladoras y comparación con Skil/Einhell. No enlazar circular y banco más de una vez por página. Verificar el código/nombre de la fila GST 75 E. |
| `/sierras/sierra-circular-dewalt-dwe560/` | Modelo DWE560 | Incluirla en `/sierras/` como modelo. Mantener hub, guía, disco, GKS 150 y SC16; quitar las menciones duplicadas a los dos competidores dentro de la misma sección. |
| `/sierras/stanley-sc16/` | Modelo SC16 | Incluirla en `/sierras/` como modelo. Mantener hub, guía, disco y comparación DWE560/GKS 150. La frase sobre banco es pertinente si se compara corte estacionario. |

### Cómo debe quedar la categoría `/sierras/`

- **Tipos y usos:** circular, sensitiva, sable, caladora, sin fin madera, banco, sin fin metal, ingletadora y sable inalámbrica (esta última como subtipo de sable, no al mismo nivel visual si se puede agrupar).
- **Marcas/gamas:** Einhell ingletadora, Skil caladora, DeWalt sensitiva/ingletadora, Total ingletadora, Black+Decker circular, Einhell caladora, Lusqtoff circular y Bosch caladora.
- **Modelos:** banco Einhell, Bosch GKS 150, DeWalt DWE560 y Stanley SC16. La página de banco Einhell es en realidad una gama; moverla a marcas/gamas si compara varios modelos.
- **Accesorios:** guía y disco para circular.
- Desde la portada, enlazar `/sierras/` y al menos una guía de familia; evitar llevar al usuario directamente a una ficha de modelo como único acceso al cluster.

### Reglas de implementación

1. Enlaces como `<a href="/sierras/.../">anchor descriptivo</a>` en HTML inicial o renderizado del servidor. Mantener breadcrumb `Inicio > Sierras > artículo`.
2. En cada ficha de modelo: un enlace a la guía de familia, uno al accesorio relevante y, como máximo, dos comparaciones directas. En cada hub: enlazar subpáginas donde se habla de ese caso.
3. No enlazar todas las 24 URLs desde un bloque idéntico. Evitar anchors genéricos como “ver más”; usar variantes naturales y comprobables.
4. Verificar que el destino responde 200, tiene URL canónica correcta y figura en sitemap cuando se publique. El enlazado interno debe apuntar a la versión canónica con barra final.

## ¿Crear más páginas?

**Ahora no abrir una tanda nueva.** Primero completar los 24 contenidos, corregir el renderizado y conectar las cuatro páginas ausentes del índice. Una revisión exhaustiva de las 140 filas del export adicional encuentra 27 consultas relacionadas con sierras o sus accesorios. Quince tienen una URL adecuada entre las 24 actuales. Las otras doce son:

| Consulta sin URL específica | Vol./KD Semrush | Decisión |
|---|---:|---|
| Ingletadora Makita | 170 / 11 | **Primera candidata posterior:** gama comercial distinta, si hay al menos dos modelos vigentes que comparar. |
| Sierra circular Makita | 210 / 14 | **Primera candidata posterior:** comparar modelos disponibles en Argentina y diferenciarla de la guía genérica. |
| Sierra sable Bosch | 210 / 14 | **Primera candidata posterior:** marca con intención comercial distinta de la guía de sable. |
| Sierra caladora DeWalt | 40 / 5 | Candidata pequeña y accesible si se pueden verificar modelos y stock local. |
| Sierra caladora Black+Decker | 140 / 16 | Segunda tanda; comparar gama real, no repetir la guía de caladoras. |
| Ingletadora Lusqtoff | 210 / 17 | Segunda tanda; verificar modelos fijos/telescópicos y diferencias útiles. |
| Sierra de banco DeWalt | 210 / 17 | Segunda tanda; confirmar modelos argentinos y separar de la guía de banco. |
| Sierra de banco Lusqtoff | 110 / 15 | Segunda tanda, según catálogo actual. |
| Hoja de sierra caladora | 140 / 18 | Primero mejorar la sección existente en `/sierras/caladoras/`; abrir guía de compatibilidad solo si aporta tabla propia por encastre, material y acabado. |
| Sierra caladora Stanley | 20 / 10 | Baja demanda; integrar en comparación del hub por ahora. |
| Sierra sable DeWalt | 110 / 27 | Aplazar por KD más alto; mencionar en la guía de sable si se compara un modelo real. |
| Sierras copa para madera | 170 / 18 | Es accesorio de perforación: evaluar en el cluster de taladros/brocas, no en sierras eléctricas. |

Priorizaría **ingletadora Makita, sierra circular Makita y sierra sable Bosch** cuando las 24 estén corregidas, y usaría la caladora DeWalt como prueba de cola larga si hay una ficha suficientemente útil. No crear URL independiente para “ingletadora telescópica”, “caladora a batería”, “disco para cortar melamina”, “mejor sierra circular calidad precio” o variantes de “opiniones” de los modelos existentes hasta validar SERP distinta, demanda y contenido único. Integrarlas en las páginas actuales. El dato “n/d” de Semrush no significa volumen cero.

## Orden de trabajo recomendado

1. Corregir afirmación de ensayos en el pie y cualquier promesa editorial no sustentada.
2. Renderizar el contenido Markdown en el servidor o generar HTML estático; probar el HTML inicial y la inspección de URL de Google tras publicar.
3. Añadir las cuatro URLs ausentes al índice `/sierras/` y ordenar las 24 por familias, marcas, modelos y accesorios.
4. Aplicar los enlaces contextuales de la tabla y quitar duplicados; comprobar destino y anchor.
5. Añadir fuentes oficiales y diferenciación en páginas de marca/modelo, comenzando por las de KD bajo.
6. Revisar títulos/H1 finos con datos de Search Console después de indexar. Mantener las URLs actuales para evitar redirecciones innecesarias.

## Disponibilidad de productos afiliables en Mercado Libre

**Fuente:** listado que el propietario compartió al buscar “Sierra” en la Central de Afiliados. Es una captura de disponibilidad, no un catálogo permanente ni una búsqueda exhaustiva por SKU. Entre los productos útiles para estas guías figuran caladoras Black+Decker BES603, Gadnic/Bron, Kanji, KLD, Dogo, Midow y una genérica; sierra sin fin Lusqtoff SFL250-8; sierra de banco Lusqtoff SML2000-8; y sensitivas genérica, Total y Lusqtoff CM-14K. La sierra sable para carne/hueso tiene otra intención y no corresponde a la guía actual de sable para madera/metal.

| URLs existentes | Decisión comercial inmediata |
|---|---|
| `/sierras/caladoras/` | Sí: recomendar 1–3 caladoras concretas de la lista según uso y presupuesto. La Black+Decker BES603 también puede aparecer aquí; no crear una página de marca solo por el enlace. |
| `/sierras/sierra-sin-fin-para-madera/` | Sí: Lusqtoff SFL250-8, si sus dimensiones y límites encajan con la recomendación editorial. |
| `/sierras/de-banco/` | Sí: Lusqtoff SML2000-8, explicando para qué trabajos conviene. No presentarla como Einhell. |
| `/sierras/sensitivas/` | Sí: comparar la genérica, Total y Lusqtoff CM-14K con códigos y datos verificados. No trasladar el producto Total a `/sierras/ingletadoras-total/`. |
| Las otras 20 URLs | Conservar si la guía resuelve una búsqueda real y tiene contenido útil. Quitar o desactivar el botón comercial de “Ver precio” hasta tener un producto que corresponda exactamente. Mantener enlaces internos hacia las cuatro guías con oferta cuando ayuden al lector, sin simular que son el mismo producto. |

**Medición comercial:** Los botones genéricos de búsqueda `listado.mercadolibre.com.ar` ya no aparecen en las vistas de sierras. Mercado Libre indica que solo los enlaces de afiliado creados con su Generador o Barra permiten seguimiento y atribución. Las páginas de sierras aún no tienen monetización activa. Cuando se elija un artículo elegible, generar el enlace oficial de ese producto, guardarlo con su código/fecha de verificación y usarlo en la página pertinente. Comprobar periódicamente que la publicación sigue disponible. No copiar precios, descuentos ni porcentaje de comisión como valores permanentes.

**Prioridad de nuevas URLs bajo esta restricción:** Antes de Makita, Bosch sable u otras marcas sin producto afiliable confirmado, mejorar las cuatro guías monetizables. Si luego se abre una URL nueva, `/sierras/caladoras-black-decker/` (140/KD 16 en Semrush) y `/sierras/de-banco-lusqtoff/` (110/KD 15) son candidatas por demanda y producto concreto; exigir contenido propio suficiente para no duplicar las guías de familia. La sensitiva Lusqtoff puede ser una sección en `/sierras/sensitivas/` por ahora.

## Referencias externas

- Google Search Central, JavaScript SEO: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google Search Central, enlaces rastreables y anchor text: https://developers.google.com/search/docs/crawling-indexing/links-crawlable
- Google Search Central, canonicalización: https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
- Mercado Libre, enlaces válidos del programa: https://www.mercadolibre.com.ar/l/afiliados-revisa-las-politicas
- Mercado Libre, generación de enlaces de afiliado: https://www.mercadolibre.com.ar/l/afiliados-links-de-afiliados
