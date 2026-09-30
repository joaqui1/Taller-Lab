"""Recorridos editoriales de los ocho hubs; enlazan guías ya publicadas."""

HUB_STEPS = (
    ("general", "guia-principal", "Guía principal", "Empezá por los criterios de elección y los límites de los datos."),
    ("necesidad", "usos", "Usos", "Buscá la tarea, el material y la alimentación que necesitás."),
    ("marcas", "marcas", "Marcas", "Compará familias y códigos; una marca no garantiza prestaciones iguales."),
    ("modelos", "modelos", "Modelos", "Revisá la variante exacta, las cifras documentadas y lo que falta confirmar."),
    ("accesorios", "accesorios", "Accesorios", "Comprobá medidas, encastres y consumibles antes de completar el equipo."),
)

COMPRESSOR_HUB_STEPS = (
    ("uso", "elegir-por-uso", "Elegir por uso", "Empezá por la tarea: inflar, pintar, aerografiar o alimentar herramientas neumáticas."),
    ("capacidad", "capacidad-y-tipo", "Capacidad y tipo", "Compará tanque, alimentación y construcción según el trabajo y el ciclo previsto."),
    ("marcas-modelos", "marcas-y-modelos", "Marcas y modelos", "Revisá fabricantes y códigos concretos con sus datos documentados."),
    ("linea", "linea-de-aire-y-accesorios", "Línea de aire y accesorios", "Comprobá mangueras, conexiones, consumibles y herramientas compatibles."),
)

COMPRESSOR_HUB_FILES = {
    "uso": [
        "01-compresor-de-aire-para-auto.md",
        "04-aerografo-con-compresor.md",
        "07-compresor-para-aerografo.md",
        "21-compresor-para-pintar.md",
        "22-inflador-de-neumaticos-portatil.md",
    ],
    "capacidad": [
        "02-compresor-de-50-litros.md",
        "11-compresor-de-100-litros.md",
        "15-compresor-sin-aceite.md",
        "16-compresor-de-200-litros.md",
        "18-compresor-de-24-litros.md",
        "19-compresor-inalambrico.md",
        "23-compresor-12v-doble-piston.md",
    ],
    "marcas-modelos": [
        "09-compresor-lusqtoff-50-litros.md",
        "12-compresor-gamma-50-litros.md",
        "14-compresor-lusqtoff-100-litros.md",
        "17-compresor-bta-25-litros.md",
        "20-compresor-stanley.md",
    ],
    "linea": [
        "03-manguera-para-compresor-de-aire.md",
        "05-pistola-para-pintar-con-compresor.md",
        "06-acople-rapido-para-compresor.md",
        "08-aceite-para-compresor-de-aire.md",
        "10-filtro-de-aire-para-compresor.md",
        "13-kit-para-compresor-de-aire.md",
    ],
}

