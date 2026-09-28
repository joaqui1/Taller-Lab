"""Decisiones y selección comercial redactadas para 16 guías concretas.

Los enlaces conocidos no certifican stock, precio ni identidad de la unidad.
Una oferta pendiente de identificación nunca recibe el sello de elección.
"""
from html import escape


def matrix(title, lead, headers, rows, note):
    return dict(kind="table", title=title, lead=lead, headers=headers, rows=rows, note=note)


def route(title, lead, question, options, note):
    return dict(kind="selector", title=title, lead=lead, question=question, options=options, note=note)


def cost(title, lead, a, b, note):
    fields = []
    for key, label in (("A", a), ("B", b)):
        for prefix, suffix in (("price", "precio confirmado"), ("shipping", "envío"), ("extras", "extras necesarios")):
            fields.append(dict(key=prefix + key, label=f"{label} · {suffix}", value=0, unit="$", minimum=0))
    return dict(kind="cost", title=title, lead=lead, fields=fields, note=note)


EXTRA_RESOURCES = {
    "/amoladoras/bosch/": route(
        "Elegí la familia Bosch por disco y alimentación",
        "Una GWS con cable de 115 mm, una variable de 125 mm y una de batería resuelven decisiones distintas. El código de pedido termina de identificar cada opción.",
        "¿Qué condición define tu compra?",
        [["Quiero una referencia con cable de 115 mm", "GWS 700 o GWS 770: contrastar el código", "GWS 700 tiene ficha argentina de 710 W. GWS 770 documenta 770 W, 115 mm y 220 V para 06013980E0 en Bosch Brasil; confirmá ese código en la oferta, kit y garantía local."],
         ["Necesito regular velocidad y usar 125 mm", "GWS 9-125 S: revisar tensión antes de elegir", "La variante 0 601 396 1D0 de la guía es de 127 V. Para una instalación de 220 V necesitás un código compatible documentado."],
         ["Quiero trabajar con batería", "GWS 180-LI: comprobar el equipo completo", "18 V y 125 mm. La masa publicada pasa de 1,6 kg sin batería a 2,2 kg con batería; confirmar batería y cargador del kit."]],
        "Selector de familias, sin ranking de rendimiento. La equivalencia a 700 W anunciada por Bosch para 180-LI no sustituye un ensayo común."),
    "/amoladoras/gamma/": cost(
        "¿Te conviene el kit o armar la compra por separado?",
        "G1910KAR reúne máquina y consumibles. Compará dos presupuestos completos para la misma herramienta y los accesorios que tu trabajo necesita.",
        "Kit G1910KAR", "G1910KAR por separado",
        "A y B deben cubrir la misma máquina y lista de accesorios. Extras B = consumibles y maletín necesarios no incluidos; extras A = faltantes del kit. Total = precio + envío + extras. No cuenta financiación, desgaste ni diferencias de prestaciones."),
    "/amoladoras/dowen-pagio/": route(
        "El motivo para pasar de 9993220.7 a otro código",
        "La comparación de catálogo permite separar una compra de 115 mm de una necesidad de velocidad variable. Más watts no documentan un mejor acabado.",
        "¿Qué función necesitás?",
        [["115 mm, sin requerimiento de velocidad variable", "9993220.7: candidato de 900 W", "12.000 rpm sin carga. El catálogo no incluye disco de corte; sumalo al presupuesto si corresponde."],
         ["115 mm, comparar otra potencia declarada", "9993220.9: 1.050 W, mismas rpm publicadas", "Diferencia de 150 W respecto de 9993220.7. No hay ensayo que traduzca esa diferencia a tiempo de corte."],
         ["Velocidad variable o disco de 125 mm", "9993224.2: revisar su variante", "4.000–12.000 rpm y 115/125 mm según catálogo. La 9993220.7 enlazada no cubre esa función."]],
        "El catálogo imprime M14 (5/8–11), designaciones que no son equivalentes. Confirmar eje y manual de la unidad para accesorios roscados."),
    "/compresores/12v-doble-piston/": matrix(
        "Una ficha Gadnic no certifica un JD Extreme",
        "El nombre doble pistón y los 150 PSI aparecen en más de una marca. Para la publicación JD Extreme 107, separá lo anunciado de lo documentado en los dos Gadnic de esta guía.",
        ["Dato para elegir", "Gadnic documentado en la guía", "JD Extreme 107 enlazado"],
        [["Corriente / conexión", "23 A máximos; conexión a batería", "Pedir manual: no trasladar corriente ni conexión Gadnic"],
         ["Caudal", "AV000009: 85 L/min; AV000012: cifras divergentes", "85 L/min anunciados; falta condición comparable"],
         ["Ciclo y pausas", "30 min recomendado / 40 min máximo publicados", "No heredar esos tiempos: comprobar el código 107"],
         ["Rapidez de inflado", "Sin ensayo común", "No se puede deducir de doble pistón ni de PSI máximos"]],
        "Esta matriz evita una equivalencia por apariencia. Los datos de JD Extreme proceden de la publicación comercial registrada; no constituyen una prueba de TallerLab."),
    "/compresores/kits-accesorios/": matrix(
        "El kit se decide por la herramienta que vas a usar",
        "Contar cinco piezas deja fuera presión, consumo e interfaz. Usá esta secuencia para el Lüsqtoff AA-5000K anunciado y para los BTA del catálogo.",
        ["Tu tarea", "Dato que necesitás", "Lo que el número de piezas no responde"],
        [["Pintar", "Tipo de pistola, pico, presión y consumo", "Un depósito de 600 ml no indica consumo de aire"],
         ["Inflar", "Manómetro, conector y límites del accesorio", "No acredita exactitud de lectura"],
         ["Soplar o lavar", "Presión admitida y accesorio identificado", "No convierte el kit en una hidrolavadora"],
         ["Conectar al compresor", "Rosca y perfil de acople en ambos extremos", "5 m de manguera no confirman diámetro interior ni compatibilidad"]],
        "AA-5000K es una oferta distinta de BTA 279010/279013. La indicación BTA de 2 HP/90 PSI no se copia al Lüsqtoff; falta contrastar consumo y salida del compresor."),
    "/taladros/taladro-percutor-inalambrico/": matrix(
        "Máquina sola frente a un kit: qué debe cerrar el presupuesto",
        "Los cuatro códigos de la tabla técnica son versiones sin batería. La oferta Ingco CIDLI20668-4 anuncia un conjunto; compará contenido antes de precio o torque.",
        ["Componente", "Bosch / DeWalt / Einhell / Milwaukee citados", "Ingco CIDLI20668-4 anunciado"],
        [["Herramienta", "Código exacto documentado por cada fabricante", "Pedir placa y código completo; no confundir con sufijo -3"],
         ["Baterías", "No incluidas en los códigos citados", "Dos anunciadas; confirmar capacidad Ah y código"],
         ["Cargador", "Cotizar el compatible por separado", "Confirmar inclusión y tensión de entrada"],
         ["Comparación económica", "Sumar lo que falta para usar el equipo", "Valorar solo los accesorios que necesitás"]],
        "Los 66 Nm y 20 V del aviso Ingco son declaraciones comerciales; no prueban ventaja frente a valores de otro fabricante. La plataforma debe validarse por código, no solo por voltaje."),
    "/taladros/combo-taladro-amoladora/": cost(
        "Dos herramientas: precio del combo frente a la misma compra separada",
        "El Kommberg con cable y el KATL-9BK de batería pertenecen a configuraciones distintas. Para saber si un combo ahorra, compará primero los mismos códigos.",
        "Combo elegido", "Mismos códigos separados",
        "A y B deben tener iguales herramientas y contenido útil. Precio B = suma de ambas máquinas; extras B = accesorios faltantes. Total = precio + envío + extras. La cuenta no declara equivalentes un kit con cable y otro a batería."),
    "/sierras/caladoras-black-decker/": route(
        "BES603 o BES602: la velocidad es la diferencia documentada",
        "Las variantes B2 citadas tienen la misma potencia y capacidades máximas. La BES603 agrega regulación; esa función es un criterio concreto para comparar.",
        "¿Qué buscás en la caladora?",
        [["Necesito regular la velocidad", "BES603-B2: función variable documentada", "Hasta 3.000 carreras/min. Confirmar que la oferta corresponda a B2, 220 V y hoja tipo T."],
         ["Estoy comparando capacidad máxima", "Las fichas coinciden: 65 mm madera y 6 mm metal", "Esos máximos no distinguen BES603-B2 de BES602-B2 ni garantizan el acabado de un corte concreto."],
         ["Estoy reponiendo hojas", "Encastre tipo T en las dos variantes", "Además del encastre, comprobar material, longitud útil y condiciones del manual."]],
        "Documentación Black+Decker Brasil para variantes B2. No traslada garantía, sufijo ni accesorios a cualquier publicación argentina."),
    "/sierras/sensitivas-total/": matrix(
        "Cuatro geometrías: 355 mm no es la capacidad de corte",
        "La fábrica documenta estos límites para TS223558. Usá la forma de tu pieza como primera comparación y confirmá por separado el sufijo -4 de la publicación.",
        ["Geometría según fábrica", "Capacidad máxima declarada", "Límite de lectura"],
        [["Tubo redondo", "100 mm", "No extrapolar a una barra maciza de 100 mm"],
         ["Sección cuadrada", "100 × 100 mm", "No inferir capacidad a inglete"],
         ["Rectangular", "120 × 100 mm", "Conservar orientación y condiciones del manual"],
         ["Barra de acero", "50 mm", "No sustituir por diámetro exterior de disco: 355 mm"]],
        "Para TS223558, fábrica publica 3.700 rpm; el aviso -4 registrado anuncia 3.800. La placa/manual de esa variante debe resolver la discrepancia antes de elegir disco o comprar."),
    "/sierras/de-banco-lusqtoff/": route(
        "La variante se elige antes que el repuesto",
        "Hay diferencias entre fichas web, catálogo y título comercial. Este recorrido identifica qué comprobación cambia tu compra.",
        "¿Qué necesitás resolver primero?",
        [["Voy a comprar un disco de repuesto", "Pedir placa y manual de la unidad", "SML2000-8 figura con 250 mm en catálogo y 255 mm en web. No elegir el diámetro por el nombre comercial."],
         ["Necesito cortar inclinado a 45°", "SML2000-9 y SML2000B-9 publican límites distintos", "60 y 55 mm respectivamente: 5 mm de diferencia documentada. No trasladar ese límite a SML2000-8."],
         ["La oferta dice -8 y su ficha -9", "Identidad pendiente: pedir aclaración al vendedor", "Solicitá código completo, foto de placa y lista de entrega por escrito antes de comparar esa oferta con una variante confirmada."]],
        "No se resuelve una discrepancia eligiendo la cifra mayor. Los 2.000 W máximos S6 no representan por sí solos potencia de entrada continua."),
    "/soldadoras/esab-handyarc-162i/": matrix(
        "HandyArc 162i: elegí por el punto de ciclo, no por el nombre",
        "La ficha ESAB 0409616 publica tres puntos de corriente. Cada uno responde una condición distinta; no interpolamos valores intermedios.",
        ["Punto de ficha", "Corriente / tensión", "Implicación para elegir"],
        [["20 %", "160 A / 26,4 V", "La cifra mayor de corriente es intermitente"],
         ["60 %", "92 A / 23,7 V", "No equivale al punto de 160 A"],
         ["100 %", "72 A / 22,9 V", "Comparar con el requisito del consumible y condiciones del manual"]],
        "La tabla no prescribe un procedimiento de soldadura ni convierte el porcentaje en un temporizador universal. Comprobar clasificación, diámetro, polaridad y corriente del electrodo."),
    "/soldadoras/lusqtoff-iron-100/": matrix(
        "Comprá el kit actual sin heredar la ficha del Iron anterior",
        "IRON-100 de catálogo y MEGAIRON100-8 son códigos distintos. Separar máquina, máscara y escuadras evita comparar paquetes incompletos.",
        ["Comprobación", "IRON-100 histórico", "MEGAIRON100-8 actual"],
        [["Corriente", "Rango 10–105 A en catálogo 2020/21", "105 A al 30 % en ficha"],
         ["Peso", "3,2 kg en catálogo", "No trasladar 3,2 kg al kit"],
         ["Contenido", "No acredita el paquete actual", "Fuente, máscara ST-1X y dos escuadras"],
         ["Garantía", "Dato histórico de seis meses", "Pedir cobertura vigente de la oferta"]],
        "La ficha actual confirma 220 V y MMA. La presencia de máscara y escuadras no demuestra que el conjunto cubra todos los requisitos del trabajo."),
    "/soldadoras/mig-lusqtoff/": route(
        "Elegí el proceso antes de comparar el kit Flux",
        "MIG en el título comercial no confirma gas ni todos los consumibles. La SML120-8DK enlazada es un código de kit que debe conservar su ficha propia.",
        "¿Qué uso necesitás documentar?",
        [["Alambre tubular autoprotegido, sin gas", "Comprobar modo FLUX y consumible exacto", "Revisar diámetro admitido, polaridad y rodillo de la variante. El kit no hereda automáticamente los datos de SML130-7 o SML150-8D."],
         ["Alambre macizo con gas", "Estas fichas Flux no acreditan ese uso", "Buscá una fuente que documente gas, torcha y consumible. No elegimos SML120-8DK por la palabra MIG del aviso."],
         ["También necesito MMA o Lift TIG", "Verificar funciones y accesorios de SML120-8DK", "La ficha registrada declara FLUX/MMA/Lift TIG; MMA y TIG 20–100 A. Una función declarada no prueba que la caja traiga su equipo completo."]],
        "La ficha del kit registra 200 V, mientras otros títulos o modelos muestran 220 V. Pedir placa y manual de SML120-8DK; no sustituir ese dato por el de otra variante."),
    "/generadores/chicos/": matrix(
        "650 W nominales: mismo número, distinto respaldo",
        "Pektra y Konan aparecen con 650 W nominales, pero la procedencia no es la misma. Antes de calcular cargas, confirmá qué documento identifica tu unidad.",
        ["Pregunta de compra", "Pektra GPK980", "Konan KGE/800"],
        [["¿Quién respalda 650 W?", "Publicación comercial; sin ficha primaria localizada", "Ficha del representante citada"],
         ["¿Qué diferencia hay con el máximo?", "720 − 650 = 70 W, si se confirma nominal", "800 − 650 = 150 W"],
         ["¿Alcanza para un motor?", "Falta demanda de arranque de la carga", "La diferencia de 150 W tampoco prueba arranque"],
         ["¿Puedo comparar autonomía?", "Sin dato primario confirmado", "4,5 h declaradas, sin ensayo común con Pektra"]],
        "Las restas no representan reserva de arranque validada. No se dimensiona una casa por el número del título. Uso del generador según su manual y condiciones de ventilación indicadas."),
    "/generadores/a-nafta/": matrix(
        "Dos publicaciones afiliadas: primero cerrar la potencia nominal",
        "Los equipos Pektra y Philco enlazados son alternativas comerciales adicionales a la tabla Lüsqtoff. Compará sus campos sin mezclar kVA y W.",
        ["Dato de la publicación registrada", "Pektra 2,2 kVA", "Philco GE-PH2500ALP"],
        [["Nominal", "No confirmada en el registro", "2.500 W anunciados"],
         ["Máxima", "2,2 kVA anunciados", "2.800 W anunciados"],
         ["Qué pedir", "Placa, modelo y potencia nominal", "Manual del código y condición de potencia"],
         ["Qué no deducir", "No convertir kVA a W sin factor de potencia", "No usar 2.800 W como nominal ni prueba de arranque"]],
        "Estos datos son comerciales, no fichas de fábrica cotejadas. Antes de elegir, completar cargas de marcha/arranque y confirmar el documento del modelo. Los 5,5/6,5 HP del motor no son potencia eléctrica útil."),
    "/hidrolavadoras/150-bar/": matrix(
        "150 bar en el nombre no identifica la misma decisión",
        "En HL100-8 el manual distingue servicio de máximo. La Logus GHL150 a nafta enlazada cambia además la alimentación: no es una sustitución automática por presión.",
        ["Cruce", "Lüsqtoff HL100-8", "Logus GHL150 registrada"],
        [["Alimentación", "Eléctrica, 2.000 W", "Motor a nafta 6,5 HP declarados"],
         ["Presión", "100 bar de trabajo / 150 permitidos", "154 bar anunciados; condición de trabajo por confirmar"],
         ["Caudal", "6,0 de trabajo / 7,5 L/min máximo", "No documentado en la ficha registrada"],
         ["Decisión", "Contrastar servicio con tarea y alimentación", "Evaluar si necesitás motor y podés cumplir condiciones del manual"]],
        "No recomendamos la Logus como más rápida o más apta por los 154 bar. Faltan punto de servicio, caudal comparable y prueba sobre la misma superficie."),
}


