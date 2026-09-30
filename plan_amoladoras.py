from analizar_amoladoras import OUT, ROOT, base, sem, additional, allsem, norm, summary
import json

# Each measured query has exactly one editorial owner, including deferred topics.
specs = [
('','Cómo elegir una amoladora: tipos, medidas y marcas','Qué amoladora comprar según el trabajo y el presupuesto','como elegir una amoladora|mejores marcas de amoladoras|mejor amoladora calidad precio|mejor amoladora profesional',
'Qué es una amoladora y para qué sirve|Angular, recta o de banco: diferencias|Qué tamaño y potencia necesitás|Con cable o a batería|Marcas y opciones según presupuesto|Cómo comparar precio, garantía y accesorios',
'Guía central. Concentra elección general, precios y marcas; deriva a páginas específicas sin repetir sus comparativas. CTA a las alternativas concretas que se hayan documentado.'),
('de-banco','Amoladora de banco: cómo elegir para tu taller','Amoladoras de banco: cuál elegir para afilar y desbastar','amoladora de banco',
'Para qué sirve una amoladora de banco|Diámetro de muela, potencia y régimen de trabajo|Muela, grano y compatibilidad con el material|Modelos para uso ocasional y taller|Qué revisar antes de instalarla y comprar',
'Prioridad por demanda y KD. Integrar esmeril de banco, precios y marcas; comparar máquinas de banco, sin mezclar con angulares. CTA a la máquina y muela compatibles.'),
('disco-flap','Disco flap: para qué sirve y qué grano elegir','Disco flap: cómo elegir grano, medida y abrasivo','disco flap',
'Qué es un disco flap y cuándo se usa|Granos 40, 60, 80 y 120: cómo compararlos|Óxido de aluminio, zirconio y cerámico|Flap, desbaste o lija: qué cambia|Diámetro, montaje y RPM compatibles|Opciones para comparar en Mercado Libre',
'Gran puerta informativa con salida comercial a consumibles. Mostrar tabla grano/material/acabado con respaldo del fabricante; no una página por grano.'),
('disco-de-desbaste','Disco de desbaste: cómo elegirlo para metal','Discos de desbaste para metal: usos, medidas y elección','disco de desbaste',
'Qué diferencia al desbaste del corte|Cómo elegir según el metal|Diámetro, espesor y velocidad máxima|Disco rígido o flap para la terminación|Cómo comparar duración y costo por trabajo',
'Acotar esta URL a abrasivos para metal. La copa para hormigón tiene otra página. CTA al tipo de disco compatible; pruebas de duración solo si se realizan.'),
('discos','Discos para amoladora: tipos y cómo elegir','Tipos de discos para amoladora y para qué sirve cada uno','',
'Qué disco corresponde a cada trabajo|Discos de corte para metal y mampostería|Flap, desbaste, cepillo y lijado|Cómo leer medida, eje y RPM|Errores de compatibilidad que debés evitar|Guías por material y opciones de compra',
'Subhub para discos para amoladora y tipos de discos para amoladora: organiza accesorios por operación, material y compatibilidad. La consulta específica de disco de corte para amoladora corresponde a /amoladoras/disco-de-corte/. CTA contextual por tarea; evitar catálogo indiscriminado.'),
('recta','Amoladora recta: eléctrica o neumática, cuál elegir','Amoladoras rectas: usos y diferencias entre eléctricas y neumáticas','amoladora recta|amoladora neumatica recta',
'Para qué sirve una amoladora recta|Diferencias frente a una angular y un minitorno|Eléctrica o neumática según el trabajo|Pinza, accesorio y velocidad compatibles|Qué necesita la versión neumática|Modelos y accesorios para comparar',
'La neumática empieza como sección propia, sin asumir que es igual a la eléctrica. Enlazar al futuro grupo de compresores. CTA a máquina, fresas compatibles y requisitos de aire.'),
('dewalt','Amoladoras DeWalt: modelos y cómo elegir','Qué amoladora DeWalt elegir según el uso','amoladora dewalt|amoladora dewalt dwe4020',
'Qué modelos DeWalt se comparan|Medida, potencia y protecciones por modelo|DWE4020: prestaciones y límites documentados|Cuándo elegir cable o batería|Alternativas y precios a consultar',
'La demanda principal justifica una guía de marca. DWE4020 empieza como H2; no crear ficha por sus 20 búsquedas si falta análisis propio. Normalizar de walt y dewalt.'),
('makita','Amoladoras Makita: modelos y diferencias','Qué amoladora Makita elegir: modelos y diferencias de uso','amoladora makita|amoladora makita 9557hpg|amoladora makita ga4530',
'Qué modelos Makita conviene comparar|9557HPG y GA4530: diferencias verificadas|Diámetro, ergonomía y trabajo previsto|Cuándo considerar una máquina más grande|Qué incluye cada publicación y dónde consultar precio',
'Integrar modelos como subsecciones, cada uno con ficha oficial y código exacto. No adjudicar experiencias de una versión a otra. CTA separado para cada modelo.'),
('stanley','Amoladoras Stanley: cómo elegir el modelo','Amoladoras Stanley: modelos, usos y qué revisar antes de comprar','amoladora stanley|amoladora stanley opiniones|amoladora stanley inalambrica',
'Qué modelos Stanley están disponibles|Diferencias de potencia, tamaño y protección|Modelos con cable y a batería|Ventajas y límites según la ficha técnica|Qué revisar en garantía, kit y precio',
'KD 8 para el término general; opiniones tiene volumen 0 y no necesita otra URL. Comparación editorial útil para competir con tiendas. CTA a SKU verificado.'),
('ingco','Amoladoras Ingco: diferencias y guía de compra','Amoladoras Ingco: qué comparar antes de elegir','amoladora ingco',
'Gamas y modelos que estamos comparando|Potencia, diámetro y uso previsto|Cable o batería y costo del kit|Prestaciones que cambian entre versiones|Opciones equivalentes y precios a consultar',
'KD 10 con demanda intermedia. Necesita diferenciación real entre modelos y fuentes oficiales; no afirmar calidad profesional solo por publicidad. CTA por versión.'),
('9-pulgadas','Amoladora de 9 pulgadas: cuándo conviene una de 230 mm','Amoladoras de 9 pulgadas y 230 mm: usos y elección','amoladora 9 pulgadas',
'Cuándo hace falta una amoladora de 230 mm|Qué cambia frente a 180 y 115 mm|Peso, agarre, potencia y protecciones|Discos compatibles y límites de uso|Modelos para comparar antes de comprar',
'KD 5. Una URL para 9 pulgadas y 230 mm. Amoladora grande es ambigua: el hub explica 180 y 230 mm; no adjudicar todo su volumen a esta URL.'),
('velocidad-variable','Amoladora con velocidad variable: cuándo conviene','Amoladoras con velocidad variable: qué mirar al elegir','amoladora velocidad variable',
'Qué permite regular la velocidad|RPM mínimas y máximas frente a velocidad constante|Compatibilidad del accesorio y el material|Qué funciones comparar entre modelos|Cuándo conviene otra herramienta',
'Integrar regulador de velocidad y velocidad regulable. No prometer que cualquier angular reemplaza a una pulidora. Enlazar modelos compatibles de las guías de marca.'),
('115-o-125','Amoladora de 115 o 125 mm: diferencias y elección','Amoladora de 115 o 125 mm: cuál elegir para tu trabajo','amoladora 115|amoladora 125|mejor amoladora 125',
'Qué significa el diámetro de una amoladora|115 y 125 mm: diferencias para elegir|Peso, potencia y capacidad según el modelo|Qué discos admite realmente cada máquina|Opciones para uso ocasional y frecuente',
'Agrupación editorial inicial por decisión compartida, no porque sean equivalentes. Incluir 4 1/2 en el bloque de 115. Nunca recomendar adaptar un disco mayor. Separar URLs solo con evidencia de intención distinta y contenido suficiente.'),
('bosch','Amoladoras Bosch: modelos y diferencias para elegir','Qué amoladora Bosch elegir según el trabajo','amoladora bosch|amoladora bosch gws 850|amoladora bosch gws 700|amoladora bosch gws 9 125 s|amoladora bosch inalambrica 18v gws 180 li brushless',
'Cómo comparar las gamas Bosch|GWS 700 y GWS 850: diferencias verificadas|GWS 9-125 S y regulación de velocidad|GWS 180-LI y costo del sistema a batería|Qué modelo corresponde a cada necesidad|Dónde consultar precio y contenido del kit',
'Mayor volumen medido del grupo. KD 17 no invalida trabajarla, pero la competencia comercial exige más investigación. Los códigos y versiones deben validarse en Argentina antes de redactar fichas.'),
('inalambricas','Amoladoras inalámbricas: cómo elegir batería y modelo','Amoladoras inalámbricas: qué conviene comprar y qué incluye el kit','amoladora inalambrica|mejor amoladora a bateria|mini amoladora inalambrica',
'Cuándo conviene una amoladora a batería|Máquina sola o kit con batería y cargador|Capacidad, plataforma y autonomía documentada|Diámetro y diferencia con una mini amoladora|Qué comparar entre marcas|Costo total y opciones en Mercado Libre',
'Una URL para inalámbrica, a batería y con batería. Mini es una subcategoría distinta que debe explicarse, no tratarse como sinónimo universal. CTA a kits comparables; no prometer autonomía sin pruebas.'),
('skil','Amoladoras Skil de 700 y 830 W: qué comparar','Amoladoras Skil de 700 y 830 W: diferencias para elegir','amoladora skil 830w|amoladora skil 700w|amoladora skil 9002 opiniones',
'Identificá el código y la versión de cada amoladora|Qué cambia entre las opciones de 700 y 830 W|Medida, ergonomía y equipamiento|Skil 9002: qué se puede afirmar con evidencia|Alternativas y precios de cada versión',
'830 W tiene KD 5 y 700 W KD 16. Son dos productos a comparar, no el mismo modelo. No dar por hecho el código solo por los watts ni trasladar opiniones entre ellos.'),
('discos-ceramica','Disco para cortar cerámica: cómo elegirlo','Qué disco elegir para cortar cerámica con amoladora','disco para cortar ceramica|mejor disco para cortar ceramica',
'Cerámica y porcelanato: por qué distinguirlos|Borde, espesor y material admitido|Diámetro, eje y compatibilidad con la máquina|Qué revisar para reducir roturas del acabado|Discos para comparar y cuándo usar otra cortadora',
'Volumen 590 y KD 16. La variante mejor tiene KD 14 y volumen n/d, no 590. La página de porcelanato profundiza ese material sin duplicar esta guía.'),
('uso-seguro','Cómo usar una amoladora: controles y uso seguro','Cómo usar una amoladora: qué revisar antes de trabajar','',
'Identificá la máquina, el accesorio y el trabajo|Qué comprobar en el manual antes de empezar|Protección personal y sujeción de la pieza|Operaciones que requieren otra herramienta|Señales para detener el trabajo y revisar el equipo|Guías de discos y accesorios compatibles',
'Página editorial de apoyo sin KD medido: atender consultas de uso presentes en la base y respaldar las recomendaciones. Revisión técnica obligatoria antes de publicar instrucciones. CTA secundario a protección y accesorios compatibles.'),
('7-pulgadas','Amoladora de 7 pulgadas: cómo elegir una de 180 mm','Amoladoras de 7 pulgadas y 180 mm: cuándo elegirlas','amoladora 7 pulgadas',
'Para qué trabajos considerar 180 mm|Qué cambia frente a 115 y 230 mm|Peso, potencia y prestaciones por modelo|Discos y accesorios admitidos|Qué comparar antes de comprar',
'260 búsquedas, KD 12. Separar de 230 porque son elecciones y catálogos distintos; no repetir la introducción completa del hub. Comparativa transversal breve con enlaces.'),
('einhell','Amoladoras Einhell a batería: modelos y kits','Amoladoras Einhell inalámbricas: qué comparar entre modelos y kits','amoladora inalambrica einhell|amoladora einhell axxio|amoladora einhell opiniones',
'Qué modelos y versiones se comparan|AXXIO: prestaciones según versión|Compatibilidad de batería y cargador|Máquina sola frente a kit completo|Ventajas, límites y alternativas',
'Priorizar inalámbrica, 140/KD 8. Opiniones genéricas 30/KD 27 se tratan con alcance explícito: la guía no evalúa todas las Einhell con cable. CTA a la versión y kit exactos.'),
('lusqtoff','Amoladoras Lusqtoff: modelos y qué revisar','Amoladoras Lusqtoff: cómo comparar modelos con cable y batería','amoladora lusqtoff|amoladora lusqtoff 850w opiniones|amoladora lusqtoff a bateria',
'Qué modelos Lusqtoff se comparan|Opciones de 850 W: identificá el código|Versiones a batería y contenido del kit|Garantía, repuestos y limitaciones documentadas|Alternativas y precios a consultar',
'Término general 1.000/KD 18; 850w opiniones tiene KD 32 y volumen desconocido. No crear esa ficha al inicio ni asignarle el KD 18 de la marca.'),
('black-decker','Amoladoras Black+Decker: G720 y otras opciones','Amoladoras Black+Decker: qué revisar en la G720 y otras versiones','amoladora black decker g720|amoladora g720 black decker opiniones',
'G720: código, versión y ficha técnica|Para qué uso está indicada según fabricante|Diferencias frente a otras Black+Decker|Qué sabemos y qué no sobre su desempeño|Qué revisar en precio, garantía y accesorios',
'La métrica 260/KD 21 corresponde a G720, no a toda la marca. Orientar el contenido inicial a ella; integrar variaciones black decker, black and decker y black & decker. No equiparar automáticamente 820 W y G720.'),
('daewoo','Amoladoras Daewoo: modelos y guía de elección','Amoladoras Daewoo: prestaciones y diferencias para elegir','amoladora daewoo|amoladora daewoo 750w opiniones',
'Identificación del modelo y su versión|Qué revisar en opciones de 750 W|Diámetro, protección y uso previsto|Ventajas y límites documentados|Alternativas y compra del modelo correcto',
'260/KD 21 para la marca. La versión de 750 W empieza como apartado y se valida por código. CTA a máquina exacta y accesorios compatibles.'),
('cepillo-de-alambre','Cepillo de alambre para amoladora: cuál elegir','Discos y cepillos de alambre para amoladora: tipos y usos','disco de alambre para amoladora',
'Cepillo de copa o circular: qué cambia|Alambre ondulado o trenzado según aplicación|Material de la pieza y del alambre|Montaje, diámetro y velocidad máxima|Opciones para comparar por tarea',
'Agrupar cepillo acero, copa y alambre, diferenciando los tipos. No mezclar cepillos de banco. CTA con rosca/montaje verificados.'),
('desbaste-hormigon','Disco de desbaste para hormigón: cómo elegir','Copas y discos para desbastar hormigón: compatibilidad y elección','disco desbaste hormigon',
'Qué accesorio corresponde al desbaste de hormigón|Copa diamantada y geometría según fabricante|Máquina, montaje y velocidad compatibles|Control del polvo y requisitos del equipo|Cómo comparar opciones y costo total',
'170/KD 15. Integra concreto, cemento y copa diamantada solo cuando corresponde al mismo trabajo. Diferenciar pulido fino y máquinas de piso. CTA al sistema compatible completo.'),
('discos-diamantados','Disco diamantado: segmentado, turbo o continuo','Discos diamantados: diferencias entre segmentado, turbo y continuo','disco diamantado segmentado',
'Qué es un disco diamantado|Segmentado, turbo y continuo: diferencias|Qué materiales admite cada referencia|Corte seco o húmedo según equipo y disco|Cómo elegir medida, eje y RPM|Guías específicas por material',
'110/KD 5 corresponde a segmentado. No asignar el KD a diamantados genérico, que tiene 50.000 en la base sin validación. CTA por material, sin repetir las guías de cerámica y porcelanato.'),
('discos-ladrillo','Disco para cortar ladrillo: cómo elegirlo','Qué disco elegir para cortar ladrillo con una máquina compatible','disco para cortar ladrillo',
'Identificá el tipo de ladrillo y el corte requerido|Qué discos admite el material según fabricante|Diámetro y capacidad de la máquina|Polvo, sujeción y condiciones de trabajo|Opciones de disco y cuándo usar otra cortadora',
'170/KD 11. Intención por material suficientemente diferenciada; integrar ladrillo refractario solo con compatibilidad documentada. CTA a disco o cortadora apropiada.'),
('discos-metal','Discos de corte para metal, chapa e inoxidable','Cómo elegir discos para cortar metal, chapa y acero inoxidable','disco para cortar chapa|disco para amoladora para cortar acero inoxidable|mejores discos de corte para metal',
'Qué metal y espesor necesitás cortar|Disco para chapa: qué características comparar|Qué exige el corte de acero inoxidable|Medida, espesor, eje y RPM|Cómo comparar discos y costo por corte',
'Una guía inicial con secciones de chapa e inoxidable; volúmenes medidos 90 y 20. No separar microconsultas antes de demostrar demanda y diferencias editoriales. CTA por material.'),
('discos-porcelanato','Disco para cortar porcelanato: cómo elegir','Qué disco elegir para cortar porcelanato y cuidar el acabado','disco para cortar porcelanato|mejor disco para cortar porcelanato',
'Por qué el porcelanato necesita una elección específica|Borde y espesor del disco según fabricante|Amoladora o cortadora dedicada|Factores que afectan el astillado|Discos para comparar y límites de cada opción',
'590/KD 31 general; mejor tiene KD 19 pero n/d volumen. Publicar después de cerámica con ejemplos y evidencia propia; no vender como oportunidad KD 19 con volumen 590.'),
('madera','Amoladora para madera: usos, límites y alternativas','Amoladora y madera: qué usos admite el equipo y qué alternativas hay','',
'Cortar, lijar y desbastar son trabajos distintos|Qué usos autoriza el manual de la máquina|Por qué no alcanza con que el disco encaje|Cuándo elegir una sierra o una lijadora|Cómo comprar una herramienta adecuada al trabajo',
'Demanda presente en la base, sin KD de estas consultas. Página de decisión y seguridad, no recomendación indiscriminada de discos dentados. CTA hacia herramientas apropiadas de los otros grupos. Requiere revisión técnica y medición antes de priorizar.'),
]
pages=[]; owners={}
for i,(slug,title,h1,keywords,h2,notes) in enumerate(specs,1):
    p=dict(id=i,phase=1 if i<=18 else 2,url='/amoladoras/'+(slug+'/' if slug else ''),title=title,h1=h1,keywords=keywords.split('|') if keywords else [],h2=h2.split('|'),notes=notes)
    if slug=='discos': p['target_queries']=['discos para amoladora','tipos de discos para amoladora']
    pages.append(p)
    for k in p['keywords']:
        assert norm(k) not in owners,k
        owners[norm(k)]=i
