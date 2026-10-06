# Observatorio gratuito de TallerLab

Preparado localmente el 4 de octubre de 2026. **Falta subirlo y activar GitHub Pages/Actions. No se publicó desde esta sesión.**

44 modelos, 7 categorías y 3 comercios. Primera captura real: 44 fichas validadas, 35 disponibles y 9 agotadas. Tres fichas agotadas no informan precio: cero no se interpreta como una oferta gratis. Todavía no hay tendencias: una primera captura por modelo.

## Activación cuando lo subas

1. Subir los cambios al repositorio **público** `joaqui1/Taller-Lab`, rama `main`. Incluir `observatorio/`, assets nuevos, `assets/datos/precios-observatorio.json`, el workflow y las pruebas. `public/`, `tmp/`, `_site/`, `_state/` y las bases locales no se suben. No subir `.env`, tokens o respaldos.
2. En GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions**. Si Actions está restringido, permitir las acciones oficiales usadas en el workflow.
3. En **Actions → Observatorio gratuito - captura y publicación → Run workflow**, ejecutar sobre `main` y comprobar que captura y publicación terminen correctamente. Si el primer push ocurrió antes de activar Pages, repetir manualmente después de configurarlo.

URL gratuita prevista: https://joaqui1.github.io/Taller-Lab/datos/precios-herramientas-argentina/

Captura diaria programada aproximadamente a las **07:17 de Argentina**. GitHub puede demorar o suspender ejecuciones; no garantiza el horario. La PC puede estar apagada. La operación externa se considera verificada después de esa primera ejecución real y de abrir el sitio publicado.

## Costos y servicios

El workflow usa Ubuntu estándar en repositorio público y GitHub Pages. No requiere API comercial, PostgreSQL, cuenta nueva, tarjeta, secreto manual ni cron de Vercel. Omite la ejecución si el repositorio es privado. Retiene el artefacto de publicación un día; no usa cachés grandes, runners pagos ni respaldos externos.

