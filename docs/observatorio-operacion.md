# Operación del observatorio gratuito

El historial durable vive en `observatorio-datos:precios-observatorio.json`.
El workflow `.github/workflows/observatorio-gratuito.yml` lo recupera, captura
las fichas pendientes del día de Argentina, guarda el historial, publica
GitHub Pages y dispara el build de www mediante `VERCEL_DEPLOY_HOOK_URL`.
El secreto debe contener la URL sin formato del deploy hook de Vercel para
`main`. No se debe guardar en el repositorio ni pegar en logs.
La rama de datos incluye un `vercel.json` con despliegues deshabilitados:
Vercel debe compilar `main`, no intentar encontrar una aplicación en el historial.

## Horarios y recuperación

- Primera ejecución: 07:17 ART. Respaldos: 10:37 y 16:37 ART.
- GitHub puede demorar u omitir ejecuciones programadas; tres horarios reducen
  el riesgo, pero no constituyen una garantía de disponibilidad.
- Las ejecuciones se serializan. Una ficha ya capturada ese día no se consulta
  otra vez. Las fallidas se reintentan y nunca se rellenan días sin evidencia.
- Para recuperar una ejecución, usar Actions → Observatorio gratuito → Run
  workflow. Por CLI: `gh api --method POST repos/joaqui1/Taller-Lab/actions/workflows/observatorio-gratuito.yml/dispatches -f ref=main`.
- Si captura pasó y publicación falló, reintentar el job fallido; no borrar el
  historial. Revisar por separado captura, Pages, hook y verificación de www.
- Una nueva fecha de ejecución no renueva por sí sola los precios: la vigencia
  de 48 horas se calcula con la fecha de cada observación.

## Verificación de publicación

El build exige todas las páginas y descargas, y comprueba que su copia en
`observatorio_publicado/` sea idéntica. El sitemap dinámico solo anuncia rutas
con archivo disponible. Un manifiesto de build, por sí solo, no acredita que
una función pueda servir una página.
La descarga del historial remoto usa una URL distinta por build y solicita
revalidación: la caché de la URL mutable de GitHub no debe reutilizar una captura
anterior justo después del push.

Después del deploy, el workflow verifica en www el dataset y todas las rutas
esperadas: HTTP 200, canonical correcto y la misma versión de publicación en
el HTML y en el JSON. También revisa vigencia y errores por ficha. Un fallo
aislado de captura se informa sin ocultar el resto; la ausencia de datos
verificados vigentes o un despliegue incompleto hacen fallar la verificación.

Comprobación manual, reemplazando FECHA por `run.finished_at` del historial:

```sh
python -m observatorio.publication_health --url https://www.tallerlab.com.ar --expected FECHA --wait-seconds 300
```

## Interpretación y límites

`reference_ars` es el importe tachado por el comercio, no una prueba de precio
de lista ni de un descuento histórico. Se clasifica fin de oferta cuando el
importe vuelve exactamente a esa referencia y deja de mostrar descuento;
inicio de oferta es el caso inverso. Otras transiciones con descuento se
rotulan cambio de oferta. El porcentaje sigue describiendo el importe a pagar,
sin atribuir automáticamente el movimiento a inflación o a un aumento de lista.

El CSV añade `precio_tachado_ars` y `tipo_cambio` al final de las columnas
existentes. Los códigos son `offer_ended`, `offer_started`, `offer_changed`,
`price_changed`, `unchanged`, o vacío cuando no existe comparación válida.

El hub expone los días con capturas y las fichas por comercio. El umbral del
veredicto se mantiene en 14 capturas con precio por modelo. No es una muestra
representativa del mercado: hay una oferta por modelo y concentración por
comercio. Ampliar la muestra requiere validar otra oferta de la misma variante
(EAN/SKU, kit, voltaje y accesorios) y separar comercio de identidad del modelo;
no alcanza con agregar URLs parecidas ni con bajar el umbral del veredicto.

## Auditoría del 7 de octubre de 2026

- Las 53 rutas respondieron 200: 44 modelos, siete categorías, hub y metodología.
  No se reprodujeron los 48 errores 404 reportados. El build productivo del
  commit `d9ff126` registró 88 observaciones y 53 páginas verificadas.
- El historial inicial tenía datos del 4 y el 6/10. El cron del 6/10 comenzó
  a las 13:47 ART aunque estaba previsto a las 07:17. No había ejecución del
  7/10 al iniciar esta revisión.
- Los logs confirmaron que faltaba `VERCEL_DEPLOY_HOOK_URL`: el éxito de Pages
  no implicaba actualizar el HTML indexable de www.
- Se configuró el hook y se recuperó la captura mediante la ejecución
  [37656855351](https://github.com/joaqui1/Taller-Lab/actions/runs/37656855351).
  La primera publicación falló por la URL del hook; se corrigió desde la salida
  JSON de Vercel y el reintento finalizó correctamente.
- Los días anteriores sin captura se conservan como huecos, no se reconstruyen.
- El control posterior a la integración detectó un build que leyó la publicación
  de las 14:11 ART a las 14:23, posterior al nuevo push del historial. La ejecución
  programada siguiente pasó el control completo; se corrigió además la descarga
  cacheada para no depender de ese reintento.