def note(title, fit, reason, limits, checks, urls, alternative, recommend=False):
    return dict(title=title, fit=fit, reason=reason, limits=limits, checks=checks,
                urls=urls, alternative=alternative, recommend=recommend)


BUYING_NOTES = {
    "/amoladoras/gamma/": note("Cuándo elegir el kit Gamma G1910KAR",
        "Para quien busca una amoladora con cable de 115 mm y necesita también consumibles y maletín.",
        "La ficha Gamma identifica el kit y su contenido. Es una opción razonada por configuración, no un ganador por precio o rendimiento.",
        "Si ya tenés esos accesorios, compará el costo completo con la compra separada en la calculadora.",
        ["G1910KAR, 220 V y contenido coincidente", "Discos indicados para material y operación", "Precio final, envío y garantía escrita"],
        [("https://meli.la/12aMvrG", "Consultar kit Gamma G1910KAR")],
        ("/amoladoras/dowen-pagio/", "Comparar una alternativa de 115 mm"), True),
    "/amoladoras/dowen-pagio/": note("Cuándo elegir Dowen Pagio 9993220.7",
        "Para una compra de 115 mm con cable cuando no necesitás regulación de velocidad ni un disco de 125 mm.",
        "El catálogo identifica 900 W y 12.000 rpm. El código afiliado coincide con la referencia de esta guía.",
        "El catálogo no incluye disco de corte y presenta una rosca ambigua: comprobar unidad y accesorios.",
        ["Código 9993220.7 y tensión de placa", "Guarda, eje y accesorio admitido por manual", "Contenido de caja y costo del disco necesario"],
        [("https://meli.la/1QUvfns", "Consultar Dowen Pagio 9993220.7")],
        ("/amoladoras/velocidad-variable/", "Comparar opciones con velocidad variable"), True),
    "/soldadoras/lusqtoff-iron-100/": note("Cuándo elegir MEGAIRON100-8",
        "Para quien busca una fuente MMA con máscara y escuadras en un mismo paquete.",
        "La ficha del kit identifica esas tres partes y un punto de 105 A al 30 %. La elección se apoya en contenido y proceso.",
        "Comprobá que el consumible y la continuidad requerida encajen con manual y ciclo; 105 A no es salida continua acreditada.",
        ["MEGAIRON100-8 en placa y factura", "Máscara ST-1X y dos escuadras en el aviso", "Manual, alimentación y garantía vigentes"],
        [("https://meli.la/1knTbU1", "Consultar kit MEGAIRON100-8")],
        ("/soldadoras/esab-handyarc-162i/", "Comparar los puntos de ciclo de ESAB"), True),
    "/soldadoras/esab-handyarc-162i/": note("Cuándo considerar HandyArc 162i",
        "Para una compra MMA que prioriza una curva de corriente/ciclo documentada y el código 0409616.",
        "La guía conserva los tres puntos de ficha ESAB; permiten cotejar el requisito del electrodo sin confundir máximo con continuo.",
        "No elegimos 162i para sostener 160 A: ese punto está publicado al 20 %. Falta verificar condiciones y accesorios de la oferta.",
        ["HandyArc 162i, código 0409616", "Consumible y condiciones del manual", "Cables, pinzas, garantía y alimentación de la unidad"],
        [("https://meli.la/1mZhwNS", "Consultar ESAB HandyArc 162i")],
        ("/soldadoras/electrodo-7018/", "Cotejar rangos documentados de electrodos"), True),
    "/amoladoras/bosch/": note("GWS 770: alternativa con ficha propia",
        "Puede entrar en la comparación si buscás una Bosch con cable de 115 mm.",
        "Existe una ficha Bosch Brasil para 06013980E0; es distinta de las tres referencias argentinas de la tabla.",
        "La documentación brasileña no confirma variante, garantía ni contenido de la publicación argentina.",
        ["Código completo y tensión de placa", "Correspondencia con el manual de la unidad", "Contenido y garantía del vendedor"],
        [("https://meli.la/1GRCAjZ", "Consultar oferta Bosch GWS 770")],
        ("/amoladoras/gamma/", "Comparar otro equipo con cable de 115 mm")),
    "/compresores/12v-doble-piston/": note("JD Extreme 107: qué falta para elegirlo",
        "Para evaluar un inflador de 12 V con doble pistón identificado en una publicación concreta.",
        "El aviso registrado identifica 107; permite pedir documentación del equipo que se entrega.",
        "Las fichas Gadnic de esta guía no verifican su corriente, ciclo ni rapidez. La elección queda condicionada al manual JD.",
        ["Modelo 107 y método de conexión", "Consumo eléctrico y ciclo de trabajo", "Manguera, adaptadores y garantía"],
        [("https://meli.la/274KM8a", "Consultar JD Extreme 107")],
        ("/compresores/para-auto/", "Revisar criterios de inflado para auto")),
    "/compresores/kits-accesorios/": note("AA-5000K: evaluá el accesorio que te importa",
        "Para armar un conjunto de accesorios de aire; el kit no incluye compresor.",
        "La publicación identifica cinco piezas y manguera de 5 m. El conjunto puede simplificar la compra si sus interfaces encajan.",
        "Faltan consumos y presión de cada herramienta para validar tu compresor. El depósito anunciado no acredita acabado.",
        ["AA-5000K y las cinco piezas detalladas", "Roscas, perfil de acople y manguera", "Consumo a presión de cada accesorio necesario"],
        [("https://meli.la/32SJoX7", "Consultar accesorios AA-5000K")],
        ("/compresores/manguera/", "Comprobar manguera y conexión")),
    "/taladros/taladro-percutor-inalambrico/": note("Ingco CIDLI20668-4: comparar el kit completo",
        "Para evaluar un percutor a batería anunciado con dos baterías y cargador.",
        "La configuración anunciada permite comparar el costo de empezar frente a herramientas solas.",
        "Los datos Ingco provienen del aviso; no acreditan superioridad en torque o durabilidad. No se usa una foto del sufijo -3 como identificación del -4.",
        ["CIDLI20668-4 en placa y caja", "Ah y códigos de ambas baterías y cargador", "Mandril, modo percutor y manual de esta variante"],
        [("https://meli.la/2xvJRJp", "Consultar kit Ingco CIDLI20668-4")],
        ("/taladros/rotomartillos/", "Comparar SDS si tu tarea requiere otro encastre")),
    "/taladros/combo-taladro-amoladora/": note("Kommberg con cable: cerrá la lista del combo",
        "Para quien prefiere dos herramientas con cable y necesita parte de los accesorios anunciados.",
        "El aviso registrado identifica KB-TP650 y KB-AA820; compararlos por separado mejora el presupuesto.",
        "Los datos son comerciales y no equivalen al KATL-9BK a batería. Un paquete de 28 piezas no mide utilidad ni ahorro.",
        ["Ambos códigos y sus manuales", "Contenido útil: discos, mechas y maletín", "Tensión, capacidades y garantía por herramienta"],
        [("https://meli.la/2z7Capd", "Consultar combo Kommberg con cable")],
        ("/taladros/lusqtoff-inalambrico/", "Revisar la alternativa de batería")),
    "/sierras/caladoras-black-decker/": note("BES603: confirmar la variante de velocidad variable",
        "Para quien necesita regulación de velocidad y encuentra una oferta que coincide con la variante documentada.",
        "BES603-B2 documenta velocidad variable y hoja T. Es el motivo funcional para compararla con BES602-B2.",
        "La publicación usa BES603 sin confirmar aquí sufijo ni garantía local. Esas comprobaciones preceden a la elección.",
        ["Código completo y 220 V en placa", "Regulación de velocidad y encastre T", "Hojas incluidas y cobertura argentina"],
        [("https://meli.la/1ntghna", "Consultar Black+Decker BES603")],
        ("/sierras/caladoras/", "Comparar otras capacidades documentadas")),
    "/sierras/sensitivas-total/": note("TS223558-4: resolver la variante antes de comprar",
        "Para evaluar una sensitiva anunciada con disco de 355 mm para metal.",
        "Hay una publicación identificada con sufijo -4 y una ficha de fábrica del código base.",
        "No recomendamos esa variante como equivalente confirmada: el registro comercial y fábrica discrepan en rpm.",
        ["TS223558-4 en placa y manual", "Rpm y capacidad por geometría de esa unidad", "Disco, agujero, accesorios y garantía"],
        [("https://meli.la/1mLrBwo", "Consultar variante Total TS223558-4")],
        ("/sierras/sensitivas-lusqtoff/", "Comparar otra sensitiva por geometría")),
    "/sierras/de-banco-lusqtoff/": note("Oferta SML2000: identificación pendiente",
        "Para consultar una publicación de sierra de banco y solicitar la variante que se entrega.",
        "El enlace permite contrastar la oferta con los códigos separados de la guía.",
        "El registro muestra -8 en título y -9 en ficha. No hay recomendación de compra hasta confirmar identidad; tampoco se presenta una foto como prueba.",
        ["Código completo por escrito y foto de placa", "Diámetro admitido y corte a 45° en su manual", "Mesa, guía, empujador y garantía incluidos"],
        [("https://meli.la/2WFpTNp", "Consultar y confirmar variante SML2000")],
        ("/sierras/de-banco-einhell/", "Comparar otra familia de sierras de banco")),
    "/soldadoras/mig-lusqtoff/": note("SML120-8DK: el proceso y el código deben coincidir",
        "Para evaluar un kit Flux con las funciones que su ficha identifica.",
        "La publicación apunta al kit SML120-8DK, que tiene datos propios registrados.",
        "Antes de elegir, resolver 200 V en la ficha y tensión de placa. No se acredita MIG con gas ni kit Lift TIG completo por el título.",
        ["SML120-8DK y tensión en placa/manual", "Consumible, rodillo y polaridad admitidos", "Torcha y accesorios de cada proceso incluido"],
        [("https://meli.la/26RsZRw", "Consultar kit SML120-8DK")],
        ("/soldadoras/soldadora-mig-con-gas/", "Revisar la configuración con gas")),
    "/generadores/chicos/": note("Pektra GPK980: comprobar nominal antes de elegir",
        "Para evaluar una publicación de generador pequeño de dos tiempos.",
        "El enlace identifica una oferta concreta adicional a la ficha Konan de la comparación.",
        "650 W nominales sigue siendo un dato comercial sin respaldo primario localizado. No lo recomendamos para una carga sin placa y manual.",
        ["GPK980 y nominal en placa/manual", "Marcha y arranque de cada carga", "Combustible, uso, garantía y accesorios"],
        [("https://meli.la/2jcLSy1", "Consultar Pektra GPK980")],
        ("/generadores/para-casa/", "Armar un inventario de cargas")),
    "/generadores/a-nafta/": note("Pektra y Philco: pedir el dato que falta",
        "Para comparar publicaciones a nafta una vez identificadas tus cargas.",
        "Los dos enlaces apuntan a alternativas comerciales registradas, con distinta unidad y respaldo de potencia.",
        "No hay ganador: faltan nominal Pektra y documentación primaria de los campos Philco. W y kVA no se ordenan como una misma unidad.",
        ["Modelo y potencia nominal de placa", "Manual y demanda de arranque de las cargas", "Condición de entrega, alimentación y garantía"],
        [("https://meli.la/2bL6gVj", "Consultar Pektra 2,2 kVA"), ("https://meli.la/1nUAUuv", "Consultar Philco GE-PH2500ALP")],
        ("/generadores/para-casa/", "Calcular un escenario de cargas documentadas")),
    "/hidrolavadoras/150-bar/": note("Logus GHL150: opción a motor, con datos por completar",
        "Para evaluar una máquina a nafta cuando la alimentación eléctrica condiciona la elección.",
        "El código GHL150 identifica una referencia a motor distinta de los tres modelos eléctricos comparados.",
        "154 bar no prueba mayor capacidad de limpieza. En la ficha registrada falta caudal y condición de servicio comparable.",
        ["GHL150 en placa y manual", "Presión de servicio y caudal bajo esa condición", "Alimentación de agua, boquillas y condiciones de uso"],
        [("https://meli.la/1KQjHgT", "Consultar Logus GHL150 a nafta")],
        ("/hidrolavadoras/gamma/", "Comparar alternativas eléctricas documentadas")),
}


