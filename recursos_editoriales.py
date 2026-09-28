"""Recursos de decisión redactados por URL sobre documentación ya citada.

Las cifras conservan modelo, condición y límites. No son ensayos propios.
"""
from html import escape
import json
from recursos_compra import EXTRA_RESOURCES
from recursos_uso import USE_RESOURCES


def table(title, lead, headers, rows, note):
    return dict(kind="table", title=title, lead=lead, headers=headers, rows=rows, note=note)


def selector(title, lead, question, options, note):
    return dict(kind="selector", title=title, lead=lead, question=question, options=options, note=note)


def calculator(kind, title, lead, fields, note):
    return dict(kind=kind, title=title, lead=lead, fields=fields, note=note)


def field(key, label, value, unit, minimum=0):
    return dict(key=key, label=label, value=value, unit=unit, minimum=minimum)


RESOURCES = {
    "/amoladoras/de-banco/": table(
        "La misma muela de 150 mm puede tener otro ancho",
        "Si estás reponiendo una muela, el diámetro exterior deja dos candidatos. El ancho y el régimen documentado vuelven a separarlos.",
        ["Comprobación", "Bosch GBG 35-15", "Lüsqtoff AB-375", "Decisión que cambia"],
        [["Diámetro", "150 mm", "150 mm", "Coinciden solo en este campo"], ["Ancho", "20 mm", "16 mm", "4 mm de diferencia; no asumir el mismo repuesto"], ["Velocidad en vacío", "3.000 rpm a 50 Hz", "2.950 rpm", "Revisar rpm admisibles de la muela"], ["Régimen", "S2: 60 min según manual", "No informado en ficha", "El dato Bosch no se traslada al AB-375"]],
        "El orificio, la fijación y la aplicación de la muela requieren comprobación adicional. La diferencia de peso no demuestra estabilidad instalada."),
    "/amoladoras/disco-flap/": selector(
        "Buscá el código del flap, no solo el grano",
        "Dentro de X571 cambian forma y grano. Este recorrido separa las variantes cuyo límite de rpm está documentado en la guía.",
        "¿Qué forma y grano necesitás comprobar?",
        [["Recto, grano 40", "Bosch 2 608 607 322", "115 / 22,23 mm; 13.300 rpm publicadas. Confirmar acero/material y apoyo en su ficha."], ["Recto, grano 80", "Bosch 2 608 607 324", "Mismas dimensiones y límite publicado que 322; cambia el grano, sin ensayo de acabado equivalente."], ["Angular T29, grano 40", "Bosch 2 608 619 008", "La revisión no reúne un límite de rpm para esta variante. Pedí la etiqueta exacta; no heredes 13.300 rpm de otro código."], ["Angular T29, grano 80", "Bosch 2 608 619 010", "115 / 22,23 mm; 13.300 rpm publicadas. Comprobar que guarda y apoyo admitan esa forma."]],
        "La selección identifica una referencia documental; no prescribe un grano universal ni predice el acabado."),
    "/amoladoras/disco-de-desbaste/": table(
        "Corte y desbaste: dos discos que no se sustituyen",
        "El agujero de 22,23 mm y el diámetro de 115 mm coinciden. Esa coincidencia geométrica no hace intercambiables las operaciones.",
        ["Campo", "PRO Metal 2 608 600 218", "PRO Metal 2 608 619 252"],
        [["Operación declarada", "Desbaste de metal", "Corte de metal"], ["Diámetro / agujero", "115 / 22,23 mm", "115 / 22,23 mm"], ["Espesor", "6 mm", "1,6 mm"], ["Relación calculada", "6 ÷ 1,6 = 3,75", "Base de comparación: 1,6 mm"]],
        "La razón de espesores es aritmética; no mide resistencia ni autoriza esfuerzo lateral sobre el disco de corte."),
    "/amoladoras/recta/": calculator(
        "rpm", "Un filtro de velocidad antes de elegir la fresa",
        "Las fichas de GGS 28 L y GD0600 declaran 33.000 y 25.000 rpm en vacío. Contrastá el máximo del accesorio con el del equipo que realmente tenés.",
        [field("tool", "Velocidad máxima de la herramienta", 33000, "rpm", 1), field("accessory", "Máximo marcado en el accesorio", 25000, "rpm", 1)],
        "Este filtro solo compara velocidades. Pinza, diámetro de vástago, material y accesorio admitido también deben coincidir con el manual."),
    "/amoladoras/discos/": selector(
        "Operación → material → referencia para comprobar",
        "Cambiar de cortar a desbastar exige cambiar de aplicación, aunque el disco mida lo mismo. Empezá por la operación concreta.",
        "¿Qué trabajo vas a contrastar?",
        [["Cortar metal", "PRO Metal 2 608 619 252", "115 × 1,6 × 22,23 mm. Código de corte; no usar como disco de desbaste."], ["Desbastar metal", "PRO Metal 2 608 600 218", "115 × 6 × 22,23 mm. Revisar material admitido y guarda en las instrucciones."], ["Lijar/desbastar acero", "Flap PRO X571 2 608 607 322", "Grano 40, 115 / 22,23 mm. La forma de apoyo y rpm se comprueban aparte."], ["Cortar hormigón", "PRO Concrete 2 608 602 651", "115 / 22,23 mm; segmento 12 mm. Aplicación declarada: hormigón."], ["Cortar azulejo", "PRO Ceramic 2 608 602 478", "115 × 1,4 × 22,23 mm. La ficha de azulejo no prueba compatibilidad con vidrio."]],
        "Referencias documentadas de Bosch, no una lista universal. El diámetro común no autoriza intercambiar materiales u operaciones."),
    "/compresores/para-auto/": selector(
        "La primera decisión del inflador es la conexión",
        "Entre las cuatro opciones hay batería incorporada y 12 V. Doble pistón describe construcción; no reemplaza la comprobación de alimentación.",
        "¿Qué dato tenés confirmado?",
        [["Quiero evitar la toma de 12 V", "Nictom IE01: revisar batería y controles", "La marca anuncia batería incorporada y pantalla digital. Pedí manual, configuración y autonomía bajo carga; 16 L/min máximos no ordena rapidez."],
         ["Solo sé que mi auto tiene una toma de 12 V", "Falta comprobar corriente y conexión", "MCL150-8 y JD 107 declaran doble pistón; AV000009 anuncia 23 A. Cotejá consumo, fusible y manual del vehículo e inflador."],
         ["Ya confirmé la conexión eléctrica", "Buscá la presión del vehículo", "Usá etiqueta/manual del vehículo y condición de carga. Los 150 psi del inflador no son el objetivo del neumático."],
         ["Quiero elegir por rapidez", "Los caudales no permiten ordenar tiempos", "Las cuatro fuentes no publican flujo a igual presión ni ensayo común. Compará conexión, ciclo, controles y accesorios."]],
        "El recorrido organiza comprobaciones. No fija presiones de neumáticos ni convierte caudal anunciado en tiempo de inflado."),
    "/compresores/50-litros/": calculator(
        "air", "¿El caudal de salida alcanza para tu herramienta?",
        "Para TE-AC 270/50 Silent hay un dato utilizable: 98 L/min a 7 bar. En las fichas Gamma y Lüsqtoff comparadas falta salida a esa misma presión.",
        [field("supply", "Caudal de salida documentado", 98, "L/min", 1), field("supplyPressure", "Presión de ese dato", 7, "bar", .1), field("demand", "Consumo de la herramienta", 100, "L/min", 1), field("demandPressure", "Presión del consumo", 7, "bar", .1)],
        "Usá caudal de salida, no aspiración. Ejemplo editable, no recomendación de combinación: faltan ciclo de trabajo, pérdidas y simultaneidad."),
    "/compresores/manguera/": selector(
        "Leé la tabla Parker por tramo y conexión",
        "El tamaño de la rosca no expresa el diámetro interior. En la tabla citada, al pasar a 10–20 m cambia el mínimo interior indicado.",
        "Elegí la fila del documento que querés consultar",
        [["1/4 in · 0–10 m", "Interior mínimo de tabla: 7 mm", "480 L/min a 6 bar; presión mínima de tabla 4 bar."], ["1/4 in · 10–20 m", "Interior mínimo de tabla: 8 mm", "480 L/min a 6 bar; 1 mm más que el tramo corto."], ["3/8 in · 0–10 m", "Interior mínimo de tabla: 10 mm", "1.100 L/min a 6 bar; presión mínima de tabla 4 bar."], ["3/8 in · 10–20 m", "Interior mínimo de tabla: 12 mm", "1.100 L/min a 6 bar; 2 mm más que el tramo corto."], ["1/2 in · 0–10 m", "Interior mínimo de tabla: 12 mm", "2.000 L/min a 6 bar; presión mínima de tabla 4 bar."], ["1/2 in · 10–20 m", "Interior mínimo de tabla: 14 mm", "2.000 L/min a 6 bar; 2 mm más que el tramo corto."]],
        "Consulta de esa tabla Parker, no dimensionamiento universal. Revisá alcance del documento, caudal requerido y presión nominal de todos los componentes."),
    "/compresores/para-pintar/": table(
        "La resta que parece alcanzar, pero compara datos distintos",
        "La admisión del BTA 25 L es 206 L/min. Restarle el consumo de una pistola genera un número, pero no prueba que el compresor entregue ese aire.",
        ["Cruce documental", "Resta nominal", "¿Permite validar suministro?"],
        [["206 L/min de admisión − AS-1021 (≈85 L/min)", "≈121 L/min", "No: falta salida del compresor a la presión de uso"], ["206 − ASP1070 (119–201 L/min)", "87 a 5 L/min", "No: admisión y consumo siguen sin ser equivalentes"], ["Presiones AS-1021 / ASP1070", "10–40 / 29–51 psi", "Confirmar presión de consumo para cada punto del rango"]],
        "206 − 201 = 5 L/min; la resta no representa reserva útil. No extrapolar desde HP o capacidad del tanque. Fuente: catálogo BTA citado en la guía."),
    "/compresores/kits-aerografo/": table(
        "Desarmá el kit antes de comparar el precio",
        "AP8 es un conjunto de aerógrafo y accesorios. La documentación de Badger 180-15 describe otro producto; no acredita un paquete compatible entre ambos.",
        ["Componente", "BTA AP8: lista de contenido", "Dato para comprar por separado"],
        [["Aerógrafo", "Incluido", "Boquilla, acción y repuestos del código"], ["Manguera / conector / soporte", "Incluidos", "Rosca e interfaz exactas"], ["Compresor", "No incluido", "Salida a presión y consumo de AP8; ese consumo no está documentado aquí"], ["Filtro / regulador", "No identificado en esa lista", "Roscas, rango y contenido de la oferta"]],
        "Badger 180-15 declara 20–23 L/min, pero el dato ausente del AP8 impide confirmar la pareja. La sugerencia de 2 HP no sustituye el consumo de aire."),
    "/hidrolavadoras/comparativa-general/": table(
        "Eléctricas: una unidad de caudal, distintas condiciones",
        "Normalizamos las referencias Gamma y agregamos las dos eléctricas enlazadas. Cada campo conserva el significado de su fuente.",
        ["Código", "Servicio / máxima", "Caudal original", "L/min"],
        [["G2509AR · 127", "65 / 100 bar", "330 L/h", "5,50 calculados"],
         ["G2513AR · 130", "90 / 130 bar", "360 L/h", "6,00 calculados"],
         ["G2514AR · 150", "100 / 150 bar", "400 L/h", "6,67 calculados"],
         ["G2515AR · 170", "No localizado / 170 bar", "400 L/h", "6,67 calculados"],
         ["Lüsqtoff HL100-7", "70 nominales / 100 máx. bar", "5,5 L/min; condición no precisada", "5,50 en ficha"],
         ["Logus HL-105", "Nominal no localizada / 105 máx. bar", "No localizado", "No calculable"]],
        "L/min = L/h ÷ 60. Normalizar unidades no iguala condiciones ni prueba limpieza. La Logus GHL150 a nafta se evalúa por separado en el artículo."),
    "/hidrolavadoras/inalambricas/": table(
        "Qué podés comparar de las baterías y qué queda sin resolver",
        "Bosch publica una duración para su configuración de 36 V y 4 Ah. El kit Lüsqtoff aporta dos baterías, pero no un ensayo equivalente de duración.",
        ["Dato", "UniversalAquatak 36V-100", "LAPL3.6-8BK", "Lectura para decidir"],
        [["Configuración citada", "36 V · 4 Ah", "18 V · dos baterías de 2 Ah", "Cantidad y Ah no fijan tiempo de limpieza"], ["Duración", "45 min publicados", "No publicada", "No calcular ventaja de autonomía"], ["Presión máxima", "100 bar", "30 bar", "Máximos de fichas distintas"], ["Caudal", "1,7–3,1 L/min", "Máx. 3,6 L/min", "No emparejar máximos como puntos simultáneos"]],
        "La autonomía Bosch corresponde al kit citado. Faltan protocolo compartido y autonomía Lüsqtoff; no completar esos datos multiplicando baterías."),
    "/hidrolavadoras/karcher/": table(
        "K2 a K5: identificá el SKU antes de normalizar",
        "Las fichas argentinas mezclan bar y psi, y publican distintas longitudes de manguera. La conversión de K5 ayuda a leer la unidad, sin convertir el listado en un ranking.",
        ["SKU / modelo", "Presión en fuente", "Lectura en bar", "Caudal / manguera"],
        [["19943220 · K2", "110 bar", "110; tipo según ficha", "280 L/h · 3 m"], ["93983550 · K3", "120 bar", "120; tipo según ficha", "330 L/h · no indicada"], ["16034020 · K4", "20–máx. 130 bar", "20–máx. 130", "Máx. 420 L/h · 8 m"], ["93982950 · K5", "2.100 psi", "≈144,8; tipo según ficha", "420 L/h · 6 m"]],
        "2.100 psi × 0,0689476 ≈ 144,8 bar. La conversión no identifica presión de servicio ni autoriza trasladar datos a kits de otro mercado."),
    "/hidrolavadoras/lusqtoff/": calculator(
        "water", "Convertí el caudal de trabajo en volumen de agua",
        "HL-120 publica 5,5 L/min de trabajo y 6,8 máximos; HL130-9, 7,5 y 9. HL100-7 publica 5,5 L/min sin precisar condición; no hereda la del HL-120.",
        [field("flow", "Caudal documentado elegido", 5.5, "L/min", .1), field("minutes", "Minutos con salida de agua activa", 10, "min", .1)],
        "Volumen teórico = caudal × minutos. El ejemplo conserva el caudal de trabajo de HL-120; no calcula tiempo de limpieza ni identifica el punto de caudal de HL100-7."),
    "/hidrolavadoras/gamma/": table(
        "Gamma 150 y 170: la cifra del nombre no completa el manual",
        "Ambas referencias publican 400 L/h. La diferencia visible de presión admisible deja sin resolver la presión de servicio del 170.",
        ["Campo", "G2514AR · 150", "G2515AR · 170", "Conclusión documental"],
        [["Caudal publicado", "400 L/h", "400 L/h", "Diferencia publicada: 0 L/h"], ["Máxima admisible", "150 bar", "170 bar", "+20 bar admisibles; no es diferencia de servicio"], ["Máxima de servicio", "100 bar", "No localizada", "No permite calcular mejora de presión de trabajo"], ["Potencia", "1.800 W", "No localizada", "No completar por el número 170"]],
        "La igualdad de caudal declarado no prueba igualdad de limpieza. Se comparan códigos y documentos, no resultados de ensayo."),
    "/sierras/circulares/": calculator(
        "cut", "¿Tu espesor entra en los máximos publicados a 90°?",
        "SC16-AR documenta 65 mm, GKS 150 64 mm y CSL1500-8 63,5 mm. Un espesor cercano al límite obliga a revisar hoja y ángulo en el manual.",
        [field("thickness", "Espesor de la pieza a contrastar", 64, "mm", .1)],
        "Filtro documental solo a 90°; no calcula corte a inglete, velocidad ni precisión. La SC16-AR discrepa entre manual (190 mm de disco) y ficha (180 mm)."),
    "/sierras/sensitivas/": selector(
        "Buscá la capacidad de tu perfil, no la mayor cifra",
        "Las tablas CM-14K y TS223558 no describen las mismas geometrías en todos sus renglones. Elegí el perfil para ver qué comparación permite la documentación.",
        "¿Qué sección querés comprobar?",
        [["Tubo redondo", "CM-14K: 110 mm · TS223558: 100 mm", "Diferencia publicada de 10 mm. Confirmar material, sujeción y ángulo que corresponden a la cifra."], ["Perfil cuadrado", "Ambas: 100 × 100 mm", "La coincidencia de capacidad no acredita igual terminación, rebaba ni duración del disco."], ["Ángulo / rectangular", "Las filas describen geometrías distintas", "CM-14K informa ángulo 120 × 120 mm; TS223558 informa rectangular 120 × 100 mm. No tratar esas dos filas como el mismo perfil."]],
        "Los máximos de catálogo no validan cualquier pieza o recubrimiento. No se deduce capacidad a 45° desde la de otro ángulo."),
    "/sierras/sable/": calculator(
        "weight", "Sumá la batería antes de comparar el peso",
        "La GSA 18V-24 figura con 1,7 kg sin batería; GSA 1100 E, con 3,6 kg publicados. El peso del pack cambia la comparación que vas a transportar.",
        [field("battery", "Masa documentada de tu batería", .6, "kg", .01)],
        "La batería de 0,6 kg es un supuesto editable, no un dato de pack Bosch. Se suma 1,7 kg + pack y se compara con 3,6 kg; no evalúa ergonomía ni accesorios añadidos."),
    "/sierras/caladoras/": calculator(
        "jigsaw", "Filtrá el espesor dentro del material documentado",
        "Los tres modelos documentan madera. Para acero se filtran solo TC-JS 85 y TE-JS 100: los 6 mm de BES603-B2 se publican como metal, sin identificar acero.",
        [field("thickness", "Espesor que querés contrastar", 70, "mm", .1)],
        "BES603-B2 queda fuera del filtro de acero hasta documentar ese material. Confirmá sufijo y 220 V de la BES603 ofrecida; el máximo no garantiza acabado ni admite cualquier hoja."),
    "/sierras/sierra-sin-fin-para-madera/": table(
        "Altura, garganta y longitud de hoja no miden lo mismo",
        "La compra de una sin fin exige tres medidas independientes. El rótulo de 200 mm del SFL300-8 no alcanza para completar una altura de corte.",
        ["Referencia", "Altura de pieza", "Garganta", "Hoja"],
        [["SFL250-8", "80 mm", "200 mm", "1.400 × 6,5 × 0,35 mm"], ["SFL300-8", "No confirmada", "No confirmada", "No confirmada"], ["SFL1100-9", "206 mm", "305 mm", "Longitud 2.360 mm"]],
        "Altura: espesor de pieza; garganta: separación hoja–columna; longitud de hoja: circuito del equipo. SFL250-8 figura discontinuada en la fuente revisada."),
    "/taladros/inalambricos/": table(
        "Primero el mandril y la función; después la etiqueta de voltaje",
        "La comparación distingue las tres fichas primarias del kit Ingco anunciado. No se normaliza una tensión cuya condición no está confirmada.",
        ["Modelo", "Tensión para leer", "Mandril", "Pregunta que resuelve"],
        [["GSR 120-LI", "12 V de plataforma", "Hasta 10 mm", "¿El vástago entra en el mandril?"],
         ["TE-CD 18/40 Li", "18 V de plataforma", "Hasta 13 mm", "¿Necesitás sujetar más de 10 mm?"],
         ["LD120", "20 V MAX · 18 V nominales", "10 mm", "¿Comparás máximo con nominal?"],
         ["Ingco CIDLI20668-4 · aviso", "20 V anunciados; condición pendiente", "13 mm anunciados", "Percutor con dos baterías: confirmar Ah, kit y manual -4"]],
        "La tensión no confirma baterías intercambiables. Los tres primeros registros no documentan percusión; Ingco la anuncia. La ficha del modelo base no acredita automáticamente el kit -4."),
    "/taladros/rotomartillos/": calculator(
        "hammer", "Buscá el diámetro en hormigón, antes de ordenar joules",
        "Los máximos publicados son 22 mm para GBH 220, 26 mm para GBH 2-26 DRE y 28 mm para TE-RH 28 5F. El filtro muestra qué límites incluyen tu diámetro.",
        [field("diameter", "Diámetro del agujero a contrastar", 24, "mm", .1)],
        "Los tres registros son SDS plus. Estar bajo el máximo no garantiza uso continuo, avance ni compatibilidad con una corona; confirmar accesorio y modo exactos."),
    "/taladros/percutores/": selector(
        "El encastre y la unidad publicada resuelven dudas distintas",
        "27.000 impactos/min y 2,0 J no se convierten entre sí. El kit Ingco es otra opción, con capacidades por material pendientes.",
        "¿Qué necesitás identificar?",
        [["Tengo una broca cilíndrica", "Revisá mandril y material", "GSB 18V-50 declara mandril de 13 mm. La sujeción no acredita que la broca admita percusión."],
         ["Busco un kit percutor a batería", "Ingco CIDLI20668-4: cerrar configuración", "El aviso anuncia mandril de 13 mm y dos baterías. Pedí manual -4, Ah, cargador y capacidades; no hereda la ficha Bosch."],
         ["Tengo un accesorio SDS plus", "Necesitás portaherramientas SDS plus", "GBH 220 declara SDS plus y 22 mm máximo en hormigón. SDS max y SDS plus son encastres distintos."],
         ["Quiero comparar potencia de golpe", "Falta una magnitud común", "GSB expresa frecuencia y GBH energía. Consultá capacidades por material y diámetro; no se convierten impactos/min en joules."]],
        "Se identifican requisitos documentales; no se predice velocidad ni se prescribe perforación. El Ingco anunciado no sustituye automáticamente un SDS."),
    "/taladros/taladro-de-banco/": table(
        "Un mandril mayor no implica más recorrido",
        "Las fichas Lüsqtoff y la oferta Omaha aportan campos distintos. Conservamos visibles los datos comerciales y los que faltan.",
        ["Requisito", "TB-16", "TBL710-9D", "Omaha AB550161K · aviso"],
        [["Vástago", "Mandril 16 mm", "Mandril 1,5–13 mm", "Hasta 16 mm anunciados"],
         ["Recorrido", "65 mm", "0–100 mm", "No confirmado"],
         ["Potencia / régimen", "450 W nominales", "710 W nominales; 900 W S2 de 5 min", "550 W anunciados; régimen pendiente"],
         ["Velocidades", "12; 300–2.550 rpm", "170–880 / 490–2.600 rpm", "Cinco; rango pendiente"]],
        "Sujeción, recorrido y capacidad de agujero son campos separados. Omaha no tiene una ficha primaria contrastada aquí; la matriz no mide rigidez, precisión o velocidad."),
    "/taladros/atornilladores-de-impacto/": selector(
        "Punta hexagonal o dado: elegí por la interfaz",
        "GDR y GDX pueden parecer similares por sus 200 Nm de apriete. El GDX suma cuadrado de 1/2 in, una diferencia funcional que el torque no cuenta.",
        "¿Qué accesorio necesitás sujetar?",
        [["Punta hexagonal de 1/4 in", "GDR 18V-200, GDX 18V-200 y DCF887 documentan esa interfaz", "Confirmar retención, dimensiones y clasificación de impacto de la punta. GDR y DCF887 no documentan cuadrado directo en esta matriz."], ["Dado de cuadrado de 1/2 in", "GDX 18V-200 documenta cuadrado y hexagonal", "No atribuir cuadradillo a GDR o DCF887. Comprobar retención y capacidad del dado exacto."], ["Quiero comparar 350 contra 205 Nm", "Son magnitudes diferentes", "350 Nm de GDX es arranque; 200–205 Nm de los otros registros es apriete. No convertir esa diferencia en un ranking."]],
        "Identificar encastre no prescribe torque final ni convierte el aparato en una llave dinamométrica."),
    "/soldadoras/electrodo-7018/": table(
        "Cruce de dos hojas: rango del electrodo y ciclo de la fuente",
        "Atom Arc 7018 publica rangos por diámetro. HandyArc 162i publica 160 A al 20 %, 92 A al 60 % y 72 A al 100 %; no existe una sola corriente continua de 160 A.",
        ["Atom Arc 7018", "Rango de ficha", "Intersección con 72 A / 100 %", "Intersección con 160 A / 20 %"],
        [["2,4 mm", "70–110 A", "72 A dentro del intervalo", "Máximo 160 A por encima del intervalo"], ["3,2 mm", "90–160 A", "72 A por debajo", "160 A dentro del intervalo"], ["4,0 mm", "130–220 A", "72 A por debajo", "160 A dentro; no cubre hasta 220 A"]],
        "Intersección aritmética de fichas regionales, no procedimiento ni validación de junta. El rango pertenece a Atom Arc 7018, no a todos los E7018."),
    "/soldadoras/lusqtoff/": selector(
        "El proceso descarta antes que el amperaje del nombre",
        "En esta muestra documental hay una dual de tres procesos, una tubular discontinuada y un kit MMA. Elegir «120» o «100» sin el código omite esas diferencias.",
        "¿Qué proceso querés comprobar?",
        [["MMA con electrodo", "SML120-8D o MEGAIRON100-8, según sus fichas", "SML120-8D declara 20–100 A MMA; MEGAIRON100-8, 105 A al 30 %. No igualar ciclos sin temperatura y condiciones."], ["Tubular autoprotegido / FLUX", "SML120-8D y SML130-7 documentan ese proceso", "SML130-7 figura discontinuada y declara ciclos a 40 °C; SML120-8D informa 25 % a 25 °C. Esas condiciones no son equivalentes."], ["Lift TIG", "SML120-8D lo declara", "Rango 20–100 A; confirmar accesorios requeridos. El dato no autoriza atribuir TIG AC a todos los equipos de la gama."]],
        "Se identifica proceso y límites de documentación, sin afirmar stock ni rendimiento del cordón."),
    "/soldadoras/soldadora-de-punto/": table(
        "400 V y 3 %: dos datos que cambian la compra",
        "Los dos Telwin citados son equipos de carrocería. La comparación útil empieza por alimentación, función y acceso a la pieza, antes de mirar corriente de punto.",
        ["Código", "Red declarada", "Dos chapas: máximo", "Peso / ciclo"],
        [["823232 · Car Spotter 5500", "400 V, dos fases, 50/60 Hz", "1,5 + 1,5 mm", "25 kg · 3 %"], ["823195 · Spotter 9000", "400 V, dos fases, 50/60 Hz", "3 + 3 mm", "78 kg · 3 %"], ["Diferencia calculada", "Coincidencia de tensión, no validación de la red", "+1,5 mm por chapa en el máximo publicado", "+53 kg; el ciclo publicado coincide"]],
        "El máximo de dos chapas no valida material, recubrimiento o geometría. Verificar manual, herramientas opcionales y suministro con responsable técnico."),
    "/soldadoras/soldadora-mig-con-gas/": table(
        "La bobina es solo una parte de la compatibilidad",
        "La ESAB admite bobina hasta 5 kg; MIGDUAL200-9 informa porta rollo de 5–15 kg. Antes de comparar precio, pedí la cadena completa de alimentación y gas.",
        ["Elemento a emparejar", "HandyArc MIG 160i", "MIGDUAL200-9", "Evidencia necesaria"],
        [["Bobina", "Hasta 5 kg", "5–15 kg", "Dimensiones y adaptación de la bobina concreta"], ["Diámetro de alambre", "Hasta 0,9 mm según ficha", "Confirmar en manual", "Rodillo y punta para el mismo diámetro"], ["Sistema de gas", "Ficha admite tubular con/sin gas", "Lista incluye manguera", "Consumible, polaridad y regulador; una manguera no confirma el kit completo"]],
        "Esta tabla ordena comprobaciones de interfaces. No elige mezcla de gas, parámetros ni una combinación certificada para una junta."),
    "/soldadoras/guantes/": table(
        "Leé código, construcción y norma juntos",
        "Los guantes ESAB de esta comparación publican la misma cadena EN 407, pero construcción y valores EN 388 distintos. Eso impide elegir protección solo por peso o aspecto.",
        ["Producto / código", "Construcción", "Declaraciones publicadas", "Peso"],
        [["Heavy Duty Black · 0615465", "Refuerzo de palma; forro hasta puño", "EN 407 413X4X · EN 12477 A · EN 388 4134X", "350 g"], ["TIG Basic · 0700500460", "Sin forro; cuero vacuno y cabra", "EN 407 413X4X · EN 12477 A · EN 388 2122X", "160 g"]],
        "La diferencia de 190 g no mide protección. Conservar exactamente las normas declaradas; no reinterpretar el nombre TIG como certificación tipo B. Cotejar etiqueta y declaración de conformidad."),
    "/generadores/comparativa-general/": table(
        "Nominal contra máxima, dentro de la misma unidad",
        "Las diferencias Honda/Gamma son cálculos de fichas. Las ofertas pequeñas se identifican sin equipararlas ni completar nominales ausentes.",
        ["Código / respaldo", "Nominal", "Máxima", "Lectura documental"],
        [["Honda EG6500CXS · ficha", "5,0 kVA", "5,5 kVA", "0,5 kVA · 10,0 % sobre nominal"],
         ["Honda EZ6500CXS · ficha", "5,5 kVA", "6,5 kVA", "1,0 kVA · 18,2 %"],
         ["Gamma GE3481AR · ficha", "5,5 kW", "6,0 kW", "0,5 kW · 9,1 %"],
         ["Pektra GPK980 · aviso", "650 W anunciados", "720 W anunciados", "Equipo pequeño; confirmar placa/manual"],
         ["Pektra GPK2200 · aviso", "No confirmada", "2,2 kVA anunciados", "No dimensionar desde el máximo"],
         ["Philco GE-PH2500ALP · aviso", "2.500 W anunciados", "2.800 W anunciados", "Contrastá manual del código"]],
        "Porcentaje = (máxima − nominal) ÷ nominal × 100, para las fichas identificadas. No representa arranque validado; no se ordenan kVA y W como la misma unidad."),
    "/generadores/precios/": calculator(
        "cost", "Armá el costo final de dos ofertas comparables",
        "Los PVP Lüsqtoff conservan su captura del 27/09/2026. Pektra/Philco no se recotizaron: usá importes que hayas confirmado para equipos que cubran la misma necesidad.",
        [field("priceA", "Oferta A · precio confirmado", 0, "$"), field("shippingA", "Oferta A · envío", 0, "$"), field("extrasA", "Oferta A · extras necesarios", 0, "$"), field("priceB", "Oferta B · precio confirmado", 0, "$"), field("shippingB", "Oferta B · envío", 0, "$"), field("extrasB", "Oferta B · extras necesarios", 0, "$")],
        "Costo = precio + envío + extras, sin financiación ni mantenimiento. Confirmá fecha, vendedor y configuración. La suma no valida equivalencia entre equipos ni costo por watt máximo."),
    "/generadores/honda/": table(
        "EU22i y EU30is: cuánto cambia la ficha al subir de tamaño",
        "Los dos son inverter de 220 V monofásicos en la documentación citada. El incremento de potencia nominal viene acompañado de una diferencia importante de masa en seco.",
        ["Dato", "EU22i", "EU30is", "Diferencia calculada"],
        [["Potencia nominal", "1,8 kVA", "2,8 kVA", "+1,0 kVA"], ["Potencia máxima", "2,2 kVA", "3,0 kVA", "+0,8 kVA"], ["Masa en seco", "21 kg", "59 kg", "+38 kg; sin combustible"]],
        "3,0 − 2,2 = 0,8 kVA (36,4 % sobre 2,2). Esta resta no determina autonomía ni ruido; no convierte kVA en kW ni incluye accesorios de transporte."),
    "/generadores/para-casa/": calculator(
        "house", "Inventario de cargas y escenario de un arranque",
        "Completá potencia de marcha y de arranque del aparato exacto. Se suman las cargas de marcha y se sustituye una por su arranque para explorar el pico de ese escenario.",
        [],
        "Datos ingresados por vos, en W. Pico explorado = suma de marcha + mayor diferencia (arranque − marcha), suponiendo un arranque a la vez. Sin factor universal, simultaneidad de arranques ni validación de la instalación; cotejar también VA, factor de potencia, tensión y manual."),
    "/generadores/inverter/": table(
        "Cuáles cifras de ruido admiten la misma comparación",
        "Ordenar 57, 68 y 75 dB sin distancia, carga y tipo de medición crearía una precisión aparente. La auditoría de condiciones conserva esas diferencias.",
        ["Referencia", "Cifra citada", "Distancia", "Carga / condición"],
        [["Honda EU22i", "57 dB(A)", "7 m", "Plena carga según Honda"], ["Lüsqtoff LGI3.5-8", "68 dB", "No publicada", "No publicada"], ["Lüsqtoff LGI3.8-8", "75 dB", "7 m", "Carga no precisada aquí"], ["LG3500EXI", "Sin dato comparable", "No publicada", "No publicada"]],
        "Coincidir en distancia no iguala carga ni ponderación A. Esta auditoría no genera un ranking de ruido ni afirma una THD que las fuentes no publican."),
    "/soldadura-electronica/estacion-de-soldadura/": selector(
        "Elegí la función que la estación realmente incluye",
        "El rango de 200–480 °C aparece para el cautín en estas fichas. Eso no significa que todas las estaciones incorporen aire caliente o igual control térmico.",
        "¿Qué función necesitás comprobar?",
        [["Solo cautín con regulación", "ES3L45-8 declara cautín regulable", "No declara pistola de aire caliente. Comprobar puntas compatibles y aclarar datos de entrada con su manual."], ["Cautín y aire caliente", "YiHUA 878D / 898D documentan ambas herramientas", "Aire 100–480 °C y cautín 200–480 °C; confirmar variante, tensión y accesorios. Las fichas agrupan códigos y no prueban el kit local."], ["Estabilidad de temperatura bajo carga", "El rango de ficha no responde esa pregunta", "Hace falta protocolo y medición en punta o aire; esta revisión no los reúne. No elegir precisión térmica por el rango máximo."]],
        "Selector de funciones documentadas, sin parámetros de trabajo para una placa ni comparación de ensayos térmicos."),
}


