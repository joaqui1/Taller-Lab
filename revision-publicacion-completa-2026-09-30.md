# Revisión de publicación — 30/09/2026

## Veredicto

El sitio ya está accesible en https://www.tallerlab.com.ar. La versión que sirve
actualmente funciona, pero no está lista para dar por publicada toda la colección
de guías. El problema principal es la exclusión editorial de archivos marcados
como publicados. No se desplegó ni se modificó el contenido durante esta revisión.

## Comprobaciones aprobadas

- Producción: 167 rutas indexables con respuesta HTTP 200, canonical correcto y
  URL final esperada, comprobadas individualmente por HTTPS.
- Local: 157 archivos de guía admitidos; 167 rutas HTTP 200 y 5.737 enlaces HTML
  válidos. Canonical, sitemap, robots y rechazo de configuraciones de producción
  incorrectas pasan `verificar_enlaces_publicados.py`.
- Revisión adicional de las 167 páginas locales: sin anclas internas inexistentes,
  IDs duplicados ni páginas con una cantidad de H1 distinta de uno.
- `verificar_soldadoras_comerciales.py`: pasó; 31 productos, 66 CTA en 27 guías,
  29 rutas HTTP 200 y repetibilidad de la integración.
- `node verificar_recursos.js`: pasó los cálculos y sus escenarios de límites.
- Navegador: portada revisada a 390 × 844 y 1440 × 900; portada y guía de
  compresores de 50 L sin desbordamiento horizontal observado a 390 px.
- Buscador: «taladro» devuelve 23 resultados y muestra inicialmente 12.
- Calculadora de caudal: cambiar consumo de 100 a 85 L/min actualiza el resultado
  a 13 L/min para salida de 98 L/min a 7 bar, con sus límites visibles.

## Pendientes antes del visto bueno completo

### 1. Alta prioridad: 21 guías devuelven 404 pese a estar marcadas como publicadas

El repositorio contiene **179 archivos**, de los cuales el filtro admite 157 y
excluye 22. Esto difiere del informe histórico de 178 guías revisadas y cero
pendientes. El archivo principal de amoladoras es uno de los excluidos, pero su
ruta sigue funcionando como hub de categoría. Las otras **21 rutas** devuelven
404 también en producción.

El filtro de `servidor_local.py:848` exige literalmente «Dato documentado»,
«Análisis TallerLab» y el encabezado `## Fuentes consultadas`. Los archivos
excluidos tienen `published: true` y metadatos de revisión, pero no cumplen una
o más de esas condiciones textuales. Amoladoras solo sirve cinco archivos de
guía; faltan, entre otros, Makita, DeWalt, Gamma, Lüsqtoff e inalámbricas. Sierras
excluye caladoras Skil y disco para sierra circular.

La lista completa, los archivos y las razones están en
`resultado-revision-publicacion-2026-09-30.json`, campos `excluded` y
`excluded_remote`. Se debe revisar el alcance editorial esperado y reconciliar
el cuerpo de esas guías con la política de publicación. Agregar etiquetas sin
verificar el contenido o desactivar el filtro no demuestra que estén listas.

### 2. Prioridad media: configuración comercial distinta del contenido visible

Cuatro ofertas configuradas no aparecen en el HTML servido:

| Guía | Modelo | Referido configurado |
| --- | --- | --- |
| `/generadores/portatiles/` | Konan KGE/800 | `https://meli.la/19gLhpz` |
| `/generadores/portatiles/` | Lüsqtoff LG950P | `https://meli.la/2oCYsWY` |
| `/sierras/sable/` | Bosch GSA18V24 | `https://meli.la/2mTTC3F` |
| `/sierras/sable/` | DeWalt DCS380B | `https://meli.la/2UW9Bfk` |

La guía de generadores portátiles deriva los equipos chicos a una comparativa
separada; esa puede ser una decisión editorial válida. Hay que ajustar la
configuración y la prueba a esa decisión, o recuperar una oferta si corresponde.
No se insertaron enlaces automáticamente.

### 3. Prioridad media: siete verificadores no pasan en el estado actual

| Verificador | Primer fallo observado |
| --- | --- |
| `verificar_integracion_comercial.py` | Conjunto de ofertas antiguo en hidrolavadoras general |
| `verificar_compresores_comerciales.py` | Supone que AV000009 no existe en todo el catálogo |
| `verificar_generadores_comerciales.py` | Falta KGE/800 en portátiles |
| `verificar_hidrolavadoras_comerciales.py` | No encuentra el encabezado esperado |
| `verificar_sierras_comerciales.py` | Diferencia de tabla en circulares respecto de Git HEAD |
| `verificar_taladros_comerciales.py` | Diferencia documental en inalámbricos respecto de Git HEAD |
| `verificar_hubs.py` | Rechaza «caudal real» en la descripción enlazada de pistolas para pintar |

Estos fallos no prueban siete defectos del sitio. Algunos controles corresponden
a una etapa previa, otros comparan contra un HEAD que ya no es una referencia
válida de todas las decisiones editoriales actuales. Deben actualizarse con una
referencia revisada, conservando controles significativos. No se alteraron tests
para convertirlos artificialmente en aprobados.

## Mejoras de interfaz de menor prioridad

- `servidor_local.py:1594`: falta un enlace para saltar al contenido principal
  mediante teclado.
- `servidor_local.py:1029`: hay varias reglas `transition: all`; conviene limitar
  las propiedades animadas. El sitio sí contempla movimiento reducido en CSS.
- `servidor_local.py:1830`: el campo del buscador carece de `name`, aunque tiene
  etiqueta accesible y funciona mediante JavaScript.

Se siguieron las [Web Interface Guidelines](https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).
La entrada Flask `app.py` coincide con una entrada admitida por la
[documentación actual de Vercel](https://vercel.com/docs/frameworks/backend/flask).
La prueba HTTP en producción confirma que el despliegue existente responde;
no se ejecutó un nuevo build o despliegue.

## Límites de esta revisión

Se verificaron rutas y enlaces internos completos, y una muestra funcional y
visual de navegador. No se cotejó nuevamente cada afirmación técnica contra
cada fuente externa, ni se confirmó individualmente el modelo, vendedor, stock
y destino final de todos los enlaces de afiliado. Varias tarjetas declaran
explícitamente «destino sin verificar»; los controles locales de afiliación
comprueban estructura y atribución, no la identidad real del producto al abrir
Mercado Libre. Tampoco se midieron Core Web Vitals con tráfico real ni se
consultó Search Console. Estos aspectos no quedan certificados por este informe.

## Evidencia reproducible

`revisar_estado_publicacion.py` guarda la exclusión editorial, las ofertas ausentes
y las respuestas de producción en `resultado-revision-publicacion-2026-09-30.json`.
Necesita las dependencias de `requirements.txt` y acceso de red.

Las dependencias temporales de esta auditoría se instalaron en
`.publication-qa-deps/`, excluida de Git. Las carpetas de dependencias de QA
preexistentes no eran legibles en el sandbox; las pruebas finales se ejecutaron
con acceso a la instalación nueva. No es un fallo del código de producción.
