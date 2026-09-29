"""Afiliados de compresores: identidad y ubicación explícitas por guía.

Los títulos recibidos identifican las ofertas; no acreditan stock ni equivalencia
entre códigos distintos. None conserva los modelos pendientes sin monetizarlos.
"""
DEFAULT_CTA = 'Ver precio y disponibilidad'
# modelo: (referido, descripción del título recibido)
OFFERS = {
    'Nictom IE01': ('2Xv53zX', 'Inflador a batería; color negro anunciado'),
    'Lüsqtoff MCL150-8': ('2r8uZXD', 'Inflador 12 V digital con linterna; 150 PSI anunciados'),
    'Lüsqtoff LC2550B-8': ('2dyFK5e', 'Compresor de 50 L y 2,5 HP anunciados'),
    'BTA AS-1021': ('1EdvSrw', 'Pistola para pintar de baja presión'),
    'BTA ASP1070': ('1EKjbss', 'Pistola HVLP de succión; depósito de 1000 cc anunciado'),
    'BTA ASPM1070': ('2Vpe8U4', 'Pistola para retoques; color plateado anunciado'),
    'Lüsqtoff LC2550BK-8': ('2FtyGQc', 'Oferta titulada LC-2550BK, 50 L monofásico; confirmar sufijo -8 y kit'),
    'Lüsqtoff LC-3550BK': ('21xNVUN', 'Bicilíndrico de 50 L con kit y 3,5 HP anunciados'),
    'Lüsqtoff LC-30100': ('2r6QkaT', 'Bicilíndrico de 100 L y 2200 W anunciados'),
    'Lüsqtoff LC-40100': ('127ZaQu', 'Mando directo de 100 L; oferta titulada LC40100-8'),
    'Gamma G2858AR': ('2TdnN1F', 'Compresor de 100 L y 3 HP anunciados'),
    'Lüsqtoff AA-5000K': ('1xhuQgp', 'Kit de cinco piezas; no incluye compresor'),
    'BTA 279010': ('2W1Y9Zs', 'Kit de aire y pintura de cinco piezas'),
    'BTA 279013': ('16F7cCu', 'Kit de cinco piezas con pistolas de pintar y sopletear'),
    'Lüsqtoff LC-0122': ('19aFAKp', 'Sin aceite; 24 L y 1 HP anunciados'),
    'BTA CSA-24-1': ('2kTMPof', 'Código 272005; sin aceite, 24 L y 2 HP anunciados'),
    'BTA D-CA2-50-6': ('1nobM6T', 'Código 272057.2; 50 L y 2 HP anunciados; distinto del CSA-50-2'),
    'Lüsqtoff LC-30200': ('2vfnWE7', 'Compresor de 200 L y 3 HP anunciados'),
    'BTA D-CA1-25-6': ('14USeGB', '25 L y 2 HP; monofásico de 50 Hz anunciado'),
    'Gamma G2860AR': ('14tM2Xh', 'Sin aceite; 24 L y 2 HP anunciados'),
    'Einhell PRESSITO 18/25': ('14u7fCt', 'Herramienta sola: confirmar batería y cargador aparte'),
    'Einhell PRESSITO 18/21': ('1iNDq73', 'Inflador de la plataforma Power X-Change; confirmar kit'),
    'Makita DMP180Z': ('2uRPKYD', 'Inflador inalámbrico LXT 18 V; confirmar batería y cargador'),
    'Stanley FCCC404STC005': ('26gU4mL', 'Oferta anunciada como 50 L y 2 HP; confirmar capacidad en placa'),
    'Einhell TC-AC 190/24/8 I OF': ('2NsPCBP', 'Compresor TC-AC 190/24/8 I OF; confirmar configuración'),
    'Gadnic AV37-TY': ('2aSkmx1', 'Doble cilindro 12 V; digital, corte automático y linterna anunciados'),
}
PENDING_MODELS = (
    'Gadnic AV000009', 'Gamma G2802AR', 'Gamma G2802KAR',
    'Fengda FD-186K', 'Fengda AS-186', 'Fengda AS-196',
    'Einhell TE-AC 270/50 Silent', 'Einhell TE-AC 430/90/10',
    'Lüsqtoff LC-40200', 'BTA CSA-50-2',
)
# número de archivo, sección de enlaces, sección de cards, modelos, colocación.
PLACEMENTS = [
    (1, 'Qué cambia según la alimentación', None, ['Nictom IE01', 'Lüsqtoff MCL150-8', 'Gadnic AV000009'], 'table'),
    (2, 'Comparativa de marcas', 'Matriz TallerLab: datos que cambian la compra', ['Lüsqtoff LC2550B-8', 'Gamma G2802AR', 'Einhell TE-AC 270/50 Silent'], 'table'),
    (4, 'Kits reales con contenido publicado', None, ['Fengda FD-186K'], 'table'),
    (5, 'Comparación documentada: tres pistolas BTA', None, ['BTA AS-1021', 'BTA ASP1070', 'BTA ASPM1070'], 'table'),
    (7, 'Cinco compresores diseñados para aerografía', None, ['Fengda AS-186', 'Fengda AS-196'], 'table'),
    (9, 'Variantes Lüsqtoff de 50 litros', 'Qué modelo considerar según tu prioridad', ['Lüsqtoff LC2550B-8', 'Lüsqtoff LC2550BK-8', 'Lüsqtoff LC-3550BK'], 'section'),
    (11, 'Qué compresor de 100 L conviene según el uso del taller', None, ['Lüsqtoff LC-30100', 'Lüsqtoff LC-40100', 'Gamma G2858AR'], 'table'),
    (12, 'G2802AR y G2802KAR: qué cambia', None, ['Gamma G2802AR', 'Gamma G2802KAR'], 'table'),
    (13, 'Kits documentados: qué trae cada presentación', None, ['Lüsqtoff AA-5000K', 'BTA 279010', 'BTA 279013'], 'table'),
    (14, 'Prestaciones documentadas: qué cambia entre modelos', 'Qué compresor Lüsqtoff de 100 L buscar según el uso', ['Lüsqtoff LC-30100', 'Lüsqtoff LC-40100'], 'section'),
    (15, 'Modelos sin aceite con datos publicados', None, ['Lüsqtoff LC-0122', 'BTA CSA-24-1', 'BTA CSA-50-2'], 'table'),
    (16, 'Tres modelos documentados de 200 L', None, ['Lüsqtoff LC-30200', 'Lüsqtoff LC-40200'], 'table'),
    (17, 'Ficha del BTA 272057.1', None, ['BTA D-CA1-25-6'], 'section'),
    (18, 'Cuál compresor de 24 litros elegir', None, ['Gamma G2860AR', 'Lüsqtoff LC-0122', 'BTA CSA-24-1'], 'table'),
    (19, 'Presión, caudal y uso: qué dato mirar', None, ['Einhell PRESSITO 18/25', 'Einhell PRESSITO 18/21', 'Makita DMP180Z'], 'table'),
    (20, 'Disponibilidad local, garantía y servicio', None, ['Stanley FCCC404STC005'], 'section'),
    (21, 'Combinaciones documentadas: qué se puede validar', None, ['Einhell TC-AC 190/24/8 I OF', 'Einhell TE-AC 270/50 Silent', 'Einhell TE-AC 430/90/10'], 'section'),
    (22, 'Cinco infladores portátiles documentados', None, ['Gadnic AV000009', 'Makita DMP180Z', 'Einhell PRESSITO 18/25'], 'table'),
    (23, 'Cuatro modelos 12 V doble pistón documentados', None, ['Lüsqtoff MCL150-8', 'Gadnic AV000009', 'Gadnic AV37-TY'], 'table'),
]

