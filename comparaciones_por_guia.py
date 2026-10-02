"""Selecciones editoriales explícitas: cada ampliación responde al contenido de su guía."""
from fotos_productos import photo_for

def documented(brand, model, source, use, power, specs, warning='', includes='Confirmá configuración y accesorios con el distribuidor.'):
    return dict(brand=brand, model=model, source=source, source_type='fabricante',
                use=use, power=power, specs=specs, includes=includes, warning=warning,
                evidence_label='Ficha de fabricante; disponibilidad local a confirmar',
                cta='Ver ficha del fabricante')

MODELS = {
 'aquatak36': documented('Bosch','UniversalAquatak 36V-100 · 06008C7002','https://www.bosch-diy.com/de/de/p/universalaquatak-36v-100-06008c7002','Limpieza móvil con modos ECO y High','36 V POWER FOR ALL',['Hasta 100 bar; trabajo no separado en la ficha','Hasta 3,1 L/min; autosucción hasta 0,5 m','Manguera de presión de 4 m; batería 4 Ah y cargador'],'Referencia europea: confirmá código, accesorios de aspiración y disponibilidad local.'),
 'ghp220': documented('Bosch','GHP 220 · 0600910EH0','https://www.bosch-professional.com/ar/es/products/ghp-220-0600910EH0','Patios y suciedad adherida; motor de inducción','220 V',['101,2 bar de trabajo / 151,8 bar máximos','6,1 L/min nominales / 7,4 L/min máximos','Manguera PVC de 8 m; motor de inducción']),
 'ghp450': documented('Bosch','GHP 4-50 · 0600910FH0','https://www.bosch-professional.com/ar/es/products/ghp-4-50-0600910FH0','Mayor alcance y bomba de cuatro pistones','220 V',['115,5 bar de trabajo / 173,2 bar máximos','7,3 L/min nominales y máximos','Manguera reforzada de 9 m; motor de inducción']),
 'hl1008': documented('Lüsqtoff','HL100-8','https://lusqtoff.com.ar/2023/uploads/Productos/4.%20HIDROLAVADORAS/HL100-8/MANUAL/Manual%20HL100-8-pdf%20curvas_compressed.pdf','Equipo doméstico de 100 bar de trabajo','220 V / 50 Hz',['100 bar de trabajo / 150 bar permitidos','6 L/min de trabajo / 7,5 L/min máximos','2.000 W; cotejá manguera y kit de la unidad'],'No equivale al HL-150: el código y la imagen corresponden al manual HL100-8.'),
 'lgi38': documented('Lüsqtoff','LGI3.8-8','https://www.lusqtoff.com.ar/ver-producto/LGI3.8-8','Escalón inverter de 3–4 kW','50 Hz; confirmar tensión en placa',['3,5 kW nominales / 3,8 kW máximos','Inverter; arranque manual','28 kg; tanque de 8 L'],'El campo Tensión de la ficha web imprime 50 Hz; no acredita voltaje. No corresponde al LGIS3.8-8 motosoldadora.'),
 'lgi11': documented('Lüsqtoff','LGI11.0-9','https://www.lusqtoff.com.ar/ver-producto/LGI11.0-9','Escalón inverter de mayor capacidad','220 / 380 V; 50 Hz',['10 kVA nominales / 11 kVA máximos','Inverter; arranque eléctrico; PF 1,0 / 0,8','86 kg; tanque de 35 L'],'Confirmá potencia por salida, reparto de fases y corriente de arranque admisible para tus cargas.'),
 'fd186kit': documented('Fengda','FD-186K','https://www.airbrush-fengda.de/fen-FD186K','Kit de doble acción con compresor y limpieza','Confirmar variante 220–240 V / 50 Hz',['BD-130 de doble acción; boquilla 0,3 mm','Compresor FD-186; 23 L/min sin presión asociada','Manguera 1,8 m; soporte, frascos y limpieza'],'La ficha presenta también 110–120 V / 60 Hz; confirmá tensión y contenido de la oferta local.'),
 'as186': documented('Fengda','AS-186','https://www.airbrush-fengda.de/Hobby-Kompressor-mit-dem-Druckbehaelter-Fengda-AS-186','Aerografía ocasional con tanque de 3 L','220–240 V / 50 Hz',['Tanque 3 L; 20–23 L/min sin carga','Ciclo automático de 3 a 4 bar; salida G1/8','Regulador, filtro, manómetro; 47 dB a 1 m'],'El proveedor excluye uso continuo industrial; confirmar distribución, garantía y variante local.'),
 'as196': documented('Fengda','AS-196','https://www.airbrush-fengda.de/Hobby-Kompressor-mit-dem-Druckbehaelter-Fengda-AS-196','Aerografía ocasional con doble pistón','220–240 V / 50 Hz',['Tanque 3,5 L; 35–40 L/min sin carga','Modo automático entre 3 y 4 bar; salida G1/8','Regulador, filtro y manómetro; protección térmica'],'El segundo modo hasta 6 bar no tiene corte automático. No acredita trabajo continuo ni caudal útil a presión.'),
 'paaschehkit': documented('Paasche','H-100D','https://paascheairbrush.com/products/h-100d','Kit de acción simple y alimentación por succión','Confirmar tensión y frecuencia',['H-3AS de acción simple; mezcla externa','D500SR con regulador y trampa de humedad','Manguera 6 pies; adaptador 1/8 BSP; limpieza AC-7'],'La lista de contenido y la descripción general discrepan en cabezales. Confirmá paquete, tensión y disponibilidad local.'),
 'paaschetgkit': documented('Paasche','TG-100D','https://paascheairbrush.com/products/tg-100d','Kit de doble acción y alimentación por gravedad','Confirmar tensión y frecuencia',['TG-3AS de doble acción; mezcla interna','D500SR con regulador y trampa de humedad','Manguera 6 pies; adaptador 1/8 BSP; limpieza AC-7'],'La lista de contenido enumera cabezales 1 y 3; la tabla describe también el 2. Confirmá cabezales, tensión y disponibilidad local.'),
 'lc40200doc': documented('Lüsqtoff','LC40200-8','https://lusqtoff.com.ar/productos/LC40200-8','Reserva de 200 L y bomba tricilíndrica a correa','380 V / 50 Hz trifásica',['200 L; 130 kg','458 L/min en ficha actual; condición no indicada','3.000 W / 4 HP; máx. 115 PSI']),
 'schulz200': documented('Schulz','MAX CSV 20/200 · 922.9303-0','https://www.schulz.com.br/pt_BR/produtos/ver/922.9303-0','Referencia de dos etapas y régimen intermitente','220 V / 60 Hz monofásica',['172,8 L; 133,1 kg netos','566 L/min de desplazamiento teórico; no FAD','5 cv / 3,7 kW; máx. 175 PSI'],'Ficha brasileña de 60 Hz; no acredita compatibilidad con 50 Hz ni disponibilidad argentina. Exigí variante y placa para la instalación local.'),
 'lcvs': documented('Lüsqtoff','LC-2550VS','https://lusqtoff.com.ar/ver-producto/LC-2550VS','Alternativa vertical sin aceite de 50 L','220 V / 50 Hz',['50 L; sin aceite','230 L/min; condición de medición no indicada','1.750 W / 2,5 HP; 72 dB sin condiciones acústicas']),
 'lcs50': documented('Lüsqtoff','LCS50-8','https://lusqtoff.com.ar/productos/compresor-de-aire-sin-aceite-50l','Alternativa actual sin aceite de 50 L','220 V / 50 Hz',['50 L; sin aceite','105 L/min; condición de medición no indicada','1.600 W / 2 HP; 30 kg']),
 'lcs100': documented('Lüsqtoff','LCS100-8','https://lusqtoff.com.ar/productos/LCS100-8','Reserva de 100 L con bomba sin aceite','220 V / 50 Hz',['100 L; sin aceite','255 L/min; condición de medición no indicada','1.280 W × 3; 50,5 kg netos']),
 'emona200': documented('Emona','F 200 · SKU 49292','https://emona.com.ar/catalogo/agua-fria/hidrolavadora-emona-f-200-bar-21-lts-x-min-trif-10-hp-completa-caccesorios', 'Agua fría con mayor caudal publicado','380 V trifásica', ['200 bar de salida; condición nominal/máxima no separada','21 L/min publicados; confirmar caudal sostenido','Interpump WS 202; manguera de 10 m'], 'Confirmá ciclo de trabajo, suministro mínimo de agua y versión fija o con carrito. La ficha no publica precio ni stock.', 'La ficha lista manguera de 10 m, lanza, pico, pistola automática y salvamotor; confirmá configuración cotizada.'),
 'gamma50': documented('Gamma','G2802AR','https://www.gammaherramientas.com.ar/producto/compresor-de-50-litros/', 'Reserva de 50 L para trabajo intermitente','220 V', ['50 L','203 L/min de desplazamiento; no FAD','2,5 HP según manual'], 'La página comercial y el manual discrepan en potencia. Confirmá variante y FAD antes de elegir.'),
 'einhell50': documented('Einhell','TE-AC 270/50 Silent','https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/', 'Comparar caudal de salida y ruido publicado','220–240 V', ['50 L','135 L/min a 4 bar; 98 L/min a 7 bar','1.650 W']),
 'einhell90': documented('Einhell','TE-AC 430/90/10','https://www.einhell.com.ar/p/4010800-te-ac-430-90-10/', 'Preselección para pistolas de mayor consumo','220–240 V', ['90 L','210 L/min a 4 bar; 200 L/min a 7 bar','3.000 W'], 'La salida a 4 bar no valida una pistola que requiere otra presión; comprobá FAD y ciclo en su punto de trabajo.'),
 'stanley24': documented('Stanley Fatmax','FHY227/10/24V','https://www.mecafer.com/compresseurs/compresseur-vertical-futura-lubrifie-24l-2hp', 'Formato vertical de 24 L','Confirmar variante eléctrica', ['24 L','190 L/min a 3 bar; 172 L/min a 7 bar','Cabeza lubricada de por vida'], 'Ficha europea; no se confirmó disponibilidad argentina. No equivale al SKU FCCC404STC005.'),
 'stanley50': documented('Stanley Fatmax','FHY227/10/50V','https://www.mecafer.com/compresseurs/compresseur-vertical-futura-lubrifie-50l-2hp', 'Más reserva con el mismo caudal que FHY227 de 24 L','Confirmar variante eléctrica', ['50 L','190 L/min a 3 bar; 172 L/min a 7 bar','Cabeza lubricada de por vida'], 'Ficha europea; disponibilidad, tensión y garantía argentinas a confirmar.'),
 'stanley100': documented('Stanley','D270/10/100V','https://www.mecafer.com/compresseurs/compresseur-vertical-100l-25hp', 'Reserva de 100 L y bomba sin aceite','Confirmar variante eléctrica', ['100 L','155 L/min a 3 bar; 135 L/min a 7 bar','Sin aceite'], 'Ficha europea; disponibilidad argentina a confirmar. Más tanque no implica mayor caudal.'),
 'gamma150': documented('Gamma','150 Elite · G2514AR','https://www.gammaherramientas.com.ar/producto/hidrolavadora-150-elite/', 'Comparar el salto desde Gamma 130','220 V / 50 Hz', ['100 bar de servicio / 150 bar admisibles','400 L/h publicados','Manguera de 5 m; 1.800 W'], 'No corresponde a Master Wash ni a Premium Wash: verificá G2514AR en la placa.'),
 'k5base': documented('Kärcher','K5 · 9.398-295.0','https://www.kaercher.com/ar/home-garden/hidrolavadora/k-5-93982950.html', 'K5 base con manguera de 6 m','Cable', ['2.100 PSI publicados; ≈145 bar convertidos','420 L/h en ficha Kärcher','Manguera de 6 m'], 'La publicación afiliada pendiente no identifica esta variante; este enlace es a la ficha del código exacto.'),
 're90': documented('STIHL','RE 90','https://www.stihl.com.ar/es/p/hidrolavadoras-re-90-141963', 'Ocasional con ruedas y más alcance que RE 80 X','220–240 V', ['10–100 bar publicados','Hasta 440 L/h según catálogo local','Manguera de 6 m'], 'Se compara la referencia argentina RE020114544; no se utiliza la oferta pendiente que anuncia 60 Hz.'),
 're110': documented('STIHL','RE 110','https://www.stihl.com.ar/es/ap/re-110-81523', 'Motor de inducción y mayor alcance','Cable', ['10–110 bar de trabajo según catálogo local','440 L/h según catálogo local','Manguera de 7 m; 17,6 kg'], 'Confirmá referencia 49500114529 y manual de la unidad.'),
 're120': documented('STIHL','RE 120','https://www.stihl.com.ar/es/p/hidrolavadoras-re-120-81512', 'Equipo doméstico más equipado','Cable', ['160 bar máximos; trabajo no publicado','Hasta 480 L/h','Manguera de 8 m; 20 kg']),
 're145': documented('STIHL','RE 145','https://www.stihl.com.ar/es/p/hidrolavadoras-re-145-167165', 'Cabezal de latón y chasis plegable','Cable', ['160 bar máximos; trabajo no publicado','Caudal no informado en la ficha consultada','Manguera de 8 m; 19,6 kg']),
 're150': documented('STIHL','RE 150','https://www.stihl.com.ar/es/p/hidrolavadoras-re-150-109158', 'Uso exigente y segmento semiprofesional','Cable', ['120 bar de trabajo / 180 bar máximos','Hasta 468 L/h','30 kg; confirmar largo de manguera']),
 'comet150': documented('Comet','K 250 10/150 Classic · C2582AR','https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-k-250-10-150-classic/', 'Agua fría con instalación monofásica','230 V monofásica', ['150 bar máximos; confirmar presión de trabajo','10 L/min máximos','Bomba de tres pistones cerámicos'], 'Pedí ciclo continuo, caudal de trabajo y servicio de bomba para tu jornada.'),
 'comet190': documented('Comet','K 250 TSR 13/190 T Classic · C2583AR','https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-k-250-tsr-13-190-t-classic/', 'Mayor caudal con red trifásica','400 V trifásica', ['190 bar máximos; confirmar presión de trabajo','13 L/min máximos; entrada mínima 970 L/h','Agua fría; bomba de pistones cerámicos'], 'Requiere verificar suministro de agua e instalación trifásica; no se reemplaza por un adaptador.'),
 'cometcaliente': documented('Comet','KM Extra 8.16 · C2586AR','https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-km-extra-8-16-16-200-t/', 'Evaluar agua caliente para grasa y aceite','400 V trifásica', ['Presión máxima depende de la temperatura','15 L/min nominales / 16 L/min máximos','Agua caliente y vapor; entrada mínima 20 L/min'], 'Revisá presión por temperatura, combustible y mantenimiento de la caldera.'),
 'c10': documented('WIPCOOL','C10','https://www.wipcool.com/portable-hvac-ac-condenser-evaporator-coils-service-cleaning-machine-product/', 'Enjuague HVAC con presión seleccionable','230 V / 50–60 Hz, o variante 100–120 V', ['3–5 / 7–10 bar de trabajo','4 L/min máximos','Manguera de salida de 5 m; 3,7 kg'], 'No tiene vapor como C30S. Usá solo presión, boquilla y método admitidos por el fabricante del aire acondicionado.'),
 'dch133': documented('DeWalt','DCH133B','https://www.dewalt.com/en-us/product/dch133b/20v-max-1-brushless-cordless-sds-plus-d-handle-rotary-hammer-tool-only', 'Más energía declarada en la misma plataforma','20 V MAX', ['SDS Plus','2,6 J','Herramienta sola; batería y cargador aparte'], 'Ficha estadounidense: confirmá código, kit y garantía local.'),
 'd25333': documented('DeWalt','D25333K-QS','https://www.dewalt.fr/fr-fr/produit/d25333k-qs/perforateur-burineur-sds-plus-950-w-35-j', 'Trabajo con cable y mayor capacidad publicada','230 V con cable', ['SDS Plus','3,5 J; 950 W','4–30 mm en hormigón según ficha QS'], 'Variante europea QS; no trasladar capacidades o tensión a otro sufijo regional.'),
 'hogert': documented('Högert','HT6D323','https://en.hoegert.com/product/step-drill-4-32-mm/', 'Más diámetros para chapa','Taladro en modo rotativo', ['4–32 mm','Chapa de hasta 4 mm según fabricante','HSS; comprobar los diámetros de los escalones']),
 'tigbasic': documented('ESAB','TIG Basic · 0700500460','https://esab.com/ae/mea_en/products-solutions/product/ppe-safety/hands-and-body/tig-basic-glove/', 'Comparar destreza y construcción para TIG','EPP; elegir talle', ['160 g publicados','Cuero vacuno dividido y piel de cabra; sin forro','EN 12477 Type A según ficha'], 'El nombre TIG no implica Type B. Cotejá marcado completo y protección requerida por tu tarea.'),
 'exl': documented('ESAB','Heavy Duty EXL · 0700500432 / 0700500433','https://esab.com/ae/mea_en/products-solutions/product/ppe-safety/hands-and-body/heavy-duty-exl/', 'Construcción robusta declarada para MIG/MMA','EPP; elegir talle', ['330 g publicados','Cuero vacuno dividido grueso; costuras Kevlar','EN 12477 Type A según ficha'], 'La ficha extranjera no confirma talle, stock ni certificación del par recibido.'),
}

