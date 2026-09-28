# Estado de revisión editorial

Fecha del inventario: 27/09/2026.

| Sección | Guías sin revisión documentada |
| --- | ---: |
| Amoladoras | 0 |
| Compresores | 0 |
| Generadores | 0 |
| Hidrolavadoras | 0 |
| Sierras | 0 |
| Soldadoras | 0 |
| Soldadura electrónica | 0 |
| Taladros | 0 |
| **Total pendiente** | **0** |

Hay 178 guías revisadas: 29 de sierras, 23 de taladros, 25 de amoladoras, 23 de compresores, 21 de generadores, 23 de hidrolavadoras, 29 de soldadoras y cinco de soldadura electrónica. Las guías separan variantes exactas, calculan diferencias derivadas de datos publicados y documentan límites entre fichas, manuales y catálogos.

Para publicar una guía, verificar cada afirmación técnica contra una ficha de modelo o una fuente técnica pertinente, registrar qué dato respalda cada enlace, corregir discrepancias, explicar los datos ausentes, agregar valor de decisión propio y registrar la revisión documental realizada por su autor, Joaquín Vallasciani. No se atribuye un revisor independiente. El frontmatter requiere `reviewed`, `published: true`, `research_type`, `physical_test`, `specifications_contrasted`, `buyer_opinions`, `primary_sources`, `information_asset` y `asset_status: verificado`. El cuerpo requiere `## Fuentes consultadas` y las etiquetas «Dato verificado» y «Análisis TallerLab». Estos son controles mínimos de estructura: la lectura editorial debe comprobar que las fuentes respaldan realmente cada cifra.

La [matriz de las 178 URL](estado-editorial-178.csv) se regenera con `python auditar_publicacion.py`. El [inventario de afirmaciones](afirmaciones-178.csv) se regenera con `python inventariar_afirmaciones.py`: toda afirmación sin etiqueta revisada queda clasificada conservadoramente como `DESCONOCIDO`. Ambos son instrumentos editoriales, no certificaciones de calidad.

La pasada masiva inicial modificó los 176 borradores existentes: añadió estado de evidencia, metadatos de transparencia, una matriz de comprobación específica basada en los datos que ya presenta cada página, referencias disponibles o ausencia explícita de ellas, y enlace al hub. Retiró 84 recuadros «Regla de taller» sin prueba documentada y tres secciones de opiniones sin muestra identificable. El respaldo previo está en `respaldo-borradores-antes-transformacion.zip`. En ese corte, 84 borradores seguían pendientes; los lotes documentados a continuación cerraron la revisión de las 178 URL inventariadas.

El cuarto lote cerró diez guías de taladros: inalámbricos Bosch, DeWalt y Einhell; Stanley, BLACK+DECKER y Milwaukee; guía general de taladros inalámbricos; atornilladores de impacto DeWalt y general; y taladros percutores inalámbricos. Las comparativas priorizan modelo/código, función, mandril, torque y límites del kit según documentación primaria. Se identificaron expresamente mercados/regiones distintos cuando la ficha no prueba disponibilidad o garantía argentina.

El quinto lote cerró diez guías adicionales de taladros: rotomartillos general, Bosch, DeWalt y Einhell; taladro percutor; brocas para cerámica y porcelanato; Forstner de 35 mm; escalonadas; y atornillador para placas de yeso. Las tablas distinguen datos de modelos concretos y sus límites de mercado, encastre, diámetro, espesor o peso. No se documentaron pruebas físicas ni opiniones de compradores.

El sexto lote cerró las tres guías restantes de taladros —combo, Lusqtoff inalámbrico y taladro de banco— y siete guías de amoladoras: selección general, 7 pulgadas, 9 pulgadas, banco, DeWalt, disco de corte y disco de desbaste. La comparación del combo se basa en la ficha oficial Lusqtoff KATL-9BK; los demás kits comerciales quedan señalados como anuncios con especificaciones pendientes. Las guías de amoladoras atribuyen las especificaciones a fabricantes y aclaran diferencias de mercado, variantes y límites de uso. Taladros queda sin borradores pendientes y amoladoras conserva 16.

