# Auditoría SEO y plan de autoridad de TallerLab

Fecha: 06/10/2026. Dominio: https://www.tallerlab.com.ar. Alcance: las 190 URLs del sitemap (179 guías, 8 hubs de categoría, portada y 4 páginas institucionales), código de generación del sitio, datos históricos de Semrush del repositorio y presencia externa en buscadores.

> **Cómo se hizo y qué límite tiene.** La red de esta sesión bloquea `tallerlab.com.ar`, así que el rastreo se hizo sobre el **mismo código que sirve producción** (`servidor_local.py` + `app.py`) con `SITE_URL=https://www.tallerlab.com.ar`, y se cruzó con la verificación de producción del 01/10 (`despliegue-verificado-2026-10-01.json`: 190 rutas idénticas a la versión aprobada). La presencia externa se midió con búsquedas web. No hay acceso a Search Console, Analytics ni a una herramienta de backlinks, así que las cifras de autoridad son observacionales y la indexación real queda por confirmar. Tabla completa por URL al final y en `auditoria-autoridad-seo-2026-10-06-urls.csv`.

---

## 1. Veredicto en una página

**La base técnica está muy bien. La autoridad está en cero. El cuello de botella ya no es el código: es la marca, los enlaces externos, las señales de experiencia real y la arquitectura de enlazado interno.**

| Dimensión | Estado | Nota |
|---|---|---|
| Técnico (rastreo, canonicals, sitemap, robots, 404, redirecciones, schema básico) | ✅ Sólido | 190/190 en 200, canonical autorreferente en todas, 0 títulos y 0 descripciones duplicadas, 0 huérfanas, 1 sola imagen sin alt (decorativa). Lighthouse móvil 93–100. |
| Contenido | ✅ Profundo, ⚠️ homogéneo | 179 guías, mediana 1.735 palabras, mínimo 747, todas con tablas y fuentes citadas. Pero todas comparten plantilla, 0 pruebas físicas y solo 4 con sección de preguntas frecuentes. |
| Arquitectura interna | ⚠️ Desbalanceada | El menú superior solo enlaza **Compresores**. Resultado: el hub de compresores recibe 237 enlaces internos y el de hidrolavadoras 25. 36 guías tienen 5 o menos enlaces entrantes. |
| Metadatos | ⚠️ Mejorables | 116 títulos superan 60 caracteres; 7 hubs tienen título genérico (“Compresores · TallerLab”) justo donde están las keywords de mayor volumen. |
| E-E-A-T | 🔴 Débil | Un autor sin foto, sin trayectoria verificable, sin perfiles externos (`sameAs` = 0). Contacto solo por GitHub Issues. Metodología 100 % documental declarada en cada página. |
| Autoridad externa | 🔴 Inexistente | No se detecta ninguna mención ni enlace externo. La búsqueda de marca “tallerlab” no devuelve el sitio. Solo 1 URL del sitio apareció en resultados de búsqueda. |
| Medición | 🔴 Ausente | Sin Search Console confirmado, sin analítica, clics de afiliado solo en logs de Vercel. |

El sitio tiene **una semana de vida pública** (primer commit 27/09, despliegue 30/09) y publicó 179 páginas en ese lapso. Para Google eso es un dominio nuevo, sin historial, con un volumen de contenido grande y uniforme. Ese perfil **necesita señales externas para que el rastreo y la indexación aceleren**; sin ellas, lo normal es que la indexación sea lenta y parcial durante meses, por bueno que sea el contenido.

---

## 2. Autoridad: diagnóstico

### 2.1 Qué se observa

- **Backlinks y menciones:** búsquedas por `"tallerlab.com.ar"`, `tallerlab` y combinaciones con “herramientas Argentina” no devuelven ningún sitio de terceros que mencione o enlace a TallerLab. El único resultado propio fue `/hidrolavadoras/200-bar/`.
- **SERP de marca:** “tallerlab” muestra laboratorios universitarios y repositorios de GitHub de otros proyectos con el mismo nombre. No existe entidad “TallerLab” para Google todavía. El nombre es genérico y compite con homónimos, así que la construcción de marca tiene que ser deliberada.
- **Entidad autor:** `Joaquín Vallasciani` aparece como `Person` en el schema, pero sin `sameAs`, sin foto, sin bio con trayectoria, sin presencia pública enlazada. Para las directrices de calidad de Google el autor hoy es un nombre, no una persona verificable.
- **Entidad organización:** `Organization` sin `sameAs`, sin dirección, sin correo, sin perfiles. El contacto público es “abrir un issue en GitHub”, lo cual es poco creíble para un lector no técnico y un mal indicador de confianza.
- **Experiencia (la primera E):** las 179 guías declaran `physical_test: no` y 177 `buyer_opinions: no`. La transparencia es correcta y defendible, pero significa que el sitio hoy no puede exhibir experiencia de primera mano, que es exactamente lo que Google pondera en reseñas de productos.

### 2.2 Quién está ocupando el espacio

| Competidor | Qué hace bien | Dónde es débil |
|---|---|---|
| **mejorescompras.com.ar** | Rankea para “mejor hidrolavadora Argentina 2026”, “mejores taladros percutores Argentina 2026”. Precios en vivo de Mercado Libre, ranking con ganador, página por producto (MLA…), año en el título. | Sin profundidad técnica, sin fuentes, contenido claramente automatizado. |
| **Blog de Mercado Libre** (sobre todo .cl) | Autoridad de dominio enorme; cubre “elección compresor 50 litros” y similares. | Genérico, no argentino, sin modelos concretos. |
| **Medios generalistas** (minutouno, El Economista) | Capturan “cuánto cuesta un grupo electrógeno” cada ola de cortes de luz. | Notas coyunturales, sin comparativa real. |
| **servidos.ar** | Tiene una calculadora de generador indexable con URL propia. | Sitio de clasificados, poco contenido. |
| **Fabricantes** (Lüsqtoff, Gamma, Bosch, Einhell, ESAB) | Fichas oficiales, rankean por modelo. | No comparan entre marcas. Son fuente, no competencia directa: hoy TallerLab les da 300+ enlaces salientes sin recibir ninguno. |

La diferenciación real de TallerLab es **rigor documental + calculadoras + separación explícita entre dato y opinión**. Nadie más en el nicho argentino hace eso. Pero ese valor hoy no está empaquetado como activo enlazable ni como marca.

---

## 3. Plan de autoridad (qué hacer, en orden)

### Nivel 0 · Fundamentos (esta semana)

1. **Search Console y Bing Webmaster Tools.** Verificar `www.tallerlab.com.ar` (propiedad de dominio), enviar el sitemap, revisar cobertura y “Páginas descubiertas pero no indexadas”. Sin esto no hay forma de saber qué está pasando con la indexación. Activar IndexNow para Bing (gratis, un endpoint).
2. **Analítica.** La página de privacidad dice “no instala Google Analytics”. Opciones coherentes con esa postura: Vercel Web Analytics o Umami/Plausible. Actualizar la página de privacidad al instalarlo. Sin datos de consultas y clics no se puede priorizar nada de lo que sigue.
3. **Contacto creíble.** Configurar `CONTACT_EMAIL` (el código ya lo soporta) y publicar un correo real. GitHub Issues puede quedar como canal secundario.
4. **Perfiles de entidad.** Crear y enlazar desde el sitio: LinkedIn del autor, perfil X/Instagram/YouTube de TallerLab (aunque arranquen vacíos), y agregar `sameAs` en `Organization` y en `Person`. Agregar foto del autor y una bio con trayectoria concreta (formación, años de taller, oficio, lo que sea real).

### Nivel 1 · Activos enlazables (semanas 2–4)