# URL comerciales ya suministradas. No se crean referidos ni se confirman stocks.
EXISTING = {
 'lgi11':'https://meli.la/25pcKkk',
 'lcvs':'https://meli.la/1Rjz39S', 'lcs50':'https://meli.la/27nVFRy', 'lcs100':'https://meli.la/21fBeVj',
 'lapl36':'https://meli.la/1YbCQgP', 'hypresso18':'https://meli.la/1TRSxkF',
 'k4base':'https://meli.la/2SvkJCm',
 'ghp180':'https://meli.la/1wNMwSL', 'ghp200':'https://meli.la/1zrcYor',
 'n700':'https://meli.la/2dFtHcP', 'b2200':'https://meli.la/2MJE81D',
 'pektra980':'https://meli.la/2jcLSy1', 'konan800':'https://meli.la/19gLhpz', 'lg950':'https://meli.la/2oCYsWY',
 'gammainverter':'https://meli.la/1B4sjDN',
 'eu22':'https://meli.la/2AwxqaH', 'eu30':'https://meli.la/2X86187',
 'eg6500':'https://meli.la/1sxNfJ5', 'ez6500':'https://meli.la/2Kt6i6Y',
 'et12000':'https://meli.la/2WRqiZR', 'lgi55':'https://meli.la/1pJFrBq',
 'mcl150':'https://meli.la/2r8uZXD', 'gadnic9':'https://meli.la/2MHTmab',
 'av37':'https://meli.la/2aSkmx1', 'nictom':'https://meli.la/2Xv53zX',
 'pressito25':'https://meli.la/14u7fCt', 'pressito21':'https://meli.la/1iNDq73',
 'dmp180':'https://meli.la/2uRPKYD',
 'lc30200':'https://meli.la/2vfnWE7',
 'lc50kit':'https://meli.la/2FtyGQc', 'lc3550':'https://meli.la/21xNVUN',
 'lc30100':'https://meli.la/2r6QkaT', 'lc40100':'https://meli.la/1GRiWbV',
 'k2':'https://meli.la/2izv76H', 'k3':'https://meli.la/1LYmDeG',
 'k4pc':'https://meli.la/149NjG2', 'k5pc':'https://meli.la/1wCKV4R',
 'g130':'https://meli.la/2SuGMdL', 'hl120':'https://meli.la/1qPbvWX',
 'hl150':'https://meli.la/1X9cSf1', 're80':'https://meli.la/1wzSW2u',
 'npro':'https://meli.la/2ChQa9Z', 'c30s':'https://meli.la/2CieWYz',
 'lc50':'https://meli.la/2dyFK5e', 'bta25':'https://meli.la/14USeGB',
 'bta24':'https://meli.la/2kTMPof', 'bta50':'https://meli.la/1nobM6T',
 'stanleylocal':'https://meli.la/26gU4mL', 'einhell24':'https://meli.la/2NsPCBP',
 'lc0122':'https://meli.la/19aFAKp', 'gamma24':'https://meli.la/14tM2Xh',
 'bta50oilfree':'https://meli.la/1b6KCiM',
 'gsb550':'https://meli.la/18iubWD',
 'gsb18':'https://www.mercadolibre.com.ar/up/MLAU364309887?pdp_filters=item_id:MLA1755860026#origin=share&sid=share&wid=MLA1755860026&action=copy',
 'dch273':'https://meli.la/1uYbzCV', 'cyl9':'https://meli.la/2wKN4UX',
 'hex9':'https://meli.la/2XU7X44', 'boschstep':'https://meli.la/2TD7cMx',
 'heavyblack':'https://meli.la/2HuWpap',
}