deferred={'amoladora gamma opiniones':'No crear URL todavía: 20 búsquedas. Considerar sección en la guía central solo con evidencia de producto.', 'amoladora total opiniones':'No crear URL todavía: KD 33 y volumen n/d. Medir primero la marca y sus modelos.'}
existing_routes={'disco de corte para amoladora':'/amoladoras/disco-de-corte/'}
assert len(pages)==30
assert len({p['url'] for p in pages})==30
assert all(norm(r['keyword']) in owners or norm(r['keyword']) in deferred or norm(r['keyword']) in existing_routes for r in allsem)
assert set(owners).issubset({norm(r['keyword']) for r in allsem})
for r in allsem:
    r['page_id']=owners.get(norm(r['keyword']))
    r['decision']=pages[r['page_id']-1]['url'] if r['page_id'] else existing_routes.get(norm(r['keyword']),deferred.get(norm(r['keyword'])))
(OUT/'plan-estructurado.json').write_text(json.dumps(dict(pages=pages,measured=allsem),ensure_ascii=False,indent=2),encoding='utf-8')

intro='''# Plan SEO de amoladoras para un dominio nuevo

Fecha de análisis: 23/09/2026. Mercado de trabajo asumido: Argentina, por la moneda ARS y el destino Mercado Libre. El país de la base Semrush no figura en los CSV: comprobarlo antes de invertir en producción. ML se interpreta como Mercado Libre. Este informe define arquitectura y briefs; no crea ni publica artículos.

## Decisión

**Crear un plan de 30 páginas: 18 en la primera tanda y 12 en la segunda.** No son 30 fichas de producto: son guías centrales, guías por tipo de máquina, comparativas de marcas y contenidos sobre accesorios/materiales. El número es una decisión editorial basada en intención y recursos de un sitio nuevo, no un óptimo matemático de tráfico. Puede ampliarse cuando aparezcan datos propios.

Primero conviene captar consultas específicas con dificultad moderada o baja y resolver una decisión de compra real. También debemos construir desde el inicio las páginas de Bosch, DeWalt, Makita e inalámbricas: tienen demanda considerable. La baja dificultad no convierte un artículo en la respuesta correcta para cualquier búsqueda de compra.

No crearía una página por variante, potencia, grano de disco, error ortográfico o combinación de marca y medida. Tampoco empezaría con 40 reseñas de productos. Los modelos pequeños se incluyen inicialmente en su guía de marca y se separan si una reseña propia aporta información suficiente.

Las 30 páginas incluyen dos editoriales sin KD: uso seguro y madera. La primera sostiene la calidad del grupo; la segunda queda en la tanda posterior y debe medirse. Las páginas legales, autoría y metodología son infraestructura del sitio, no se cuentan como páginas de este grupo.

## Qué revisé y qué permiten concluir los datos

- `keywords_amoladora.csv`: **4.913 filas**, **4.892 consultas únicas** después de normalizar mayúsculas, tildes y espacios. La normalización reduce 21 filas; no agrupa automáticamente todas las variantes semánticas.
- `semrush_amoladoras.csv`: **40 consultas**.
- `semrush_consulta_adicional.csv`: **19 consultas adicionales relevantes**, incluyendo discos y accesorios; ninguna repite las 40 anteriores.
- Total: **59 consultas únicas con KD**, todas presentes también en el archivo base. **17 tienen volumen n/d, 1 tiene volumen 0 y 41 tienen volumen positivo.**
- Las 59 equivalen aproximadamente al **1,2% de las 4.892 consultas normalizadas**. No significa que solo esté estudiado el 1,2% de la demanda: las mediciones seleccionadas incluyen muchos términos principales. Tampoco habilita a atribuir KD a las miles de variantes restantes.
- El volumen de Google Ads solo toma cuatro valores: 50.000 (1 fila), 5.000 (27), 500 (271) y 50 (4.614). Esa discretización impide tratarlo como una medición fina; no consta cómo se exportaron o transformaron los rangos. Sirve para descubrir temas y jerarquías aproximadas.
- `diamantados` tiene 50.000 en esa base, pero es ambiguo y no tiene KD propio. No es una justificación para construir una página que prometa capturar 50.000 visitas.
- Competencia de Google Ads y CPC son métricas publicitarias. No sustituyen dificultad SEO ni comisión de afiliados.
- Los encabezados mensuales de la base abarcan septiembre de 2025 a agosto de 2026. No se usa una tendencia mensual sin valores útiles. Semrush conserva referencias relativas como “Ahora” o “1 mes”, no una fecha de exportación verificable; consultas adicionales no informa actualización.

**No sumo los volúmenes como tráfico potencial del sitio.** Existen búsquedas próximas, variantes, solapamientos y diferencias entre fuentes. Volumen no equivale a clics ni visitantes únicos. Sin posiciones, CTR y conversión propios no se puede dar una previsión fiable.

Se conserva el KD de cada consulta exacta. Ejemplo clave: `disco para cortar porcelanato` tiene 590 y KD 31; `mejor disco para cortar porcelanato` tiene volumen n/d y KD 19. No se puede presentar la segunda como una oportunidad de 590 búsquedas y KD 19.

## Qué cambia al incorporar consultas adicionales

El archivo adicional cambia la estrategia: abre guías de marca con demanda mucho mayor que las reseñas de 10–30 búsquedas. Las 19 mediciones son:

| Keyword exacta | Volumen Semrush | KD |
|---|---:|---:|
'''
parts=[intro]
for r in additional:parts.append(f"| {r['keyword']} | {r['volume']} | {r['kd']} |\n")
parts.append('''
## Priorización y comprobación de intención

Uso KD 0–14 como primer filtro de facilidad relativa, 15–29 como segunda franja y 30+ con más cautela. Son franjas orientativas de Semrush; KD no es una probabilidad de éxito ni evalúa por sí solo este dominio. [Documentación de Semrush](https://www.semrush.com/kb/1158-what-is-kd).

Cruzo ese filtro con demanda, intención, valor de compra, posibilidad de producir evidencia y esfuerzo editorial. Un disco flap puede atraer muchas visitas y vender consumibles; una amoladora de menor demanda puede generar una compra de mayor importe. Sin comisiones y conversiones reales no asigno un ingreso estimado.

Se hizo un muestreo web, no una captura geolocalizada del top 10 de Google Argentina ni una validación de solapamiento para las 59 consultas:

- Hay guías de elección de herramientas, como la [guía de amoladoras de Sodimac](https://www.sodimac.com.ar/sodimac-ar/content/a110039/amoladoras). Esto respalda ensayar contenido de elección general.
- En banco aparece una [categoría de Makita Argentina](https://makita.com.ar/categorias/amoladoras/amoladoras-de-banco/). La intención comercial requiere comparar alternativas concretas, no solo definir la herramienta.
- En flap existe contenido informativo del fabricante, como [la guía de Norton](https://www.nortonabrasives.com/es-pe/blog/como-elegir-un-disco-flap). La oportunidad editorial está en aclarar la selección y documentar resultados; no se presupone ausencia de competencia.
- Una búsqueda restringida a tiendas y marca para Stanley devolvió [listados de Mercado Libre](https://listado.mercadolibre.com.ar/amoladora-stanley). Confirma que hay competencia comercial, pero ese filtro no permite afirmar qué porcentaje de la SERP completa ocupan las tiendas.

Por eso las agrupaciones 115/125, modelos Skil, recta/neumática y cerámica/porcelanato son decisiones editoriales iniciales. Antes de separar más URLs, comparar resultados orgánicos para cada par en Argentina: si predominan las mismas URLs y la necesidad es la misma, mantener juntas; si predominan resultados distintos y hay contenido propio suficiente, separar. No hay un umbral de coincidencia universal.

## Las 30 páginas y su orden de producción

Volumen y KD que siguen pertenecen a la consulta de referencia, **no a toda la página**. “s/m” significa sin medición Semrush. IDs 01–18: primera tanda; IDs 19–30: segunda tanda. Las URLs son propuestas para un sitio cuya estructura actual no fue facilitada.

| ID | URL | Consulta de referencia | Volumen | KD |
|---:|---|---|---:|---:|
''')
lookup={norm(r['keyword']):r for r in allsem}
for p in pages:
    r=lookup[norm(p['keywords'][0])] if p['keywords'] else None
    query='discos para amoladora / tipos de discos para amoladora' if p['id']==5 else (r['keyword'] if r else 'Apoyo editorial; ver brief')
    parts.append(f"| {p['id']:02} | `{p['url']}` | {query} | {r['volume'] if r else 's/m'} | {r['kd'] if r else 's/m'} |\n")
