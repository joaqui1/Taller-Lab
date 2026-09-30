# Afiliados de generadores — 29/09/2026

Integración local de 25 productos en 20 guías, con 74 CTA nuevos. La tabla de distribución por producto recibida define las ubicaciones; sus totales aproximados por página no siempre coinciden con esa distribución.

| Guía bajo /generadores/ | Productos nuevos |
| --- | ---: |
| comparativa-general | 7 |
| precios | 7 |
| honda | 5 |
| honda-6500 | 2 |
| para-casa | 5 |
| inverter | 5 |
| trifasicos | 2 |
| a-nafta | 8 |
| hyundai | 1 |
| gamma-6500 | 1 |
| lusqtoff | 5 |
| gamma | 5 |
| monofasicos | 5 |
| diesel | 0 |
| portatiles | 5 |
| silenciosos | 3 |
| gamma-950 | 1 |
| niwa | 2 |
| a-gas | 1 |
| estacion-de-energia-portatil | 2 |
| chicos | 2 |

Las filas de modelos llevan «Ver precio →»; las alternativas separadas usan el CTA específico recibido. El HTML aplica `target="_blank"` y `rel="nofollow sponsored noopener noreferrer"`. Los enlaces se registraron en el catálogo para validar los eventos de clic. Las guías usan sus tablas y bloques contextuales, sin un estante adicional que repita los nuevos productos al pie.

LGIS3.8-8, GNW-55-E, DELTA 2 Max y AC70P tienen bloques separados de LGI3.8-8, GNW-55-ER, DELTA 2 y AC70. Se conservan las especificaciones editoriales y los precios históricos con sus fuentes originales. Los referidos nuevos son ofertas separadas: no acreditan que el vendedor, precio o stock histórico corresponda a su destino.

Se completaron las etiquetas de atribución editorial que el servidor exige para mostrar las guías marcadas `published: true`. Las 20 rutas con nuevos CTA responden HTTP 200 en la verificación local.

## Pendiente de identidad

Hyundai HHY2200: el referido `https://meli.la/2fgrR1N` queda reservado en el catálogo de integración, sin CTA activo, hasta comprobar que Modelo/placa identifique **HHY2200F**. No se pudo verificar ese destino con la herramienta web; los enlaces cortos consultados tampoco permitieron comprobar las publicaciones. No se acreditan stock ni precios actuales de los referidos.

## Verificación

`python verificar_generadores_comerciales.py`: OK, 74 CTA, 25 productos, 20 rutas HTTP 200, atributos completos, tablas con columnas consistentes, encabezados originales conservados, variantes separadas y ejecución idempotente.

`python verificar_compresores_comerciales.py`: falla en la condición histórica sobre el modelo `AV000009`, relacionada con modificaciones previas del catálogo de compresores. Esos cambios no se modificaron en esta integración.

El detalle exacto de modelo, URL y guía está en `generadores-ofertas.json`. No se realizó despliegue externo.
