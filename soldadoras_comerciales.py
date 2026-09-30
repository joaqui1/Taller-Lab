"""Ofertas suministradas por el usuario; títulos separados de las fichas técnicas."""
from html import escape

# Código interno: nombre recibido normalizado, referido, comprobación de identidad/uso.
OFFERS = {
    'IRON100': ('Lüsqtoff Mega Iron 100 + máscara', '1p8rvV8', 'MMA: confirmá MEGAIRON100-8 en placa y qué máscara incluye el paquete.'),
    'IRON250': ('Lüsqtoff MEGAIRON250 + máscara + kit', '26R9o7z', 'MMA: confirmá equipo IRON-250, ciclo de trabajo y accesorios; el nombre 250 no acredita 250 A de salida.'),
    'SLCEL200': ('Lüsqtoff SLCEL200-9 Black Series', '26RyVcZ', 'MMA / Lift TIG: verificá ciclo, electrodo admitido y si la torcha TIG se vende aparte.'),
    'SML120': ('Lüsqtoff SML120-8DK', '26xX924', 'Flux / MMA: distinguí el kit 8DK del equipo 8D; confirmá máscara, bobina y accesorios entregados.'),
    'SML150': ('Lüsqtoff SML150-8D', '1UGCFFq', 'Flux / MMA: alternativa a la SML150-8 discontinuada. El título dice 20 A: cotejá rango y ciclo con placa/manual.'),
    'MIGDUAL200': ('Lüsqtoff MIGDUAL200-9', '252cwEq', 'MIG con gas / MMA: comprobá configuración, rodillos y kit. Los 38 A del título no identifican la corriente de salida.'),
    'PROTIG180': ('Lüsqtoff PROTIG180-8', '2J6hGMz', 'TIG DC: confirmá torcha y accesorios; no es una alternativa TIG AC/DC para aluminio.'),
    'SMARTTIG': ('Lüsqtoff Smart TIG-ACDC-20', '2vsBinj', 'TIG AC/DC: confirmá código completo SMARTTIG-ACDC-20 en placa, red y controles incluidos.'),
    'TIG350': ('Lüsqtoff TIG350ACDC-9 Black Series', '1dRAroP', 'TIG AC/DC: cotejá red trifásica de 380 V en la ficha y placa; no elegir como equipo monofásico por el nombre.'),
    'ST1N': ('Lüsqtoff ST-1N', '1oPpFmw', 'Para comparar una máscara de tono fijo: verificá filtro y procesos admitidos; TIG de baja corriente no confirmado en la guía.'),
    'ST1E': ('Lüsqtoff ST-1E', '1W1WXvh', 'Para comparar regulación de sombra y sensibilidad: confirmá controles y especificaciones del filtro ofrecido.'),
    'ST1B': ('Lüsqtoff ST-1B', '1L34ttG', 'Para comparar el modelo de cuatro sensores documentado: confirmá filtro y rango TIG; no extrapolar datos a ST-1X.'),
    'ST1X': ('Lüsqtoff ST-1X', '2uoDsq6', 'Verificá lote, manual, estado y repuestos: hay discrepancias históricas en la velocidad publicada del filtro.'),
    'ESAB162': ('ESAB HandyArc 162i', '1bLo7UL', 'MMA: confirmá código 0409616 y accesorios. Los 160 A máximos son intermitentes según el ciclo documentado.'),
    'ESABMIG160': ('ESAB HandyArc MIG 160i', '2V4LNfM', 'MIG/MAG y tubular, además de MMA: confirmá código 0410060, rodillo, bobina y polaridad. Es otro proceso que HandyArc 162i.'),
    'ESABET200': ('ESAB ET 200i AC/DC', '1vSNzRV', 'TIG AC/DC: confirmá código 0738827, torcha, control y sistema de gas incluidos en la oferta.'),
    'GUANTES': ('ESAB Heavy Duty Black', '2HuWpap', 'Verificá modelo, talle y protección declarada para tu proceso; no se presenta como guante TIG de precisión.'),
    'ESABWIRE18': ('Conarco/ESAB MIG E70-S6 · 1,6 mm × 18 kg', '1fzxaCM', 'Presentación industrial según título, distinta de 0,8 mm × 5 kg. Confirmá clasificación en etiqueta, diámetro y capacidad física del alimentador.'),
    'NI100': ('ESAB 92.18 Ni-100 · 3,2 mm × 1 kg', '1mXhaLW', 'Confirmá identificación OK 92.18 y clasificación ENi-CI en etiqueta/ficha; Ni-100 no equivale a NiFe.'),
    'GASFREE5': ('ESAB Gas Free · 0,8 mm × 5 kg', '2x4GdMW', 'Confirmá clasificación AWS, diámetro, polaridad y medidas del carrete de 5 kg; no trasladar parámetros de otras bobinas.'),
    'DOG160': ('Dogo Dogostar MMA 160', '1iiKCDU', 'MMA: el título no confirma Moderna DOG50044. Pedí código/placa antes de aplicar la ficha de la guía.'),
    'DOG180': ('Dogo Dogostar 180 Moderna', '2KQQEjE', 'MMA: confirmá código DOG50045, corriente asociada al servicio por diámetro y kit real.'),
    'DOG200': ('Dogo Dogostar 200 Moderna DOG50046', '2XwX5wy', 'MMA: verificá placa DOG50046, servicio por diámetro y contenido; 200 A máximos no acreditan salida continua.'),
    '7018-32': ('Conarco 7018 Punta Verde · 3,2 mm × 5 kg', '1W8ddJX', 'Confirmá diámetro 3,2 mm en etiqueta, clasificación completa, polaridad y envase. No aplicar rangos de Atom Arc a Conarco.'),
    '7018-25': ('Conarco 7018 Punta Verde · 2,5 mm × 1 kg', '2fBaR3k', 'Presentación de 1 kg: confirmá peso, clasificación, polaridad y conservación; compará precio por kilo entre paquetes.'),
    '6013-25': ('Conarco 6013 13A Punta Azul · 2,50 mm × 5 kg', '1Xxa67E', 'Confirmá producto 13A, diámetro, corriente/polaridad y estado del envase; los rangos de otros E6013 no son universales.'),
    '6013-325': ('Conarco 6013 13A Punta Azul · 3,25 mm × 5 kg', '1EF3Gcn', 'Confirmá diámetro 3,25 mm, producto 13A y rango de su ficha; no sustituirlo por datos de 3,2 mm de otra marca.'),
    'BREMEN8240': ('Bremen ER70S-6 8240 · 0,8 mm × 5 kg', '1RwSNLU', 'Alambre macizo para MIG con gas: verificá código 8240, gas indicado, rodillo y tamaño del carrete; no es alambre Flux.'),
}

