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

Esta primera ampliación resolvió los pendientes de CS1004-AR, TC-JS 18 Li-Solo y los tres Bosch GST. El estado actual después del segundo lote se detalla abajo; SML2000-8 queda como referido excluido, reemplazado comercialmente por SML2000-9.

## Segundo lote del 30/09: afiliados y kits complementarios

Se activaron SKIL 4380 (`1cCuNwX`) y 4550 (`2nTwNzm`), Diablo D0760X (`158XrS6`) y Lüsqtoff SCL2200-8 (`33Aphuu`). La oferta D0760X está identificada por separado del D0760A de las tablas documentales; no se presupone equivalencia entre códigos.

La guía `/sierras/caladoras-black-decker/` ahora trata la BES603 en lugar de comparar con la BES602: conserva íntegros los datos documentados de BES603-B2, la comprobación de variante y el afiliado `2azLzTF`. El CTA de BES603 también identifica marca y modelo en la guía general de caladoras.

En `/sierras/sierra-circular-inalambrica/` se incorporaron tres kits, cada uno debajo del CTA de su sierra:

| Sierra | Complementario | Referido |
| --- | --- | --- |
| Einhell TP-CS 18/190 Li BL-Solo | Starter Kit Power X-Change 18 V 4 Ah, batería y cargador rápido según el título recibido | `2Ut4FSd` |
| Bosch GKS 185-LI | Kit Professional 18 V 1600A015TD, dos baterías de 4 Ah y cargador según el título recibido | `1aD8WYE` |
| DeWalt DCS570B | Kit 20V MAX POWERSTACK DCBP034C, batería y cargador según el título recibido | `237pWXz` |

Se retiraron de pendientes TC-SM 2131/2 Dual en sus dos guías, TOTAL TS42182553, EXPERT19060 y CS1350P. Permanecen como referencias sin afiliado por decisión del usuario. BES602 queda registrada como reemplazada; D0760A, como referencia documental con oferta D0760X separada. PRO19054 sigue sin enlace y con monetización sin urgencia. GSA 1100 E continúa pendiente de una publicación coherente; SML2000-8 permanece excluida.

El manifiesto actual registra **60 CTA en 30 guías y 42 productos activos**; este lote suma siete CTA respecto del manifiesto anterior (53). Los totales de los informes anteriores son históricos y no sustituyen el manifiesto actual. No se realizó despliegue externo.

La herramienta web no pudo acceder a los ocho referidos cortos consultados. Los títulos de ofertas proceden del usuario; no se verificaron destinos, stock, precio, contenido ni tensión de los cargadores. Junto a cada kit se solicita confirmar plataforma y tensión de entrada del cargador.

Verificación de este lote: `python verificar_sierras_comerciales.py --pages 4 8 10 14 15 17 20 21 25 30`, OK: **21 CTA en 10 rutas HTTP 200**, ubicación de los kits, textos, atributos, registro de clics e idempotencia. Se comprueba la conservación de tablas documentales, proyectando la columna BES603 para la sustitución solicitada.

Se agregó `--pages` a integración y verificación para actualizar solo las guías seleccionadas. La ejecución global ya tenía una desincronización ajena a este lote: la guía de sable no contiene el encabezado «Sierra sable con cable o inalámbrica» indicado por su configuración histórica. Esa guía no se modificó.