def cta(number, model):
    if number == 13:
        return 'Ver precio del kit'
    if number in {4, 7, 12, 14, 16, 17, 20}:
        name = model.replace('Lüsqtoff ', '').replace('Gamma ', '')
        return f'Ver precio del {name}'
    return DEFAULT_CTA

def install_catalog(products, facts, placements):
    """Registrar ofertas sin ampliar las guías con productos de otra categoría."""
    for model, (code, description) in OFFERS.items():
        url = 'https://meli.la/' + code
        guide = next((path for path, config in placements.items() if model in config['models']), '/compresores/50-litros/')
        products['compresores'].append((model, description, url, guide))
        brand, identifier = model.split(' ', 1)
        facts[url] = dict(brand=brand, model=identifier, use='Según consumo y ciclo de trabajo',
            power='Confirmar alimentación en la publicación', specs=[description],
            includes='Confirmar contenido con el vendedor', image=None, source=url,
            source_type='publicación comercial', evidence_label='Título de la oferta suministrado; destino sin verificar',
            warning=('El título recibido indica 50 L; la publicación histórica citada en la guía indica 24 L para este código. Confirmá placa, capacidad y manual antes de comprar.' if model.startswith('Stanley') else
                     'La oferta no incluye el sufijo -8 en su título. Confirmá código de placa y kit antes de trasladar los datos de LC2550BK-8.' if model == 'Lüsqtoff LC2550BK-8' else ''))
        if model == 'Nictom IE01':
            facts[url]['source'] = facts['https://meli.la/2m7TJWQ']['source']
            facts[url]['source_type'] = 'marca'
            facts[url]['evidence_label'] = 'Modelo documentado por la marca; oferta negra suministrada, sin verificar destino'
