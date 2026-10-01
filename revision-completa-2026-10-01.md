# Revisión final de TallerLab — 1 de octubre de 2026

Versión publicada: commit `3cd9d9b`, https://www.tallerlab.com.ar, CSS v11.

Se corrigió el problema de la captura adjunta: las citas de Mercado Libre heredaban el estilo del botón comercial. El estilo de botón ahora se aplica a `.btn-mercado-libre`; las fuentes conservan su presentación de enlace de texto. Comprobado en producción en celular y escritorio, y en los 340 enlaces de fuentes presentes en las rutas revisadas.

| Control | Resultado y evidencia |
|---|---|
| Publicación | 190 rutas y 267 recursos iguales a la versión local; sitemap de 190 URLs. `despliegue-verificado-2026-10-01.json` |
| Fotos | 243 referencias con foto, 235 WebP del catálogo y 16 adicionales para las guías, sin pendientes. Media 22.2 KB; máximo 58.6 KB. `verificacion-fotos-modelos.json` |
| Portadas | Corregida la decisión anterior: las 179 guías en ocho categorías usan fotos reales, cero ilustraciones. `portadas-guias.json` |
| Visual en producción | 570 vistas: 190 rutas a 320, 390 y 1440 px, incluyendo secciones desplegables abiertas; sin imágenes rotas, desbordes, errores JS, ilustraciones, recortes por el marco ni etiquetas superpuestas. `qa-encuadres-produccion.json` |
| Imágenes del buscador | Las 179 portadas a 320, 390 y 1440 px: foto igual a la asignación, ajuste contain, carga y encuadre completos, sin superposición. `qa-imagenes-buscador.json` |
| Interacciones en producción | 190 rutas, 74 recursos, 108 filtros y 36 comparadores; sin fallas ni errores JS. `qa-interacciones-produccion-2026-10-01.json` |
| Buscador | Recuperación tras HTTP 503, resultados, ver más, búsqueda vacía y limpieza comprobados en navegador. Mismo registro de interacciones |
| Enlaces y estructura | 7.314 enlaces HTML; canonical, fuentes, H1, anclas, redirecciones con query, robots, sitemap, 404, HEAD y rechazo de rutas inválidas. `verificar_enlaces_publicados.py`, `verificar_hubs.py`, `verificar_produccion.py` |
| Comercio | 179 guías y 470 enlaces afiliados registrados; atribución y condiciones de variante conservadas. `verificar_integracion_comercial.py` |
| Catálogos | Controles de compresores, generadores, hidrolavadoras, sierras, soldadoras y taladros pasaron; posiciones, modelos, exclusiones, CTA y eventos. Scripts `verificar_*_comerciales.py` |
| Cálculos y selección | Límites, materiales, presiones, listas, costos y autonomía verificados; 74 recursos y 24 configuraciones de compra. `verificar_recursos.js`, `verificar_seleccion.py` |

El control histórico de compresores se actualizó para comprobar el cierre del contenedor de desplazamiento que ahora llevan las tablas con fotos; sigue exigiendo que no haya contenido adicional entre la tabla y sus tarjetas.

Capturas del bloque corregido: `vista-fotos/produccion-fuentes-390.png` y `vista-fotos/produccion-fuentes-1100.png`.

El encuadre de fotos se corrigió globalmente: las tarjetas tienen filas independientes para etiquetas, fotografía y procedencia. La imagen ocupa su propio marco con ajuste contain, sin transformaciones ni recortes. Las fotografías originales no fueron modificadas. La imagen Bosch GHP 180 conserva los 422 × 422 px del archivo del fabricante. Captura actual de producción: `vista-fotos/bosch-despues-produccion.png`.

El contenido distingue fichas de fabricantes, publicaciones comerciales y variantes pendientes. Los controles de publicación no certifican precio, stock, vendedor ni contenido actual de las ofertas externas; esas condiciones se consultan en la publicación enlazada.