El séptimo lote cerró otras diez guías de amoladoras: discos segmentados, flap, cerámica, vidrio y guía general; además de Dowen Pagio, Gamma, inalámbricas, INGCO y Lusqtoff. Las matrices separan aplicaciones de corte, desbaste y terminación, y cotejan accesorios y herramientas por código. Las fichas INGCO consultadas son de distintos mercados y no confirman disponibilidad argentina; la guía de vidrio deja como desconocida cualquier compatibilidad no especificada por fabricante. Amoladoras conserva seis borradores.

La comparativa de 50 litros incluye una matriz de uso, caudal, potencia, peso, batería, garantía, repuestos, precio y consumibles. La página [Cómo trabajamos](/como-trabajamos/) explica las reglas generales. Ninguna URL publicada afirma una prueba propia ni muestra `Product`/`Review` para una reseña individual inexistente. Incorporar ese marcado únicamente cuando una página visible evalúe un producto concreto con pros y contras sustentados; no generar puntuaciones ni mezclar opiniones externas como propias.

El octavo lote cerró las seis guías restantes de amoladoras —Makita, recta, Skil 9004, Stanley, Total y velocidad variable— y cuatro de compresores: 100 L, 12 V de doble pistón, 200 L y 24 L. Se compararon modelos por código y se calcularon diferencias solo cuando las fichas ofrecían magnitudes compatibles. La guía Makita distingue GA4534 de GA4530; Stanley y Total muestran diferencias entre códigos/mercados; el Gadnic AV000012 presenta caudales divergentes en su propia ficha; y LC-30200 tiene cifras de caudal distintas entre catálogos de años diferentes. La guía de 24 L corrige LC-2024: la ficha Lüsqtoff indica 40 L. Se retiraron afirmaciones heredadas de ciclo, FAD, ruido, vida útil, seguridad eléctrica y rendimiento que no contaban con respaldo suficiente. Amoladoras queda sin pendientes; compresores conserva 18.


El noveno lote cerró diez guías de compresores: aceite, acoples rápidos, BTA 25 L, filtros, Gamma 50 L, infladores a batería y portátiles, kits neumáticos/aerografía y Lüsqtoff 100 L. Las páginas comparan datos con fuentes primarias, marcan las diferencias entre ficha y manual, agregan un activo documental y el bloque común de transparencia (análisis documental, sin prueba física, fuentes primarias sí, sin reseñas analizadas, revisión 27/09/2026). La guía de lubricación evita grados universales; la de Gamma deja visible 2 HP frente a 2,5 HP según campo del fabricante; la de Lüsqtoff registra pesos discordantes y no completa la ficha LCS100-8 sin evidencia primaria suficiente. Compresores conserva ocho borradores pendientes.

El décimo lote cerró las ocho guías restantes de compresores —Lüsqtoff 50 L, mangueras, aerografía, auto, pintura, pistolas, sin aceite y Stanley— y dos guías de generadores: gas y nafta. Los activos comparan caudales de manguera según tabla Parker, consumo de aire de pistolas BTA y admisión de compresores con sus límites de medición; separan generadores diseñados para gas de kits de conversión; y dejan visibles discrepancias de cilindrada/peso del LGI3.8-8 y potencia del LG3000. Compresores queda sin borradores; generadores conserva 19. Se regeneraron la matriz editorial y el inventario de afirmaciones.

El undécimo lote cerró diez guías de generadores: chicos, comparativa general, diésel, estaciones portátiles, Gamma 6500, Gamma 950, gama Gamma, Honda 6500, gama Honda y Hyundai. Las tablas comparan potencia nominal/máxima solo cuando las fichas lo indican; calculan escenarios de energía portatil con Wh/W como estimaciones ideales; y dejan documentadas la diferencia de rotulación del Gamma 950, la discontinuidad del Gamma 6500V, las variantes Honda EG/EZ6500CXS y los campos ausentes en fichas comerciales diésel. Generadores conserva nueve borradores pendientes.