def plan(models, reason):
    return dict(models=models, reason=reason)

PLANS = {
 '/hidrolavadoras/karcher-k4/': plan(['k3','k4base','k4pc','k5base'], 'Los cuatro códigos de la tabla: K3, K4 estándar, K4 Power Control y K5 base. Compará caudal, alcance y kit sin mezclar las dos K4.'),
 '/hidrolavadoras/inalambricas/': plan(['lapl36','aquatak36','hypresso18'], 'Las dos clases comparadas en la guía y la alternativa Einhell de presión media. Compará presión, autonomía y kit: Bosch usa 36 V; Einhell se ofrece sin batería ni cargador.'),
 '/hidrolavadoras/bosch/': plan(['ghp180','ghp200','ghp220','ghp450'], 'Los cuatro códigos argentinos de la guía: compará presión de trabajo, caudal nominal, largo de manguera y motor. GHP 220 y GHP 4-50 conservan ficha y foto oficiales mientras se completa su publicación de compra.'),
 '/hidrolavadoras/150-bar/': plan(['gamma150','hl1008','n700','b2200'], 'Los cuatro modelos de la tabla. El rótulo de 150 bar es máximo o permitido; compará presión de trabajo y caudal bajo la condición publicada. Gamma y HL100-8 tienen enlace documental y foto del modelo exacto.'),
 '/generadores/chicos/': plan(['pektra980','konan800','lg950'], 'Los dos modelos de la comparación y la alternativa LG950P desarrollada en la guía. Contrastá nominal, máximo, unidades y mezcla del manual propio; el Pektra conserva datos de vendedor.'),
 '/generadores/inverter/': plan(['eu22','gammainverter','eu30','lgi38','lgi55','lgi11'], 'Compará los cuatro modelos de la tabla y los dos inverter adicionales de la guía. Conservamos kW y kVA en sus unidades publicadas; el LGI5.5-8 necesita potencia nominal confirmada para dimensionar marcha.'),
 '/compresores/kits-aerografo/': plan(['fd186kit','paaschehkit','paaschetgkit'], 'Compará los tres paquetes completos de la tabla: acción simple por succión frente a doble acción por gravedad, compresor y accesorios incluidos. Son fichas documentales; tensión y disponibilidad argentina requieren confirmación.'),
 '/compresores/para-aerografo/': plan(['as186','as196'], 'Compará los dos Fengda de la guía por tanque, pistones, caudal sin carga y modos de control. No equivalen a kits con aerógrafo ni autorizan uso continuo.'),
 '/compresores/para-auto/': plan(['nictom','mcl150','gadnic9'], 'Compará batería integrada con dos equipos conectados a 12 V: corriente, controles, alcance y ciclo publicado. Los caudales sin presión asociada no forman un ranking de velocidad.'),
 '/compresores/inalambricos/': plan(['pressito25','pressito21','dmp180'], 'Los tres infladores de la tabla: compará plataforma, caudal a presión y salida de baja presión. Confirmá el contenido de cada SKU y las pausas de su manual.'),
 '/compresores/inflador-neumaticos-portatil/': plan(['gadnic9','mcl150','av37','dmp180','pressito25'], 'Los cinco modelos desarrollados: conexión directa a batería, conexión dual o batería de herramientas; alta presión y bomba separada de alto volumen cuando corresponde.'),
 '/compresores/12v-doble-piston/': plan(['mcl150','gadnic9','av37'], 'Compará conexión, corriente, corte automático, alcance y ciclo entre los tres modelos con publicación suministrada. El número de pistones no acredita caudal útil ni velocidad.'),
 '/compresores/200-litros/': plan(['lc30200','lc40200doc','schulz200'], 'Los tres modelos documentados en el artículo, con alimentación y frecuencia explícitas. El Schulz de 60 Hz requiere acreditar una variante compatible para compra local; tanque y caudal teórico no prueban rendimiento sostenido.'),
 '/compresores/lusqtoff-50-litros/': plan(['lc50','lc50kit','lc3550','lcvs','lcs50'], 'Las cinco variantes desarrolladas en la guía: básico, kits y dos alternativas sin aceite. Compará accesorios y mantenimiento; los caudales no tienen condiciones comunes de medición.'),
 '/compresores/lusqtoff-100-litros/': plan(['lc30100','lc40100','lcs100'], 'Correa lubricada, mando directo lubricado y sin aceite. Son los tres modelos de la guía; confirmá entrega de aire a presión y ciclo para la herramienta prevista.'),
 '/compresores/50-litros/': plan(['lc50','gamma50','einhell50'], 'Compará los tres modelos desarrollados en la guía: reserva, aire publicado y ruido. Desplazamiento y caudal de salida son datos distintos.'),
 '/compresores/bta-25-litros/': plan(['bta25','bta24','bta50'], 'La decisión es entre 25 L, 24 L sin aceite y más reserva de 50 L; duplicar tanque no aumenta por sí solo la producción de aire.'),
 '/compresores/stanley/': plan(['stanleylocal','stanley24','stanley50','stanley100'], 'Separá el SKU local de las referencias europeas: compará reserva, lubricación y salida a presión. Las fichas europeas no confirman stock argentino.'),
 '/compresores/para-pintar/': plan(['einhell24','einhell50','einhell90'], 'Tres escalones de tanque y caudal de salida. Ninguno queda validado para tu pistola sin cotejar presión, consumo, pérdidas y ciclo de trabajo.'),
 '/hidrolavadoras/stihl/': plan(['re80','re90','re110','re120','re145','re150'], 'Compará la gama eléctrica RE de la guía por alcance, peso y construcción; RCA a batería y RB a gasolina pertenecen a otros segmentos.'),
 '/hidrolavadoras/karcher-k5/': plan(['k5pc','k5base','k4pc'], 'Compará K5 base, K5 Power Control y K4 Power Control: cambian código, manguera, kit y caudal publicado.'),
 '/hidrolavadoras/karcher-k3/': plan(['k3','k2','k4pc'], 'Ubicá la K3 entre K2 Basic y K4 Power Control, como desarrolla la guía: frecuencia de uso, alcance y configuración.'),
 '/hidrolavadoras/gamma-130/': plan(['g130','gamma150'], 'Compará Gamma 130 con Gamma 150 por datos de trabajo, caudal y kit; no interpretes la presión máxima como sostenida.'),
 '/hidrolavadoras/gamma-150/': plan(['gamma150','g130'], 'Contrastá G2514AR con G2513AR para decidir si necesitás el escalón superior; son códigos concretos, con fichas y accesorios diferentes.'),
 '/hidrolavadoras/lusqtoff-hl-120/': plan(['hl120','hl150'], 'La alternativa desarrollada en esta guía es HL-150 eléctrica: compará presión de trabajo, caudal, alcance y contenido del kit.'),
 '/hidrolavadoras/profesionales/': plan(['comet150','comet190','cometcaliente','npro'], 'Compará configuraciones de agua fría monofásica, fría trifásica y caliente trifásica. Para la Niwa comercial también hay que acreditar caudal sostenido, régimen de trabajo e instalación.'),
 '/hidrolavadoras/200-bar/': plan(['comet190','cometcaliente','emona200'], 'Los tres equipos desarrollados en la tabla: Comet de agua fría, Comet con caldera y Emona F 200 de 21 L/min. Compará proceso, caudal e instalación; las fichas no usan la misma condición de presión.'),
 '/hidrolavadoras/hidrolavadora-para-aire-acondicionado/': plan(['c30s','c10'], 'Compará un equipo con vapor con una lavadora HVAC de enjuague. Ninguno habilita un método universal para todos los serpentines; seguí el procedimiento del aire acondicionado.'),
 '/taladros/percutores/': plan(['gsb550','gsb18'], 'Cable frente a batería para la tarea descrita: revisá código exacto, capacidad por material y costo del kit.'),
 '/taladros/rotomartillo-dewalt/': plan(['dch273','dch133','d25333'], 'Los tres SDS Plus de la guía: movilidad, energía declarada y cable. Las variantes estadounidenses y europeas requieren confirmar disponibilidad y garantía locales.'),
 '/taladros/brocas-ceramica/': plan(['cyl9','hex9'], 'CYL-9 para cerámica blanda frente a HEX-9 HardCeramic para baldosa dura: compará dureza admitida y modo de perforación, no solo diámetro.'),
 '/taladros/mechas-escalonadas/': plan(['boschstep','hogert'], '4–20 frente a 4–32 mm. Confirmá referencia Bosch: la oferta 2608597519 no hereda automáticamente las medidas del código 2608597524 de la tabla.'),
 '/soldadoras/guantes/': plan(['heavyblack','tigbasic','exl'], 'Compará los tres modelos ESAB desarrollados: construcción, peso, talle y marcado. La protección se verifica para el modelo y la tarea concretos.'),
}

