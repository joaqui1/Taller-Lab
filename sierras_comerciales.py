"""Referidos recibidos y ubicaciones editoriales para las guías de sierras."""
OFFERS = {
    'GKS150': ('Bosch GKS 150', '1Chp49C', 'Confirmá código 0 601 6B3 0H0 y contenido del kit.'),
    'SC16': ('Stanley SC16', '1WX3aEo', 'Confirmá variante SC16-AR, tensión y disco admitido en placa/manual.'),
    'DWE560': ('DeWalt DWE560', '2zyLxUA', 'Confirmá variante DWE560-AR y tensión de la unidad ofrecida.'),
    'CSL1500-8': ('Lüsqtoff CSL1500-8', '2XbUjXk', 'Revisá disco, eje y capacidad del código exacto.'),
    'CM-14K': ('Lüsqtoff CM-14K', '28Unx3L', 'Confirmá código y capacidad según la forma del perfil.'),
    'TS223558-4': ('TOTAL TS223558-4', '194gVdS', 'Confirmá sufijo -4 y RPM en placa/manual; no trasladés datos del código base.'),
    'GSA1100E': ('Bosch GSA 1100 E', '2cEAQKh', 'El título recibido dice 110 W; comprobá la potencia en la placa del modelo, sin usar ese título como ficha técnica.'),
    'GSA18V24': ('Bosch GSA 18V-24', '2mTTC3F', 'La oferta menciona GSA18V-24N: confirmá código y si incluye batería y cargador.'),
    'DCS380B': ('DeWalt DCS380B', '2UW9Bfk', 'Confirmá plataforma y contenido: cuerpo, batería y cargador se verifican por separado.'),
    'BES603': ('Black+Decker BES603', '2azLzTF', 'Confirmá sufijo BES603-AR y 220 V; la tabla documental B2 no identifica la variante ofrecida.'),
    'TC-JS85': ('Einhell TC-JS 85', '1PmtLAQ', 'Consultá código, hojas y accesorios incluidos.'),
    'TE-JS100': ('Einhell TE-JS 100', '2N5KYMc', 'Consultá código, hojas y accesorios incluidos.'),
    'SFL300-8': ('Lüsqtoff SFL300-8', '27H5LQK', 'Confirmá altura de corte, garganta y medida de cinta para este código.'),
    'SFL1100-9': ('Lüsqtoff SFL1100-9', '2Pg3D6X', 'Confirmá altura de corte, garganta y medida de cinta para este código.'),
    'TC-TS2025': ('Einhell TC-TS 2025/2 U', '2mWYUA8', 'Verificá código completo, mesa y accesorios incluidos.'),
    'SML2000-8': ('Lüsqtoff SML2000-8', '119eQpU', 'Confirmá placa, potencia y disco: los documentos de este código presentan discrepancias.'),
    '646003': ('BTA Tools 646003', '1fovw5N', 'Confirmá código, capacidad por perfil y posiciones de trabajo.'),
    '646001': ('BTA Tools 646001', '1rjCMVL', 'Confirmá código, capacidad por perfil y posiciones de trabajo.'),
    'TC-MS2112': ('Einhell TC-MS 2112', '1SD2tF3', 'Confirmá capacidad al ángulo previsto y disco adecuado al material.'),
    'TC-TS2225': ('Einhell TC-TS 2225 U', '1SQmxVn', 'Verificá código completo, mesa y accesorios incluidos.'),
    '4380': ('SKIL 4380', '1cCuNwX', 'Pendiente: unidad nueva exacta, tensión local y habilitación por Afiliados.'),
    '4550': ('SKIL 4550', '1aq4mGc', 'Pendiente: unidad nueva exacta, tensión local y habilitación por Afiliados.'),
    'KMA2685': ('Kreg Rip-Cut KMA2685', '2zYHZrk', 'Confirmá que la base y el montaje de tu sierra sean compatibles; no equivale a un riel propietario.'),
    'SURPLEE-DW3278': ('Surplee compatible con DW3278', '1xjT5i9', 'Accesorio de terceros, no identificado como DeWalt original. Confirmá medidas y compatibilidad con tu sierra.'),
    'D28720': ('DeWalt D28720', '2ZwgGLw', 'Confirmá variante D28720-AR y capacidad para el perfil previsto.'),
    'D28730': ('DeWalt D28730', '2LmS81p', 'Confirmá variante regional y capacidad para el perfil previsto.'),
    'DWS713': ('DeWalt DWS713', '1cgXhkN', 'Confirmá variante regional, revisión y contenido del kit.'),
    'DWS780': ('DeWalt DWS780', '11C2Bud', 'Confirmá variante regional, revisión y espacio para el carro telescópico.'),
    'TS42142107': ('TOTAL TS42142107', '1ci9crb', 'Confirmá código, tensión y capacidad al ángulo que necesitás.'),
}
PENDING = {'4380', '4550'}
# Número de archivo: modelos, encabezado de referencia, punto de inserción.
PLACEMENTS = {
    1: (['GKS150', 'SC16', 'DWE560', 'CSL1500-8'], 'Diámetro y espesor: dos límites separados', 'section'),
    2: (['CM-14K', 'TS223558-4'], 'Qué capacidad necesitás según la forma del perfil', 'section'),
    3: (['GSA1100E', 'GSA18V24', 'DCS380B'], 'Sierra sable con cable o inalámbrica', 'section'),
    4: (['BES603', 'TC-JS85', 'TE-JS100'], 'Capacidad publicada de tres modelos', 'table'),
    5: (['SFL300-8', 'SFL1100-9'], 'Altura de corte y garganta: qué determina cada una', 'section'),
    6: (['TC-TS2025', 'SML2000-8'], 'Qué sierra de banco elegir según el tamaño de pieza', 'table'),
    7: (['646003', '646001'], 'Portátil o de banco', 'section'),
    8: (['TC-MS2112', 'TC-SM2131'], 'TC-MS 2112 o TC-SM 2131/2 Dual: cuál tiene sentido', 'table'),
    9: (['TC-TS2025', 'TC-TS2225'], 'Cuál elegir según tamaño de pieza y espacio', 'table'),
    10: (['4380', '4550'], 'Vigencia y disponibilidad de los modelos', 'section'),
    11: (['KMA2685', 'SURPLEE-DW3278'], 'Compatibilidad con GKS150, DWE560 y SC16', 'table'),
    12: (['D28720', 'D28730'], 'D28720 o D28730: cuál tiene sentido según el trabajo', 'heading'),
    13: (['DWS713', 'DWS780'], 'Fija o telescópica: cuándo compensa la DWS780', 'table'),
    14: (['TS42142107', 'TS42182553'], 'Qué cambia realmente entre los dos modelos', 'table'),
    15: (['D0760A', 'EXPERT19060', 'PRO19054'], 'Qué disco usar según el corte', 'section'),
    16: (['GKS150'], 'Para quién tiene sentido la GKS150', 'section'),
    17: (['CS1004-AR', 'CS1350P'], 'Qué Black+Decker elegir según el trabajo', 'table'),
    18: (['TC-JS85', 'TE-JS100', 'TC-JS18'], 'Tres caladoras Einhell según alimentación y capacidad', 'table'),
    19: (['GSA18V24', 'DCS380B'], 'La plataforma de batería puede decidir la compra', 'section'),
    20: (['CSL1500-8', 'SCL2200-8'], 'CSL1500-8 y SCL2200-8: capacidades documentadas', 'table'),
    21: (['TC-MS2112', 'TC-SM2131', 'DWS713', 'DWS780'], 'Fija o telescópica', 'section'),
    22: (['GST650', 'GST680', 'GST185LI'], 'Comparación de GST 650, GST 680 y GST 185-LI', 'table'),
    23: (['DWE560'], 'Para quién tiene sentido la DWE560', 'section'),
    24: (['SC16'], 'Para qué espesores tiene sentido', 'section'),
    25: (['BES603', 'BES602'], 'BES603 y BES602: velocidad variable y variante', 'table'),
    26: (['SML2000-8', 'SML2000-9', 'SML2000B-9'], 'Tres códigos de banco y una discrepancia documental', 'table'),
    27: (['CM-14K'], 'Capacidades y datos publicados de la CM-14K', 'table'),
    28: (['SFL300-8', 'SFL1100-9'], 'SFL250-8 vs SFL300-8 vs SFL1100-9', 'table'),
    29: (['TS223558-4'], 'TS223558 vs TS223558-4: qué sabemos realmente', 'section'),
}

def url(key):
    return 'https://meli.la/' + OFFERS[key][1]

def install_catalog(products, facts, configs):
    for key, (name, code, note) in OFFERS.items():
        if key in PENDING:
            continue
        guide = next(path for path, config in configs.items() if key in config['models'])
        products['sierras'].append((name, note, url(key), guide))
        brand, model = name.split(' ', 1)
        facts[url(key)] = dict(brand=brand, model=model, use=note,
            power='Consultar placa y manual de la unidad', specs=['Modelo: ' + model],
            includes='Consultar contenido de la publicación', image=None, source=url(key),
            source_type='publicación comercial', evidence_label='Oferta suministrada; destino sin verificar')