PENDING = {
    'ESABWIRE5': 'Falta referido ESAB/Conarco WELD ER70S-6 0,8 mm × 5 kg; el suministrado es 1,6 mm × 18 kg.',
    'BREMENFLUX': 'Falta referido Bremen E71T-GS 0,8 mm × 1 kg; el Bremen 8240 recibido es macizo.',
    'ESABFLUX1': 'Falta referido ESAB Gas Free E71T-GS 1,0 mm × 1 kg; el recibido dice 0,8 mm × 5 kg y no confirma AWS.',
}

# Archivo: [(modelos, encabezado exacto, posición tras tabla/sección, título comercial)].
PLACEMENTS = {
    0: [(['IRON100', 'SML120', 'ESABMIG160', 'ESABET200'], 'Qué soldadora elegir según el trabajo', 'section', 'Una oferta por proceso: MMA, Flux, MIG y TIG')],
    1: [(['7018-25', '7018-32'], 'Opciones de compra', 'section', 'Compará diámetro y presentación del 7018')],
    2: [(['IRON100', 'IRON250'], 'MMA', 'table', 'Opciones MMA de la familia Iron'), (['SML120', 'MIGDUAL200'], 'Flux/MIG', 'table', 'Opciones Flux y MIG: verificá el proceso')],
    3: [],
    4: [(['ESABMIG160', 'MIGDUAL200'], 'Comparativa y costo del equipo completo', 'table', 'Máquinas MIG con gas para comparar'), (['ESABWIRE5'], 'Gas, alambre y accesorios necesarios', 'section', 'Alambre compatible: oferta pendiente')],
    5: [(['GUANTES'], 'Opciones de compra', 'section', 'Consultá talle y protección del guante')],
    6: [(['PROTIG180', 'SMARTTIG', 'ESABET200'], 'Modelos documentados', 'table', 'Compará TIG DC y TIG AC/DC')],
    7: [(['SML120', 'SML150', 'ESABMIG160'], 'Comparativa de equipos y kits', 'table', 'Opciones para alambre tubular: confirmá montaje')],
    8: [(['ESABWIRE5', 'BREMEN8240', 'ESABWIRE18'], 'Opciones de compra', 'section', 'Alambre MIG macizo: diámetros y bobinas distintos')],
    9: [(['ST1N', 'ST1E', 'ST1B'], 'Modelos y qué comparar', 'table', 'Tres máscaras para decisiones distintas')],
    10: [(['6013-25', '6013-325'], 'Opciones de compra', 'section', 'Compará las presentaciones Conarco 13A')],
    11: [(['SLCEL200', 'DOG200'], 'Modelos y qué comparar', 'table', 'Opciones de 200 A: revisá el ciclo de trabajo')],
    12: [(['NI100'], 'Opciones de compra', 'section', 'Consultá la referencia de níquel para fundición')],
    13: [(['BREMENFLUX', 'ESABFLUX1', 'GASFREE5'], 'Opciones de compra y bobinas', 'section', 'Oferta Flux recibida: verificá clasificación y bobina')],
    14: [(['DOG180'], 'Ficha técnica y ciclo de trabajo', 'section', 'Consultá la Dogo 180 Moderna'), (['DOG160', 'DOG200'], 'Comparación contextual con Dogo 160 y 200', 'table', 'Alternativas MMA de 160 y 200 A')],
    15: [(['ESAB162'], 'MMA', 'section', 'Oferta ESAB MMA'), (['ESABMIG160'], 'MIG', 'section', 'Oferta ESAB MIG'), (['ESABET200'], 'TIG', 'section', 'Oferta ESAB TIG AC/DC')],
    16: [],
    17: [(['ESABET200', 'TIG350'], 'Referencias de equipo documentadas', 'table', 'Opciones TIG AC/DC: verificá la red disponible')],
    18: [(['IRON250'], 'Versión y especificaciones verificadas', 'section', 'Consultá el kit MEGAIRON250'), (['DOG180', 'ESAB162'], 'Accesorios, alternativas y qué comparar', 'table', 'Alternativas MMA para comparar')],
    19: [(['ESABET200', 'SMARTTIG', 'TIG350'], 'Modelos y qué comparar', 'table', 'Opciones TIG AC/DC y alimentación eléctrica')],
    20: [(['ESAB162', 'DOG160', 'ESABMIG160'], 'Modelos, kits y qué comparar', 'table', 'MMA de 160 A y una alternativa MIG de otro proceso')],
    21: [(['IRON100'], 'Qué incluye MEGAIRON100-8', 'section', 'Consultá el paquete Iron 100'), (['IRON250', 'ESAB162'], 'Comparación con Iron 250 y HandyArc 162i', 'table', 'Alternativas MMA para comparar')],
    22: [(['SML120', 'SML150'], 'Comparativa de la familia SML', 'table', 'Opciones actuales de la familia SML')],
    23: [(['SML150', 'SML120'], 'Comparación de variantes documentadas', 'table', 'Alternativas actuales a la SML150-8 discontinuada')],
    24: [(['SML120', 'SML150'], 'SML120-8D vs SML120-8DK', 'table', 'Consultá el kit 8DK y otra alternativa actual')],
    25: [],
    26: [(['ESAB162'], 'Cómo investigamos esta guía', 'table', 'Consultá HandyArc 162i: verificá código 0409616'), (['DOG160', 'DOG180'], 'Proceso y funciones documentadas', 'section', 'Alternativas MMA Dogo: confirmá códigos')],
    27: [(['ST1B', 'ST1X'], 'Identificar ST-1X y diferenciarla de ST-1B', 'section', 'ST-1B como alternativa; ST-1X por código y lote')],
    28: [(['SML120', 'SML150'], 'Cuándo conviene pasar a una alternativa actual', 'section', 'Alternativas actuales a la SML130-7')],
}