GitHub documenta [la gratuidad de los runners estándar en repositorios públicos](https://docs.github.com/en/billing/concepts/product-billing/github-actions) y [Pages para repositorios públicos de GitHub Free](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages). Esto no cambia los costos de otros productos o proyectos de tu cuenta.

## Cómo funciona

- `observatorio/piloto_gratuito.json`: modelos, variantes, URLs y reglas de identidad. 24 fichas de Mega Store Lüsqtoff Hurlingham, 18 de DGM Maquinarias y 2 de Bulonfer. Selección editorial por tareas y gamas; no ranking de ventas ni todo el mercado.
- `observatorio/gratuito.py`: revisa robots, identidad, moneda, precio principal y stock. Espacia solicitudes y pausa el dominio ante 403/429/503. No evade CAPTCHA ni bloqueos. Acepta automáticamente los cambios corroborados con el precio visible del mismo producto y variante. Registra los saltos de 35% o más frente a la mediana de hasta siete observaciones disponibles con `jump_verified` y comienza una nueva referencia.
- `assets/datos/precios-observatorio.json`: primera captura pública real. Sin HTML, cookies o credenciales. Los centavos estructurados de DGM deben coincidir exactamente con el redondeo visible al peso.
- Rama `observatorio-datos`: guarda el historial durable de hasta 365 días. **No borrarla**. El workflow no modifica `main` diariamente.
- `observatorio/estatico.py`: genera hub, siete categorías, metodología, CSV por categoría, JSON, sitemap y estado. Una oferta por modelo/variante; no compara todos los vendedores.
- Precio actual: disponible, verificado y con antigüedad máxima de 48 horas. Un error posterior, stock desconocido o fecha vencida lo excluye. El navegador revisa la edad al abrirse y cada minuto. Sin JavaScript se ve la instantánea fechada del último build.

## Integración con las rutas originales

Las cinco rutas originales y las cuatro categorías nuevas funcionan en local. `app.py` y `servidor_local.py` sirven las páginas generadas en `public/`. El build existente genera el piloto sin reemplazar la portada principal. Se retiró solamente el cron del observatorio en Vercel.

Cuando estos cambios estén también desplegados en **www.tallerlab.com.ar**, las páginas intentarán leer el JSON actualizado de Pages, validando modelo, variante y URL. Las descargas apuntan al historial de Pages. Si no se puede leer el JSON, muestran la captura guardada con su fecha, ocultan precios vencidos y ofrecen un enlace a Pages. Esa lectura cruzada y las URLs públicas deben comprobarse después de activar Pages; no están verificadas en producción.

Pages publica el observatorio: no migra automáticamente el resto del sitio ni cambia tu dominio. Las rutas originales de www requieren desplegar el código actual de TallerLab. El observatorio en Pages funciona por sí solo sin pagar Vercel.

## Verlo y actualizarlo localmente

Desde PowerShell en esta carpeta:

```powershell
.\iniciar-observatorio-gratuito.ps1
```

Abrir http://127.0.0.1:8921/datos/precios-herramientas-argentina/ en el navegador. Ctrl+C cierra el servidor. Para capturar manualmente antes de abrirlo:

```powershell
.\iniciar-observatorio-gratuito.ps1 -Actualizar
```

Se guarda como máximo una captura válida por modelo y día argentino; repetir no duplica el historial. Necesita Python 3.12 y las dos dependencias gratuitas de requirements. El script usa el runtime local de Codex si está instalado.

Generar páginas sin consultar nuevamente los comercios:

```text
python -m observatorio.gratuito --skip-collection
```

## Fuentes y variantes

Se revisaron páginas públicas, robots y condiciones cuando estaban enlazadas. Eso no se presenta como licencia o contrato del comercio. Se publican hechos observados, identificadores, enlaces y hashes propios; no se redistribuyen fotos o descripciones. No se consulta Mercado Libre: algunas URLs de DGM contienen códigos de sus publicaciones, pero las solicitudes van exclusivamente a DGM.

La ficha GHP 4-50 declara 60 Hz: confirmar antes de comprar. Las propiedades técnicas dudosas del vendedor no se toman como recomendaciones. La Belarra de la URL «130bar» se identifica por ficha y referencia como **H1500**. Se excluyó GWS 2200-180 por identidad contradictoria e IRON-180 por precio cero con stock; se incorporó IRON-MIG-100 en una ficha verificable.

## Si falla una captura

Revisar el workflow y `estado.json`. Los errores se publican como «sin verificación» y conservan el historial. Una falla parcial genera un aviso después de publicar; el siguiente ciclo vuelve a intentar el producto afectado. Los cambios de precio corroborados son automáticos. Para un cambio real de SKU/variante, confirmar la ficha, actualizar el manifiesto y documentar la revisión. Una variante nueva requiere un identificador nuevo; no mezclar kits.

Las fallas de permisos de Pages o de la rama de datos se resuelven en GitHub. Ante bloqueos del vendedor, revisar la fuente sin aumentar solicitudes ni eludir restricciones.

No se necesita `price_review` para cambios de precio. Se conservan las marcas históricas `jump_reviewed`, pero las nuevas verificaciones automáticas usan `jump_verified`. La comprobación de Pages exige el identificador temporal de esta ejecución y reintenta mientras se propaga la publicación. Una publicación inaccesible, vencida, incompleta o sin ningún producto capturado sigue marcando error.

## Verificación local

Suite de observatorio: 48 pruebas ejecutadas, 47 aprobadas y una de PostgreSQL omitida por falta de instancia de prueba (este sistema no la necesita). Incluye identidad, precio principal/cuotas, redondeo DGM, agotado/cero, vigencia, fallas posteriores, robots, bloqueo HTTP, saltos de precio corroborados automáticamente y rechazo de precios contradictorios, idempotencia, historial durable, siete categorías, CSV y subruta de Pages. El contrato HTTP del sistema anterior está aislado del piloto nuevo.

Verificación adicional: las nueve rutas HTML devolvieron 200, los ocho CSV contienen las filas correspondientes y el sitemap incluye las siete categorías. Se ensayó guardar/recuperar el historial y avanzar su rama en repositorios temporales de Git. Búsqueda, orden por precio e historial comprobados en el navegador; vista de celular de 390 px sin desborde horizontal.

Pendiente externo: subir, activar Pages/Actions y verificar la primera captura y publicación. No se hizo push, cambio de DNS ni alta de un servicio pago.

## Modelos seleccionados

### compresores (8)

- Lüsqtoff LC2550B-8 — Ficha individual del comercio
- Lüsqtoff LC-2550BK — Ficha individual del comercio
- Lüsqtoff LC-3550BK — Ficha individual del comercio
- Lüsqtoff LC-0122 — Ficha individual del comercio
- Lüsqtoff LC-40100 — Ficha individual del comercio
- Lüsqtoff LC-30100 — Ficha individual del comercio
- Lüsqtoff MCL150-8 — Ficha individual del comercio
- Lüsqtoff LC-826 — Ficha individual del comercio

### hidrolavadoras (7)

- Lüsqtoff HL-120 — Ficha individual del comercio
- Lüsqtoff HL100-7 — Ficha individual del comercio
- Lüsqtoff HL1800-8 — Ficha individual del comercio
- Lüsqtoff HL2100-9 — Ficha individual del comercio
- Bosch GHP 4-50 — 220 V · ficha del vendedor: 60 Hz (confirmar antes de comprar)
- Belarra H1200 — Ficha individual del comercio
- Belarra H1500 — Ficha individual del comercio

### generadores (6)

- Lüsqtoff LG950P — Ficha individual del comercio
- Lüsqtoff LG3000 — Ficha individual del comercio
- Lüsqtoff LG3000E — Ficha individual del comercio
- Lüsqtoff LG7500EX — Ficha individual del comercio
- Lüsqtoff LGI2.5-8 — Ficha individual del comercio
- Lüsqtoff LGI8.0-9 — Ficha individual del comercio

### soldadoras (5)

- Lüsqtoff IRON-100-8 — Ficha individual del comercio
- Lüsqtoff IRON-140 — Ficha individual del comercio
- Lüsqtoff IRON-MIG-100 — Ficha individual del comercio
- Lüsqtoff SML120-8D — Ficha individual del comercio
- Lüsqtoff EVO-MIG-175 — Ficha individual del comercio

### taladros (7)

- Bosch GSB 13 RE — 220V - 230V · ficha individual
- Bosch GSB 16 RE — 220V · ficha individual
- Bosch GSB 185-LI — Kit: 2 baterías de 2 Ah + cargador
- Bosch GSB 183-LI — Kit: 2 baterías de 2 Ah + cargador
- Bosch GBH 185-LI — 18 V · referencia BO06119240E0; confirmar kit
- Einhell TE-CD 18/40 Li BL — Solo / sin batería; confirmar accesorios
- Einhell TP-CD 18/80 Li-i BL — Solo / sin batería; confirmar accesorios

### amoladoras (5)

- Bosch GWS 700 — 220V · ficha individual
- Bosch GWS 18V-8 — Solo / sin batería; confirmar accesorios
- Einhell TE-AG 125/1010 CE — 220V · ficha individual
- Einhell TE-AG 18/115 Q Li — Solo / sin batería; confirmar accesorios
- Einhell TE-AG 180 DP — 220V · ficha individual

### sierras (6)

- Einhell TC-SM 254 — 220V - 240V · ficha individual
- Einhell TC-MS 216 — 220V · ficha individual
- Einhell TE-SM 10 L Dual — 220V · ficha individual
- Bosch GTS 254 — 220V · ficha individual
- Hamilton HCA003 — 220V · ficha individual
- Lüsqtoff SCL710-8 — Ficha individual del comercio

## SEO y autoridad (5 de octubre de 2026)

La versión que posiciona es **www.tallerlab.com.ar**. GitHub Pages queda como copia técnica: sus páginas llevan `noindex, follow` y su canonical apunta a www, sin sitemap. Así los enlaces y la autoridad quedan en el dominio principal.

- **53 páginas**: hub, 7 categorías, metodología y **una página por modelo** (`/datos/precios/<categoría>/<marca-modelo>/`) con último precio, veredicto «¿Es buen precio hoy?» (desde 14 capturas, contra la mediana de las últimas 90), mínimo/mediana/máximo, gráfico SVG sin JavaScript, todas las capturas, guías relacionadas y otros modelos de la categoría.
- Títulos y descripciones únicos por página, H1 con la búsqueda real, Open Graph, `BreadcrumbList` y `Dataset` completo (licencia, cobertura temporal y geográfica, fecha de modificación).
- Bloque «Los precios que más se movieron» (30 días; aparece solo cuando hay variaciones) y bloque «Citá estos datos» con licencia **CC BY 4.0**. Si preferís otra licencia, cambiar `DATA_LICENSE` en `observatorio/estatico.py`.
- Metodología: nuevas secciones de independencia (reparto de fichas por comercio y política de enlaces sin afiliado) y de licencia/cita.
- Enlazado interno: «Precios» en el menú principal, sección en la portada, bloque en cada hub de categoría y bloque «¿Cuánto cuestan hoy?» en las guías que mencionan un modelo seguido (`observatorio/guias_por_modelo.json`; regenerar con `python -m observatorio.mapear_guias` cuando cambien las guías o el manifiesto).

### Paso extra al activar (recomendado, gratis)

Para que el HTML de www tenga los precios del día (lo que ve Google), crear en Vercel un **Deploy Hook** (Project → Settings → Git → Deploy Hooks, rama `main`) y guardarlo en GitHub como secreto `VERCEL_DEPLOY_HOOK_URL` (Settings → Secrets and variables → Actions). El workflow lo llama después de cada captura y el build de www (`preparar_assets_publicos.py`) descarga el historial de la rama `observatorio-datos`. Sin el secreto todo funciona igual, pero el HTML de www queda con la captura del último deploy y los precios se actualizan solo en el navegador.

Después del primer deploy: enviar `https://www.tallerlab.com.ar/sitemap.xml` en Search Console y pedir indexación del hub y de 3–5 páginas de modelo.

### Revisión de puesta en marcha (5 de octubre de 2026)

- Workflows actualizados a acciones con Node 24 (`checkout@v7`, `setup-python@v7`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`, `upload-artifact@v7`): GitHub retiró Node 20 de los runners el 23/09/2026.
- El build de páginas ya no necesita `requests`/`bs4`; si el observatorio falla, el deploy de www sigue y el log muestra `ERROR OBSERVATORIO`.
- El sitemap de www incluye las 53 rutas aunque la función de Vercel no vea `public/`.
- `.gitignore` ahora excluye `node_modules/` (había ~530 archivos de `compresor-reel/node_modules` sin ignorar).
- Los deploy hooks de Vercel requieren el repositorio de GitHub conectado al proyecto (Settings → Git). Si solo desplegás con `vercel --prod`, conectalo o desplegá a mano.