RESOURCES.update(EXTRA_RESOURCES)
RESOURCES.update(USE_RESOURCES)


def render_resource(article):
    resource = RESOURCES.get(article["url"])
    if not resource:
        return ""
    kind = resource["kind"]
    content = ""
    if kind == "table":
        head = "".join(f'<th scope="col">{escape(item)}</th>' for item in resource["headers"])
        rows = "".join('<tr>' + "".join(f'<{"th scope=\"row\"" if i == 0 else "td"}>{escape(value)}</{"th" if i == 0 else "td"}>' for i, value in enumerate(row)) + '</tr>' for row in resource["rows"])
        content = f'<div class="resource-table-scroll" tabindex="0" role="region" aria-label="{escape(resource["title"], quote=True)}"><table><caption>{escape(resource["title"])}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>'
    elif kind == "checklist":
        content = '<div class="resource-checklist">' + "".join(
            f'<label><input type="checkbox" data-resource-check="{i}"><span><strong>{escape(label)}</strong><span>{escape(why)}</span></span></label>'
            for i, (label, why) in enumerate(resource["checks"])
        ) + '</div>'
        content += '<div class="resource-result" role="status" aria-live="polite"><strong data-result-title>Registrá las comprobaciones realizadas</strong><p data-result-body>Marcá solo lo que cotejaste en los documentos de la unidad. La lista no valida automáticamente un montaje o una compra.</p></div><noscript><p>Sin JavaScript podés leer y marcar la lista; el resumen de pendientes no se actualiza.</p></noscript>'
    elif kind == "selector":
        options = "".join(f'<option value="{i}">{escape(option[0])}</option>' for i, option in enumerate(resource["options"]))
        content = f'<label class="resource-field">{escape(resource["question"])}<select data-resource-input="choice">{options}</select></label>'
        content += '<div class="resource-result" role="status" aria-live="polite"><strong data-result-title>' + escape(resource["options"][0][1]) + '</strong><p data-result-body>' + escape(resource["options"][0][2]) + '</p></div>'
        content += '<details class="resource-alternatives"><summary>Ver todas las alternativas documentadas</summary>' + "".join(f'<p><strong>{escape(label)} · {escape(title)}</strong><br>{escape(body)}</p>' for label, title, body in resource["options"]) + '</details>'
    else:
        content = '<div class="resource-fields">'
        for item in resource["fields"]:
            content += f'<label class="resource-field">{escape(item["label"])}<span><input type="number" inputmode="decimal" min="{item["minimum"]}" step="any" value="{item["value"]}" data-resource-input="{item["key"]}"><span>{escape(item["unit"])}</span></span></label>'
        content += '</div>'
        if kind == "jigsaw":
            content += '<label class="resource-field">Material de la ficha<select data-resource-input="material"><option value="wood">Madera</option><option value="steel">Acero</option></select></label>'
        if kind == "house":
            content += '<div class="resource-loads">'
            for i in range(3):
                content += f'<fieldset><legend>Carga {i + 1}</legend><label>Nombre<input type="text" data-load="name" placeholder="Nombre del aparato"></label><label>Marcha (W)<input type="number" min="0" step="any" data-load="run" placeholder="Dato de placa"></label><label>Arranque (W)<input type="number" min="0" step="any" data-load="start" placeholder="Dato documentado"></label></fieldset>'
            content += '</div><p class="resource-instruction">Completá al menos una carga; dejá las filas sin usar vacías. Si el manual confirma que arranque y marcha coinciden, ingresá el mismo valor.</p>'
        content += '<div class="resource-result" role="status" aria-live="polite"><strong data-result-title>Completá los datos para calcular</strong><p data-result-body>El resultado mostrará el cálculo y sus límites.</p></div><noscript><p>El cálculo requiere JavaScript. La fórmula y sus supuestos están explicados a continuación.</p></noscript>'
    config = json.dumps(resource, ensure_ascii=False).replace("<", "\\u003c")
    return f'''<section class="editorial-resource resource-{kind}" aria-labelledby="resource-title" data-resource-kind="{kind}">
      <span class="resource-kicker">{escape({"table": "CRUCE DE DOCUMENTOS", "selector": "RECORRIDO DE ELECCIÓN", "checklist": "COMPROBACIÓN PASO A PASO"}.get(kind, "CÁLCULO CON TUS DATOS"))} · TALLERLAB</span>
      <h2 id="resource-title">{escape(resource["title"])}</h2><p class="resource-lead">{escape(resource["lead"])}</p>
      {content}<p class="resource-method">{escape(resource["note"])}</p>
      <p class="resource-provenance">Análisis documental de TallerLab · <a href="#fuentes-consultadas">Documentos y límites de esta guía</a> · Revisión de fuentes: {escape(article["reviewed"])}. La pieza no representa una prueba física.</p>
      <script type="application/json" class="resource-config">{config}</script>
    </section>'''