5. **Dar URL propia a cada calculadora.** Hoy las seis calculadoras (potencia para la casa, caudal de compresor, costo final, consumo de agua, espesor de corte, disco por tarea) viven embebidas en la portada, sin URL indexable. Son el **activo enlazable más fuerte del sitio** y están invisibles. Crear `/calculadoras/`, `/calculadoras/potencia-grupo-electrogeno/`, `/calculadoras/caudal-compresor/`, etc., con texto explicativo, ejemplo resuelto, fórmulas y supuestos. Es el tipo de página que medios, foros y docentes enlazan.
6. **Índice de precios TallerLab.** El repo ya acumula relevamientos de precios con fecha (`*-ofertas.json`). Publicar un “Relevamiento mensual de precios de herramientas en Argentina” (grupos electrógenos, hidrolavadoras, compresores) con tabla, variación mensual y metodología. Es dato original, es argentino y es periodístico: cada ola de calor o de cortes de luz los medios buscan exactamente eso.
7. **Páginas “mejores marcas de…”.** Semrush muestra demanda (`mejores marcas de hidrolavadoras` 140, `mejores marcas de taladros` 140, `mejores marcas de generadores`) y no hay página que la cubra. Son páginas de autoridad temática y atraen enlaces de foros.

### Nivel 2 · Conseguir enlaces (desde la semana 3, continuo)

8. **Digital PR estacional.** Noviembre–febrero es temporada de cortes de luz: preparar con anticipación el relevamiento de precios de grupos electrógenos y la calculadora de potencia, y ofrecerlos a periodistas de economía/consumo (los que ya escriben “cuánto cuesta un grupo electrógeno”). Mismo esquema con hidrolavadoras antes del verano y con compresores/soldadoras para Día del Padre y Hot Sale.
9. **Fabricantes y distribuidores.** TallerLab enlaza 100+ veces a Lüsqtoff, 42 a Bosch, 30 a Gamma, 18 a ESAB. Pedirles reciprocidad concreta: que sus blogs o secciones de “guías” enlacen la comparativa, o que compartan la guía en sus redes. Argumento: TallerLab cita sus manuales y corrige errores de fichas (las guías documentan discrepancias). Ferreterías con blog o newsletter son un segundo anillo.
10. **Comunidades.** Reddit (r/argentina, r/BuenosAires y subs de bricolaje en español), grupos de Facebook de herramientas y oficios, Taringa, foros de soldadura y carpintería. No para dejar enlaces: para responder preguntas con la calculadora o la tabla y enlazar cuando aporte. Medir qué URLs reciben tráfico desde ahí.
11. **YouTube.** El nicho de herramientas en Argentina está dominado por reseñadores de YouTube. Dos caminos: (a) producir videos cortos propios con la metodología de las guías y enlazar desde la descripción; (b) ofrecer a reseñadores existentes datos de las comparativas a cambio de mención. Un canal también crea la SERP de marca que hoy no existe.
12. **Colaboraciones editoriales.** Notas invitadas en medios de arquitectura/construcción y revistas del sector ferretero, y aportes a cámaras sectoriales. Una nota al mes con enlace a una guía o calculadora es realista.
13. **Wikipedia y referencias.** No como enlace directo (será nofollow) sino como validación de entidad: si TallerLab publica datos originales (índice de precios), puede ser citado en artículos de Wikipedia en español sobre grupos electrógenos o hidrolavadoras.

### Nivel 3 · Experiencia de primera mano (desde el mes 2)

14. **Programa “Probado por TallerLab”.** No hace falta probar los 179 productos. Alcanza con empezar por las 10 guías de mayor volumen y agregar una medición propia y barata: consumo real con un medidor de enchufe, nivel de ruido con decibelímetro de celular, peso en balanza, tiempo de carga, fotos propias con fecha. Cambiar `physical_test` a “parcial” solo donde sea cierto y mostrarlo en la página. Esto habilita schema `Review` con `positiveNotes`/`negativeNotes` y desbloquea la primera E de E-E-A-T.
15. **Opiniones de lectores.** Un formulario simple por guía (“¿Tenés este modelo? Contanos”), con moderación. Genera contenido nuevo, señales de uso y fechas de actualización legítimas.
16. **Historial de correcciones visible.** Solo 1 de 179 guías lo tiene. Cada corrección documentada es una señal de confianza y una actualización legítima de `dateModified`.

---

## 4. Arquitectura y enlazado interno

### 4.1 El problema del menú

El header enlaza: Inicio · Compresores · Cómo trabajamos · Autor. Nada más. Las otras siete categorías solo se alcanzan desde las tarjetas de la portada, breadcrumbs y enlaces contextuales. Consecuencia medida:

| Hub | Enlaces internos entrantes |
|---|---:|
| `/compresores/` | 237 |
| `/sierras/` | 61 |
| `/amoladoras/` | 55 |
| `/taladros/` | 47 |
| `/soldadoras/` | 39 |
| `/generadores/` | 38 |
| `/hidrolavadoras/` | 25 |
| `/soldadura-electronica/` | 7 |

Las keywords de mayor volumen del sitio son de nivel hub o cercanas (grupo electrógeno 6.600, hidrolavadora inalámbrica 5.400, generador eléctrico 5.400) y están en las categorías con menos enlaces.

**Acciones:**
- Menú con las 8 categorías (en móvil, desplegable). 
- Footer con las 8 categorías y las 3 guías principales de cada una (mega-footer de ~32 enlaces). Hoy el footer no enlaza ninguna categoría.
- En cada guía, el bloque “Guías relacionadas” ya existe (3 enlaces). Agregar un segundo bloque “Empezá por acá” con la comparativa general y el hub de la categoría.

### 4.2 Guías con pocos enlaces entrantes

36 guías tienen 5 o menos enlaces entrantes (lista completa en la tabla final, señal `pocos enlaces entrantes`). Casos que duelen porque tienen demanda:

| URL | Entrantes | Keyword (vol.) |
|---|---:|---|
| `/amoladoras/de-banco/` | 5 | amoladora de banco (3.600) |
| `/amoladoras/recta/` | 5 | amoladora recta (1.000) |
| `/hidrolavadoras/hidrolavadora-para-aire-acondicionado/` | 3 | 260 |
| `/sierras/sierra-sable-inalambrica/` | 4 | — |
| `/soldadoras/mascaras-fotosensibles/` | 5 | máscara de soldar fotosensible (880) |
| `/hidrolavadoras/inalambricas/` | 10 | hidrolavadora inalámbrica (5.400) |
| `/amoladoras/disco-flap/` | 13 | disco flap (2.900) |

Regla práctica: toda guía con volumen Semrush ≥ 500 debería tener ≥ 15 enlaces internos entrantes, incluyendo uno desde la portada o el footer.

### 4.3 Anchor text

Los anchors contextuales son buenos y variados (“comparativa general de generadores”, “cómo dimensionar un grupo electrógeno”). Los anchors de tarjetas arrastran ruido (“RELACIONADO 7 min Foto del producto Grupos electrógenos…”) porque la tarjeta entera es el enlace. Mover el `<a>` al título de la tarjeta, o usar `aria-label`, limpia la señal.

---

## 5. Metadatos y marcado

### 5.1 Títulos

- 116 de 190 títulos superan 60 caracteres (mediana 62, máximo 86). No es un error, pero Google recorta y a veces reescribe. Priorizar las 25 más largas (lista en el crawl) y las de mayor volumen.
- **7 hubs con título genérico:** “Compresores · TallerLab”, “Generadores · TallerLab”, “Taladros y atornilladores · TallerLab”, “Soldadura electrónica · TallerLab”, etc. Son las páginas que deberían capturar el término de cabecera. Propuesta:
  - `/generadores/` → “Grupos electrógenos y generadores: cuál elegir en Argentina (guía 2026)”
  - `/hidrolavadoras/` → “Hidrolavadoras: cómo elegir presión, caudal y marca en Argentina”
  - `/compresores/` → “Compresores de aire: guía para elegir por litros, caudal y uso”
  - `/taladros/` → “Taladros, rotomartillos y atornilladores: cuál elegir según el trabajo”
