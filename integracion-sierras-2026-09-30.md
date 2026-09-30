# Afiliados de sierras — ampliación del 30/09/2026

Se incorporaron los siete referidos recibidos en cinco guías, con ocho CTA del lote: SML2000-9 aparece tanto en la guía de marca como en la guía general de banco. La integración completa queda en **32 productos activos, 50 CTA y 27 guías**. Esta actualización es local; no se realizó despliegue externo.

| Ruta | Incorporación o actualización |
| --- | --- |
| `/sierras/circulares-black-decker/` | CS1004-AR después de la tabla comparativa, con «Confirmá variante CS1004-AR, 220 V y disco incluido.» |
| `/sierras/caladoras-einhell/` | TC-JS 18 Li-Solo como tercera fila, después de TC-JS 85 y TE-JS 100; se aclara que Solo no incluye batería ni cargador. |
| `/sierras/sierra-caladora-bosch/` | Bloque después de la tabla GST 650 / GST 680 / GST 185-LI, con las tres ofertas en ese orden. GST 185-LI se presenta como herramienta sola/sin batería según el título recibido; cargador y kit deben confirmarse. |
| `/sierras/de-banco-lusqtoff/` | SML2000-9 y SML2000B-9, en ese orden, con los nuevos referidos. SML2000-8 queda excluida del bloque comercial. |
| `/sierras/de-banco/` | Nuevo referido de SML2000-9 junto a Einhell TC-TS 2025/2 U, sin oferta adicional de SML2000-8. |

Los siete modelos usan el CTA solicitado «Ver precio de [marca y modelo] →». Se conservan las comparaciones documentales y se evita duplicar ofertas por guía. Los enlaces mantienen apertura en otra pestaña, `nofollow sponsored noopener noreferrer`, aviso de afiliación y validación de clics.

El título recibido de SML2000-9 anuncia disco de 250 mm, mientras la documentación ya contrastada publica 255 mm. Se explica esa diferencia junto al CTA y se solicita confirmar placa/disco; no se modifica la ficha técnica para hacerla coincidir con el anuncio.

Los siete enlaces cortos no fueron accesibles mediante la herramienta web. Los títulos comerciales proceden del usuario; no se afirma haber verificado el destino, precio, stock ni contenido actual del kit.

## Verificación

`python verificar_sierras_comerciales.py`: OK. Se comprobaron los 50 CTA, sus textos visibles, ubicación, atributos, ausencia de enlaces excluidos, registro de clics, conservación de tablas y encabezados, integración idempotente y 27 rutas HTTP 200. También se cotejaron los siete referidos exactos y el orden solicitado en las cinco guías.

Esta ampliación resuelve los pendientes de CS1004-AR, TC-JS 18 Li-Solo y los tres Bosch GST. Continúan los pendientes de los otros modelos del informe del 29/09; SML2000-8 queda como referido excluido, reemplazado comercialmente por SML2000-9.
