# Fotos de modelos — revisión final del 1 de octubre de 2026

Publicado en https://www.tallerlab.com.ar el 1 de octubre de 2026, commit 1f2aa1f. Verificado que las 190 rutas y 268 recursos públicos coinciden con la versión local aprobada.

Cobertura: 243 de 243 referencias comerciales con foto, sin pendientes. 235 archivos únicos; 221 fotos distintas utilizadas en las páginas publicables.

WebP de hasta 640 px. Peso medio: 22.2 KB; máximo: 58.6 KB. El catálogo completo ocupa 5.22 MB, pero cada página carga sus propias fotos de forma diferida. Dimensiones explícitas, caché immutable de un año y archivos con huella de contenido para actualizarse sin servir fotos viejas.

Las fotos de fabricante y las fotos principales de las publicaciones comerciales se registran por separado en fotos-modelos.json. En las ofertas ambiguas, la imagen corresponde a la publicación enlazada: no se deducen marca, código ni accesorios adicionales. Los avisos sobre identidad, variantes y contenido permanecen visibles.

Verificaciones: 190 rutas en tres anchos (320, 390 y 1440 px), total 570 vistas. Sin fotos rotas, errores JavaScript, desbordes horizontales ni alternativas ilustrativas activas. Se verificaron además 179 guías, formato y tamaño de todos los archivos, metadatos, canonical, JSON-LD, sitemap, anclas y enlaces de compra.

## Rendimiento móvil local

Los resultados finales de Lighthouse se registran en rendimiento-fotos-resumen.json. Son pruebas de laboratorio del proyecto local con simulación móvil: no son mediciones de usuarios reales ni del servidor publicado.

Inicio, categoría de taladros, guía de taladros inalámbricos y guía de generadores con más fotos.


| Página | Rendimiento | LCP | CLS | Bloqueo JS |
|---|---:|---:|---:|---:|
| home | 99/100 | 2.12 s | 0 | 0 ms |
| hub | 98/100 | 2.19 s | 0 | 0 ms |
| guia | 98/100 | 2.19 s | 0 | 0 ms |
| mas-fotos | 97/100 | 2.28 s | 0 | 20 ms |

## Verificación en producción

Las 190 rutas, 268 recursos y el sitemap coinciden con la versión aprobada. Las 244 imágenes versionadas usadas por estos controles responden con caché immutable de un año.

La revisión de navegador de producción pasó en 320, 390 y 1440 px: 570 vistas sin imágenes rotas, errores JavaScript, desbordes ni portadas genéricas. Registro: qa-fotos-produccion-2026-10-01.json.

Lighthouse móvil sobre el dominio público: inicio 100/100, categoría de taladros 99/100 y ambas guías 97/100. LCP entre 1.24 y 1.39 segundos; CLS 0 en las cuatro páginas. Son mediciones de laboratorio, no datos de usuarios reales.

Evidencia: despliegue-verificado-2026-10-01.json, produccion-rendimiento-fotos-resumen.json y produccion-lighthouse-fotos-*.json.

## Evidencia

- fotos-modelos.json: archivo, producto, procedencia y verificación de cada foto.
- verificacion-fotos-modelos.json: cobertura, tamaño y formato.
- qa-fotos-navegador.json: las 570 vistas verificadas.
- rendimiento-fotos-resumen.json y lighthouse-fotos-*.json: pruebas de rendimiento.

Para repetir: verificar_fotos_modelos.py, verificar_integracion_comercial.py, verificar_produccion.py, verificar_fotos_navegador.cjs y medir_rendimiento_fotos.cjs. Los dos controles de navegador necesitan el servidor local de Flask y las herramientas ya instaladas. Los scripts de descubrimiento y corrección descargan fotos solamente al ejecutarse de forma manual; el sitio no depende de los proveedores al cargar una página.