def url(key):
    return 'https://meli.la/' + OFFERS[key][1]


def cta(key, number):
    if key == 'ST1X':
        return 'Ver disponibilidad y verificar lote'
    if number in (23, 28):
        return 'Ver precio de la alternativa actual'
    return 'Ver precio y disponibilidad'


def render_block(keys, title, number):
    cards = []
    for key in keys:
        name, _, note = OFFERS[key]
        cards.append(f'<article class="offer-card"><div class="offer-card-top"><span>MERCADO LIBRE</span></div>'
                     f'<h3>{escape(name)}</h3><p class="offer-description">{escape(note)}</p>'
                     f'<div class="offer-actions"><a class="offer-button" href="{url(key)}" target="_blank" '
                     f'rel="nofollow sponsored noopener noreferrer" data-affiliate-placement="soldadoras-contextual">{escape(cta(key, number))} ↗</a></div></article>')
    return ('<section class="affiliate-shelf" aria-label="Opciones con enlace de afiliado">'
            f'<div class="affiliate-heading"><h3>{escape(title)}</h3></div>'
            '<div class="offer-grid">' + ''.join(cards) + '</div>'
            '<p>Enlaces de afiliado: TallerLab puede recibir una comisión, sin costo adicional para vos. '
            'Confirmá código, contenido, precio y stock en la publicación antes de aplicar los datos de la guía a esa unidad.</p></section>')


def install_catalog(products, facts, configs):
    for key, (name, _, note) in OFFERS.items():
        guide = next(path for path, config in configs.items() if key in config['models'])
        products['soldadoras'].append((name, note, url(key), guide))
        brand, model = name.split(' ', 1)
        facts[url(key)] = dict(brand=brand, model=model, use=note,
            power='Consultar placa y manual', specs=['Identidad y presentación a confirmar'],
            includes='Consultar contenido de la publicación', image=None, source=url(key),
            source_type='título suministrado por el usuario', evidence_label='Destino sin verificar')
