"""Referidos del usuario, con ruta y CTA explícitos y límites de identidad visibles."""
from html import escape

# Nombre, destino recibido, ruta principal, CTA y condición de la oferta.
OFFERS = {
    'GSR120': ('Bosch GSR 120-LI', 'https://meli.la/2hBcHa8', '/taladros/bosch-inalambrico/', 'Ver precio del Bosch GSR 120-LI', 'Taladro/atornillador Professional 12 V sin percusión. Confirmá baterías, cargador y número de pedido del kit.'),
    'BCD702': ('Black+Decker BCD702C1-AR', 'https://meli.la/1eiXebK', '/taladros/black-decker/', 'Ver precio del BCD702C1', 'Taladro/atornillador sin percusión. Confirmá sufijo AR, batería y cargador de la publicación local.'),
    'TECD1840': ('Einhell TE-CD 18/40 Li Solo', 'https://meli.la/2A1rX5b', '/taladros/einhell-inalambrico/', 'Ver precio del TE-CD 18/40 Li', 'Taladro/atornillador sin percusión, Power X-Change 18 V. Solo: batería y cargador se compran aparte.'),
    'GBH220': ('Bosch GBH 220', 'https://meli.la/2cRLSJx', '/taladros/rotomartillo-bosch/', 'Ver precio del Bosch GBH 220', 'Rotomartillo con cable y encastre SDS Plus. Confirmá 220 V, código completo y accesorios.'),
    'GBH226': ('Bosch GBH 2-26 DRE', 'https://meli.la/16mozwd', '/taladros/rotomartillo-bosch/', 'Ver precio del Bosch GBH 2-26 DRE', 'Rotomartillo con cable y encastre SDS Plus. Confirmá variante DRE, tensión y contenido del maletín.'),
    'GBH180': ('Bosch GBH 180-LI', 'https://meli.la/29WzeN7', '/taladros/rotomartillo-bosch/', 'Ver precio del Bosch GBH 180-LI', 'Rotomartillo inalámbrico SDS Plus. Es otro modelo que el GBH 18V-26 D de la tabla: no hereda su energía, capacidad ni peso. Confirmá kit y ficha propia.'),
    'GSB550': ('Bosch GSB 550 RE', 'https://meli.la/18iubWD', '/taladros/percutores/', 'Ver precio del Bosch GSB 550 RE', 'Taladro percutor con cable. Confirmá número de pedido, tensión y correspondencia con el GSB 550 documentado.'),
    'GSB1850': ('Bosch GSB 18V-50', 'https://www.mercadolibre.com.ar/up/MLAU364309887?pdp_filters=item_id:MLA1755860026#origin=share&sid=share&wid=MLA1755860026&action=copy', '/taladros/bosch-inalambrico/', 'Ver precio del Bosch GSB 18V-50', 'Taladro percutor Professional 18 V. Confirmá si es herramienta sola o kit; el enlace recibido es una publicación directa de Mercado Libre.'),
    'TBL167': ('Lüsqtoff TBL16-7', 'https://meli.la/2ehG4uD', '/taladros/taladro-de-banco/', 'Ver publicación del Lüsqtoff TBL16-7', 'Taladro de banco según el título recibido. TBL16-7 no confirma el TB-16 de las tablas: pedí placa/manual antes de atribuirle velocidades, recorrido o peso.'),
    'TBL710': ('Lüsqtoff TBL710-9D', 'https://meli.la/1MCEYGV', '/taladros/taladro-de-banco/', 'Ver precio del TBL710-9D', 'Taladro de banco: el título recibido dice 230 W, mientras la ficha citada publica 710 W nominales y 900 W S2/5 min. Confirmá placa y modelo antes de comparar.'),
    'DCF887': ('DeWalt DCF887B', 'https://meli.la/1hh4SkK', '/taladros/atornillador-impacto-dewalt/', 'Ver precio del DeWalt DCF887B', 'Atornillador de impacto con encastre hexagonal de 1/4, para fijaciones. No es un taladro; la variante B es herramienta sola.'),
    'DCD796': ('DeWalt DCD796D2', 'https://meli.la/1STm31d', '/taladros/dewalt-inalambrico/', 'Ver precio del DeWalt DCD796D2', 'Taladro percutor/atornillador. Confirmá sufijo regional, capacidad de las dos baterías, cargador y contenido del kit D2.'),
    'TPCD1850': ('Einhell TP-CD 18/50 Li- BL Solo · sufijo a confirmar', 'https://meli.la/1sp5STW', '/taladros/einhell-inalambrico/', 'Ver precio del TP-CD 18/50 Li-i BL', 'El título recibido omite Li-i. Confirmá TP-CD 18/50 Li-i BL y código 4513942 antes de atribuirle la percusión de la tabla. Solo: sin batería ni cargador.'),
    'GTB650': ('Bosch GTB 650', 'https://meli.la/2DibsdV', '/taladros/para-durlock/', 'Ver precio del Bosch GTB 650', 'Atornillador con tope de profundidad para placas, con cable. Confirmá tensión, puntas y accesorios; no es un taladro ni un atornillador de impacto.'),
    'DCF620': ('DeWalt DCF620B', 'https://meli.la/2Rfk4Q2', '/taladros/para-durlock/', 'Ver precio del DeWalt DCF620B', 'Atornillador brushless para drywall con tope de profundidad. Herramienta sola: confirmá batería, cargador y alimentador que necesitás comprar aparte.'),
    'BLD783': ('Black+Decker BLD783D1', 'https://meli.la/2GYZ2VP', '/taladros/black-decker/', 'Ver precio del BLD783D1', 'Taladro percutor inalámbrico Powerconnect. Confirmá batería, cargador, tensión del cargador y configuración del kit local.'),
    'TCRH620': ('Einhell TC-RH 620 4F', 'https://meli.la/2fHsXDs', '/taladros/rotomartillo-einhell/', 'Ver precio del TC-RH 620 4F', 'Rotomartillo con cable y encastre SDS Plus. Confirmá código 4257990, tensión y accesorios del paquete.'),
    'TERH281': ('Einhell TE-RH 28/1 5F', 'https://meli.la/1gnYgwd', '/taladros/rotomartillo-einhell/', 'Ver publicación del TE-RH 28/1 5F · código 4257972', 'Einhell identifica TE-RH 28/1 5F como código 4257972. Confirmá que la unidad ofrecida corresponda a ese código y revisá el contenido de la caja.'),
    'DCH273': ('DeWalt DCH273B', 'https://meli.la/1uYbzCV', '/taladros/rotomartillo-dewalt/', 'Ver precio del DeWalt DCH273B', 'Rotomartillo inalámbrico SDS Plus. La variante B es herramienta sola; sumá batería y cargador compatibles al costo.'),
    'DCD805': ('DeWalt DCD805B · sin batería', 'https://meli.la/1R9rAch', '/taladros/dewalt-inalambrico/', 'Ver precio del DCD805B sin batería', 'Taladro percutor inalámbrico, herramienta sola. La tabla describe un kit DCD805D2: sus dos baterías, cargador y bolso no se incluyen por el nombre DCD805B.'),
    'HEX9': ('Bosch EXPERT HEX-9 HardCeramic · 6 mm', 'https://meli.la/2XU7X44', '/taladros/mecha-porcelanato/', 'Ver precio de la Bosch HEX-9 6 mm', 'Mecha para baldosa dura/porcelanato. Confirmá referencia y medida de 6 mm; rotación sin percusión y condiciones de su ficha.'),
    'EASYGRES': ('RUBI EASYGRES · 6 mm · corte húmedo', 'https://meli.la/1SEcMe1', '/taladros/mecha-porcelanato/', 'Ver precio de la Rubi Easy Gres 6 mm', 'Mecha diamantada para corte húmedo, sin percusión. Confirmá si se vende la mecha sola y qué guía o sistema de agua requiere.'),
    'M123404': ('Milwaukee M12 FUEL 3404-20', 'https://meli.la/1zxo6Um', '/taladros/milwaukee/', 'Ver precio del Milwaukee 3404-20', 'Taladro percutor/atornillador M12. Confirmá herramienta sola o kit, batería M12, cargador y garantía local.'),
    'M182904': ('Milwaukee M18 FUEL 2904-259A', 'https://meli.la/157Rjx8', '/taladros/milwaukee/', 'Ver precio del kit Milwaukee 2904-259A', 'Kit/bundle con el taladro percutor M18 FUEL 2904-20 de la tabla. Confirmá baterías, cargador, accesorios y contenido de esta publicación.'),
    'TIL23': ('Lüsqtoff TIL23-8B', 'https://meli.la/113Ew5S', '/taladros/lusqtoff-inalambrico/', 'Ver precio del TIL23-8B', 'Taladro/atornillador de 12 V sin percusión confirmada. Verificá baterías, capacidad en Ah y cargador de la oferta.'),
    'TAL60': ('Lüsqtoff TAL60-9B', 'https://meli.la/1KgRGVw', '/taladros/lusqtoff-inalambrico/', 'Ver precio del TAL60-9B', 'Taladro/atornillador brushless sin percusión, plataforma Iron Volt. La ficha citada lo vende sin batería ni cargador: confirmá contenido.'),
    'TIL45131': ('Lüsqtoff TIL45131-8BK', 'https://meli.la/1UgHPbY', '/taladros/lusqtoff-inalambrico/', 'Ver precio del TIL45131-8BK', 'Taladro percutor/atornillador brushless Iron Volt. Confirmá batería de 2 Ah, cargador, maletín y código del kit.'),
    'CYL9': ('Bosch CYL-9 · 6 mm · cerámica/azulejo', 'https://meli.la/2wKN4UX', '/taladros/brocas-ceramica/', 'Ver precio de la Bosch CYL-9 6 mm', 'Confirmá CYL-9 Soft Ceramic de 6 mm: la familia citada es para cerámica blanda. El nombre EXPERT del título no acredita compatibilidad con porcelanato duro.'),
    'SDH700': ('Stanley SDH700', 'https://meli.la/1b2mqhW', '/taladros/stanley/', 'Ver precio del Stanley SDH700', 'Taladro percutor con cable. Confirmá variante AR, placa de 220 V/50 Hz y accesorios incluidos.'),
    'SBD715': ('Stanley SBD715C2K', 'https://meli.la/2B5Nkky', '/taladros/stanley/', 'Ver precio del Stanley SBD715C2K', 'Taladro percutor inalámbrico V20. Confirmá sufijo AR, dos baterías, cargador, maleta y el accesorio anunciado.'),
    'DCF850': ('DeWalt DCF850B', 'https://meli.la/1xNiZKX', '/taladros/atornillador-impacto-dewalt/', 'Ver precio del DeWalt DCF850B', 'Atornillador de impacto compacto con encastre de 1/4. No es un taladro; herramienta sola, sin batería ni cargador.'),
    'HSS420': ('Bosch HSS escalonada 4–20 mm · 2608597519', 'https://meli.la/2TD7cMx', '/taladros/mechas-escalonadas/', 'Ver precio de la Bosch HSS 4–20 mm', 'La oferta identifica 2608597519; la tabla documenta 2608597524. Confirmá vástago, secuencia de diámetros y espesor admitido de esta referencia, sin trasladar datos de la otra.'),
}

