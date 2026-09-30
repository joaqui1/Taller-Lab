"""Enlaces suministrados y posiciones editoriales del clúster de limpieza."""
OFFERS = {
    'K2': ('Kärcher', 'K2 Basic Black · 1.994-322.0', '2izv76H', 'Limpieza ocasional y suciedad ligera'),
    'K2CAR': ('Kärcher', 'K2 Car Black · 1.994-052.0', '2Cq2ivp', 'Kit para auto; confirmar accesorios y stock'),
    'K3': ('Kärcher', 'K3 Black Edition · 9.398-355.0', '1LYmDeG', 'Más frecuencia de uso que la K2'),
    'K4': ('Kärcher', 'K4 · 9.398-294.0', '2SvkJCm', 'Comparar esta versión con Power Control'),
    'K4PC': ('Kärcher', 'K4 Power Control · 1.603-402.0', '149NjG2', 'Patio y auto; configuración Power Control'),
    'K5PC': ('Kärcher', 'K5 Power Control · 1.603-501.0', '1wCKV4R', 'Limpieza frecuente; configuración Power Control'),
    'K5': ('Kärcher', 'K5 AR', '2uTVRge', 'Variante pendiente de identificar'),
    'G130': ('Gamma', '130 Elite Red Line · G2513AR', '2SuGMdL', 'Escalón doméstico intermedio'),
    'MASTER': ('Gamma', 'Master Wash 1500 · G2521AR', '1zWPTU6', 'Entrada de la selección Gamma'),
    'PREMIUM': ('Gamma', 'Premium Wash 3000 · G2520AR', '2nquiBB', 'Mayor prestación dentro de esta selección Gamma'),
    'HL120': ('Lüsqtoff', 'HL-120', '1qPbvWX', 'Opción compacta para tareas domésticas'),
    'HL150': ('Lüsqtoff', 'HL-150', '1X9cSf1', 'Comparar alcance y caudal con HL-120'),
    'HL1109': ('Lüsqtoff', 'HL110-9', '1uvMFdz', 'Mayor prestación dentro de la selección Lüsqtoff'),
    'LAPL': ('Lüsqtoff', 'LAPL3.6-8BK', '1YbCQgP', 'Portátil a batería; confirmar contenido del kit'),
    'N300': ('Niwa', 'HDNW-300 · 1040300', '1Dy1F8P', 'Entrada para limpieza ocasional'),
    'N500': ('Niwa', 'HDNW-500 · 1040550', '15xwrHT', 'Alternativa doméstica para auto'),
    'N700': ('Niwa', 'HDNW-700 · 1040700', '2dFtHcP', 'Doméstica de mayor prestación'),
    'NPRO': ('Niwa', 'HDNW PRO-10 · 1040900', '2ChQa9Z', 'Evaluar instalación y caudal antes de comprar'),
    'B1300': ('BLACK+DECKER', 'BEPW1300-AR', '1zzNj8Z', 'Limpieza doméstica ocasional'),
    'B2200': ('BLACK+DECKER', 'BEPW2200-AR', '2MJE81D', 'Mayor prestación dentro de esta selección'),
    'GHP180': ('Bosch', 'GHP 180', '1wNMwSL', 'Auto y tareas domésticas ocasionales'),
    'GHP200': ('Bosch', 'GHP 200', '1zrcYor', 'Auto y patio; comparar caudal y manguera'),
    'GHP220': ('Bosch', 'GHP 220', '13efsmG', 'Código y frecuencia pendientes'),
    'RE80': ('STIHL', 'RE 80 X', '1wzSW2u', 'Tareas domésticas puntuales'),
    'RE90': ('STIHL', 'RE 90', '1fBYuUY', 'Frecuencia pendiente'),
    'TC130': ('Einhell', 'TC-HP 130 · 4140750', '2Qpd7no', 'Compacta con cable'),
    'TE140': ('Einhell', 'TE-HP 140 · 4140760', '26hgiky', 'Más capacidad dentro de la selección con cable'),
    'HYPRESSO': ('Einhell', 'HYPRESSO 18/24-1 Li · 4140135', '1TRSxkF', 'Portátil Power X-Change; confirmar batería y cargador'),
    'C30S': ('WIPCOOL', 'C30S', '2CieWYz', 'Equipo específico para limpieza de aire acondicionado'),
}
PENDING = {
    'K5': 'El título suministrado dice 380 L/h: falta confirmar el código 9.398-295.0 y la variante.',
    'GHP220': 'Falta acreditar código argentino 0600910EH0 y frecuencia de placa; el título dice 50/60 Hz.',
    'RE90': 'El título indica 60 Hz: confirmar placa compatible con la instalación argentina de 50 Hz.',
    'G150': 'Falta enlace de Gamma 150 Elite G2514AR.',
    'HL1008': 'Falta enlace de Lüsqtoff HL100-8.',
    'B1800': 'Falta enlace de BEPW1800T-AR.',
    'HYUNDAI_LIST': 'Falta lista afiliada Hyundai.',
    '200BAR_LIST': 'Falta lista afiliada de 200 bar.',
}
# Posición = final de la sección editorial indicada, antes del siguiente H2.
PLACEMENTS = {
    1: ('Elegí por tarea', ['K2', 'G130', 'N700', 'K4PC']),
    2: ('Elegí por tipo de equipo', ['LAPL', 'HYPRESSO']),
    3: ('Comparativa de la gama Lüsqtoff', ['HL120', 'HL150', 'HL1109']),
    4: ('Qué Gamma elegir según la tarea', ['MASTER', 'G130', 'PREMIUM']),
    5: ('Elegí por frecuencia de uso', ['RE80', 'RE90']),
    6: ('Cuál conviene para casa y auto', ['GHP180', 'GHP200', 'GHP220']),
    7: ('Qué elegir para casa y auto', ['B1300', 'B1800', 'B2200']),
    8: ('Qué K2 conviene para cada trabajo', ['K2', 'K2CAR']),
    9: ('Cuándo conviene comprar una K5', ['K5', 'K5PC']),
    10: ('Selector rápido', ['G150']),
    11: ('Qué necesita un lavadero de autos', ['NPRO', 'GHP220']),
    12: ('K2, K3 y K4 argentinos: dónde cae la K3', ['K3']),
    13: ('Selector por uso', ['TC130', 'TE140', 'HYPRESSO']),
    14: ('¿Me alcanza la Gamma 130?', ['G130']),
    15: ('', ['HYUNDAI_LIST']),
    16: ('Conviene si / no conviene si', ['HL120']),
    17: ('Precio local por versión', ['K4', 'K4PC']),
    18: ('Comparación: presión de trabajo, caudal y alimentación', ['G150', 'HL1008', 'N700']),
    19: ('', ['200BAR_LIST']),
    20: ('Respuesta rápida: elegir por entorno y ritmo', ['N300', 'N700', 'NPRO']),
    21: ('Selector rápido', ['K2', 'K3', 'K4PC', 'K5']),
    22: ('Qué revisar antes de elegir', ['K2', 'K3', 'N500']),
    23: ('Equipo específico para limpieza de aire acondicionado', ['C30S']),
}
REPEATS = {10: 'Precio de Gamma 150', 12: 'Precio y stock', 14: 'Precio y stock', 16: 'Precio relevado'}

def url(key):
    return 'https://meli.la/' + OFFERS[key][2]

def install_catalog(products, facts, configs):
    # Reemplazar las tres ofertas genéricas previas del clúster.
    products['hidrolavadoras'] = []
    for key, (brand, model, code, use) in OFFERS.items():
        if key in PENDING:
            continue
        guide = next(path for path, config in configs.items() if key in config['models'])
        products['hidrolavadoras'].append((brand + ' ' + model, use, url(key), guide))
        facts[url(key)] = dict(brand=brand, model=model, use=use,
            power='Batería' if key in {'LAPL', 'HYPRESSO'} else 'Cable',
            specs=['Referencia a cotejar: ' + model],
            includes='Confirmar accesorios, versión regional y contenido con el vendedor',
            image=None, source=guide, source_type='guía documental del modelo',
            evidence_label='Enlace suministrado; publicación sin verificar')
