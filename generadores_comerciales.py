"""Ofertas suministradas: códigos exactos y distribución editorial autorizada."""
OFFERS = {
    'EU22i': ('Honda EU22i', '2AwxqaH', 'Honda EU22i'),
    'GE3497AR': ('Gamma GE3497AR', '1B4sjDN', 'Gamma Inverter 2 kW'),
    'LGIS3.8-8': ('Lüsqtoff LGIS3.8-8', '2TcYRTK', 'Lüsqtoff LGIS3.8-8'),
    'GE3480AR': ('Gamma GE3480AR', '31SZbvv', 'Gamma 3000V'),
    'GE3481AR': ('Gamma GE3481AR', '15vKtBp', 'Gamma 6000V'),
    'EU30is': ('Honda EU30is', '2X86187', 'Honda EU30is'),
    'EG6500CXS': ('Honda EG6500CXS', '1sxNfJ5', 'Honda EG6500CXS'),
    'EZ6500CXS': ('Honda EZ6500CXS', '2Kt6i6Y', 'Honda EZ6500CXS'),
    'GNW-55-E': ('Niwa GNW-55-E', '1JRpbcM', 'Niwa GNW-55-E'),
    'GNW-70-ER': ('Niwa GNW-70-ER', '18BCMV2', 'Niwa GNW-70-ER'),
    'KGE/800': ('Konan KGE/800', '19gLhpz', 'Konan KGE/800'),
    'LG950P': ('Lüsqtoff LG950P', '2oCYsWY', 'Lüsqtoff LG950P'),
    'LGI5.5-8': ('Lüsqtoff LGI5.5-8', '1pJFrBq', 'Lüsqtoff LGI5.5-8'),
    'GE3491AR': ('Gamma GE3491AR TF10000', '2sRF5ic', 'Gamma TF10000'),
    'LG7500EXT': ('Lüsqtoff LG7500EXT', '1k8qxpL', 'Lüsqtoff LG7500EXT'),
    'ET12000': ('Honda ET12000', '2WRqiZR', 'Honda ET12000'),
    'DELTA 2 Max': ('EcoFlow DELTA 2 Max', '2N74aN6', 'EcoFlow DELTA 2 Max'),
    'AC70P': ('BLUETTI AC70P', '1z4M5aB', 'BLUETTI AC70P'),
    'LG3000': ('Lüsqtoff LG3000', '2fhftj7', 'Lüsqtoff LG3000'),
    'LGI8.0-9': ('Lüsqtoff LGI8.0-9', '2xPEW5s', 'Lüsqtoff LGI8.0-9'),
    'GE3482AR': ('Gamma GE3482AR', '1Ha3UGR', 'Gamma 8500V'),
    'EZ3000CX': ('Honda EZ3000CX', '2dryX8a', 'Honda EZ3000CX'),
    'DTGEAB08-4': ('Dyllu DTGEAB08-4', '221u1rq', 'Dyllu DTGEAB08-4'),
    'CMC 3000 W': ('CMC 3000 W', '2r7eRux', 'CMC 3000 W'),
    'HHY2200F': ('Hyundai HHY2200F', '2fgrR1N', 'Hyundai HHY2200F'),
    'HY7500LE': ('Hyundai HY7500LE', '1oUjAJk', 'Hyundai HY7500LE'),
}
# HHY2200 no acredita el sufijo F: conservar el referido sin asociarlo a esa fila.
PENDING = {'HHY2200F': 'Confirmar Modelo/placa HHY2200F en la publicación HHY2200.'}
PLACEMENTS = {
    1: ['EU22i', 'GE3480AR', 'GE3481AR', 'EG6500CXS', 'EZ6500CXS', 'ET12000', 'EZ3000CX'],
    2: ['GE3481AR', 'LG3000', 'LGI8.0-9', 'GE3482AR', 'EZ3000CX', 'DTGEAB08-4', 'CMC 3000 W'],
    3: ['EU22i', 'EU30is', 'EG6500CXS', 'EZ6500CXS', 'ET12000'],
    4: ['EG6500CXS', 'EZ6500CXS'],
    5: ['EU22i', 'GE3480AR', 'GE3481AR', 'EU30is', 'EG6500CXS'],
    6: ['EU22i', 'GE3497AR', 'EU30is', 'LGI5.5-8', 'DTGEAB08-4'],
    7: ['LG7500EXT', 'ET12000'],
    8: ['EU22i', 'GE3497AR', 'GE3480AR', 'GE3481AR', 'EG6500CXS', 'EZ6500CXS', 'LG3000', 'GE3482AR'],
    9: ['HY7500LE'],
    10: ['GE3481AR'],
    11: ['LGIS3.8-8', 'LG950P', 'LGI5.5-8', 'LG7500EXT', 'LG3000'],
    12: ['GE3497AR', 'GE3480AR', 'GE3481AR', 'GE3491AR', 'GE3482AR'],
    13: ['EU22i', 'GE3480AR', 'GE3481AR', 'EU30is', 'EG6500CXS'],
    14: [],
    15: ['EU22i', 'GE3497AR', 'EU30is'],
    16: ['EU22i', 'GE3497AR', 'LGI5.5-8'],
    17: ['LG950P'],
    18: ['GNW-55-E', 'GNW-70-ER'],
    19: ['GE3491AR'],
    20: ['DELTA 2 Max', 'AC70P'],
    21: ['KGE/800', 'LG950P'],
}

def url(key):
    return 'https://meli.la/' + OFFERS[key][1]

def cta(key):
    return ('Ver precio de ' if key in {'DELTA 2 Max', 'AC70P'} else 'Ver precio del ') + OFFERS[key][2]

def install_catalog(products, facts, configs):
    for key, (name, code, label) in OFFERS.items():
        if key in PENDING:
            continue
        guide = next(path for path, config in configs.items() if key in config['models'])
        products['generadores'].append((name, 'Oferta del modelo indicado; consultar precio y condiciones vigentes', url(key), guide))
        brand, model = name.split(' ', 1)
        facts[url(key)] = dict(brand=brand, model=model, use='Dimensionar con la guía del modelo',
            power='Confirmar nominal, tensión y fase', specs=['Modelo: ' + model],
            includes='Consultar contenido de la publicación', image=None, source=url(key),
            source_type='publicación comercial', evidence_label='Oferta suministrada; destino sin verificar')