El duodécimo lote cerró las nueve guías restantes de generadores —inverter, Lüsqtoff, monofásicos, Niwa, para casa, portátiles, precios, silenciosos y trifásicos— y la guía de hidrolavadoras de 150 bar. Los activos comparan potencia nominal y máxima sin convertir kVA a kW, preservan diferencias entre fichas y manuales, y separan presión máxima de presión de trabajo. En la guía de precios, los importes son PVP oficiales capturados el 27/09/2026, no precios de mercado ni cotizaciones. Generadores queda sin borradores; hidrolavadoras conserva 21.

El decimotercer lote cerró diez guías de hidrolavadoras: 200 bar, comparativa general, BLACK+DECKER, Bosch, Einhell, Gamma (guía de marca, 130 y 150) y Hyundai, además de limpieza de aire acondicionado. Las tablas distinguen presión admisible, de servicio y máxima cuando las fuentes lo especifican; comparan códigos concretos y señalan los catálogos extranjeros. La guía de aire acondicionado enlaza instrucciones de Carrier y Daikin, y limita el dato de 3–5 barg al serpentín Cu/Al de la familia UATYA. Hidrolavadoras conserva 11 borradores.

El decimocuarto lote cerró diez guías de hidrolavadoras: inalámbricas, Kärcher K2, K3, K4, K5 y comparativa de marca, Lüsqtoff, Niwa, para autos y profesionales. Se compararon fichas y manuales por SKU, distinguiendo presión nominal/máxima, caudal y accesorios; los kits regionales se dejaron sin equivalencia cuando la documentación no la demuestra. La guía inalámbrica registra que Bosch publica 45 minutos para una configuración de batería concreta, mientras la ficha Lüsqtoff no informa autonomía. Hidrolavadoras conserva un borrador.


El decimoquinto lote cerró la guía de hidrolavadoras STIHL y nueve guías de soldadura: hub general, alambre flux, alambre MIG, carro para soldadora, electrodos E6013/E7018, inoxidables y fundición, y ESAB HandyArc 162i. Los activos comparan modelos/códigos y reproducen rangos de fichas primarias, dejando explícitos los límites de región y producto. Se separaron clasificación de consumible, amperaje por diámetro y ciclo de trabajo de la fuente; no se formularon procedimientos ni se atribuyó experiencia de uso. Hidrolavadoras queda sin borradores; soldadoras conserva 19. Total: 154 publicadas y 24 borradores.

El decimosexto lote cerró diez páginas: guía de equipos ESAB, guantes de soldar, soldadoras Lüsqtoff Iron 100 e Iron 250, SML120-8D, SML130-7, hub Lusqtoff, máscara ST-1X, guía general de máscaras fotosensibles y MIG Flux Lüsqtoff. Las comparativas distinguen equipos y códigos, registran datos faltantes y muestran discrepancias entre nombres comerciales, fichas, manuales y catálogos sin trasladar valores entre variantes. Soldadoras conserva nueve borradores; soldadura electrónica conserva cinco. Total: 164 publicadas y 14 borradores.


El decimoséptimo lote cerró nueve guías de soldadoras y la primera de soldadura electrónica: MIG sin gas, soldadora para aluminio, soldadura de punto, Dogo 180, inverter 160 A y 200 A, MIG con gas, TIG AC/DC y TIG general, y estación de soldadura/retrabajo. Las tablas identifican modelos y condiciones documentadas, contrastan diferencias de proceso y ciclo, y dejan como desconocidos los parámetros que no aparecen en fuentes primarias. Soldadoras quedó sin borradores; soldadura electrónica conservaba cuatro. Total al cierre: 174 publicadas y 4 borradores.


El decimoctavo y último lote cerró las cuatro guías restantes de soldadura electrónica: Gadnic 878D, Yihua 898D, kits de soldador de estaño y soportes con lupa. Las tablas comparan modelos y accesorios declarados por fabricantes, y preservan discrepancias concretas: Gadnic presenta 750 W en su texto comercial y 370 W en el cuadro técnico; Yihua agrupa variantes con distinta potencia; los kits y soportes se comparan con sus límites de tensión, mercado y datos ausentes. No se atribuyeron pruebas físicas ni opiniones. Total final: 178 guías revisadas y 0 pendientes.
