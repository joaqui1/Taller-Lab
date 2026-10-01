# Cierre de publicación SEO de TallerLab

Fecha de revisión: 30/09/2026, horario de Argentina. Dominio: https://www.tallerlab.com.ar.

## Veredicto

**El sitio cumple los controles técnicos de publicación ejecutados y está desplegado.** Se aprobaron 179 guías y 190 rutas indexables. Esto permite publicar y rastrear la colección; no equivale a certificar indexación, posiciones, conversiones ni exactitud exhaustiva de todas las afirmaciones técnicas.

La auditoría inicial `auditoria-seo-consultor-2026-09-30.md` conserva el diagnóstico anterior a las correcciones. Este documento describe el cierre y prevalece para conocer el estado final.

## Qué se corrigió

- Se incorporaron las guías de amoladoras al conjunto publicado después de explicitar evidencia documental, análisis y limitaciones. Se conservaron las fechas de consulta originales y la declaración de que no hubo pruebas físicas.
- Se agregaron metadatos Open Graph/Twitter, imagen en Article y BreadcrumbList. Se conservaron títulos y descripciones únicos, canonicals y enlaces de autor.
- Se corrigieron anclas y jerarquías puntuales de encabezados. Se agregaron acceso directo al contenido principal, contacto y una descripción de privacidad acorde al código.
- Se retiraron enlaces comerciales que conducían a variantes incompatibles de Hamilton, Total y alambre ESAB, y un enlace de kit de estaño que devolvía 404. Las alternativas y pendientes quedaron explícitos; no se inventaron destinos.
- Se verificaron destinos de compresores y se distinguió la identificación del título de la comprobación de código, kit, stock y especificaciones.
- Se recuperaron enlaces documentales, se conservaron citas históricas de documentos retirados y se retiró un enlace cuyo certificado había vencido. Una cita histórica no se presenta como revalidación técnica actual.
- Se corrigieron regeneradores comerciales para conservar contenido, tablas y repetibilidad. Los controles antiguos se ajustaron a la colección actual conservando las comprobaciones de variantes, atribución y precios históricos.
- Se sirvieron tipografías locales con sus licencias, se optimizaron logo y hero, y se prepararon assets públicos para Vercel con caché. Se corrigieron desbordamientos y contraste detectados.
- Se integró el remoto sin sobrescribirlo y se resolvió el rechazo de `git push` mediante un push normal a `main`.

## Controles realizados

| Revisión | Resultado y alcance |
| --- | --- |
| Rutas locales | 190 HTTP 200; 179 guías. GET/HEAD, canonical, metadatos únicos, H1, JSON-LD y enlaces de autor aprobados. |
| Producción | Comparación de las 190 rutas con la versión aprobada y de los recursos publicados. Evidencia en `despliegue-verificado-2026-09-30.json`. |
| Sitemap y robots | Sitemap con las 190 URL canónicas previstas; robots permite rastreo. Buscador auxiliar noindex y ruta inexistente con 404 real. |
| Enlaces internos y anclas | Control de la colección completa aprobado; sin destinos internos rotos detectados. |
| Afiliación | CTA registrados, atributos sponsored/noopener y eventos inválidos rechazados. Las verificaciones comerciales por categoría pasaron. |
| Móvil | 190 rutas a 320 y 390 px, sin desbordamientos ni imágenes rotas observadas. Es una inspección de layout y carga, no una certificación completa WCAG. |
| Interacción | Búsqueda con resultados y sin coincidencias; calculadora de agua 6 L/min × 20 min = 120 L y rechazo de valor negativo. Pruebas de cálculos y límites aprobadas. |
| Rendimiento | Lighthouse móvil en portada, guía y hub. Los resultados son de laboratorio, no datos de visitantes reales. |
| Fuentes y destinos externos | Rastreo de más de 1.200 destinos. Los 264 enlaces cortos comerciales respondieron 200. Sin 404 activos detectados tras las reparaciones. |

Resultados completos de los controles reproducibles: `checks-produccion-2026-09-30.json`, `produccion-rutas-verificadas-2026-09-30.json` y `qa-movil-2026-09-30.json`.

## Rendimiento medido en producción

| Plantilla | Rendimiento | Accesibilidad | Buenas prácticas | SEO | LCP | CLS |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Portada | 98 | 100 | 100 | 100 | 1,8 s | 0 |
| Guía: compresor de 50 litros | 93 | 100 | 100 | 100 | 2,2 s | 0 |
| Hub: compresores | 100 | 100 | 100 | 100 | 1,4 s | 0 |

Archivos originales: `lighthouse-produccion-home-2026-09-30.json`, `lighthouse-produccion-guia-2026-09-30.json` y `lighthouse-produccion-hub-2026-09-30.json`. La portada se midió antes del último ajuste de colores; la guía se volvió a medir después de corregir el contraste. Las puntuaciones pueden variar entre ejecuciones.

La configuración de assets sigue el directorio `public/**` documentado para [Flask en Vercel](https://vercel.com/docs/frameworks/backend/flask). Se observaron respuestas `X-Vercel-Cache: HIT` y caché de un año para las fuentes versionadas. La preparación se ejecuta durante el build, desde los assets fuente del repositorio.

## Límites y seguimiento después de publicar

1. **Search Console no fue accesible.** Queda verificar envío/lectura del sitemap, páginas indexadas, canonical elegida por Google, acciones manuales y problemas de seguridad. Una búsqueda pública sin resultados no demuestra que el sitio esté desindexado.
2. **Core Web Vitals reales no están certificados.** Se necesita muestra de CrUX/Search Console para LCP, INP y CLS de usuarios. La API de PageSpeed rechazó la consulta por cuota; se usó Lighthouse como medición de laboratorio.
3. **Los bloqueos externos se documentan, no se ocultan.** Hay 403, desafíos antiautomatización y fallos de TLS locales en algunas fuentes. HTTP 200 tampoco prueba vigencia, stock, contenido íntegro ni equivalencia exacta de la variante. No se evitó validación TLS ni se resolvieron desafíos.
4. **Las afirmaciones y derechos de imágenes no tienen certificación exhaustiva.** Las guías distinguen investigación documental de ensayos físicos; faltan acceso a documentación no disponible y una revisión de derechos para acreditar permisos que no constan en el repositorio.
5. **Canibalización, demanda y autoridad necesitan datos.** No se dispone de consultas por URL, backlinks, conversiones ni métricas actuales de competidores. Los mapas históricos de Semrush son insumos de priorización, no diagnósticos actuales ni errores del sitio.
6. **Contacto y medición:** el canal publicado es GitHub, con reportes públicos y cuenta requerida. Puede configurarse un correo público mediante `CONTACT_EMAIL`. Los clics quedan en logs del alojamiento; todavía no hay una base persistente de analítica de conversiones.

Estas limitaciones impiden afirmar «SEO 100% certificado». No constituyen un fallo de despliegue ni un bloqueo técnico de las páginas aprobadas. El estado comprobado es **publicación técnica lista y verificable**, con seguimiento de indexación y rendimiento real pendiente.
