# Integración de afiliados de hidrolavadoras — 29/09/2026

Se integraron 26 productos suministrados en 20 guías, con 40 asociaciones producto/página y 43 CTA. Las 23 guías del clúster responden HTTP 200 en el servidor local. Se respetaron las posiciones editoriales solicitadas y se repitió el mismo producto en precio para K3, Gamma 130 y HL-120. Gamma 150 queda sin CTA hasta recibir su enlace.

Los bloques usan las tarjetas, filtros y comparación existentes. No se repiten al pie ni muestran las ofertas genéricas anteriores de Logus o HL100-7. Las tarjetas presentan el código de referencia que debe cotejarse y dejan explícito que no se verificó el destino comercial. Los enlaces conservan exactamente los identificadores suministrados, con `nofollow sponsored noopener noreferrer`, apertura en otra pestaña y registro de clic compatible con el sitio.

Las guías ya declaraban `published: true`, revisión fechada y activo verificado. Se completaron las etiquetas de dato documentado/análisis y se normalizó el encabezado de fuentes para que pasen el filtro editorial existente. No se cambiaron sus tablas técnicas ni precios históricos. La guía HVAC reemplaza el bloque SpeedClean por WIPCOOL C30S con fuente del fabricante y discrepancia de potencia documentada.

## Pendientes

| Producto o lista | Motivo |
| :--- | :--- |
| Gamma 150 Elite G2514AR | Falta enlace. Afecta Gamma 150 y 150 bar. |
| Lüsqtoff HL100-8 | Falta enlace. Afecta 150 bar. |
| BLACK+DECKER BEPW1800T-AR | Falta enlace. |
| Lista Hidrolavadoras Hyundai | Falta enlace afiliado. |
| Lista hidrolavadora 200 bar | Falta enlace afiliado. |
| Kärcher K5 AR, enlace `2uTVRge` | Título de 380 L/h; falta confirmar código 9.398-295.0 y variante. No se asocia al SKU de la guía. |
| Bosch GHP 220, enlace `13efsmG` | Confirmar código argentino 0600910EH0 y frecuencia de placa. |
| STIHL RE 90, enlace `1fBYuUY` | El título suministrado indica 60 Hz; confirmar placa para instalación argentina de 50 Hz. |

No se crearon enlaces sustitutos ni listas de búsqueda sin afiliación. Los intentos de apertura de enlaces cortos mediante la herramienta web fallaron: no hay verificación de destino, precio o stock. El catálogo permite completar las posiciones pendientes y volver a ejecutar la integración.

## WIPCOOL C30S

La [ficha WIPCOOL](https://www.wipcool.com/high-quality-for-refrigeration-hand-oil-pump-steam-cleaning-machine-c30s-wipcool-product/) documenta la aplicación HVAC, modos de agua/vapor y versiones eléctricas. La ficha de 230 V declara 3.300 W máximos frente a 3.000 W en el título suministrado; la guía pide confirmar placa, potencia, kit y compatibilidad con la unidad. No se trasladan al equipo garantías universales sobre serpentines ni afirmaciones comerciales de desinfección.

## Verificación

- `python verificar_hidrolavadoras_comerciales.py`: pasó. HTTP 200 en 23 guías, tarjetas/CTA previstos, ubicación, exclusión de pendientes, atributos, tablas e idempotencia.
- `python verificar_generadores_comerciales.py`: pasó, 74 CTA en 20 guías.
- `git diff --check`: pasó.
- `python verificar_compresores_comerciales.py`: falla en la exclusión de AV000009 de su línea 65. El catálogo de compresores ya incluía ese modelo antes de esta integración; queda pendiente actualizar esa prueba en el trabajo de compresores.

Archivos: `hidrolavadoras_comerciales.py`, `hidrolavadoras-ofertas.json`, `integrar_hidrolavadoras_comerciales.py`, `verificar_hidrolavadoras_comerciales.py`, las 23 guías y la integración contextual en `servidor_local.py`. No se desplegó el sitio.