- `/soldadoras/` tiene doble marca: “… | Taller Lab · TallerLab”. Corregir.
- `/hidrolavadoras/` es el único hub sin sufijo de marca (inconsistencia del `replace` en `render_category_page`).
- Solo 2 títulos empiezan con “Cómo elegir”: bien, no hay patrón repetitivo. Mantener.

### 5.2 Descripciones

37 superan 160 caracteres (máximo 221). Las de soldadoras son las más largas y las más técnicas; recortar a una promesa clara + un dato diferencial.

### 5.3 Datos estructurados

Lo que hay está bien implementado: `Organization`, `WebSite`, `BreadcrumbList`, `Article` con `dateModified`, `author` y `image`, `ProfilePage` en autor. Faltan:

| Falta | Dónde | Para qué |
|---|---|---|
| `datePublished` en `Article` | 179 guías | Google lo usa para mostrar fecha; hoy solo hay `dateModified`. El frontmatter no guarda fecha de publicación: agregarla. |
| `sameAs` en `Organization` y `Person` | todas | Consolidación de entidad (punto 4 del plan). |
| `CollectionPage` + `ItemList` | 8 hubs | Describe el hub como listado curado; ayuda a entender la jerarquía. |
| `FAQPage` | guías con FAQ | Ya no da rich result general, pero el contenido FAQ alimenta “Otras preguntas” y respuestas de IA. Primero hay que escribir las FAQ: solo 4 páginas las tienen. |
| `SearchAction` en `WebSite` | portada | El buscador interno existe; declararlo. |
| `lastmod` en sitemap | sitemap | El dato existe (`reviewed`), solo no se emite. Ayuda a priorizar recrawl. |
| Favicon PNG/ICO 48×48 + `apple-touch-icon` + `theme-color` | shell | El favicon actual es un emoji en SVG. Google muestra favicon en móvil; un emoji renderiza distinto según plataforma. |

### 5.4 Canibalización

Keywords declaradas en más de una página:

| Keyword | Páginas |
|---|---|
| soldadora tig ac dc | `/soldadoras/soldadora-tig-ac-dc/`, `/soldadoras/tig/`, `/soldadoras/` |
| soldadora mig sin gas | `/soldadoras/mig-sin-gas/`, `/soldadoras/` |
| soldadora de punto | `/soldadoras/soldadora-de-punto/`, `/soldadoras/` |
| soldadora mig lusqtoff | `/soldadoras/mig-lusqtoff/`, `/soldadoras/lusqtoff/` |
| soldadora inverter lusqtoff | `/soldadoras/lusqtoff-iron-250/`, `/soldadoras/lusqtoff/` |
| hidrolavadora lusqtoff hl 120 | `/hidrolavadoras/lusqtoff/`, `/hidrolavadoras/lusqtoff-hl-120/` |
| amoladora grande | `/amoladoras/9-pulgadas/`, `/amoladoras/7-pulgadas/` |

Además, `/generadores/comparativa-general/` lleva las tres keywords más grandes del sitio (grupo electrógeno, generador eléctrico, grupo electrógeno precio) mientras el hub `/generadores/` tiene título genérico. Decidir: o el hub captura el término de cabecera y la comparativa va a “cómo elegir la potencia”, o se fusionan. Hoy compiten entre sí sin que ninguna gane.

Regla: una keyword principal por URL; el hub se queda con el término de categoría y las guías con las variantes.

---

## 6. Contenido: fortalezas y riesgos

**Fortalezas verificadas:** profundidad (ninguna guía bajo 700 palabras, 0 páginas delgadas), tablas en el 100 % de las guías (mediana 3), fuentes citadas con enlace (2.462 enlaces externos, 531 nofollow en comerciales, 534 sponsored), fecha de revisión visible con nombre de autor en cada guía, enlaces de afiliado correctamente marcados `sponsored nofollow noopener`.

**Riesgos:**

1. **Homogeneidad de plantilla.** 179 guías con “Fuentes consultadas” (179), “Cómo investigamos esta guía” (48), “Lectura de la evidencia de esta comparación” (20), mismos párrafos de descargo. Publicadas todas en 3 semanas. Para un evaluador de calidad eso se parece a contenido escalado. Mitigación: variar la estructura según intención (modelo vs. categoría vs. accesorio), agregar elementos únicos por página (foto propia, medición, FAQ específica, caso de uso real).
2. **Sin FAQ.** 175 guías sin sección de preguntas. Las “Otras preguntas de los usuarios” de Google y las respuestas de IA se alimentan de eso. Tres o cuatro preguntas reales por guía, respondidas en 40–60 palabras.
3. **Sin “año” ni frescura en títulos.** Los competidores usan “2026”. No hace falta en todas, pero las comparativas generales y las de precios lo justifican, y hay que mantenerlo.
4. **15 guías sin ningún enlace de afiliado** (aceite, acoples, filtros, manguera, kits aerógrafo, 200 bar, hyundai, sable, carro MIG, soldadora de punto, estación de soldadura, atornilladores de impacto, mecha forstner, gamma 50 litros, para aerógrafo). Son páginas que no monetizan.
5. **Las 7 guías más cortas** (soporte con lupa, kit estaño, Bosch GKS 150, Gadnic 878D, estación de soldadura, sensitivas Lusqtoff, sierra sable) están entre 747 y 982 palabras. No es delgado, pero son candidatas a ampliar o consolidar.

---

## 7. Oportunidades de keywords (de los datos Semrush del repo)

### 7.1 Páginas existentes para empujar primero (volumen alto, ya publicadas)

| URL | Keyword | Vol. | KD | Acción |
|---|---|---:|---:|---|
| `/generadores/comparativa-general/` | grupo electrógeno / generador eléctrico | 6.600 / 5.400 | 20–25 | Resolver canibalización con el hub, +enlaces, FAQ, índice de precios enlazado |
| `/hidrolavadoras/inalambricas/` | hidrolavadora inalámbrica | 5.400 | 27 | Solo 10 enlaces entrantes. Footer + portada + FAQ |
| `/amoladoras/disco-flap/` | disco flap | 2.900 | 9 | KD bajo. Agregar tabla de granos y video corto |
| `/soldadoras/mig-sin-gas/` | soldadora mig sin gas | 1.600 | 25 | Sacar la keyword del hub |
| `/amoladoras/disco-de-desbaste/` | disco de desbaste | 1.600 | 12 | Enlaces + FAQ |
| `/taladros/taladro-percutor-inalambrico/` | taladro percutor inalámbrico | 1.000 | 15 | Competidor directo: mejorescompras. Agregar precios relevados con fecha |
| `/compresores/50-litros/` | compresor 50 litros | 1.000 | 15 | Ya es la mejor guía del sitio; convertirla en caso de PR |
| `/soldadoras/soldadora-mig-con-gas/` | soldadora mig con gas | 1.000 | 11 | Recortar descripción, FAQ |
| `/soldadoras/mascaras-fotosensibles/` | máscara de soldar fotosensible | 880 | 14 | 5 enlaces entrantes: subir a 15 |
| `/amoladoras/de-banco/` | amoladora de banco | 3.600 | 13 | 5 enlaces entrantes. Es la segunda keyword del sitio y está escondida |
| `/amoladoras/recta/` | amoladora recta | 1.000 | 12 | Ídem |
| `/sierras/sierra-sin-fin-para-madera/` | sierra sin fin para madera | 720 | 8 | KD muy bajo |
| `/soldadoras/soldadora-inverter-200-amp/` | soldadora inverter 200 amp | 720 | 12 | — |

### 7.2 Páginas nuevas con demanda medida y sin cobertura

Cruce de las 319 consultas Semrush contra slugs, títulos y keywords de las 179 guías. Estas no tienen página que las cubra completa:

