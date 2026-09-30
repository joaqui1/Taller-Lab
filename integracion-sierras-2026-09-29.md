# Afiliados de sierras — 29/09/2026

Integración local del primer lote: **27 productos, 45 CTA en 25 guías**. Se respetaron los puntos editoriales de la tabla recibida; las tablas de capacidad conservan sus datos y los referidos aparecen en bloques separados. La comparación de sensitivas DeWalt lleva el bloque inmediatamente después de «Cuál elegir según el trabajo».

| Ruta bajo /sierras/ | CTA incorporados |
| --- | ---: |
| circulares | 4 |
| sensitivas | 2 |
| sable | 3 |
| caladoras | 3 |
| sierra-sin-fin-para-madera | 2 |
| de-banco | 2 |
| sin-fin-metal | 2 |
| ingletadoras-einhell | 1 |
| de-banco-einhell | 2 |
| guia-para-sierra-circular | 2 |
| sensitivas-dewalt | 2 |
| ingletadoras-dewalt | 2 |
| ingletadoras-total | 1 |
| bosch-gks-150 | 1 |
| caladoras-einhell | 2 |
| sierra-sable-inalambrica | 2 |
| circulares-lusqtoff | 1 |
| ingletadoras | 3 |
| sierra-circular-dewalt-dwe560 | 1 |
| stanley-sc16 | 1 |
| caladoras-black-decker | 1 |
| de-banco-lusqtoff | 1 |
| sensitivas-lusqtoff | 1 |
| sin-fin-lusqtoff | 2 |
| sensitivas-total | 1 |

Los enlaces usan `target="_blank"` y `rel="nofollow sponsored noopener noreferrer"`; están registrados para validar eventos de clic. Se desactivó la repetición en estantes y notas comerciales de estas rutas. El CTA antiguo de BES603 en la guía general fue sustituido, conservando su fuente y la explicación del sufijo B2.

Las variantes AR/B2 y los kits se identifican como datos a confirmar: no se afirma que el referido acredite el sufijo, la tensión o los accesorios. No se trasladaron precios, vendedores o stock de publicaciones históricas a los nuevos referidos. Se retiró el enlace de GSA 1100 E: la publicación activa titula «110 W» y una alternativa con «1.100 W» figura no disponible. La ficha técnica sigue respaldada por documentación de Bosch; el CTA queda pendiente de una publicación comercial coherente.

## Guía de terceros

El referido `https://meli.la/1xjT5i9` se presenta como **Surplee compatible con DW3278**, acorde al título recibido. No se rotula como producto original DeWalt ni se afirma compatibilidad universal. Kreg KMA2685 conserva una comprobación de base y montaje.

## Pendientes históricos del 29/09

Esta lista registra el estado de aquel lote. Las resoluciones recibidas el 30/09 figuran en `integracion-sierras-2026-09-30.md`; los modelos declarados sin afiliado ya no se consideran pendientes.

- GSA 1100 E: sin CTA activo hasta hallar una oferta disponible cuyo título y datos sean coherentes.
- Lüsqtoff SML2000-8: sin CTA activo por discrepancias entre documentos y una publicación que mezcla variantes; las guías enlazan por separado SML2000-9 y SML2000B-9.
- SKIL 4380 y 4550: referidos guardados sin CTA activo. La propuesta exige unidades nuevas exactas habilitadas por Afiliados; no se pudo comprobar esa condición porque la herramienta web no accedió a sus enlaces cortos.
- Faltan enlaces para Einhell TC-SM 2131/2 Dual; TOTAL TS42182553; los tres discos; Black+Decker CS1004-AR y CS1350P; Einhell TC-JS 18 Li-Solo; Lüsqtoff SCL2200-8; Bosch GST 650, GST 680 y GST 185-LI; Black+Decker BES602. Se conservan las condiciones de variante y código de la propuesta.

El detalle de distribución, anclas y pendientes está en `sierras-ofertas.json`. El lote puede ampliarse con los enlaces restantes.

## Verificación

`python verificar_sierras_comerciales.py`: OK. 45 CTA sin duplicación, atributos completos, registro de clics, encabezados originales conservados, tablas consistentes, ubicaciones e integración idempotente; las 25 rutas con nuevos CTA responden HTTP 200.

Las verificaciones de generadores e hidrolavadoras también pasaron después de esta integración. No se realizó despliegue externo. Los destinos cortos consultados no fueron accesibles con la herramienta web: esta verificación no acredita precios, stock ni contenido actual de las publicaciones.