BUYING_NOTES.update({
    "/hidrolavadoras/comparativa-general/": note(
        "Dos eléctricas con documentación identificada",
        "Para contrastar una compra eléctrica por presión nominal, alimentación y contenido.",
        "HL100-7 tiene ficha propia de 70 bar nominales. HL-105 publica 105 bar máximos y deja nominal/caudal por completar; sus máximos no forman un ranking de limpieza.",
        "GHL150 a nafta se trata en una sección separada del artículo. La identidad, el kit y la oferta vigente se confirman antes de elegir.",
        ["HL100-7 o HL-105 en placa y manual", "Presión nominal y condición de caudal del código", "Contenido, vendedor y garantía"],
        [("https://meli.la/1cZXqxL", "Consultar Lüsqtoff HL100-7"), ("https://meli.la/2Rcddpg", "Consultar Logus HL-105")],
        ("/hidrolavadoras/150-bar/", "Evaluar por separado la alternativa a nafta")),
    "/hidrolavadoras/lusqtoff/": note(
        "HL100-7: elegí por el código completo",
        "Para evaluar la eléctrica de 1.200 W y 70 bar nominales documentados por Lüsqtoff.",
        "Su ficha separa nominal de máximo y permite incorporar el modelo realmente enlazado a esta guía.",
        "HL100-7 no es HL100-8. La tasa de flujo no precisa aquí condición nominal/máxima; no hereda la del HL-120.",
        ["HL100-7 y 220 V–50 Hz en placa", "Manguera y accesorios del kit", "Manual, repuestos y garantía de esa unidad"],
        [("https://meli.la/1cZXqxL", "Consultar HL100-7")],
        ("/hidrolavadoras/comparativa-general/", "Contrastar otras eléctricas")),
    "/taladros/inalambricos/": note(
        "Ingco: compará el costo de empezar con el kit",
        "Para quien busca una opción anunciada con percusión, dos baterías y cargador.",
        "El contenido del kit cambia la compra frente a una herramienta sola; la tabla separa sus datos comerciales de las fichas Bosch, Einhell y Black+Decker.",
        "CIDLI20668-4 sigue condicionado a identificar la variante y los packs. Los 66 Nm anunciados no demuestran superioridad frente a torques de otras fichas.",
        ["CIDLI20668-4 en placa y caja", "Ah, código y cantidad de baterías", "Cargador, manual del sufijo -4 y garantía"],
        [("https://meli.la/2xvJRJp", "Consultar kit Ingco CIDLI20668-4")],
        ("/taladros/taladro-percutor-inalambrico/", "Revisar el percutor inalámbrico")),
    "/taladros/percutores/": note(
        "Una opción percutora a batería para contrastar",
        "Para evaluar un kit con mandril convencional, después de decidir si necesitás percusión o SDS.",
        "El aviso Ingco anuncia percusión, mandril de 13 mm y dos baterías. Es otra referencia; los Bosch siguen explicando el mecanismo.",
        "No se atribuyen diámetros Bosch ni joules/encastre SDS a Ingco. Faltan capacidades y manual del sufijo -4 para el material concreto.",
        ["Material y diámetro admitidos por el manual", "CIDLI20668-4 y modo percutor", "Baterías, cargador y broca compatible"],
        [("https://meli.la/2xvJRJp", "Consultar percutor Ingco")],
        ("/taladros/rotomartillos/", "Revisar SDS si tu tarea lo requiere")),
    "/taladros/taladro-de-banco/": note(
        "Omaha AB550161K: cerrar recorrido y régimen",
        "Para evaluar otra configuración de banco con mandril de 16 mm y cinco velocidades anunciadas.",
        "La oferta permite pedir un kit identificado y comparar su costo con los Lüsqtoff de la guía.",
        "550 W anunciados no bastan para elegir: faltan recorrido, rango de rpm, régimen y capacidad por material. No se heredan datos del TB-16.",
        ["AB550161K en placa y manual", "Recorrido, rpm, régimen y capacidad", "Tensión, morsa, mesa, fijación y garantía"],
        [("https://meli.la/2Znq55m", "Consultar Omaha AB550161K")],
        ("/taladros/", "Explorar otras guías de taladros")),
    "/compresores/para-auto/": note(
        "Batería o 12 V: dos ofertas con decisiones distintas",
        "Para contrastar IE01 a batería o JD Extreme 107 de 12 V con tu conexión y controles requeridos.",
        "La ficha de marca IE01 identifica batería y pantalla; JD 107 tiene una publicación comercial que anuncia doble pistón.",
        "No se ordena rapidez por caudal anunciado. JD requiere corriente, ciclo y conexión; IE01 requiere autonomía bajo carga y configuración.",
        ["IE01 o JD 107 en la unidad", "Conexión, corriente y ciclo o batería", "Presión del vehículo, manguera y adaptadores"],
        [("https://meli.la/2m7TJWQ", "Consultar Nictom IE01 a batería"), ("https://meli.la/274KM8a", "Consultar JD Extreme 107 de 12 V")],
        ("/compresores/12v-doble-piston/", "Ver qué documentación pedir para JD")),
    "/sierras/caladoras/": note(
        "BES603: contrastá primero el sufijo",
        "Para evaluar una caladora con regulación de velocidad cuando su variante coincide con la documentación de tu tarea.",
        "BES603-B2 documenta hasta 65 mm en madera y 6 mm en metal; el filtro de acero conserva solo las Einhell con ese material identificado.",
        "El aviso identifica BES603 sin confirmar B2. No se garantizan acero, acabado ni kit por el código base o por estar bajo un máximo.",
        ["Sufijo B2, 220 V y manual de la unidad", "Material, espesor y hoja admitidos", "Hoja T, regulación, contenido y garantía local"],
        [("https://meli.la/1ntghna", "Consultar y confirmar variante BES603")],
        ("/sierras/caladoras-black-decker/", "Comparar variantes Black+Decker")),
    "/generadores/comparativa-general/": note(
        "Tres ofertas, distintas escalas de carga",
        "Para consultar un generador identificado después de reunir marcha, arranque y alimentación de tus cargas.",
        "GPK980 es una referencia pequeña; GPK2200 deja nominal pendiente y Philco anuncia nominal en W. El artículo separa esas condiciones y su respaldo comercial.",
        "No sustituyen automáticamente los Honda/Gamma de la tabla. No se convierten kVA a W sin factor de potencia ni se dimensiona desde máximos.",
        ["Modelo, nominal y manual de la unidad", "Marcha/arranque, tensión y fase de cada carga", "Combustible, precio, contenido y garantía"],
        [("https://meli.la/2jcLSy1", "Consultar Pektra GPK980"), ("https://meli.la/2bL6gVj", "Consultar Pektra GPK2200"), ("https://meli.la/1nUAUuv", "Consultar Philco GE-PH2500ALP")],
        ("/generadores/para-casa/", "Preparar el inventario de cargas")),
    "/generadores/precios/": note(
        "Cotizá la configuración que responde a tu carga",
        "Para obtener importes confirmados de las publicaciones Pektra/Philco registradas, en una sección distinta de los PVP Lüsqtoff históricos.",
        "Los enlaces permiten pedir precio, vendedor y configuración para completar la calculadora con datos propios.",
        "No se recotizaron estos referidos ni se confirmó stock. Los PVP Lüsqtoff del 27/09/2026 no son sus precios ni validan equivalencia entre equipos.",
        ["Modelo y nominal en la misma unidad", "Fecha/hora, vendedor y precio contado/financiado", "Envío, extras, stock observado y garantía"],
        [("https://meli.la/2jcLSy1", "Consultar precio de GPK980"), ("https://meli.la/2bL6gVj", "Consultar precio de GPK2200"), ("https://meli.la/1nUAUuv", "Consultar precio de Philco")],
        ("/generadores/comparativa-general/", "Elegir primero por carga y documentación")),
})