# Datos de las fichas ya citadas en cada artículo. Se conserva cualquier
# advertencia sobre la identidad de la publicación suministrada.
DETAILS = {
 'k4base': ('https://www.kaercher.com/ar/home-garden/hidrolavadora/k4-93982940.html', ['1.885 PSI publicados; ≈130 bar convertidos','360 L/h publicados','Manguera de 6 m; motor de inducción; 1.700 W']),
 'ghp180': ('https://www.bosch-professional.com/ar/es/products/ghp-180-0600910CH0', ['83 bar de trabajo / 124,5 bar máximos','4 L/min nominales / 5,6 L/min máximos','Manguera PVC de 5 m; aplicador de 450 ml']),
 'ghp200': ('https://www.bosch-professional.com/ar/es/products/ghp-200-0600910DH0', ['92 bar de trabajo / 138 bar máximos','5,1 L/min nominales / 7,7 L/min máximos','Manguera PVC de 6 m; aplicador de 450 ml']),
 'n700': ('https://www.rumbosrl.com.ar/marcas/niwa/productos-de-limpieza/hidrolavadoras-y-accesorios/hidrolavadoras-electricas/hidrolavadora-electrica-niwa-hdnw-700-1040700', ['120 bar promedio / 150 bar máximos','390 L/h nominales / 450 L/h máximos','Manguera de 5 m; 2.200 W; 220 V / 50 Hz']),
 'konan800': ('https://www.konan.com.ar/productos/generador-electrico-kge-800', ['650 W nominales / 800 W máximos','220 V / 50 Hz; arranque manual; motor 2T','Tanque de 4 L; masa no publicada por fabricante']),
 'lg950': ('https://www.lusqtoff.com.ar/ver-producto/LG950P', ['0,65 kVA nominales / 0,8 kVA máximos','220 V / 50 Hz; arranque manual; motor 2T','16,2 kg; tanque de 4 L']),
 'gammainverter': ('https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-inverter-2kw/', ['2 kW nominales / 2,2 kW de pico','Inverter; 220 V / 50 Hz; arranque manual','17 kg; tanque de 4 L']),
 'eu22': ('https://pf.honda.com.ar/producto/EU22i', ['1,8 kVA nominales / 2,2 kVA máximos','Inverter; 220 V / 50 Hz; arranque manual','21 kg en seco; tanque de 3,6 L']),
 'eu30': ('https://pf.honda.com.ar/producto/EU30is', ['2,8 kVA nominales / 3 kVA máximos','Inverter; 220 V / 50 Hz; arranque eléctrico','59 kg en seco; tanque de 13 L']),
 'eg6500': ('https://pf.honda.com.ar/producto/EG6500CXS', ['5 kVA nominales / 5,5 kVA máximos','D-AVR; 220 V / 50 Hz; arranque eléctrico y manual','87 kg en seco; tanque de 24 L']),
 'ez6500': ('https://pf.honda.com.ar/producto/EZ6500CXS', ['5,5 kVA nominales / 6,5 kVA máximos','AVR; 220 V / 50 Hz; arranque eléctrico y manual','80 kg en seco; tanque de 15,5 L']),
 'et12000': ('https://pf.honda.com.ar/producto/ET12000', ['10 / 11 kVA nominales / máximos; trifásica 3 × 2,7 / 3 × 3 kVA','220 / 380 V; 50 Hz; AVR; arranque eléctrico','Tanque de 31 L; ficha discrepa entre 150 y 162 kg en seco']),
 'lgi55': ('https://lusqtoff.com.ar/ver-producto/LGI5.5-8', ['5,2 kVA máximos; nominal no publicada en la ficha','Inverter; 220 V / 50 Hz; arranque manual y eléctrico','30 kg; tanque de 10 L; 62 dB sin condiciones publicadas']),
 'mcl150': ('https://lusqtoff.com.ar/ver-producto/MCL150-8', ['150 PSI máx.; 60 L/min sin presión asociada','275 W; 2,63 kg; incluye pinzas y extensión de 5 m','Manómetro digital, corte automático y luz; ciclo no publicado']),
 'gadnic9': ('https://www.gadnic.com.ar/infladores-y-compresores/compresor-de-aire-12v-85l-min', ['150 PSI máx.; 85 L/min de desplazamiento sin presión asociada','12 V; máx. 23 A; conexión directa a batería','30 min recomendados / 40 min máximos; cable 3 m y manguera 0,25 + 5 m']),
 'av37': ('https://www.gadnic.com.ar/infladores-y-compresores/compresor-12v-doble-cilindro-gadnic-av37-ty-digital-auto-linterna', ['150 PSI máx.; 35 L/min sin presión asociada','12 V por toma o pinzas; corriente y ciclo no publicados','Digital con corte automático; cable 2,6 m; manguera 0,60 + 3 m']),
 'nictom': ('https://www.nictom.com.ar/productos/inflador-compresor-de-aire-portatil-bateria-powerbank-ie01-gris/', ['Batería integrada; 16 L/min máximos anunciados','Pantalla digital, luz y función PowerBank anunciadas','Autonomía bajo carga, presión máxima y ciclo a confirmar en manual']),
 'pressito25': ('https://www.einhell.com.ar/p/4020420-pressito-18-25/', ['11 bar máx.; 17 / 11 / 9 L/min a 0 / 4 / 7 bar','Power X-Change 18 V; batería y cargador aparte','Alta y baja presión; 2,28 kg sin batería; manual: 5 min de uso / 5 min de enfriamiento']),
 'pressito21': ('https://www.einhell.com.ar/p/4020467-pressito-18-21/', ['10,5 bar máx.; 14 / 9 / 6 L/min a 0 / 4 / 7 bar','Power X-Change 18 V; batería y cargador aparte','Alta y baja presión, succión, pantalla y corte automático']),
 'dmp180': ('https://makita.com.ar/wp-content/uploads/2025/09/CATALOGO-2025-v2.pdf', ['830 kPa máx.; 12 / 8 / 7 L/min a 200 / 700 / 830 kPa','Makita LXT 18 V; confirmar contenido del SKU ofrecido','Manguera de 65 cm; pantalla, luz y corte automático']),
 'lc30200': ('https://lusqtoff.com.ar/productos/LC30200-8', ['200 L; a correa; bicilíndrico','335 L/min; condición de medición no indicada','2.200 W / 3 HP; 220 V / 50 Hz']),
 'lc50kit': ('https://www.lusqtoff.com.ar/productos/compresor-de-aire-con-kit-o-25-hp-50-l-lc-2550bk', ['50 L; lubricado','206 L/min; condición de medición no indicada','2,5 HP; confirmar sufijo -8 y kit']),
 'lc3550': ('https://lusqtoff.com.ar/ver-producto/LC-3550BK', ['50 L; lubricado; bicilíndrico','300 L/min; condición de medición no indicada','3,5 HP; kit con manguera de 5 m']),
 'lc30100': ('https://lusqtoff.com.ar/2023/uploads/Productos/16.%20COMPRESORES/LC-30100/MANUAL/LC-30100.pdf', ['100 L; a correa; lubricado','335 L/min; condición de medición no indicada','2.200 W / 3 HP; 220 V / 50 Hz']),
 'lc40100': ('https://lusqtoff.com.ar/productos/LC40100-8', ['100 L; mando directo; bicilíndrico lubricado','356 L/min en ficha actual; condición no indicada','4 HP / 3.000 W; 220 V / 50 Hz; 76 kg']),
 'k3': ('https://www.kaercher.com/ar/home-garden/hidrolavadora/k-3-black-edition-93983550.html', ['120 bar publicados','330 L/h publicados','Manguera incluida: largo no publicado; 7,3 kg']),
 'k4pc': ('https://www.kaercher.com/ar/home-garden/hidrolavadora/k-4-power-control-16034020.html', ['20–130 bar máximos','420 L/h máximos','Manguera de 8 m; inducción refrigerada por agua']),
 'k5pc': ('https://puntogardenia.com.ar/productos/hidrolavadora-k-5-power-control-ar-karcher-1-603-501-0/', ['20–145 bar máximos','480 L/h en esta ficha; otras publican 500 L/h','Manguera de 10 m; 2.100 W']),
 'g130': ('https://www.gammaherramientas.com.ar/producto/hidrolavadora-130-elite/', ['90 bar de servicio / 130 bar admisibles','360 L/h publicados','Manguera de 5 m; 1.600 W']),
 'hl120': ('https://www.lusqtoff.com.ar/ver-producto/HL-120', ['70 bar de trabajo / 105 bar permitidos','5,5 L/min de trabajo / 6,8 L/min máximos','5,2 kg; verificar manguera y kit']),
 'hl150': ('https://www.lusqtoff.com.ar/files/catalogo-lusqtoff-2023-2024.pdf', ['90 bar publicados; condición según manual','7,5 L/min de trabajo en catálogo','1.500 W; 8 kg; confirmar manguera y kit']),
 're80': ('https://www.stihl.com.ar/es/ap/re-80-x-141950', ['10–100 bar publicados','Hasta 430 L/h según catálogo local','Manguera de 5 m; 7 kg']),
 'npro': ('https://www.rumbosrl.com.ar/marcas/niwa/productos-de-limpieza/hidrolavadoras-y-accesorios/hidrolavadoras-electricas/hidrolavadora-electrica-niwa-hdnw-pro-10-1040900', ['100 bar promedio / 130 bar máximos','384 L/h nominales / 474 L/h máximos','Bomba con cigüeñal y biela; manguera de 8 m']),
 'c30s': ('https://www.wipcool.com/steam-cleaning-machine-c30s-product/', ['3–6 bar publicados','Hasta 3 L/min','Vapor, agua caliente/fría, pulso y ozono']),
 'lc50': ('https://www.lusqtoff.com.ar/productos/compresor-de-aire-o-25-hp-50-lts-lc2550b-8', ['50 L','206 L/min de flujo declarado; no FAD','2,5 HP; confirmar ciclo de trabajo']),
 'bta25': ('https://btatools.com.ar/producto/compresor-de-aire-25-litros-2-0-hp', ['25 L','206 L/min de admisión; FAD no publicado','2 HP; lubricación exacta a confirmar']),
 'bta24': ('https://btatools.com.ar/producto/compresor-de-aire-24-litros-2-0-hp-portatil-sin-aceite', ['24 L','170 L/min de admisión; FAD no publicado','2 HP; sin aceite']),
 'bta50': ('https://btatools.com.ar/producto/compresor-de-aire-50-litros-2-0-hp', ['50 L','206 L/min de admisión; FAD no publicado','2 HP; mando directo']),
 'einhell24': ('https://www.einhell.com.ar/p/4007375-tc-ac-190-24-8-i-of/', ['24 L','75 L/min a 4 bar; 55 L/min a 7 bar','Sin aceite; S3 50%']),
 'lc0122': ('https://lusqtoff.com.ar/ver-producto/LC-0122', ['24 L','180 L/min de caudal; condición de medición no indicada','750 W / 1 HP; sin aceite']),
 'gamma24': ('https://www.gammaherramientas.com.ar/producto/compresor-sin-aceite-24-l-2-hp/', ['24 L','236 L/min llamados flujo continuo; FAD a presión no definido','1.500 W / 2 HP; sin aceite']),
 'bta50oilfree': ('https://btatools.com.ar/producto/compresor-de-aire-50-litros-1-5-hp-silenciado-sin-aceite', ['50 L','260 L/min de admisión; FAD no publicado','1.100 W / 1,5 HP; sin aceite; 65 dB publicados']),
 'gsb550': ('https://www.bosch-professional.com/ar/es/products/gsb-550-06011B60H0', ['Referencia GSB 550: mandril hasta 13 mm','Referencia GSB 550: 550 W','La oferta GSB 550 RE requiere confirmar equivalencia de código']),
 'gsb18': ('https://www.bosch-professional.com/ar/es/products/gsb-18v-50-06019H51E2', ['Mandril de 13 mm','27.000 impactos/min según ficha','1,1 kg sin batería; confirmar kit']),
 'dch273': ('https://www.dewalt.com/en-us/product/dch273b/20v-max-xr-brushless-cordless-1-25mm-sds-plus-l-shape-rotary-hammer-tool-only', ['SDS Plus','2,1 J','Herramienta sola; batería y cargador aparte']),
 'cyl9': ('https://www.bosch-professional.com/es/es/broca-cyl-9-soft-ceramic-7724656-ocs-ac/', ['6 mm anunciados; confirmar código','Para cerámica blanda según familia CYL-9','Rotación sin percusión; confirmar medida recibida']),
 'hex9': ('https://www.bosch-professional.com/es/es/broca-expert-hex-9-hard-ceramic-2867225-ocs-ac/', ['6 mm anunciados; confirmar código','Para baldosa dura y porcelanato según familia HEX-9','Rotación sin percusión; menos de 500 rpm']),
 'heavyblack': ('https://esab.com/pe/sam_es/products-solutions/product/ppe-safety/hands-and-body/heavy-duty-black-gloves/', ['350 g publicados','Palma reforzada y forro hasta el puño','EN 12477 Type A según ficha']),
}