| Keyword | Vol. | KD | Página propuesta |
|---|---:|---:|---|
| hidrolavadora inalámbrica einhell | 170 | 13 | `/hidrolavadoras/inalambrica-einhell/` |
| hidrolavadora karcher k1 | 140 | 23 | ampliar `/hidrolavadoras/karcher-k2/` a K1/K2 o página propia |
| mejores marcas de hidrolavadoras | 140 | 18 | `/hidrolavadoras/mejores-marcas/` |
| mejores marcas de taladros | 140 | 12 | `/taladros/mejores-marcas/` |
| compresor lusqtoff 25 litros | 140 | 13 | `/compresores/lusqtoff-25-litros/` |
| compresor daewoo 50 litros | 140 | 12 | `/compresores/daewoo-50-litros/` |
| soldadora lusqtoff iron 180 | 110 | 9 | `/soldadoras/lusqtoff-iron-180/` |
| compresor gamma 25 litros | 110 | 9 | `/compresores/gamma-25-litros/` |
| compresor niwa 50 litros | 110 | 8 | `/compresores/niwa-50-litros/` |
| taladro para madera | 110 | 30 | `/taladros/para-madera/` |
| ingletadora para aluminio | 110 | 30 | `/sierras/ingletadora-para-aluminio/` |
| disco para cortar melamina | 110 | 29 | `/sierras/disco-para-melamina/` |
| hidrolavadora gamma 170 | 110 | 12 | `/hidrolavadoras/gamma-170/` |
| disco para cortar chapa | 90 | 9 | `/amoladoras/disco-para-chapa/` |
| accesorios para hidrolavadora | 90 | 8 | `/hidrolavadoras/accesorios/` |
| taladro bosch gsb 13 re | 70 | 18 | `/taladros/bosch-gsb-13-re/` |
| electrodo 6013 vs 7018 | 30 | 5 | ampliar `/soldadoras/electrodo-6013/` |
| taladro para hormigón | 30 | 21 | `/taladros/para-hormigon/` |
| sierra circular de inmersión | 30 | 17 | `/sierras/de-inmersion/` |
| generador para soldar / 3000 W / para negocio | 20 c/u | 5–8 | una guía “qué generador según el uso” que las agrupe |

El archivo `analisis-semrush-prioridades.md` ya tiene 100 consultas más por medir. Con Search Console funcionando, la prioridad pasa a ser: qué consultas ya traen impresiones en posición 8–20 (ahí la ganancia es más rápida que crear páginas nuevas).

---

## 8. Técnico: lo que queda (todo menor)

| Ítem | Estado | Acción |
|---|---|---|
| Redirecciones http→https, no-www→www, barra final | ✅ 308/301 correctos | — |
| Compresión | Local sin gzip; Vercel aplica brotli | Confirmar en producción con `content-encoding` |
| Peso HTML | Portada 30 KB, mediana 43 KB, máximo 69 KB | Bien |
| CSS inline 16 KB, 1 JS diferido | Bien | — |
| Imágenes | 1.587, 0 sin dimensiones, 1.206 lazy, 1 sin alt (hero decorativo, `alt=""` es válido) | Imágenes editoriales de 160–210 KB: bajar a <100 KB |
| `lang="es"` | Bien | Opcional `es-AR` (el `WebSite` ya declara `inLanguage: es-AR`) |
| 404 real, `search-cards.html` con `X-Robots-Tag: noindex` | Bien | — |
| Sitemap sin `lastmod` | ⚠️ | Emitir `reviewed` como `lastmod` |
| Sin feed RSS | ⚠️ | `/feed.xml` con las últimas revisiones: ayuda a descubrimiento y a agregadores |
| Sin `llms.txt` | Opcional | Lista curada de hubs y calculadoras para rastreadores de IA |
| `/equipo-editorial` responde 200 en local | ⚠️ | En producción (`app.py`) redirige 301 al autor; el servidor local no. Sin impacto público, pero unificar |

---

## 9. Plan de 90 días

| Semana | Entregable | Métrica |
|---|---|---|
| 1 | Search Console + Bing + IndexNow + analítica + correo de contacto + perfiles sociales + `sameAs` + foto y bio del autor | Páginas indexadas (línea base) |
| 2 | Menú con 8 categorías, mega-footer, títulos de los 8 hubs, doble marca en soldadoras, `lastmod`, `datePublished`, favicon PNG | Enlaces entrantes mínimos: hubs ≥ 60, guías con vol ≥ 500 ≥ 15 |
| 3–4 | Calculadoras con URL propia (6 páginas) + página índice. FAQ en las 20 guías de mayor volumen. Resolver 7 canibalizaciones | Indexación de calculadoras; impresiones en consultas de hub |
| 5–6 | Primer “Relevamiento de precios TallerLab” (generadores) + pitch a 10 periodistas. Primeras 5 páginas nuevas de la tabla 7.2 | 1–3 menciones/enlaces editoriales |
| 7–8 | Programa “Probado por TallerLab” en 5 guías (mediciones propias + fotos). Contacto con 5 fabricantes para reciprocidad | `physical_test: parcial` en 5 guías; 1–2 enlaces de fabricantes |
| 9–10 | Canal YouTube: 4 videos cortos basados en las guías top. Participación en 3 comunidades | Búsquedas de marca > 0 en Search Console |
| 11–12 | Segundo relevamiento de precios (hidrolavadoras, pre-verano). Revisión de consultas en posición 8–20 y refuerzo | Dominios de referencia ≥ 10; clics orgánicos semanales con tendencia |

**Qué no hacer:** comprar enlaces, directorios masivos, intercambios recíprocos a escala, PBN. Con un dominio de una semana y 179 páginas, un patrón de enlaces artificial es la forma más rápida de quedar marcado. La estrategia de arriba es más lenta pero construye algo que compite con mejorescompras.com.ar en un año y lo supera en dos.

---

## 10. Para volver a auditar en vivo

La política de red de este entorno bloqueó `tallerlab.com.ar` y `www.tallerlab.com.ar`. Para que una próxima sesión rastree producción directamente, agregar esos dos hosts en “Network access” del entorno (Custom → Allowed domains). Guía: https://code.claude.com/docs/en/cloud-environments#network-access.

---

## Anexo · Las 190 URLs

Columnas: longitud de título y descripción en caracteres; palabras del contenido principal; cantidad de H2 y tablas; enlaces internos entrantes; enlaces de afiliado; volumen Semrush de la keyword asociada cuando existe; señales a revisar (`title>60`, `desc>160`, `corto<1000`, `pocos enlaces entrantes` = ≤5, `sin afiliado`, `sin faq`, `title hub generico`).