# Número de archivo: encabezado exacto, posición y título del bloque.
PLACEMENTS = {
    3: ('Modelos con cable y a batería', 'section', 'Consultá el percutor Bosch con cable'),
    4: ('Potencia, velocidades y capacidad del mandril', 'section', 'Dos publicaciones de banco: confirmá modelo y potencia'),
    6: ('Comparativa de modelos por trabajo', 'section', 'Rotomartillos Bosch SDS Plus: cable o batería'),
    8: ('Cable, batería o alimentador', 'section', 'Atornilladores específicos para placas'),
    9: ('Modelos con cable e inalámbricos', 'section', 'Black+Decker: sin percusión o con percusión'),
    10: ('Diferencias entre modelos', 'section', 'Rotomartillos Einhell: comprobá la variante'),
    11: ('Modelos según exigencia', 'section', 'Consultá el rotomartillo DeWalt DCH273B'),
    12: ('TE-CD 18/40 y TP-CD 18/50: sin y con percusión', 'section', 'Einhell Solo: confirmá función y presupuesto completo'),
    13: ('Modelos para uso doméstico y profesional', 'section', 'DeWalt: kit D2 o herramienta sola B'),
    14: ('Tipos de broca para porcelanato', 'section', 'Mechas de 6 mm: carburo o diamante húmedo'),
    15: ('Diferencias entre M12 y M18', 'section', 'Milwaukee: compará plataforma y contenido'),
    16: ('Comparativa de modelos y prestaciones', 'section', 'Lüsqtoff: 12 V, Iron Volt y percusión'),
    17: ('Tipos de punta y materiales compatibles', 'section', 'Consultá la mecha CYL-9 para cerámica blanda'),
    18: ('Modelos con cable e inalámbricos', 'section', 'Stanley: percusión con cable o V20'),
    19: ('Diferencias entre modelos', 'section', 'Atornilladores de impacto DeWalt'),
    20: ('Diferencias entre GSR y GSB', 'section', 'Bosch: GSR 12 V sin percusión o GSB 18 V percutor'),
    21: ('Opciones para comparar', 'section', 'Consultá la referencia Bosch HSS 4–20 mm'),
}