parts.append('''
### Secuencia práctica

**Bloque 1:** publicar 01, 05 y 18 como estructura de navegación y referencia; acompañar con 02, 03, 04 y 06 para empezar con banco, flap, desbaste y recta. La página de uso debe pasar revisión técnica, aunque su volumen no esté medido.

**Bloque 2:** 07, 08, 09, 10, 11, 12 y 13. Combinar marcas con KD bajo, medida y velocidad variable.

**Bloque 3:** 14, 15, 16 y 17. Bosch e inalámbricas tienen potencial amplio; no dejarlas indefinidamente para después. Skil y cerámica agregan decisiones específicas.

**Segunda tanda:** 19–30 después de completar los primeros briefs y comprobar indexabilidad y calidad. Priorizar entre ellas 19, 20, 21, 25 y 26; luego completar las demás según capacidad y señales propias. Porcelanato merece más evidencia por su KD general 31. Madera requiere medición y revisión técnica antes de competir por búsquedas de corte.

No hace falta esperar un plazo fijo ni inventar una “maduración” obligatoria del dominio. Revisar datos a los 30, 60 y 90 días desde publicación como rutina de gestión, sin convertir esos plazos en promesas de resultados.

## Briefs: title, H1, H2 y salida comercial

Los titles se mantienen descriptivos, sin año que envejezca y sin “mejor” cuando no existe una comparación que lo sostenga. Un H1 por artículo facilita una estructura consistente; los H2 siguientes son el esquema editorial. El detalle de cada modelo puede bajar a H3 para conservar legibilidad.

''')
for p in pages:
    parts.append(f"### {p['id']:02}. {p['url']} — tanda {p['phase']}\n\n**Title:** {p['title']}\n\n**H1:** {p['h1']}\n\n**H2 propuestos, en orden:**\n\n")
    parts.extend(f'{i}. {h}\n' for i,h in enumerate(p['h2'],1))
    if p.get('target_queries'):
        parts.append('\n**Intención principal:** '+ ' / '.join(p['target_queries'])+'. Sin métricas Semrush exactas asignadas en esta planificación.\n')
    if p['keywords']:
        parts.append('\n**Consultas medidas asignadas:** '+ '; '.join(f"{k} ({lookup[norm(k)]['volume']}; KD {lookup[norm(k)]['kd']})" for k in p['keywords'])+'.\n')
    parts.append('\n**Enfoque y conversión:** '+p['notes']+'\n\n')