| URL | Tipo | Título (chars) | Desc (chars) | Palabras | H2 | Tablas | Enlaces entrantes | Afiliados | Vol. Semrush (kw) | Señales a revisar |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `/` | home | 68 | 152 | 447 | 5 | 0 | 563 | 0 | — | title>60 |
| `/amoladoras/` | hub | 62 | 141 | 2780 | 14 | 2 | 55 | 3 | — | title>60 sin faq |
| `/compresores/` | hub | 23 | 174 | 1061 | 4 | 0 | 237 | 0 | — | desc>160 title hub generico |
| `/generadores/` | hub | 23 | 159 | 1008 | 6 | 0 | 38 | 0 | — | title hub generico |
| `/hidrolavadoras/` | hub | 44 | 162 | 1114 | 5 | 0 | 25 | 0 | — | desc>160 |
| `/sierras/` | hub | 57 | 151 | 1304 | 6 | 1 | 61 | 0 | — | ok |
| `/soldadoras/` | hub | 81 | 184 | 1973 | 13 | 1 | 39 | 5 | — | title>60 desc>160 sin faq |
| `/soldadura-electronica/` | hub | 33 | 173 | 365 | 5 | 0 | 7 | 0 | — | desc>160 title hub generico |
| `/taladros/` | hub | 37 | 151 | 1092 | 5 | 0 | 47 | 0 | — | title hub generico |
| `/amoladoras/115-o-125/` | guia | 61 | 134 | 1726 | 9 | 3 | 22 | 2 | — | title>60 sin faq |
| `/amoladoras/7-pulgadas/` | guia | 62 | 123 | 1810 | 10 | 4 | 18 | 2 | — | title>60 sin faq |
| `/amoladoras/9-pulgadas/` | guia | 66 | 115 | 1830 | 11 | 2 | 14 | 2 | — | title>60 sin faq |
| `/amoladoras/bosch/` | guia | 63 | 104 | 2072 | 13 | 3 | 16 | 2 | — | title>60 sin faq |
| `/amoladoras/de-banco/` | guia | 58 | 132 | 2500 | 14 | 4 | 5 | 2 | — | pocos enlaces entrantes sin faq |
| `/amoladoras/dewalt/` | guia | 52 | 134 | 2037 | 11 | 3 | 11 | 2 | — | sin faq |
| `/amoladoras/disco-de-corte/` | guia | 72 | 111 | 2301 | 16 | 3 | 14 | 1 | — | title>60 sin faq |
| `/amoladoras/disco-de-desbaste/` | guia | 55 | 113 | 1881 | 14 | 3 | 10 | 2 | 1600 (disco de desbaste) | sin faq |
| `/amoladoras/disco-diamantado-segmentado/` | guia | 59 | 134 | 1615 | 11 | 2 | 11 | 2 | — | sin faq |
| `/amoladoras/disco-flap/` | guia | 57 | 106 | 2341 | 12 | 5 | 13 | 2 | 2900 (disco flap) | sin faq |
| `/amoladoras/discos-ceramica/` | guia | 53 | 112 | 1780 | 12 | 2 | 11 | 2 | 0 (mejor disco para cortar ceramica) | sin faq |
| `/amoladoras/discos-vidrio/` | guia | 69 | 111 | 1570 | 10 | 1 | 8 | 3 | — | title>60 sin faq |
| `/amoladoras/discos/` | guia | 63 | 123 | 1844 | 9 | 3 | 17 | 3 | — | title>60 sin faq |
| `/amoladoras/dowen-pagio/` | guia | 68 | 115 | 1735 | 9 | 3 | 5 | 2 | — | title>60 pocos enlaces entrantes sin faq |
| `/amoladoras/gamma/` | guia | 68 | 123 | 1685 | 11 | 2 | 5 | 2 | — | title>60 pocos enlaces entrantes sin faq |
| `/amoladoras/inalambricas/` | guia | 65 | 110 | 2799 | 17 | 4 | 14 | 2 | 0 (mejor amoladora a bateria) | title>60 sin faq |
| `/amoladoras/ingco/` | guia | 59 | 113 | 1950 | 10 | 2 | 4 | 2 | — | pocos enlaces entrantes sin faq |
| `/amoladoras/lusqtoff/` | guia | 54 | 151 | 1717 | 12 | 4 | 6 | 2 | — | sin faq |
| `/amoladoras/makita/` | guia | 52 | 132 | 1998 | 12 | 3 | 8 | 2 | — | sin faq |
| `/amoladoras/recta/` | guia | 63 | 118 | 1821 | 13 | 4 | 5 | 1 | — | title>60 pocos enlaces entrantes sin faq |
| `/amoladoras/skil-830w/` | guia | 65 | 135 | 1325 | 9 | 2 | 5 | 1 | — | title>60 pocos enlaces entrantes sin faq |
| `/amoladoras/stanley/` | guia | 53 | 143 | 1672 | 11 | 2 | 6 | 2 | 0 (amoladora stanley opiniones) | sin faq |
| `/amoladoras/total/` | guia | 58 | 129 | 1548 | 10 | 1 | 11 | 1 | — | sin faq |
| `/amoladoras/velocidad-variable/` | guia | 60 | 136 | 1687 | 10 | 2 | 7 | 1 | — | sin faq |
| `/autor/joaquin-vallasciani/` | guia | 68 | 95 | 1533 | 3 | 0 | 743 | 0 | — | title>60 |
| `/como-trabajamos/` | institucional | 27 | 97 | 668 | 7 | 0 | 743 | 0 | — | title hub generico |
| `/compresores/100-litros/` | guia | 61 | 139 | 2797 | 10 | 3 | 11 | 9 | — | title>60 sin faq |
| `/compresores/12v-doble-piston/` | guia | 68 | 142 | 2301 | 11 | 2 | 8 | 6 | — | title>60 sin faq |
| `/compresores/200-litros/` | guia | 65 | 131 | 2561 | 11 | 3 | 7 | 2 | — | title>60 sin faq |
| `/compresores/24-litros/` | guia | 64 | 135 | 2976 | 12 | 3 | 11 | 8 | — | title>60 sin faq |
| `/compresores/50-litros/` | guia | 64 | 139 | 2814 | 13 | 4 | 22 | 2 | 1000 (compresor 50 litros) | title>60 sin faq |
| `/compresores/aceite/` | guia | 67 | 146 | 1676 | 10 | 1 | 20 | 0 | — | title>60 sin afiliado sin faq |
| `/compresores/acoples-rapidos/` | guia | 68 | 101 | 1599 | 8 | 3 | 11 | 0 | — | title>60 sin afiliado sin faq |
| `/compresores/bta-25-litros/` | guia | 59 | 131 | 2014 | 12 | 3 | 5 | 3 | — | pocos enlaces entrantes sin faq |
| `/compresores/filtros/` | guia | 66 | 143 | 1606 | 6 | 2 | 15 | 0 | — | title>60 sin afiliado sin faq |
| `/compresores/gamma-50-litros/` | guia | 56 | 137 | 1664 | 8 | 2 | 8 | 0 | — | sin afiliado sin faq |
| `/compresores/inalambricos/` | guia | 58 | 149 | 2379 | 11 | 2 | 8 | 6 | — | sin faq |
| `/compresores/inflador-neumaticos-portatil/` | guia | 86 | 127 | 3018 | 11 | 3 | 5 | 8 | — | title>60 pocos enlaces entrantes sin faq |
| `/compresores/kits-accesorios/` | guia | 59 | 113 | 2612 | 11 | 4 | 7 | 11 | — | sin faq |
| `/compresores/kits-aerografo/` | guia | 65 | 146 | 2346 | 11 | 4 | 3 | 0 | — | title>60 pocos enlaces entrantes sin afiliado sin faq |
| `/compresores/lusqtoff-100-litros/` | guia | 65 | 150 | 2450 | 10 | 3 | 6 | 6 | — | title>60 sin faq |
| `/compresores/lusqtoff-50-litros/` | guia | 56 | 153 | 2181 | 7 | 2 | 12 | 9 | 20 (compresor lusqtoff 50 litros opiniones) | sin faq |
| `/compresores/manguera/` | guia | 65 | 155 | 2192 | 7 | 3 | 10 | 0 | — | title>60 sin afiliado sin faq |
| `/compresores/para-aerografo/` | guia | 61 | 110 | 2610 | 12 | 2 | 6 | 0 | 20 (compresor para aerografo silencioso) | title>60 sin afiliado sin faq |
| `/compresores/para-auto/` | guia | 52 | 176 | 2282 | 10 | 2 | 5 | 9 | 10 (mejor compresor de aire para auto) | desc>160 pocos enlaces entrantes sin faq |
| `/compresores/para-pintar/` | guia | 78 | 150 | 4120 | 14 | 6 | 9 | 1 | — | title>60 sin faq |
| `/compresores/pistola-para-pintar/` | guia | 58 | 166 | 2130 | 11 | 2 | 7 | 9 | — | desc>160 sin faq |
| `/compresores/sin-aceite/` | guia | 52 | 150 | 2702 | 12 | 3 | 5 | 6 | 10 (compresor sin aceite opiniones) | pocos enlaces entrantes |
| `/compresores/stanley/` | guia | 61 | 146 | 2635 | 12 | 2 | 3 | 6 | — | title>60 pocos enlaces entrantes sin faq |
| `/contacto/` | institucional | 35 | 64 | 125 | 2 | 0 | 190 | 0 | — | title hub generico |
| `/generadores/a-gas/` | guia | 64 | 141 | 1874 | 9 | 3 | 12 | 1 | 40 (generador electrico a gas) | title>60 sin faq |
| `/generadores/a-nafta/` | guia | 59 | 151 | 2832 | 10 | 5 | 15 | 12 | — | sin faq |
| `/generadores/chicos/` | guia | 68 | 153 | 2004 | 9 | 2 | 7 | 3 | — | title>60 sin faq |
| `/generadores/comparativa-general/` | guia | 63 | 129 | 2088 | 13 | 5 | 31 | 18 | 6600 (grupo electrogeno) | title>60 sin faq |
| `/generadores/diesel/` | guia | 70 | 156 | 2416 | 10 | 4 | 13 | 2 | — | title>60 sin faq |
| `/generadores/estacion-de-energia-portatil/` | guia | 73 | 145 | 2252 | 10 | 3 | 8 | 2 | 0 (estación de energía portátil) | title>60 sin faq |
| `/generadores/gamma-6500/` | guia | 63 | 140 | 2001 | 8 | 3 | 8 | 1 | — | title>60 sin faq |
| `/generadores/gamma-950/` | guia | 52 | 164 | 1245 | 7 | 1 | 8 | 1 | — | desc>160 sin faq |
| `/generadores/gamma/` | guia | 63 | 143 | 2334 | 8 | 5 | 13 | 5 | — | title>60 sin faq |
| `/generadores/honda-6500/` | guia | 59 | 137 | 1784 | 8 | 2 | 7 | 2 | — | sin faq |
| `/generadores/honda/` | guia | 60 | 145 | 1485 | 8 | 2 | 6 | 5 | — | sin faq |
| `/generadores/hyundai/` | guia | 60 | 160 | 2113 | 8 | 4 | 7 | 1 | 170 (generador hyundai) | sin faq |
| `/generadores/inverter/` | guia | 63 | 137 | 2450 | 9 | 3 | 19 | 5 | 480 (generador inverter) | title>60 sin faq |
| `/generadores/lusqtoff/` | guia | 73 | 179 | 2222 | 8 | 3 | 4 | 6 | 260 (generador lusqtoff) | title>60 desc>160 pocos enlaces entrantes sin faq |
| `/generadores/monofasicos/` | guia | 64 | 142 | 1882 | 9 | 2 | 18 | 5 | — | title>60 sin faq |
| `/generadores/niwa/` | guia | 60 | 110 | 1772 | 6 | 3 | 5 | 3 | — | pocos enlaces entrantes sin faq |
| `/generadores/para-casa/` | guia | 65 | 143 | 2137 | 9 | 3 | 25 | 5 | 390 (generador electrico para casa) | title>60 sin faq |
| `/generadores/portatiles/` | guia | 77 | 168 | 1933 | 8 | 4 | 14 | 3 | 0 (mejores generadores electricos portatiles) | title>60 desc>160 sin faq |
| `/generadores/precios/` | guia | 67 | 172 | 2038 | 9 | 3 | 23 | 23 | — | title>60 desc>160 sin faq |
| `/generadores/silenciosos/` | guia | 66 | 145 | 1585 | 10 | 1 | 15 | 3 | 110 (generador eléctrico silencioso) | title>60 sin faq |
| `/generadores/trifasicos/` | guia | 60 | 134 | 1709 | 9 | 1 | 11 | 2 | — | sin faq |
| `/hidrolavadoras/150-bar/` | guia | 64 | 179 | 1954 | 9 | 3 | 13 | 2 | — | title>60 desc>160 sin faq |
| `/hidrolavadoras/200-bar/` | guia | 55 | 158 | 1933 | 8 | 2 | 6 | 0 | — | sin afiliado sin faq |
| `/hidrolavadoras/black-decker/` | guia | 62 | 148 | 1943 | 8 | 2 | 4 | 6 | — | title>60 pocos enlaces entrantes sin faq |
| `/hidrolavadoras/bosch/` | guia | 62 | 157 | 1829 | 8 | 2 | 7 | 2 | — | title>60 sin faq |
| `/hidrolavadoras/comparativa-general/` | guia | 64 | 184 | 2340 | 7 | 3 | 24 | 9 | 20 (mejor hidrolavadora calidad precio) | title>60 desc>160 sin faq |
| `/hidrolavadoras/einhell/` | guia | 60 | 159 | 2085 | 8 | 4 | 5 | 3 | — | pocos enlaces entrantes sin faq |
| `/hidrolavadoras/gamma-130/` | guia | 63 | 155 | 1731 | 9 | 3 | 7 | 2 | — | title>60 sin faq |
| `/hidrolavadoras/gamma-150/` | guia | 60 | 154 | 1970 | 11 | 3 | 10 | 1 | — | sin faq |
| `/hidrolavadoras/gamma/` | guia | 66 | 116 | 2198 | 9 | 5 | 8 | 19 | 10 (hidrolavadora gamma opiniones) | title>60 sin faq |
| `/hidrolavadoras/hidrolavadora-para-aire-acondicionado/` | guia | 62 | 182 | 2087 | 9 | 2 | 3 | 1 | 260 (hidrolavadora para aire acondicionado) | title>60 desc>160 pocos enlaces entrantes sin faq |
| `/hidrolavadoras/hyundai/` | guia | 58 | 162 | 1619 | 8 | 3 | 5 | 0 | — | desc>160 pocos enlaces entrantes sin afiliado sin faq |
| `/hidrolavadoras/inalambricas/` | guia | 67 | 173 | 2326 | 10 | 6 | 10 | 2 | 5400 (hidrolavadora inalambrica) | title>60 desc>160 sin faq |
| `/hidrolavadoras/karcher-k2/` | guia | 64 | 183 | 2023 | 8 | 3 | 14 | 3 | — | title>60 desc>160 sin faq |
| `/hidrolavadoras/karcher-k3/` | guia | 59 | 157 | 1715 | 8 | 1 | 8 | 4 | — | sin faq |
| `/hidrolavadoras/karcher-k4/` | guia | 59 | 148 | 2187 | 11 | 3 | 9 | 3 | — | sin faq |
| `/hidrolavadoras/karcher-k5/` | guia | 64 | 174 | 1752 | 8 | 3 | 10 | 2 | — | title>60 desc>160 sin faq |
| `/hidrolavadoras/karcher/` | guia | 66 | 179 | 2081 | 8 | 4 | 11 | 3 | — | title>60 desc>160 sin faq |
| `/hidrolavadoras/lusqtoff-hl-120/` | guia | 58 | 131 | 1868 | 12 | 4 | 4 | 4 | 30 (hidrolavadora lusqtoff hl 120 opiniones) | pocos enlaces entrantes sin faq |
| `/hidrolavadoras/lusqtoff/` | guia | 58 | 164 | 1939 | 9 | 3 | 12 | 10 | — | desc>160 sin faq |
| `/hidrolavadoras/niwa/` | guia | 65 | 155 | 2327 | 10 | 4 | 10 | 4 | 30 (hidrolavadora niwa opiniones) | title>60 sin faq |
| `/hidrolavadoras/para-autos/` | guia | 67 | 172 | 2103 | 7 | 2 | 13 | 3 | 10 (mejores hidrolavadoras para autos) | title>60 desc>160 sin faq |
| `/hidrolavadoras/profesionales/` | guia | 64 | 164 | 2807 | 10 | 3 | 10 | 1 | 390 (hidrolavadora profesional) | title>60 desc>160 sin faq |
| `/hidrolavadoras/stihl/` | guia | 64 | 149 | 2066 | 9 | 3 | 3 | 1 | — | title>60 pocos enlaces entrantes sin faq |
| `/privacidad/` | institucional | 30 | 77 | 270 | 3 | 0 | 189 | 1 | — | title hub generico |
| `/sierras/bosch-gks-150/` | guia | 60 | 103 | 834 | 5 | 2 | 10 | 3 | 140 (sierra circular bosch gks 150) | corto<1000 sin faq |
| `/sierras/caladoras-black-decker/` | guia | 58 | 133 | 1332 | 6 | 2 | 6 | 1 | — | sin faq |
| `/sierras/caladoras-einhell/` | guia | 59 | 95 | 1262 | 6 | 2 | 10 | 3 | — | sin faq |
| `/sierras/caladoras-skil/` | guia | 61 | 123 | 1213 | 5 | 2 | 3 | 2 | — | title>60 pocos enlaces entrantes sin faq |
| `/sierras/caladoras/` | guia | 63 | 104 | 1576 | 8 | 4 | 21 | 3 | 0 (mejor sierra caladora calidad precio) | title>60 sin faq |
| `/sierras/circulares-black-decker/` | guia | 59 | 120 | 1034 | 4 | 2 | 5 | 1 | — | pocos enlaces entrantes sin faq |
| `/sierras/circulares-lusqtoff/` | guia | 62 | 107 | 1132 | 5 | 2 | 11 | 2 | 0 (sierra circular lusqtoff opiniones) | title>60 sin faq |
| `/sierras/circulares/` | guia | 66 | 95 | 1709 | 8 | 3 | 20 | 4 | 0 (mejor sierra circular calidad precio) | title>60 sin faq |
| `/sierras/de-banco-einhell/` | guia | 65 | 135 | 1192 | 4 | 2 | 9 | 2 | 10 (sierra de banco einhell opiniones) | title>60 sin faq |
| `/sierras/de-banco-lusqtoff/` | guia | 65 | 151 | 1700 | 6 | 4 | 7 | 2 | — | title>60 sin faq |
| `/sierras/de-banco/` | guia | 55 | 128 | 1489 | 6 | 4 | 18 | 2 | 0 (mejor sierra de mesa calidad precio) | sin faq |
| `/sierras/disco-para-sierra-circular/` | guia | 65 | 104 | 1848 | 8 | 4 | 5 | 1 | 170 (disco para sierra circular) | title>60 pocos enlaces entrantes sin faq |
| `/sierras/guia-para-sierra-circular/` | guia | 61 | 122 | 1191 | 5 | 3 | 9 | 2 | 390 (guia para sierra circular) | title>60 sin faq |
| `/sierras/ingletadoras-dewalt/` | guia | 67 | 120 | 1499 | 4 | 2 | 6 | 2 | — | title>60 sin faq |
| `/sierras/ingletadoras-einhell/` | guia | 63 | 158 | 1288 | 4 | 2 | 9 | 1 | 20 (ingletadora einhell opiniones) | title>60 sin faq |
| `/sierras/ingletadoras-total/` | guia | 63 | 105 | 1067 | 4 | 3 | 5 | 1 | — | title>60 pocos enlaces entrantes sin faq |
| `/sierras/ingletadoras/` | guia | 62 | 139 | 1606 | 7 | 4 | 8 | 3 | — | title>60 sin faq |
| `/sierras/sable/` | guia | 54 | 86 | 982 | 5 | 1 | 7 | 0 | — | corto<1000 sin afiliado sin faq |
| `/sierras/sensitivas-dewalt/` | guia | 69 | 111 | 1265 | 4 | 3 | 6 | 2 | — | title>60 sin faq |
| `/sierras/sensitivas-lusqtoff/` | guia | 69 | 159 | 907 | 5 | 2 | 11 | 2 | — | title>60 corto<1000 sin faq |
| `/sierras/sensitivas-total/` | guia | 62 | 110 | 1176 | 6 | 4 | 5 | 4 | — | title>60 pocos enlaces entrantes sin faq |
| `/sierras/sensitivas/` | guia | 62 | 97 | 1740 | 7 | 3 | 10 | 2 | — | title>60 sin faq |
| `/sierras/sierra-caladora-bosch/` | guia | 70 | 90 | 1167 | 5 | 2 | 7 | 3 | 140 (sierra caladora bosch) | title>60 sin faq |
| `/sierras/sierra-circular-dewalt-dwe560/` | guia | 62 | 127 | 1185 | 7 | 2 | 10 | 3 | 30 (sierra circular dewalt dwe560) | title>60 sin faq |
| `/sierras/sierra-circular-inalambrica/` | guia | 69 | 130 | 1495 | 7 | 1 | 10 | 6 | — | title>60 sin faq |
| `/sierras/sierra-sable-inalambrica/` | guia | 68 | 100 | 1220 | 4 | 4 | 4 | 2 | 90 (sierra sable inalambrica) | title>60 pocos enlaces entrantes sin faq |
| `/sierras/sierra-sin-fin-para-madera/` | guia | 63 | 104 | 1611 | 6 | 4 | 8 | 2 | 720 (sierra sin fin para madera) | title>60 sin faq |
| `/sierras/sin-fin-lusqtoff/` | guia | 66 | 137 | 1178 | 6 | 4 | 6 | 2 | — | title>60 sin faq |
| `/sierras/sin-fin-metal/` | guia | 58 | 155 | 1538 | 7 | 4 | 11 | 2 | — | sin faq |
| `/sierras/stanley-sc16/` | guia | 64 | 133 | 1166 | 7 | 3 | 9 | 3 | 30 (sierra circular stanley sc16) | title>60 sin faq |
| `/soldadoras/alambre-flux/` | guia | 55 | 144 | 1645 | 8 | 2 | 9 | 3 | 70 (alambre flux 0.8) | sin faq |
| `/soldadoras/alambre-para-soldadura-mig/` | guia | 59 | 145 | 1749 | 8 | 3 | 9 | 2 | 320 (alambre para soldadura mig) | sin faq |
| `/soldadoras/carro-para-soldadora-mig/` | guia | 63 | 174 | 1755 | 8 | 2 | 3 | 0 | — | title>60 desc>160 pocos enlaces entrantes sin afiliado sin faq |
| `/soldadoras/electrodo-6013/` | guia | 57 | 160 | 1496 | 8 | 2 | 11 | 4 | — | sin faq |
| `/soldadoras/electrodo-7018/` | guia | 57 | 198 | 1602 | 9 | 3 | 9 | 4 | — | desc>160 sin faq |
| `/soldadoras/electrodo-para-acero-inoxidable/` | guia | 56 | 161 | 1717 | 11 | 4 | 8 | 4 | — | desc>160 sin faq |
| `/soldadoras/electrodo-para-fundicion/` | guia | 57 | 203 | 1766 | 9 | 3 | 10 | 2 | — | desc>160 sin faq |
| `/soldadoras/esab-handyarc-162i/` | guia | 68 | 189 | 1576 | 9 | 4 | 11 | 3 | — | title>60 desc>160 sin faq |
| `/soldadoras/esab/` | guia | 62 | 147 | 1147 | 7 | 3 | 5 | 3 | — | title>60 pocos enlaces entrantes sin faq |
| `/soldadoras/guantes/` | guia | 61 | 179 | 1600 | 9 | 3 | 8 | 1 | 0 (mejores guantes para soldar) | title>60 desc>160 sin faq |
| `/soldadoras/lusqtoff-iron-100/` | guia | 68 | 171 | 1545 | 8 | 3 | 8 | 5 | — | title>60 desc>160 sin faq |
| `/soldadoras/lusqtoff-iron-250/` | guia | 63 | 173 | 1386 | 8 | 2 | 11 | 4 | 320 (soldadora lusqtoff iron 250) | title>60 desc>160 sin faq |
| `/soldadoras/lusqtoff-sml120-8d/` | guia | 57 | 153 | 1128 | 8 | 1 | 11 | 2 | — | sin faq |
| `/soldadoras/lusqtoff-sml130-7/` | guia | 60 | 189 | 1428 | 6 | 2 | 8 | 2 | — | desc>160 sin faq |
| `/soldadoras/lusqtoff-sml150-8/` | guia | 63 | 128 | 1101 | 6 | 1 | 8 | 2 | — | title>60 sin faq |
| `/soldadoras/lusqtoff/` | guia | 64 | 133 | 1380 | 9 | 4 | 13 | 6 | 20 (soldadora lusqtoff opiniones) | title>60 sin faq |
| `/soldadoras/mascara-lusqtoff-st-1x/` | guia | 64 | 189 | 1430 | 8 | 1 | 4 | 2 | — | title>60 desc>160 pocos enlaces entrantes sin faq |
| `/soldadoras/mascaras-fotosensibles/` | guia | 63 | 179 | 1947 | 8 | 3 | 5 | 3 | 880 (mascara de soldar fotosensible) | title>60 desc>160 pocos enlaces entrantes sin faq |
| `/soldadoras/mig-lusqtoff/` | guia | 62 | 159 | 1368 | 7 | 1 | 16 | 2 | — | title>60 sin faq |
| `/soldadoras/mig-sin-gas/` | guia | 63 | 140 | 1739 | 10 | 3 | 14 | 3 | 1600 (soldadora mig sin gas) | title>60 sin faq |
| `/soldadoras/para-aluminio/` | guia | 59 | 160 | 2425 | 8 | 4 | 9 | 2 | 210 (soldadora para aluminio) | sin faq |
| `/soldadoras/soldadora-de-punto/` | guia | 57 | 176 | 1416 | 9 | 3 | 4 | 0 | — | desc>160 pocos enlaces entrantes sin afiliado sin faq |
| `/soldadoras/soldadora-dogo-180/` | guia | 61 | 161 | 1545 | 8 | 3 | 7 | 3 | 110 (soldadora dogo 180) | title>60 desc>160 sin faq |
| `/soldadoras/soldadora-inverter-160-amp/` | guia | 62 | 144 | 1778 | 8 | 3 | 12 | 3 | 210 (soldadora inverter 160 amp) | title>60 sin faq |
| `/soldadoras/soldadora-inverter-200-amp/` | guia | 59 | 127 | 1484 | 9 | 4 | 11 | 2 | 720 (soldadora inverter 200 amp) | sin faq |
| `/soldadoras/soldadora-mig-con-gas/` | guia | 61 | 205 | 1994 | 9 | 4 | 11 | 3 | 1000 (soldadora mig con gas) | title>60 desc>160 sin faq |
| `/soldadoras/soldadora-tig-ac-dc/` | guia | 62 | 141 | 1950 | 8 | 3 | 13 | 3 | 90 (soldadora tig ac dc) | title>60 sin faq |
| `/soldadoras/tig/` | guia | 63 | 141 | 1763 | 9 | 3 | 10 | 3 | 0 (mejor soldadora tig) | title>60 sin faq |
| `/soldadura-electronica/estacion-de-soldadura/` | guia | 69 | 221 | 906 | 4 | 1 | 10 | 0 | — | title>60 desc>160 corto<1000 sin afiliado sin faq |
| `/soldadura-electronica/gadnic-878d/` | guia | 59 | 154 | 861 | 4 | 1 | 9 | 1 | — | corto<1000 sin faq |
| `/soldadura-electronica/kit-soldador-de-estano/` | guia | 66 | 126 | 813 | 4 | 1 | 9 | 1 | — | title>60 corto<1000 sin faq |
| `/soldadura-electronica/soporte-para-soldar-con-lupa/` | guia | 60 | 146 | 747 | 4 | 1 | 5 | 1 | — | corto<1000 pocos enlaces entrantes sin faq |
| `/soldadura-electronica/yihua-898d/` | guia | 58 | 121 | 1069 | 5 | 2 | 6 | 1 | — | sin faq |
| `/taladros/atornillador-impacto-dewalt/` | guia | 56 | 128 | 1401 | 7 | 1 | 8 | 2 | — | sin faq |
| `/taladros/atornilladores-de-impacto/` | guia | 65 | 143 | 1643 | 9 | 3 | 10 | 0 | 20 (mejor atornillador de impacto) | title>60 sin afiliado sin faq |
| `/taladros/black-decker/` | guia | 61 | 120 | 1179 | 7 | 1 | 5 | 2 | — | title>60 pocos enlaces entrantes sin faq |
| `/taladros/bosch-inalambrico/` | guia | 61 | 135 | 1667 | 9 | 3 | 11 | 2 | — | title>60 sin faq |
| `/taladros/brocas-ceramica/` | guia | 61 | 141 | 1570 | 8 | 1 | 7 | 2 | — | title>60 sin faq |
| `/taladros/combo-taladro-amoladora/` | guia | 65 | 131 | 1658 | 10 | 1 | 3 | 3 | — | title>60 pocos enlaces entrantes |
| `/taladros/dewalt-inalambrico/` | guia | 61 | 117 | 1176 | 8 | 1 | 12 | 2 | — | title>60 sin faq |
| `/taladros/einhell-inalambrico/` | guia | 53 | 111 | 1280 | 7 | 1 | 13 | 2 | — | sin faq |
| `/taladros/inalambricos/` | guia | 58 | 156 | 1867 | 9 | 5 | 24 | 4 | 40 (mejor taladro inalambrico) | sin faq |
| `/taladros/lusqtoff-inalambrico/` | guia | 63 | 118 | 1324 | 7 | 2 | 10 | 3 | — | title>60 sin faq |
| `/taladros/mecha-forstner-35-mm/` | guia | 66 | 147 | 1592 | 8 | 2 | 6 | 0 | — | title>60 sin afiliado sin faq |
| `/taladros/mecha-porcelanato/` | guia | 61 | 125 | 2032 | 8 | 3 | 8 | 2 | — | title>60 sin faq |
| `/taladros/mechas-escalonadas/` | guia | 61 | 149 | 1938 | 10 | 1 | 7 | 1 | — | title>60 |
| `/taladros/milwaukee/` | guia | 53 | 123 | 1662 | 7 | 3 | 6 | 2 | — | sin faq |
| `/taladros/para-durlock/` | guia | 61 | 115 | 1363 | 7 | 1 | 5 | 2 | 20 (que atornillador comprar para durlock) | title>60 pocos enlaces entrantes sin faq |
| `/taladros/percutores/` | guia | 58 | 115 | 1711 | 9 | 2 | 9 | 2 | 20 (mejor taladro percutor) | ok |
| `/taladros/rotomartillo-bosch/` | guia | 63 | 116 | 1264 | 7 | 1 | 7 | 3 | — | title>60 sin faq |
| `/taladros/rotomartillo-dewalt/` | guia | 60 | 112 | 1491 | 9 | 1 | 7 | 1 | — | sin faq |
| `/taladros/rotomartillo-einhell/` | guia | 62 | 117 | 1376 | 7 | 1 | 5 | 2 | — | title>60 pocos enlaces entrantes sin faq |
| `/taladros/rotomartillos/` | guia | 58 | 159 | 1763 | 8 | 4 | 20 | 1 | — | sin faq |
| `/taladros/stanley/` | guia | 60 | 117 | 1350 | 7 | 2 | 8 | 2 | 20 (taladro stanley opiniones) | sin faq |
| `/taladros/taladro-de-banco/` | guia | 57 | 165 | 1876 | 8 | 5 | 7 | 5 | — | desc>160 sin faq |
| `/taladros/taladro-percutor-inalambrico/` | guia | 63 | 136 | 1454 | 10 | 2 | 15 | 2 | 1000 (taladro percutor inalambrico) | title>60 sin faq |
