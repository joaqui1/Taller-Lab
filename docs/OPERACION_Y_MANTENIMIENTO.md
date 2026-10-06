# Operación del Observatorio TallerLab — versión 2

El sistema está preparado para un piloto. No contiene fuentes acreditadas ni demuestra todavía capturas de tiendas reales. No debe describirse como un servicio productivo hasta verificar fuentes, URLs y entorno.

## Configuración

- Local: SQLite en `observatorio/observatorio.db` o `OBSERVATORY_SQLITE_PATH`.
- Vercel producción: `DATABASE_URL` PostgreSQL es obligatoria; no hay fallback a SQLite.
- `CRON_SECRET`: token que usa Vercel para el cron. Tiene prioridad sobre `OBSERVATORY_SECRET`; el monitor debe usar el mismo token.
- `OBSERVATORY_MAX_BATCH_SIZE=50`: entre 1 y 50 ofertas por ejecución. El parámetro HTTP también se acota.
- `OBSERVATORY_RUN_BUDGET_SECONDS=240`: presupuesto máximo entre ofertas/intentos. Una petición puede superar ligeramente el límite restante; Vercel tiene `maxDuration=300` configurado. Confirmar que el plan y el despliegue acepten ese límite.
- `SITE_URL`: URL efectiva del despliegue.

## Inicialización y migración

Instalar `requirements.txt` y ejecutar:

```sh
python -m observatorio.cli init-db
python -m observatorio.cli seed-catalog
```

`init-db` migra las columnas antes de crear índices. En SQLite crea automáticamente un respaldo previo si detecta el esquema anterior. Las observaciones antiguas sin procedencia explícita quedan sintéticas; los hashes de fixtures conocidos quedan retenidos. No modifica los archivos de la base hasta ejecutar el comando. Para PostgreSQL, obtener un respaldo comprobado del proveedor antes de migrar.

`seed-catalog` sincroniza el registro: fuentes no acreditadas permanecen pendientes o descartadas, sin permisos de captura/publicación. Conserva pausas operativas de ofertas. No vuelve a habilitar una fuente solo porque su estado anterior en la base fuese habilitada.

## Habilitación de fuentes

Verificar acceso, condiciones de uso y correspondencia de cada URL con modelo, tensión, condición y kit. En `sources.py`, registrar la referencia comprobable, fecha, `capture_allowed`, `redistribution_allowed` y estado. El registro inicial deja todas pendientes y Mercado Libre descartada. Una fecha o un booleano no sustituyen evidencia.

El CSV y los históricos requieren permiso explícito de redistribución. No hay que habilitar fuentes para llenar el catálogo. Empezar con 10 modelos comprobados.

## Captura y cobertura

```sh
python -m observatorio.cli run-collector --batch-size 50
python -m observatorio.operations health
```

Vercel dispara el cron a las 10:00 UTC / 07:00 ART. La clave de captura es día ART + oferta + procedencia. Los reintentos no duplican un estado válido. Los intentos fallidos quedan separados y ocultan un precio anterior de los mínimos vigentes hasta verificar nuevamente.

El bloqueo utiliza una fila de concesión actualizada atómicamente. Dura 15 minutos, superior al presupuesto de ejecución. Los límites por dominio incluyen reintentos. Un Retry-After que no cabe en el presupuesto difiere la oferta; no lo acorta. Las redirecciones requieren corregir y verificar la URL final en la configuración.

La respuesta y el diagnóstico indican ofertas pendientes. Un lote completado no acredita cobertura del catálogo; el monitor exige todas las ofertas previstas para el día. Cero fuentes verificadas es un estado degradado, no un éxito.

## Supervisor y respaldos independientes

Se entrega `.github/workflows/observatorio-operacion.yml`, sin activar servicios ni cargar credenciales. Para habilitarlo en GitHub:

- Variable `OBSERVATORY_OPERATIONS_ENABLED=true` y `OBSERVATORY_SITE_URL`.
- Secretos `OBSERVATORY_CRON_SECRET`, `OBSERVATORY_DATABASE_URL`, `OBSERVATORY_BACKUP_PASSPHRASE`.
- Confirmar compatibilidad de `pg_dump` del runner con la versión del servidor; actualizar el cliente si fuera necesario.
- Verificar la política de notificaciones de ejecuciones fallidas en GitHub.

A las 11:15 UTC completa hasta tres lotes pendientes y comprueba cobertura. El job de respaldo funciona independientemente de la salud del cron. Genera un dump, comprueba su índice, cifra con GPG y guarda solo el archivo cifrado, con retención de 14 días. El archivo sin cifrar se elimina del runner incluso si ocurre un error.

Esto todavía requiere prueba real de restauración; comprobar el índice de un dump no es restaurarlo. Descargar un respaldo, descifrar en un entorno privado y restaurar exclusivamente a una base vacía de prueba, usando `pg_restore --no-owner --exit-on-error`. No utilizar `--clean` sobre una base productiva. Comparar tablas, conteos, observaciones y cobertura. Conservar la contraseña de cifrado fuera del repositorio.

Para SQLite local:

```sh
python -m observatorio.cli backup --dest copia.db
```

Usa la API de backup de SQLite y cierra conexiones; no copia un archivo mientras se escribe.

## Pruebas

```sh
python -m unittest discover -s tests -p 'test_observatorio*.py' -v
```

La suite usa una base temporal y verifica su ruta efectiva antes de borrar filas. Una integración PostgreSQL adicional se ejecuta si se proporciona `OBSERVATORY_TEST_DATABASE_URL`: crea y elimina un esquema desechable en una instancia de pruebas. Nunca proporcionar la URL productiva para este test.

## Publicación

Las páginas vacías quedan fuera del sitemap y sin Dataset. Cada categoría se evalúa dinámicamente. Las comparaciones muestran vendedor, precio, transferencia, captura y enlace. El histórico por modelo presenta una observación por día ART y vendedor; los días faltantes interrumpen las líneas. El CSV comienza directamente por el encabezado; versiones y metodología se documentan aquí y en la página pública.

No se ha medido todavía costo ni duración con fuentes reales. No hay garantía de costo cero, de cobertura nacional ni de funcionamiento sin mantenimiento. Para habilitar producción faltan evidencia de fuentes, credenciales, prueba PostgreSQL, captura real programada y restauración comprobada.