parts.append('''## Qué unificar y qué no crear todavía

| Familia o consulta | Decisión inicial | Motivo |
|---|---|---|
| Batería / a batería / con batería / inalámbrica | Una URL: 15 | Cambia la forma de decirlo, no la necesidad principal. |
| 9 pulgadas / 230 mm; 7 pulgadas / 180 mm | Una URL por medida: 11 y 19 | Unificar unidades; conservar diferencia entre máquinas. |
| Precio / oferta / barata | Apartados de compra en la página pertinente | No publicar clones ni ofertas sin mantenimiento. |
| GWS 850 / GWS 700 / GWS 9-125 S / GWS 180-LI | Secciones dentro de 14 | Son modelos diferentes; compartir guía no implica equivalencia. |
| Makita GA4530 y 9557HPG; DeWalt DWE4020 | Secciones en 08 y 07 | 20 búsquedas cada una en las mediciones disponibles. |
| Mejor calidad precio / mejor profesional / marcas | Página central 01 con criterios diferenciados | Evitar varias listas genéricas con el mismo contenido. |
| Flap 40 / 60 / 80 / 120, discoflap y flapper | Página 03 | Tabla de grano y aplicación; no cuatro artículos repetidos. |
| Gamma opiniones | Posponer URL | 20 búsquedas y KD 14: posible después de medir gamma genérico y conseguir evidencia. |
| Total opiniones | Posponer URL | KD 33 y volumen n/d; no prioridad inicial. |
| Metabo, Milwaukee, Hamilton, Dowen Pagio, otras marcas | Lista de investigación | Hay variantes en la base, pero faltan KD y demanda más precisa de sus consultas principales. |
| Easy, Sodimac, tiendas concretas, usadas | No crear landing inicial | Navegación hacia terceros o intención de segunda mano; afinidad menor con la propuesta editorial inicial. |
| Diamantados | No usar como objetivo principal | Ambigüedad y volumen de base no validado. |
| Discos de 14 pulgadas, tronzadora, minitorno, Dremel, pavimento | Revisar para otro grupo | Aparecen en el CSV, pero no toda consulta de disco pertenece a amoladoras. |
| Vidrio, mármol, granito, pulido de pisos | Investigación posterior | Distintas máquinas, materiales y procesos; no forzar equivalencias para ganar volumen. |

La página 13 compara 115 y 125 mm; la 01 explica la elección de herramienta. La 05 explica familias de accesorios; 03 y 04 profundizan acabado y desbaste. La 26 compara diseños diamantados; 17 y 29 resuelven materiales concretos. Cada una debe enlazar a la otra sin repetir su desarrollo.

## Cómo llevar las visitas a Mercado Libre

El recorrido propuesto es **consulta → respuesta concreta → criterios de elección → opción adecuada → clic voluntario a ML**. Las guías deben ser útiles aunque el lector no compre.

1. Abrir con una respuesta breve y una tabla de decisión según tarea, material, medida y presupuesto. En comparativas, indicar para quién sirve y para quién no cada opción.
2. Mostrar de tres a cinco alternativas solo cuando haya opciones justificadas; no rellenar listas por cantidad. Incluir código, alimentación, diámetro, protecciones, contenido del kit, limitaciones y fuente de las especificaciones.
3. Usar botones específicos: “Ver precio de este modelo en Mercado Libre” o “Ver disco compatible”. Las páginas de batería deben aclarar máquina sola, batería y cargador; las de discos, diámetro y montaje.
4. Enlazar una publicación o producto que corresponda al modelo evaluado. Si se utiliza una búsqueda como alternativa por falta de stock, identificarla como tal; no prometer una oferta concreta. No se seleccionaron publicaciones ni se verificó stock en este trabajo.
5. Si no hay actualización fiable, mostrar “Consultar precio” en lugar de un importe fijo. Revisar periódicamente enlaces, disponibilidad y cambios de modelo. No afirmar “más barato” sin comparación vigente.
6. Si hay afiliación, informar la relación de manera visible y etiquetar los enlaces remunerados con `rel="sponsored"`. Google indica cómo tratar [enlaces de afiliados](https://developers.google.com/search/blog/2021/07/link-tagging-and-link-spam-update). Usar enlaces generados por la cuenta autorizada; no inventar identificadores, comisiones ni condiciones del programa.
7. Medir `click_ml` con página, posición del botón, categoría, modelo y destino. Separar clics salientes de ventas: la compra y comisión solo se confirman con el reporte disponible en la cuenta de afiliación.

Fórmulas de gestión, sin supuestos inventados: **tasa de salida = sesiones orgánicas con al menos un clic a ML / sesiones orgánicas de la página**; **ingreso por 1.000 sesiones = comisiones confirmadas atribuibles / sesiones orgánicas × 1.000**, solo si existe atribución compatible. Contar sesiones únicas para que varios clics de una persona no inflen la tasa.

Para maximizar ingresos hay que medir tráfico útil, clics y comisiones conjuntamente. Las páginas de consumibles pueden tener más visitas pero tickets distintos a las de máquinas; no está demostrado cuál dejará más dinero.

## Enlazado interno y contenido que merece publicarse

- La home o categoría de herramientas enlaza a 01. El hub 01 enlaza a tipos, medidas, marcas y 05. Cada artículo tiene un enlace de vuelta a su guía principal.
- 05 enlaza a flap, desbaste, metal, cerámica, porcelanato, alambre, hormigón, diamantados y ladrillo.
- 02 enlaza a 06 cuando compara tareas de precisión; 06 a compresores cuando explica neumática. Esos enlaces solo se activan cuando la página de destino existe.
- Las guías de marcas enlazan a 13 o 15 según la elección; las guías de trabajo enlazan a los discos apropiados y a 18. La página 30 deriva a sierras y lijadoras cuando corresponda.
- Evitar publicar la misma tabla extensa en diez artículos. Las fichas técnicas pueden compartir datos verificables, pero el análisis debe responder a la decisión propia de cada página.
- Publicar fotografías y pruebas originales cuando existan. Si no se probó una máquina, presentarla como comparación documental y declarar las fuentes. No inventar experiencia, mediciones, opiniones ni puntuaciones.

Google recomienda aportar evidencia, diferencias, ventajas y limitaciones en las [reseñas de calidad](https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews). Sus políticas también describen la [afiliación con poco valor añadido y el abuso de contenido a escala](https://developers.google.com/search/docs/essentials/spam-policies). La implicación para este proyecto es aportar tablas de compatibilidad, comparación propia y criterios útiles en cada URL; copiar el catálogo de ML y agregar botones no alcanza.

Las guías de uso deben citar manuales del equipo y del accesorio, con revisión de alguien competente. La arquitectura no autoriza a recomendar cualquier disco por diámetro: deben verificarse montaje, RPM, material y uso admitido. Este informe propone contenidos, no instrucciones operativas de corte.

## Qué medir después y cuándo ampliar

Primera lista de consultas presentes en el archivo base a consultar en Semrush: `amoladora angular`, `amoladora black decker`, `amoladora grande`, `amoladora gamma`, `amoladora total`, `amoladora metabo`, `amoladora milwaukee`, `amoladora hamilton`, `amoladora dowen pagio`, `disco diamantado`, `tipos de discos para amoladora`, `disco de lija para amoladora`, `para que sirve una amoladora`, `como usar una amoladora para cortar hierro`, `como cortar porcelanato con amoladora`, `amoladora para madera`, `disco para cortar madera`, `como lijar madera con amoladora`, `amoladora de banco lusqtoff`, `mini amoladora`.

Consultar además las formulaciones editoriales sin métrica: `amoladora 115 o 125`, `como usar una amoladora`, `amoladora recta electrica o neumatica`, `disco flap o desbaste`. Son propuestas de investigación, no datos ya presentes o medidos que se den por confirmados.

Registrar para cada consulta volumen, KD, país, fecha y composición real de resultados. No completar faltantes con cero ni heredar KD de la keyword parecida. Las búsquedas de seguridad pueden ser necesarias por utilidad, aunque su volumen sea bajo.

En Search Console revisar consulta/página, indexación, impresiones, clics y CTR. Si una página recibe consultas específicas relevantes, primero mejorar la sección correspondiente. Crear una URL nueva solo si responde una necesidad diferente, puede aportar evidencia propia y la separación no duplica páginas existentes. Si dos páginas compiten por lo mismo, ajustar alcance o consolidar tras evaluar rendimiento; no borrar por una semana sin visitas.

Antes de publicar: verificar sitemap con URLs canónicas e indexables, respuesta 200, enlaces internos accesibles, títulos únicos y renderizado móvil. No se auditó el sitio real porque no se facilitó dominio ni implementación; no se afirma que esas condiciones estén cumplidas.

## Anexo: trazabilidad de las 59 consultas Semrush

La asignación conserva una única URL por consulta: 56 consultas se integran en las 30 páginas planificadas, una apunta a la guía específica de corte ya existente y dos se posponen. Se mantiene cada volumen y KD original; el mapping no afirma equivalencia técnica entre modelos. Origen A = `semrush_amoladoras.csv`; origen B = `semrush_consulta_adicional.csv`.

| Keyword exacta | Volumen | KD | Origen | Página / decisión |
|---|---:|---:|---|---|
''')
for r in allsem:
    label=f"{r['page_id']:02} · {r['decision']}" if r['page_id'] else r['decision']
    parts.append(f"| {r['keyword']} | {r['volume']} | {r['kd']} | {'A' if r['source']=='semrush_amoladoras.csv' else 'B'} | {label} |\n")
