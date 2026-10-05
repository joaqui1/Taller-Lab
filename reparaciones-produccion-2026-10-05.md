# Reparaciones locales de producción — 5 de octubre de 2026

Las correcciones de código y la versión reproducible quedaron preparadas localmente en la rama `codex/produccion-2026-10-05`. El commit principal es `5019161`. Por indicación del usuario, no se subió el código, no se abrió un PR y no se modificó producción. La aprobación de funcionamiento remoto requiere las comprobaciones operativas indicadas abajo.

## Cambios realizados

- **Compatibilidad:** reconoce `ALERTAS_DATABASE_DATABASE_URL`, la conexión que ya aporta la integración Neon del proyecto. Conserva prioridad para `COMPATIBILITY_DATABASE_URL` y `DATABASE_URL`. Usa sus tablas propias, con un límite de conexión de diez segundos. No necesita copiar credenciales entre variables. Los errores internos del mantenimiento quedan en registros, sin devolver detalles de conexión al cliente.
- **Observatorio y descargas:** el build exige las 53 páginas y todos los CSV y datasets. Si falta el historial o falla la generación, termina con error. Las descargas de las siete categorías se comprobaron por HTTP sin depender de la base del observatorio anterior.
- **Sitemap:** requiere páginas generadas o el manifiesto producido por un build verificado. La mera existencia del historial ya no anuncia rutas que podrían faltar. El manifiesto se incluye en el código de la función para instalaciones donde el CDN sirve `public/` por separado.
- **Vista previa local:** Flask sirve también los assets generados, incluido el JSON público de precios.
- **Pruebas:** se aisló el contrato del observatorio anterior y se agregaron pruebas para generación fallida, archivos faltantes, manifiestos incompletos, descargas HTTP y selección de la base existente. Hay una prueba PostgreSQL de publicación, conflictos y rollback de compatibilidad en un esquema desechable.
- **Versión completa:** se registraron los módulos que faltaban en Git, con sus datos y assets. Se fijaron Python 3.12 y las versiones de dependencias utilizadas en las pruebas. Se excluyeron del despliegue directorios de descarte y resultados de auditoría.
- **CI:** `.github/workflows/verificacion-produccion.yml` ejecuta la suite, las verificaciones adicionales y el build, con PostgreSQL 17 aislado para las integraciones. Está preparado localmente; no se ejecutó en GitHub.

## Validación local

- Suite final: 208 pruebas, 206 aprobadas y dos omitidas por no disponer de PostgreSQL de pruebas. Sin fallas.
- Alertas y relevamiento: 33 pruebas adicionales aprobadas.
- Descargas y publicación del piloto: 18 pruebas aprobadas, incluidas en la suite principal.
- Recorrido local: 1.079 solicitudes, 760 respuestas HTML examinadas, 370 rutas de sitemap y **cero hallazgos** de enlaces, recursos o metadatos. El 503 de compatibilidad es esperado en ese entorno aislado sin base; el único 404 corresponde a una ruta inexistente usada para comprobar la respuesta.
- Build desde una copia limpia del commit: 384 assets, 44 observaciones y 53 páginas verificadas. Se comprobó el fallback al historial versionado cuando la red no está disponible.

Las versiones exactas están en [requirements.lock](<C:/Users/joaqu/Desktop/Taller Lab/requirements.lock>). El historial versionado es una copia de respaldo: la actualización diaria necesita activar la operación remota.

## Aplicación futura, cuando se autorice publicar

1. Subir la rama completa, abrir el PR y comprobar el workflow con PostgreSQL. La configuración del repositorio debe exigir ese check si se quiere bloquear fusiones que no lo aprueben.
2. Crear un despliegue de Vercel con variables de producción y sin promover inicialmente el dominio. Comprobar las páginas de precios, descargas, JSON público, sitemap y la interfaz móvil.
3. Ejecutar el cron de compatibilidad desde el panel autorizado de Vercel. Confirmar HTTP 200 en `/api/compatibilidad/estado`, persistencia disponible, fuentes comprobadas y fecha vigente. Repetir la lectura después de reiniciar o desplegar otra instancia.
4. Activar GitHub Pages con publicación mediante Actions y ejecutar `observatorio-gratuito.yml`. Comprobar la rama durable `observatorio-datos`, la captura real y las descargas publicadas. Configurar un deploy hook de Vercel si se quiere actualizar diariamente también el HTML del dominio principal; el cliente ya contempla la actualización desde Pages.
5. Obtener un respaldo independiente y restaurarlo en una base de prueba, sin reemplazar tablas productivas. Comprobar conteos, versiones y datos recuperados. Esta prueba de recuperación remota no se ejecutó.
6. Promover el despliegue y repetir las comprobaciones públicas. Comunidad y relevamiento conservan su configuración cerrada; abrir recepción de datos exige validar sus variables y recorridos contra la base real.

## Evidencia

- [Suite final](<C:/Users/joaqu/Desktop/Taller Lab/tmp/reparacion-produccion-tests-final.log>).
- [Alertas y relevamiento](<C:/Users/joaqu/Desktop/Taller Lab/tmp/reparacion-alertas-relevamiento.log>).
- [Descargas HTTP](<C:/Users/joaqu/Desktop/Taller Lab/tmp/reparacion-descargas-http-tests.log>).
- [Recorrido local](<C:/Users/joaqu/Desktop/Taller Lab/tmp/reparacion-recorrido-local.json>).
- [Build de la copia limpia](<C:/Users/joaqu/Desktop/Taller Lab/tmp/reparacion-build-limpio.log>).
- [Auditoría anterior y problemas del dominio publicado](<C:/Users/joaqu/Desktop/Taller Lab/revision-produccion-2026-10-05.md>).