def install_models(facts):
    for key, model in MODELS.items():
        fact = dict(model)
        if key == 'hl1008':
            fact.update(cta='Ver manual del fabricante')
        if key in {'fd186kit','as186','as196'}:
            fact.update(source_type='proveedor de marca', evidence_label='Ficha del proveedor de marca; variante y disponibilidad local a confirmar', cta='Ver ficha del proveedor')
        photo = photo_for(model['source']) or photo_for(brand=model['brand'],model=model['model'])
        if photo:
            fact.update(image=photo['image'],image_source=photo['source'],image_width=photo['width'],image_height=photo['height'],illustrative=False)
        facts[model['source']] = fact
        if key in {'lcvs','lcs50','lcs100','lgi11'}:
            facts[EXISTING[key]] = dict(fact,cta='Ver precio y disponibilidad',evidence_label='Ficha y foto oficiales; enlace suministrado por el usuario')
    for key,(source,specs) in DETAILS.items():
        fact=facts[EXISTING[key]]
        fact.update(source=source, specs=specs, source_type='ficha citada en la guía', evidence_label='Datos del modelo documentado; confirmá que la oferta corresponda al código y kit')
    facts[EXISTING['lc40100']].update(model='LC40100-8',warning='Ficha actual de LC40100-8: 356 L/min y 76 kg. El manual anterior LC-40100 publica 360 L/min y 58 kg; confirmar revisión de placa. No corresponde al LC40200-8 de 200 L y 380 V.')
    facts[EXISTING['lapl36']].update(specs=['30 bar máximos','3,6 L/min máximos','Dos baterías 18 V / 2 Ah y cargador'],power='18 V a batería',use='Enjuague y limpieza ligera desde recipiente')
    facts[EXISTING['hypresso18']].update(specs=['24 bar máximos','240 L/h máximos','Succión de 5 m; sin batería ni cargador'],power='18 V Power X-Change',use='Presión media para enjuagar y regar')
    for key, use, power in [
        ('eu22', 'Inverter portátil de 1,8 kVA nominales', '220 V / 50 Hz monofásica'),
        ('eu30', 'Inverter de 2,8 kVA nominales', '220 V / 50 Hz monofásica'),
        ('eg6500', 'D-AVR de 5 kVA nominales', '220 V / 50 Hz monofásica'),
        ('ez6500', 'AVR de 5,5 kVA nominales', '220 V / 50 Hz monofásica'),
        ('et12000', 'Dimensionar cada fase y el modo de salida', '220 / 380 V; 50 Hz'),
        ('lgi55', 'Inverter; confirmar potencia nominal', '220 V / 50 Hz'),
        ('mcl150', 'Inflado 12 V con controles digitales', '12 V del vehículo; incluye pinzas'),
        ('gadnic9', 'Inflado 12 V con ciclo publicado', '12 V directo a batería; máx. 23 A'),
        ('av37', 'Inflado 12 V con conexión dual', '12 V por toma o pinzas'),
        ('pektra980', 'Carga pequeña; datos de vendedor', '220 V monofásica; confirmar frecuencia'),
        ('konan800', 'Carga pequeña; salida documentada en W', '220 V / 50 Hz monofásica'),
        ('lg950', 'Carga pequeña; salida documentada en kVA', '220 V / 50 Hz monofásica'),
        ('gammainverter', 'Inverter compacto de 2 kW nominales', '220 V / 50 Hz monofásica'),
        ('nictom', 'Inflador compacto con batería integrada', 'Batería integrada recargable'),
        ('pressito25', 'Alta y baja presión; caudal publicado por presión', 'Power X-Change 18 V'),
        ('pressito21', 'Alta y baja presión; caudal publicado por presión', 'Power X-Change 18 V'),
        ('dmp180', 'Alta presión; caudal publicado por presión', 'Makita LXT 18 V'),
        ('lc50', 'Versión básica de 50 L', '220 V monofásica'),
        ('lc50kit', '50 L lubricado con kit documentado', '220 V monofásica'),
        ('lc3550', '50 L bicilíndrico con kit documentado', '220 V monofásica'),
        ('lc30100', '100 L lubricado a correa', '220 V / 50 Hz monofásica'),
        ('lc40100', '100 L lubricado de mando directo', '220 V / 50 Hz monofásica'),
        ('lc30200', '200 L bicilíndrico a correa', '220 V / 50 Hz monofásica'),
    ]:
        facts[EXISTING[key]].update(use=use, power=power)
    facts[EXISTING['pektra980']].update(source='https://mercadocordoba.com.ar/producto/163', source_type='publicación comercial', evidence_label='Datos de vendedor; sin ficha primaria', specs=['650 W nominales / 720 W máximos según vendedor','220 V monofásica; motor 2T según vendedor','16 kg según vendedor; tanque no verificado'],warning='Potencia y masa sin confirmación primaria; cotejá placa y manual del GPK980.',includes='Confirmá manual, configuración y contenido de la publicación.')
    facts[EXISTING['stanleylocal']]['specs']=['24 L en la fuente histórica / 50 L en el título recibido','FAD no confirmado para este SKU','2 HP anunciados; confirmar placa y manual']
    facts[EXISTING['boschstep']]['specs']=['4–20 mm anunciados; SKU 2608597519','Espesor máximo no confirmado para esta referencia','No atribuir los nueve pasos de 2608597524 sin verificar código']
    facts[EXISTING['boschstep']].update(source='https://www.bosch-professional.com/gb/en/hss-step-drill-bits-with-hex-shank-2868008-ocs-ac/',source_type='familia Bosch; confirmar SKU exacto')
    for key in ['npro','c30s','gsb550','gsb18','dch273','cyl9','hex9','boschstep','heavyblack']:
        fact=facts[EXISTING[key]]
        extra='Confirmá código exacto y contenido de la publicación antes de aplicar los datos del modelo documentado.'
        if extra not in (fact.get('warning') or ''):
            fact['warning']=((fact.get('warning') or '')+' '+extra).strip()

