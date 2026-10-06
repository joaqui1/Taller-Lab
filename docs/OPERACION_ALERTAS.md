# Operación del centro de documentación y alertas

Editor responsable: **Joaquín Vallasciani**. Esta asignación no acredita revisión personal de los registros anteriores. Cada aprobación conserva revisor, fecha y versión.

## Activación en Vercel

El 4 de octubre de 2026 se desplegó y verificó la versión pública con Neon PostgreSQL gratuito, claves de producción, recolección diaria e histórica reales y respaldo automático. Los cron están habilitados en Vercel; sus ejecuciones programadas futuras se comprueban con estado y logs. No confundir una ejecución manual correcta con evidencia de una ejecución futura.

Configurar en Production del proyecto `taller-lab`:

| Variable | Uso |
| --- | --- |
| `ALERTAS_DATABASE_URL` | PostgreSQL con TLS. La integración Neon con prefijo genera `ALERTAS_DATABASE_DATABASE_URL`, también admitida. Admite `DATABASE_URL` como alternativa. |
| `CRON_SECRET` | Secreto aleatorio para los cron; conservar el existente si otros servicios lo usan. |
| `ALERTAS_EDITOR_TOKEN` | Clave independiente para mesa editorial y respaldo. |
| `ALERTAS_RUN_BUDGET_SECONDS` | Opcional, 210 por defecto, máximo 240. |

No introducir secretos en repositorio, URLs ni reportes. SQLite y archivos locales sirven para QA, no para persistencia en Vercel. La primera conexión crea dos tablas e importa el snapshot incluido. Luego las aprobaciones se reflejan sin reconstrucción. No reinicializar la base para actualizar código.

`vercel.json` programa la tarea diaria desde las 09:00 de Argentina y la histórica los domingos desde las 10:00. Hobby ejecuta dentro de la hora, sin puntualidad al minuto: [límites oficiales](https://vercel.com/docs/cron-jobs/usage-and-pricing).

Tras desplegar, llamar `/api/alertas/ejecutar` con cabecera `Authorization: Bearer CRON_SECRET` y comprobar `/api/alertas/estado`. HTTP 200 acredita esa ejecución, no el próximo cron. Verificar también la primera ejecución programada en Vercel. HTTP 503 señala resultado parcial o configuración incompleta; 409, operación concurrente; 401, autenticación incorrecta. Una ejecución abandonada se recupera pasados seis minutos.

## Fuentes y límites

CPSC: novedades por última publicación, con solapamiento de dos días desde la última ejecución diaria correcta; sin antecedente, siete días. Se comprueban los números de campañas publicadas. La conciliación histórica por marcas se ejecuta aparte. Un error interno de la API nunca cuenta como respuesta vacía.

Argentina: planilla oficial completa filtrada por marcas y términos de herramientas. La última comprobación real revisó 531 filas. Un filtro de marca puede producir candidatos ajenos al catálogo; requiere cotejo. Reordenar filas no cambia la identidad, pero cambios de fecha, marca o descripción pueden crear un candidato que debe conciliarse.

SERNAC: seguimiento de las tres publicaciones citadas, con HTML archivado y contenido normalizado. No es rastreo exhaustivo del portal chileno.

Cada tarea admite dos intentos y tiempo limitado. Los fallos conservan la publicación previa y quedan registrados. Una ejecución histórica correcta no oculta una diaria fallida. Más de 48 horas sin éxito diario exige atención. El presupuesto puede dejar marcas históricas pendientes; al ampliar el catálogo, dividir o rotar lotes antes de anunciar mayor cobertura.

La descarga automática no renueva la revisión editorial ni autoriza el rótulo «sin alertas». Las revisiones de más de 90 días se señalan para revalidación.

## Mesa editorial

Abrir `/alertas/editorial/` y conectar con `ALERTAS_EDITOR_TOKEN`. La clave se conserva únicamente en memoria y se envía por cabecera; recargar o desconectar la elimina.

Consultar fuente original, payload y captura. Verificar modelo, variantes, mercado, lotes, excepciones, riesgo y acción oficial. Completar campos obligatorios; si no se informa un dato, declararlo expresamente después de cotejarlo. Confirmar la revisión como Joaquín Vallasciani solamente cuando corresponda.

La aprobación exige la misma versión abierta: ante una actualización, recargar y revisar de nuevo. Un aviso con varios modelos mantiene coincidencias pendientes. Una modificación conserva el texto publicado con advertencia hasta aprobar la nueva versión. Descartar exige motivo.

Una campaña CPSC o SERNAC no se convierte en argentina cambiando un campo. Equivalencias regionales, garantías y servicios locales requieren evidencia propia. Los registros históricos sin vínculo editorial moderno se exportan con `revision_version=cotejo_pendiente`; no completar ese dato sin revisión.

## Recursos y recuperación

- `/alertas/metodologia/`: criterios, cobertura y correcciones.
- `/alertas/estado/` y `/api/alertas/estado`: salud, antigüedad y pendientes.
- `/datos/alertas/avisos.csv` y `/datos/alertas/avisos.json`: publicaciones con fuentes y versiones.
- `/api/alertas/respaldo`: ZIP autenticado, capturas referenciadas y manifiesto SHA-256. Disponible también desde la mesa.

Antes de la primera recolección diaria se guarda automáticamente una copia ZIP en la misma base, con retención de 14 días y verificación SHA-256. Consultar `/api/alertas/respaldos` y descargar `/api/alertas/respaldos/AAAA-MM-DD` con la clave editorial. Esto protege frente a cambios accidentales, pero comparte el riesgo de pérdida de la base. Respaldar también antes de migraciones y conservar copias fuera de ella; ensayar la recuperación en una base aislada.

```powershell
python alertas_respaldo.py --guardar respaldo-alertas.zip
python alertas_respaldo.py --restaurar respaldo-alertas.zip
```

La restauración valida rutas, tamaños, manifiesto y hashes antes de reemplazar el estado transaccionalmente.

## Verificación y mantenimiento

```powershell
python alertas_operacion.py
python alertas_operacion.py --historico
python alertas_operacion.py --estado
python gestionar_alertas.py auditar
python -m unittest verificar_alertas
python -m unittest discover -s tests -p 'test_alertas*.py'
```

`ALERTAS_DATA_DIR` señala un directorio duradero local; `ALERTAS_STATE_PATH` habilita SQLite de QA. `ALERTAS_SOLO_LECTURA=1` impide mutaciones. Vercel sin PostgreSQL sirve el snapshot y rechaza la ingestión.

Las pruebas cubren SQLite, rollback, concurrencia local, versiones, reintentos, autenticación, mercado, aprobación y restauración. Se verificó PostgreSQL remoto, lectura concurrente durante la recolección, respaldo y acceso autenticado en Vercel. La revisión visual se hizo sobre el despliegue, en escritorio y móvil. Los reportes `qa-alertas-vercel-2026-10-04.json` y `qa-alertas-historico-vercel-2026-10-04.json` conservan resultados sin claves.
