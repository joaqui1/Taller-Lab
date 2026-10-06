# Operación de TallerLab Data

La edición es documental. No exige medir herramientas, adquirir equipos ni realizar ensayos físicos. La recuperación de un documento y una coincidencia textual no certifican rendimiento ni exactitud técnica.

## Edición entregada

100 modelos, seis categorías y 431 observaciones: 189 con concordancia textual. Las fichas muestran por separado las observaciones concordantes y las referencias excluidas. Los 16 candidatos están excluidos de esta edición con motivo registrado. Las 100 ofertas iniciales están archivadas sin evidencia y no representan precios actuales.

El comparador permite seleccionar entre dos y cuatro modelos, conserva valores originales, rechaza equivalencias dimensionales o contextuales no establecidas y explica sus exclusiones. No produce ganadores por cifras aisladas.

Las familias de aplicación separan taladros/percutores, rotomartillos, atornilladores de impacto y máquinas de banco. Las selecciones iniciales buscan pares de la misma familia; una familia con un único modelo no introduce un sustituto arbitrario. Las selecciones explícitas mezcladas se muestran con exclusión numérica. Las fichas se ordenan por proporción de observaciones concordantes, cantidad de observaciones concordantes y orden alfabético.

`affiliates.py` contiene doce asociaciones explícitas a enlaces existentes, con control de código de producto. No se generan enlaces por semejanza de marca o categoría. Se presentan como publicaciones comerciales para consultar, con aviso de comisión; no se usan como evidencia de precio, stock, kit exacto ni rendimiento. Cambiar ese registro no altera el orden documental.

## Archivos necesarios para publicación

Publicar el módulo `tallerlab_data`, sus datos JSON y `data/documentos/*.txt`, junto con las integraciones de `app.py` y `servidor_local.py`. El proyecto utiliza Flask y su configuración Vercel existente. No publicar bases SQLite, respaldos ni credenciales.

`data/catalog_snapshot.json` reconstruye automáticamente SQLite si no existe, con decisiones y correcciones. En Vercel se reconstruye en el directorio temporal. No se usa una escritura local serverless como persistencia compartida. La reconstrucción se prepara en un archivo temporal y se instala al terminar para evitar un catálogo parcialmente cargado.

`data/documentary_sources.json` registra recuperación, fecha, resultado HTTP y huellas de documentos. Los textos conservados permiten reproducir la concordancia sin una nueva descarga. `data/editorial_history.json` conserva las introducciones históricas retiradas del texto principal por falta de respaldo suficiente.

`data/reviewed_observations.json` contiene cinco incorporaciones documentales separadas: torque duro y suave y rango de peso DHP453, y rango de catálogo y peso de ficha web HR2470. El cierre exige localizar su código y valor antes de agregarlas, registra una corrección y no vuelve a insertar una observación ya existente. `source_publishers.json` registra la página oficial BTA que enlaza su catálogo alojado en Google Drive; el alojamiento externo se mantiene explícito. Las páginas PDF se derivan del texto conservado y los enlaces usan `#page=`.

## Ediciones posteriores, solo si se decide actualizar

Con las dependencias de `requirements.txt` instaladas, desde la raíz:

```powershell
python -m tallerlab_data.refresh_sources
python -m tallerlab_data.operacion cerrar-edicion
python -m tallerlab_data.operacion verificar
```

La actualización no es necesaria para que funcione la edición entregada. Recuperar fuentes requiere acceso a Internet; los PDF sin texto legible no se presuponen válidos. `cerrar-edicion` respalda SQLite, registra correcciones, excluye observaciones sin evidencia, cierra candidatos y guarda el snapshot. No transforma una ausencia documental en medición pendiente.

Para una incorporación documental explícita, `pipeline.resolve_candidate` exige decisión y justificación. Una aceptación requiere código exacto, ficha completa y evidencia por observación; no sobrescribe modelos existentes. Estas operaciones son de administración local y no son endpoints públicos.

## Descargas públicas

- `/herramientas/investigacion/descargar-datos.csv`: una fila por observación, incluidos estado documental y condición atribuida.
- `/herramientas/investigacion/descargar-datos.json`: edición completa y versión reproducible, sin candidatos internos.
- `/herramientas/investigacion/fuentes.json`: inventario documental, sin rutas locales.

La versión SHA-256 se calcula sobre el JSON público sin la clave `version`, serializado con claves ordenadas, sin espacios, caracteres Unicode sin escapes, separadores `,` y `:` y codificación UTF-8. Así puede comprobarse independientemente.

Las observaciones concordantes indican que el código aparece en el contenido y que el valor se encuentra con su unidad. En PDF se limita la búsqueda a páginas que contienen el código. Las referencias a protocolo o presión que no aparecen se bloquean. La presencia de esas referencias tampoco verifica su asociación semántica con todos los valores: revisar el documento original y la variante sigue siendo necesario.

## Recuperación

Los respaldos locales están en `tallerlab_data/data/respaldos/`. Para volver a una edición publicada, restaurar su snapshot y documentos conservados; detener la instancia local antes de reemplazar SQLite. La edición distribuida es el snapshot, no la base temporal de una instancia Vercel.

La publicación en el dominio existente requiere acceso al proyecto de despliegue. Esta entrega local no acredita que haya sido publicada.