parts.append('''
## Archivos fuente y alcance

- [Base de keywords](C:/Users/joaqu/Desktop/keywords/keywords_amoladora.csv).
- [Semrush amoladoras](C:/Users/joaqu/Desktop/keywords/semrush/semrush_amoladoras.csv).
- [Semrush consultas adicionales](C:/Users/joaqu/Desktop/keywords/semrush/semrush_consulta_adicional.csv).

Los archivos fuente se conservaron sin cambios. Se procesó toda la base para normalización y cruce, se revisaron las consultas de mayor volumen y las familias informativas, y se asignaron editorialmente las 59 consultas medidas. No se adjudicó una URL definitiva a cada una de las 4.892 consultas normalizadas: hay ruido, productos ajenos y variantes que requieren validación. Las propuestas de este informe reemplazan el mapa provisional anterior únicamente para planificar este grupo, sin modificar aquellos documentos.
''')
report=''.join(parts)
(OUT/'plan-seo-amoladoras.md').write_text(report,encoding='utf-8')
assert report.count('**Title:**')==30
assert report.count('**H1:**')==30
print('VERIFICADO: 30 páginas; 18 + 12; 59 consultas medidas; 56 asignadas, 1 a URL existente y 2 pospuestas; titles/H1/URLs únicos:',len({p['title'] for p in pages}),len({p['h1'] for p in pages}),len({p['url'] for p in pages}))
print('Informe:',OUT/'plan-seo-amoladoras.md')