HUB_EDITORIAL = {
    "hidrolavadoras": {
        "page_title": "Hidrolavadoras: guías, marcas y comparativas",
        "intro": "Elegí por tarea y compará presión declarada/documentada, caudal declarado/documentado y accesorios del código exacto. Separá presión de trabajo de presión máxima.",
        "start_links": [
            ("Comparativa general", "/hidrolavadoras/comparativa-general/"),
            ("Para autos", "/hidrolavadoras/para-autos/"),
            ("Inalámbricas", "/hidrolavadoras/inalambricas/"),
            ("Profesionales", "/hidrolavadoras/profesionales/"),
            ("Aire acondicionado", "/hidrolavadoras/hidrolavadora-para-aire-acondicionado/"),
        ],
        "criteria": ["Presión de trabajo y máxima por separado", "Caudal con su condición de medición", "Manguera, conexión y alimentación de agua"],
        "accessories": ["Confirmá el encastre de pistola, lanza y boquillas en el manual del código exacto.", "Revisá longitud y presión admisible de la manguera, y si el kit incluye dosificador.", "No deduzcas compatibilidad entre gamas por compartir marca."],
    },
    "compresores": {
        "intro": "Partí del consumo de aire de tu tarea. Compará caudal declarado/documentado a la presión de uso, volumen del tanque y alimentación; la admisión no equivale al aire entregado.",
        "criteria": ["Caudal de salida y presión de referencia", "Tanque, alimentación y ciclo documentado", "Mangueras, acoples y consumo de la herramienta"],
    },
    "amoladoras": {
        "intro": "Empezá por el material y el disco compatible. Después compará diámetro, velocidad en vacío, alimentación y funciones documentadas por modelo.",
        "criteria": ["Diámetro, eje y rpm del disco", "Tipo de corte o desbaste y material", "Código, alimentación y guarda indicada"],
    },
    "taladros": {
        "intro": "Distinguí perforación, percusión y atornillado. Elegí función y encastre antes de comparar torque declarado, plataforma de batería y contenido del kit.",
        "main": "01-taladro-inalambrico.md",
        "criteria": ["Función y material de trabajo", "Mandril o encastre SDS", "Plataforma y baterías incluidas por código"],
        "task_selector": [
            ("Atornillar y perforar sin cable", "Inalámbricos", "Para madera, metal y tareas cotidianas donde importa la movilidad.", "/taladros/inalambricos/"),
            ("Perforar ladrillo y mampostería", "Percutores", "La percusión ayuda en mampostería; elegí la broca según el material.", "/taladros/percutores/"),
            ("Perforar hormigón o cincelar", "Rotomartillos", "Sistema SDS para perforaciones exigentes y trabajos de cincelado compatibles.", "/taladros/rotomartillos/"),
            ("Ajustar fijaciones exigentes", "Atornilladores de impacto", "Encastre hexagonal y golpes tangenciales para atornillar; no reemplaza un taladro.", "/taladros/atornilladores-de-impacto/"),
            ("Atornillar placas de yeso", "Durlock", "Controlá la profundidad para colocar tornillos de forma pareja.", "/taladros/para-durlock/"),
            ("Perforar recto y en serie", "Taladros de banco", "La pieza queda apoyada mientras la broca baja guiada por la columna.", "/taladros/taladro-de-banco/"),
            ("Perforar cerámica", "Brocas para cerámica", "Usá una broca adecuada y evitá la percusión para reducir roturas.", "/taladros/brocas-ceramica/"),
            ("Perforar porcelanato", "Mechas para porcelanato", "Elegí una mecha específica y seguí las indicaciones para ese material.", "/taladros/mecha-porcelanato/"),
        ],
    },
    "sierras": {
        "page_title": "Sierras: tipos y cómo elegir según el trabajo",
        "intro": "Elegí la familia por material y geometría del corte: recto, curvo, longitudinal o a inglete. Compará capacidad documentada y compatibilidad de la hoja.",
        "main": "01-sierra-circular.md",
        "criteria": ["Material y tipo de corte", "Capacidad a cada ángulo publicado", "Diámetro, eje o encastre de la hoja"],
        "task_selector": [
            ("Cortes rectos portátiles en madera", "Sierra circular", "/sierras/circulares/"),
            ("Cortes curvos o siguiendo un trazo", "Sierra caladora", "/sierras/caladoras/"),
            ("Demolición y cortes en lugares de acceso difícil", "Sierra sable", "/sierras/sable/"),
            ("Cortes longitudinales repetidos con la pieza sobre una mesa", "Sierra de banco", "/sierras/de-banco/"),
            ("Cortes transversales e ingletes repetidos", "Ingletadora", "/sierras/ingletadoras/"),
            ("Cortes curvos o piezas anchas de madera apoyadas en mesa", "Sierra sin fin para madera", "/sierras/sierra-sin-fin-para-madera/"),
            ("Cortes repetidos de perfiles metálicos sujetos en una base", "Sensitiva", "/sierras/sensitivas/"),
            ("Cortes de perfiles metálicos con cinta dentada", "Sierra sin fin para metal", "/sierras/sin-fin-metal/"),
        ],
    },
    "soldadoras": {
        "intro": "Elegí el proceso según el material y el consumible. Compará corriente con su ciclo de trabajo, tensión y accesorios del código exacto; el nombre comercial no prueba la salida continua.",
        "criteria": ["Proceso y consumible compatible", "Corriente a cada ciclo de trabajo", "Tensión, conexiones y contenido del kit"],
    },
    "soldadura-electronica": {
        "intro": "Separá cautín, aire caliente y accesorios de sujeción. Compará funciones, temperatura declarada, tensión y variantes exactas sin trasladar cifras entre estaciones parecidas.",
        "criteria": ["Cautín, aire caliente o ambos", "Tensión y rango de temperatura declarado", "Puntas, boquillas y soporte compatibles"],
    },
    "generadores": {
        "intro": "Partí de las cargas y sus arranques. Distinguí potencia nominal de máxima, kW de kVA, fases y combustible; una cifra máxima no describe el suministro continuo.",
        "criteria": ["Potencia nominal, máxima y unidad", "Fases, tensión y cargas previstas", "Combustible y autonomía con su condición"],
        "separate_category": {
            "filename": "20-estaciones-de-energia-portatiles.md",
            "title": "Estaciones de energía / baterías",
            "description": "Una alternativa a la combustión para cargas compatibles: compará energía almacenada, potencia de salida y formas de recarga.",
        },
        "start_links": [
            ("Elegir generador", "/generadores/comparativa-general/"),
            ("Calcular para casa", "/generadores/para-casa/"),
            ("Ver precios", "/generadores/precios/"),
        ],
        "accessories": ["Confirmá tomas, tensión y corriente admitida en el manual del generador.", "Consultá los consumibles de mantenimiento por código de motor; no uses una especificación universal.", "Para respaldo de una instalación, definí conexión y transferencia con un instalador habilitado."],
    },
}