def render_buying_note(article, product_facts):
    item = BUYING_NOTES.get(article["url"])
    if not item:
        return ""
    links = []
    sources = []
    for url, label in item["urls"]:
        facts = product_facts[url]
        links.append(f'<a class="buying-link" href="{escape(url, quote=True)}" target="_blank" rel="nofollow sponsored noopener noreferrer" data-affiliate-placement="editorial-choice">{escape(label)} ↗</a>')
        sources.append(f'<a href="{escape(facts["source"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(facts["brand"] + " " + facts["model"])} · {escape(facts["source_type"])}</a>')
    alt_url, alt_label = item["alternative"]
    badge = "ELECCIÓN POR CONFIGURACIÓN" if item["recommend"] else "OFERTA PARA CONTRASTAR"
    checks = "".join(f'<li>{escape(check)}</li>' for check in item["checks"])
    return f'''<aside class="buying-note" aria-labelledby="buying-title" data-buying-status="{"choice" if item["recommend"] else "check"}">
      <div class="buying-intro"><span class="resource-kicker">{badge} · TALLERLAB</span>
        <h2 id="buying-title">{escape(item["title"])}</h2><p>{escape(item["fit"])}</p></div>
      <div class="buying-reasons"><p><strong>Motivo de la selección</strong>{escape(item["reason"])}</p>
        <p><strong>Cuándo cambia la decisión</strong>{escape(item["limits"])}</p></div>
      <div class="buying-checks"><h3>Antes de avanzar</h3><ul>{checks}</ul></div>
      <div class="buying-actions">{"".join(links)}<a class="buying-alternative" href="{escape(alt_url, quote=True)}">{escape(alt_label)} →</a></div>
      <p class="buying-sources">Respaldo de la referencia comercial: {" · ".join(sources)}. <a href="#fuentes-consultadas">Documentación de la comparación</a>.</p>
      <p class="buying-disclosure">Enlace de afiliado: TallerLab puede recibir una comisión. Priorizamos la opción enlazada cuando encaja con tu uso y su documentación; precio, stock, variante y vendedor se comprueban en la publicación.</p>
    </aside>'''
