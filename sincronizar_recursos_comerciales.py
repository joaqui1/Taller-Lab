from pathlib import Path
import re

def replace_entry(text, key, replacement):
    pattern = r'    "' + re.escape(key) + r'": .*?(?=\n    "/|\n})'
    text, count = re.subn(pattern, replacement.rstrip(), text, count=1, flags=re.S)
    assert count == 1, key
    return text

entries = {
'/compresores/para-auto/': '''    "/compresores/para-auto/": selector(
        "La primera decisión del inflador es la conexión",
        "Entre las cuatro opciones hay batería incorporada y 12 V. Doble pistón describe construcción; no reemplaza la comprobación de alimentación.",
        "¿Qué dato tenés confirmado?",
        [["Quiero evitar la toma de 12 V", "Nictom IE01: revisar batería y controles", "La marca anuncia batería incorporada y pantalla digital. Pedí manual, configuración y autonomía bajo carga; 16 L/min máximos no ordena rapidez."],
         ["Solo sé que mi auto tiene una toma de 12 V", "Falta comprobar corriente y conexión", "MCL150-8 y JD 107 declaran doble pistón; AV000009 anuncia 23 A. Cotejá consumo, fusible y manual del vehículo e inflador."],
         ["Ya confirmé la conexión eléctrica", "Buscá la presión del vehículo", "Usá etiqueta/manual del vehículo y condición de carga. Los 150 psi del inflador no son el objetivo del neumático."],
         ["Quiero elegir por rapidez", "Los caudales no permiten ordenar tiempos", "Las cuatro fuentes no publican flujo a igual presión ni ensayo común. Compará conexión, ciclo, controles y accesorios."]],
        "El recorrido organiza comprobaciones. No fija presiones de neumáticos ni convierte caudal anunciado en tiempo de inflado."),''',
'/hidrolavadoras/comparativa-general/': '''    "/hidrolavadoras/comparativa-general/": table(
        "Eléctricas: una unidad de caudal, distintas condiciones",
        "Normalizamos las referencias Gamma y agregamos las dos eléctricas enlazadas. Cada campo conserva el significado de su fuente.",
        ["Código", "Servicio / máxima", "Caudal original", "L/min"],
        [["G2509AR · 127", "65 / 100 bar", "330 L/h", "5,50 calculados"],
         ["G2513AR · 130", "90 / 130 bar", "360 L/h", "6,00 calculados"],
         ["G2514AR · 150", "100 / 150 bar", "400 L/h", "6,67 calculados"],
         ["G2515AR · 170", "No localizado / 170 bar", "400 L/h", "6,67 calculados"],
         ["Lüsqtoff HL100-7", "70 nominales / 100 máx. bar", "5,5 L/min; condición no precisada", "5,50 en ficha"],
         ["Logus HL-105", "Nominal no localizada / 105 máx. bar", "No localizado", "No calculable"]],
        "L/min = L/h ÷ 60. Normalizar unidades no iguala condiciones ni prueba limpieza. La Logus GHL150 a nafta se evalúa por separado en el artículo."),''',
'/hidrolavadoras/lusqtoff/': '''    "/hidrolavadoras/lusqtoff/": calculator(
        "water", "Convertí el caudal de trabajo en volumen de agua",
        "HL-120 publica 5,5 L/min de trabajo y 6,8 máximos; HL130-9, 7,5 y 9. HL100-7 publica 5,5 L/min sin precisar condición; no hereda la del HL-120.",
        [field("flow", "Caudal documentado elegido", 5.5, "L/min", .1), field("minutes", "Minutos con salida de agua activa", 10, "min", .1)],
        "Volumen teórico = caudal × minutos. El ejemplo conserva el caudal de trabajo de HL-120; no calcula tiempo de limpieza ni identifica el punto de caudal de HL100-7."),''',
'/sierras/caladoras/': '''    "/sierras/caladoras/": calculator(
        "jigsaw", "Filtrá el espesor dentro del material documentado",
        "Los tres modelos documentan madera. Para acero se filtran solo TC-JS 85 y TE-JS 100: los 6 mm de BES603-B2 se publican como metal, sin identificar acero.",
        [field("thickness", "Espesor que querés contrastar", 70, "mm", .1)],
        "BES603-B2 queda fuera del filtro de acero hasta documentar ese material. Confirmá sufijo y 220 V de la BES603 ofrecida; el máximo no garantiza acabado ni admite cualquier hoja."),''',
'/taladros/inalambricos/': '''    "/taladros/inalambricos/": table(
        "Primero el mandril y la función; después la etiqueta de voltaje",
        "La comparación distingue las tres fichas primarias del kit Ingco anunciado. No se normaliza una tensión cuya condición no está confirmada.",
        ["Modelo", "Tensión para leer", "Mandril", "Pregunta que resuelve"],
        [["GSR 120-LI", "12 V de plataforma", "Hasta 10 mm", "¿El vástago entra en el mandril?"],
         ["TE-CD 18/40 Li", "18 V de plataforma", "Hasta 13 mm", "¿Necesitás sujetar más de 10 mm?"],
         ["LD120", "20 V MAX · 18 V nominales", "10 mm", "¿Comparás máximo con nominal?"],
         ["Ingco CIDLI20668-4 · aviso", "20 V anunciados; condición pendiente", "13 mm anunciados", "Percutor con dos baterías: confirmar Ah, kit y manual -4"]],
        "La tensión no confirma baterías intercambiables. Los tres primeros registros no documentan percusión; Ingco la anuncia. La ficha del modelo base no acredita automáticamente el kit -4."),''',
'/taladros/percutores/': '''    "/taladros/percutores/": selector(
        "El encastre y la unidad publicada resuelven dudas distintas",
        "27.000 impactos/min y 2,0 J no se convierten entre sí. El kit Ingco es otra opción, con capacidades por material pendientes.",
        "¿Qué necesitás identificar?",
        [["Tengo una broca cilíndrica", "Revisá mandril y material", "GSB 18V-50 declara mandril de 13 mm. La sujeción no acredita que la broca admita percusión."],
         ["Busco un kit percutor a batería", "Ingco CIDLI20668-4: cerrar configuración", "El aviso anuncia mandril de 13 mm y dos baterías. Pedí manual -4, Ah, cargador y capacidades; no hereda la ficha Bosch."],
         ["Tengo un accesorio SDS plus", "Necesitás portaherramientas SDS plus", "GBH 220 declara SDS plus y 22 mm máximo en hormigón. SDS max y SDS plus son encastres distintos."],
         ["Quiero comparar potencia de golpe", "Falta una magnitud común", "GSB expresa frecuencia y GBH energía. Consultá capacidades por material y diámetro; no se convierten impactos/min en joules."]],
        "Se identifican requisitos documentales; no se predice velocidad ni se prescribe perforación. El Ingco anunciado no sustituye automáticamente un SDS."),''',
'/taladros/taladro-de-banco/': '''    "/taladros/taladro-de-banco/": table(
        "Un mandril mayor no implica más recorrido",
        "Las fichas Lüsqtoff y la oferta Omaha aportan campos distintos. Conservamos visibles los datos comerciales y los que faltan.",
        ["Requisito", "TB-16", "TBL710-9D", "Omaha AB550161K · aviso"],
        [["Vástago", "Mandril 16 mm", "Mandril 1,5–13 mm", "Hasta 16 mm anunciados"],
         ["Recorrido", "65 mm", "0–100 mm", "No confirmado"],
         ["Potencia / régimen", "450 W nominales", "710 W nominales; 900 W S2 de 5 min", "550 W anunciados; régimen pendiente"],
         ["Velocidades", "12; 300–2.550 rpm", "170–880 / 490–2.600 rpm", "Cinco; rango pendiente"]],
        "Sujeción, recorrido y capacidad de agujero son campos separados. Omaha no tiene una ficha primaria contrastada aquí; la matriz no mide rigidez, precisión o velocidad."),''',
'/generadores/comparativa-general/': '''    "/generadores/comparativa-general/": table(
        "Nominal contra máxima, dentro de la misma unidad",
        "Las diferencias Honda/Gamma son cálculos de fichas. Las ofertas pequeñas se identifican sin equipararlas ni completar nominales ausentes.",
        ["Código / respaldo", "Nominal", "Máxima", "Lectura documental"],
        [["Honda EG6500CXS · ficha", "5,0 kVA", "5,5 kVA", "0,5 kVA · 10,0 % sobre nominal"],
         ["Honda EZ6500CXS · ficha", "5,5 kVA", "6,5 kVA", "1,0 kVA · 18,2 %"],
         ["Gamma GE3481AR · ficha", "5,5 kW", "6,0 kW", "0,5 kW · 9,1 %"],
         ["Pektra GPK980 · aviso", "650 W anunciados", "720 W anunciados", "Equipo pequeño; confirmar placa/manual"],
         ["Pektra GPK2200 · aviso", "No confirmada", "2,2 kVA anunciados", "No dimensionar desde el máximo"],
         ["Philco GE-PH2500ALP · aviso", "2.500 W anunciados", "2.800 W anunciados", "Contrastá manual del código"]],
        "Porcentaje = (máxima − nominal) ÷ nominal × 100, para las fichas identificadas. No representa arranque validado; no se ordenan kVA y W como la misma unidad."),''',
'/generadores/precios/': '''    "/generadores/precios/": calculator(
        "cost", "Armá el costo final de dos ofertas comparables",
        "La guía reúne ocho precios publicados consultados el 28/09/2026 y conserva una referencia PVP Lüsqtoff del día anterior. Cargá dos configuraciones que cubran la misma necesidad para sumar sus costos finales.",
        [field("priceA", "Oferta A · precio confirmado", 0, "$"), field("shippingA", "Oferta A · envío", 0, "$"), field("extrasA", "Oferta A · extras necesarios", 0, "$"), field("priceB", "Oferta B · precio confirmado", 0, "$"), field("shippingB", "Oferta B · envío", 0, "$"), field("extrasB", "Oferta B · extras necesarios", 0, "$")],
        "Costo = precio + envío + extras, sin costo financiero. Confirmá fecha, vendedor, modelo y configuración; compará nominales y requisitos de carga antes de usar el resultado."),''',
}
path = Path('recursos_editoriales.py')
text = path.read_text(encoding='utf-8')
for key, value in entries.items(): text = replace_entry(text, key, value)
path.write_text(text, encoding='utf-8')

path = Path('recursos_compra.py')
text = path.read_text(encoding='utf-8')
text = text.replace('["Quiero una referencia con cable de 115 mm", "GWS 700 en la comparación argentina", "710 W y 12.000 rpm documentadas. La oferta GWS 770 enlazada abajo es otro modelo: no hereda la ficha de GWS 700."]', '["Quiero una referencia con cable de 115 mm", "GWS 700 o GWS 770: contrastar el código", "GWS 700 tiene ficha argentina de 710 W. GWS 770 documenta 770 W, 115 mm y 220 V para 06013980E0 en Bosch Brasil; confirmá ese código en la oferta, kit y garantía local."]')
path.write_text(text, encoding='utf-8')
print('Sincronizados nueve recursos y el selector Bosch.')
