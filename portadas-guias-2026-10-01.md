# Portadas de las guías — 1 de octubre de 2026

Corregidas las miniaturas de las 179 guías, en las ocho categorías, en el buscador y en las tarjetas relacionadas. Se reemplazan los emojis usados como portada.

Las 179 tarjetas usan fotos reales de productos. Se eliminaron las 26 ilustraciones que habían quedado en la primera versión. Se reutilizan las fotos verificadas del catálogo y se agregan 16 fotos de fabricantes para las guías de accesorios, aerógrafos y estaciones de soldadura.

Las tarjetas mantienen alto fijo, dimensiones explícitas, carga diferida y decodificación asíncrona. Los equipos se muestran completos sobre fondo blanco. Las fotos usan caché immutable de un año y nombres con huella de contenido. Los metadatos Open Graph y Article también usan las fotos reales; no hay reemplazos por imágenes ilustrativas en caso de error.

Revisión: 190 rutas en anchos de 320, 390 y 1440 px, además de capturas de las ocho categorías en celular y escritorio. Se conservaron los controles de enlaces, metadatos, sitemap y recursos.

Rendimiento móvil local de inicio, categoría, guía y guía con más fotografías:
- home: 99/100; LCP 2.12 s; CLS 0.
- hub: 98/100; LCP 2.19 s; CLS 0.
- guia: 98/100; LCP 2.19 s; CLS 0.
- mas-fotos: 97/100; LCP 2.28 s; CLS 0.

Son mediciones de laboratorio local. El cambio se publicó en https://www.tallerlab.com.ar el 1 de octubre de 2026 (commit 1f2aa1f). Se verificaron las 190 rutas y 268 recursos públicos frente al contenido local, además de capturas de las ocho categorías en celular y escritorio.

Lighthouse móvil de producción: inicio 100/100, categoría de taladros 99/100 y ambas guías 97/100; LCP entre 1.24 y 1.39 s y CLS 0. Son mediciones de laboratorio sobre el dominio público, no datos de usuarios reales. Evidencia: despliegue-verificado-2026-10-01.json y produccion-rendimiento-fotos-resumen.json.

Asignaciones: portadas-guias.json; fotografías adicionales y fuentes: fotos-portadas-reales.json. Regeneración manual: python preparar_portadas_guias.py, antes de python preparar_assets_publicos.py. El generador y el renderer rechazan una guía indexable sin foto real. El despliegue sólo copia los archivos preparados, sin descargar fotos ni necesitar PIL para generarlas.

Evidencia: qa-fotos-navegador.json, rendimiento-fotos-resumen.json y vista-fotos/portadas-*.png.

La revisión de navegador en producción pasó en las 570 vistas (190 rutas en tres anchos), sin fallas. Registro: qa-fotos-produccion-2026-10-01.json. Capturas de producción: vista-fotos/produccion-portadas-*.png.
