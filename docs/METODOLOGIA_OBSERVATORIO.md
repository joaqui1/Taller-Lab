# Metodología del Observatorio — 2026.2

Observaciones de ofertas de modelos exactos en pesos argentinos. No representa todo el mercado ni garantiza el menor precio nacional. El piloto está pendiente de acreditar fuentes y realizar capturas reales.

- Identidad: código de fabricante normalizado exacto o identificación inequívoca en título; los códigos contradictorios se rechazan. No se comparan tensiones, condiciones o kits incompatibles. Los GTIN sin evidencia permanecen vacíos.
- Precio: pago único declarado en ARS; no se deduce moneda ni se toma una cuota. Los precios principales visibles contradictorios se retienen. Transferencia y referencia se registran solo en el bloque del producto. No se verifica por checkout el precio final ni el envío; deben describirse como declarados por el vendedor.
- Procedencia: las muestras nunca se publican. Las observaciones retenidas tampoco aparecen en CSV, series, históricos o mínimos. Se preserva evidencia limitada y hash; un hash demuestra integridad del contenido capturado, no veracidad del precio.
- Fuentes: evaluación documentada, fecha y permisos separados de captura y redistribución. Estado pendiente/descartado implica cero capturas. Mercado Libre permanece descartada. La habilitación técnica no constituye por sí misma acreditación jurídica.
- Vigencia: hasta 48 horas, sin fechas futuras. Se usa el último estado de cada oferta con desempate determinista. Agotamiento, anomalía o un intento fallido posterior ocultan el precio anterior de la comparación vigente.
- Captura: una observación válida por día ART y oferta. Se registran intentos separados. Fallos y anomalías pueden volver a intentarse sin fabricar precios.
- Estadísticas: mínimo, mediana y máximo entre ofertas elegibles; no promedio de observaciones repetidas. El histórico conserva las capturas válidas publicables.
- Series: último valor publicable de cada día ART por vendedor, hasta 365 días. Días faltantes explícitos; no interpolación. Se muestra la fecha de cada oferta, separada del estado general de actualización.
- Descuentos: comparación con días previos del mismo vendedor, excluyendo todo el período continuo del precio actual. Una observación por día. Requiere al menos tres días previos distintos; sin cobertura suficiente no emite una conclusión. No equivale a prueba de fraude o de una promoción engañosa.
- Canasta: suma de cinco modelos fijos, publicada solamente con cobertura completa. No es un índice mensual ni mide inflación. Un índice base 100 requiere diseñar y publicar su canasta, período base y tratamiento de faltantes por separado.
- Descargas: CSV UTF-8 con encabezado inicial y protección de fórmulas en texto. Su elegibilidad exige permisos de redistribución. La metodología no otorga derechos que pertenezcan a terceros.
- Correcciones: conservar observación y evidencia originales, registrar motivo y decisión; no aprobar precios manualmente mediante UPDATE sin trazabilidad. Resolver una incidencia administrativa no cambia automáticamente la observación.

La puesta en marcha exige validar fuentes y ofertas, probar PostgreSQL, supervisión y restauración, y medir cobertura con capturas reales antes de publicar investigaciones.