def render_block(keys, title):
    cards = []
    for key in keys:
        name, destination, _, cta, note = OFFERS[key]
        cards.append('<article class="offer-card"><div class="offer-card-top"><span>MERCADO LIBRE</span></div>'
            f'<h3>{escape(name)}</h3><p class="offer-description">{escape(note)}</p>'
            f'<div class="offer-actions"><a class="offer-button" href="{escape(destination, quote=True)}" '
            'target="_blank" rel="nofollow sponsored noopener noreferrer" '
            f'data-affiliate-placement="taladros-contextual">{escape(cta)} ↗</a></div></article>')
    return ('<section class="affiliate-shelf" aria-label="Opciones con enlace de afiliado">'
        f'<div class="affiliate-heading"><h3>{escape(title)}</h3></div><div class="offer-grid">'
        + ''.join(cards) + '</div><p>Enlaces comerciales suministrados por el usuario. TallerLab puede recibir una comisión '
        'por los enlaces de afiliado, sin costo adicional para vos. Confirmá modelo, contenido, precio y stock '
        'en la publicación; no se verificó su contenido actual.</p></section>')


def install_catalog(products, facts, configs):
    for name, destination, guide, _, note in OFFERS.values():
        assert destination in {o['url'] for o in configs[guide]['offers']}
        products['taladros'].append((name, note, destination, guide))
        brand, model = name.split(' ', 1)
        facts[destination] = dict(brand=brand, model=model, use=note,
            power='Consultar modelo y plataforma', specs=['Identidad y kit a confirmar'],
            includes='Consultar publicación', image=None, source=destination,
            source_type='título suministrado por el usuario', evidence_label='Destino sin verificar')
