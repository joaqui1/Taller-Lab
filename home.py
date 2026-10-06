"""Selección editorial de la portada; el catálogo completo sigue en el buscador."""

# Orden basado en el análisis comercial local del 27/09/2026 y cobertura por uso.
# No representa un ranking de ventas ni de productos.
HOME_COMPARISONS = (
    ("/hidrolavadoras/comparativa-general/", "Hidrolavadoras", "Compará presión de trabajo, caudal y accesorios para tu limpieza."),
    ("/taladros/inalambricos/", "Taladros inalámbricos", "Elegí función, plataforma de batería y contenido del kit."),
    ("/generadores/comparativa-general/", "Grupos electrógenos", "Separá potencia nominal y máxima antes de comparar equipos."),
    ("/taladros/rotomartillos/", "Rotomartillos", "Revisá encastre y capacidad para el material que vas a perforar."),
    ("/amoladoras/bosch/", "Amoladoras Bosch", "Compará familias por diámetro de disco y alimentación."),
    ("/compresores/50-litros/", "Compresores de 50 litros", "El tanque es el punto de partida: comprobá el aire entregado."),
    ("/soldadoras/lusqtoff/", "Soldadoras Lüsqtoff", "Elegí el proceso y contrastá corriente, ciclo de trabajo y kit."),
    ("/sierras/de-banco/", "Sierras de banco", "Compará capacidad de corte, mesa y compatibilidad del disco."),
)

HOME_TOOLS = (
    ("/generadores/para-casa/", "Calculadora", "Potencia para tu casa", "Sumá cargas de marcha y explorá un escenario de arranque.", "W"),
    ("/compresores/50-litros/", "Calculadora", "Caudal del compresor", "Contrastá suministro y consumo a la misma presión.", "L/min"),
    ("/generadores/precios/", "Calculadora", "Costo final de dos ofertas", "Incluí precio, envío y extras antes de decidir.", "$"),
    ("/hidrolavadoras/lusqtoff/", "Calculadora", "Consumo de agua", "Convertí caudal y minutos de uso en litros.", "L"),
    ("/sierras/circulares/", "Selector", "Espesor de corte", "Filtrá modelos por sus máximos documentados a 90°.", "mm"),
    ("/amoladoras/discos/", "Selector", "Disco según tu tarea", "Partí de la operación y el material para comprobar referencias.", "Ø"),
)

HOME_CATEGORY_COPY = {
    "hidrolavadoras": "Limpieza, caudal y presión",
    "compresores": "Aire para cada herramienta",
    "amoladoras": "Corte, desbaste y discos",
    "taladros": "Perforación y atornillado",
    "sierras": "Madera, metal y tipos de corte",
    "soldadoras": "Procesos, equipos y consumibles",
    "soldadura-electronica": "Estaciones y reparación de placas",
    "generadores": "Energía y respaldo para tu uso",
}

# Fotos existentes del catálogo para las entradas visuales de portada.
HOME_CATEGORY_IMAGES = {
    "taladros": ("Taladros", "ingcocidli206684-962e2fdef9.webp"),
    "compresores": ("Compresores", "lusqtofflc2550b8-ed19d06e8e.webp"),
    "sierras": ("Sierras", "dewaltdwe560-40a8fb62d7.webp"),
    "amoladoras": ("Amoladoras", "lusqtoffaml8508-79bb71a188.webp"),
    "hidrolavadoras": ("Hidrolavadoras", "lusqtoffhl120-89281b0422.webp"),
    "generadores": ("Generadores", "lusqtofflg3000-4ce50bc801.webp"),
    "soldadoras": ("Soldadoras", "lusqtoffmegairon1008-9c0c5a14a7.webp"),
    "soldadura-electronica": ("Soldadura electrónica", "portada-real-soldadura-electronica-estacion-de-soldadura-fe40ab1529.webp"),
}