LABELS = {
 'generadores': ['Potencia nominal / máxima','Salida / tecnología / arranque','Peso / tanque'],
 'hidrolavadoras': ['Presión declarada','Caudal declarado','Alcance / configuración'],
 'compresores': ['Tanque','Aire publicado','Potencia / construcción'],
 'taladros': ['Encastre / diámetro','Prestación / material','Kit / límites'],
 'soldadoras': ['Peso publicado','Construcción','Marcado declarado'],
}

def editorial_config(path, category):
    labels = ['Presión / aire publicado','Alimentación / configuración','Controles / alcance / ciclo'] if path in {
        '/compresores/para-auto/', '/compresores/inalambricos/',
        '/compresores/inflador-neumaticos-portatil/', '/compresores/12v-doble-piston/',
    } else LABELS[category]
    if path == '/compresores/kits-aerografo/':
        labels = ['Aerógrafo / acción','Compresor incluido','Manguera / accesorios']
    return dict(PLANS[path],labels=labels, placement=category+'-contextual' if category in {'taladros','soldadoras'} else 'shelf-'+category)

def selection(path, category, facts):
    config = PLANS.get(path)
    if not config:
        return None
    result = []
    for key in config['models']:
        url = EXISTING[key] if key in EXISTING else MODELS[key]['source']
        fact = facts[url]
        result.append((category, (fact['brand']+' '+fact['model'],fact['use'],url,path)))
    return result
