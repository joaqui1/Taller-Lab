"""Agrega CTA una vez por modelo, junto a la comparación o como alternativa explícita."""
import json
import re
from pathlib import Path
from generadores_comerciales import OFFERS, PLACEMENTS, PENDING, url, cta

ROOT = Path(__file__).parent
FORCE_BLOCKS = {10: {'GE3481AR'}, 18: {'GNW-70-ER'}}
NOTES = {
    'GNW-70-ER': ('Consultar el Niwa GNW-70-ER', 'El 70-ER de la comparación publica 6 kVA nominales y 7 kVA máximos, arranque eléctrico, ruedas y tanque de 25 L. Contrastá la carga y sus picos antes de elegir ese margen sobre el 55-ER. [Ficha del importador](https://www.rumbosrl.com.ar/printficha.php?product_id=128).'),
    'GE3480AR': ('Gamma 3000V / GE3480AR', 'La [ficha y manual Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-3000v-ge3480ar/) documentan 2,7 kW nominales y 3 kW máximos, salida de 220 V, nafta y tanque de 15 L. Confirmá los picos de las cargas y la batería de arranque, que no está incluida.'),
    'GE3482AR': ('Gamma 8500V / GE3482AR', 'La [ficha Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-8500v/) publica 8,5 kW máximos. El rótulo de 8 kW no identifica inequívocamente potencia continua: pedí confirmación para el código exacto antes de dimensionar una carga sostenida.'),
    'EZ6500CXS': ('Honda EZ6500CXS', 'La [ficha Honda](https://pf.honda.com.ar/producto/EZ6500CXS) publica 5,5 kVA nominales y 6,5 kVA máximos, salida de 220 V y arranque eléctrico. Compará sus datos con los del EG6500CXS en la [guía Honda 6500](/generadores/honda-6500/).'),
    'GE3497AR': ('Gamma Inverter 2 kW', 'La [ficha Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-inverter-2kw/) publica 2 kW nominales y 2,2 kW de pico; tanque de 4 L y 17 kg. Para el ruido, la documentación de esta categoría indica 63 dB al 50 % y 69 dB al 100 %, ambos a 7 m.'),
    'EU30is': ('Honda EU30is: siguiente escalón inverter', 'Honda publica 2,8 kVA nominales y 3 kVA máximos, con salida monofásica de 220 V. Compará la carga de marcha y sus picos por separado. [Ficha Honda](https://pf.honda.com.ar/producto/EU30is).'),
    'GE3481AR': ('Alternativa Gamma actual: 6000V', 'El GE3481AR / 6000V es un modelo distinto del Gamma 6500V. Su manual publica 5,5 kW nominales y 6 kW máximos; tanque de 25 L y arranque eléctrico, con batería no incluida. [Ficha y manual Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-6000v/).'),
    'LGIS3.8-8': ('Alternativa con función motosoldadora', 'El **LGIS3.8-8** es la motosoldadora: su código es distinto del **LGI3.8-8** de la comparativa. La [ficha Lüsqtoff](https://lusqtoff.com.ar/ver-producto/LGIS3.8-8) publica 3,5 kW nominales / 3,8 kW máximos como generador y función MMA de 20–130 A. No incluye pinza porta masa ni porta electrodos.'),
    'GNW-55-E': ('GNW-55-E: otra variante disponible', 'La oferta suministrada identifica **GNW-55-E**, un código distinto del **GNW-55-ER** comparado arriba. No trasladamos al E la potencia, el arranque, el peso ni las ruedas del ER: pedí placa y ficha del código ofrecido antes de dimensionarlo.'),
    'LG950P': ('Alternativa nueva de baja potencia: Lüsqtoff LG950P', 'La [ficha Lüsqtoff](https://lusqtoff.com.ar/ver-producto/LG950P) publica 0,65 kVA nominales y 0,8 kVA máximos; motor 2T, tanque de 4 L y peso de 16,2 kg. Usá la mezcla indicada en su propio manual. Es otro modelo, con especificaciones propias.'),
    'KGE/800': ('Konan KGE/800: opción de baja potencia', 'La [guía de generadores chicos](/generadores/chicos/) documenta 650 W nominales y 800 W máximos según Konan, motor 2T y tanque de 4 L. Confirmá peso y dimensiones de la unidad ofrecida, porque los vendedores publican cifras diferentes.'),
    'LGI5.5-8': ('Lüsqtoff LGI5.5-8: inverter de mayor salida', 'La [ficha Lüsqtoff](https://lusqtoff.com.ar/ver-producto/LGI5.5-8) publica 5,2 kVA máximos, tanque de 10 L y 30 kg; no encontramos potencia nominal en esa ficha. Publica 62 dB sin distancia ni carga: esa cifra no permite compararlo directamente con las mediciones Honda/Gamma.'),
    'GE3491AR': ('Opción trifuel: Gamma TF10000', 'El **GE3491AR / TF10000** es una opción comercial distinta del TF8500 documentado en esta guía. La [ficha Gamma](https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-trifuel-tf10000/) publica potencias continuas de 9 / 8,1 / 7,2 kW y máximas de 10 / 9 / 8 kW con nafta / GLP / gas natural, respectivamente. Elegí por el combustible que usarás y verificá los requisitos de conexión.'),
    'DELTA 2 Max': ('Opciones de mayor capacidad: EcoFlow DELTA 2 Max', 'Es un modelo distinto del DELTA 2 de las tablas. [EcoFlow](https://www.ecoflow.com/us/delta-2-max-portable-power-station) publica **2.048 Wh** y **2.400 W de salida CA** para DELTA 2 Max. La fuente corresponde a la versión estadounidense: confirmá tensión, enchufes y manual de la unidad ofrecida para Argentina.'),
    'AC70P': ('BLUETTI AC70P: variante separada del AC70', 'La **AC70P** tiene **864 Wh** y **1.000 W continuos** según el [manual multirregional de BLUETTI](https://s4.bluettipower.com/bluetti_lgf/support/2025/06/c7116c12-6152-460d-8380-f044baa7c75f.pdf). No es la AC70 de 768 Wh de la tabla. Confirmá tensión y versión regional en la publicación antes de comprar.'),
    'DTGEAB08-4': ('Dyllu DTGEAB08-4: escalón de alrededor de 5 kW', 'La publicación documentada en la [guía de precios](/generadores/precios/) anuncia 5 kW nominales y 5,5 kW máximos para este inverter. Son datos comerciales de esa publicación, sin ensayo físico de TallerLab; confirmá placa y manual de la unidad ofrecida.'),
    'LG3000': ('Lüsqtoff LG3000: escalón de 2–3 kVA', 'La [ficha Lüsqtoff](https://www.lusqtoff.com.ar/ver-producto/LG3000) publica 2,5 kVA nominales / 2,8 kVA máximos, arranque manual y tanque de 15 L. La [guía a nafta](/generadores/a-nafta/) conserva la discrepancia entre esos campos y otro rótulo de potencia del fabricante; confirmá placa y manual.'),
}

def main():
    configs = {}
    for number, keys in PLACEMENTS.items():
        file = next((ROOT / 'paginas/generadores').glob(f'{number:02d}-*.md'))
        text = file.read_text(encoding='utf-8')
        path = re.search(r'^url: "([^"]+)"', text, re.M)[1]
        if keys:
            labels = []
            if 'Dato documentado' not in text:
                labels.append('**Dato documentado:** las especificaciones se atribuyen a las fuentes enlazadas; los datos comerciales y las variantes se identifican por separado.')
            if 'Análisis TallerLab' not in text:
                labels.append('**Análisis TallerLab:** los criterios de selección interpretan la documentación según la carga prevista; esta guía no incluye prueba física de los equipos.')
            if labels:
                position = text.index('\n## ')
                text = text[:position] + '\n\n' + '\n\n'.join(labels) + '\n' + text[position:]
        # Reconstruir siempre desde el contenido editorial, sin acumular columnas/bloques.
        previous_extras = re.findall(r'<!-- GENERADORES-EXTRAS -->\s*(.*?)\s*<!-- /GENERADORES-EXTRAS -->', text, flags=re.S)
        text = re.sub(r'\n*<!-- GENERADORES-EXTRAS -->.*?<!-- /GENERADORES-EXTRAS -->\n*', '\n\n', text, flags=re.S)
        def clean_table(m):
            rows = m[0].splitlines()
            rows = [row for row in rows if not row.startswith('| Oferta |') or row == rows[0]]
            if rows[0].rstrip().endswith(('| Oferta |', '| Precio |')):
                rows = [row[:row.rfind('|', 0, row.rfind('|')) + 1].rstrip() for row in rows]
            return '\n'.join(rows) + '\n'
        text = re.sub(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', clean_table, text)
        matched = set()
        def table(match):
            rows = match[0].splitlines()
            hits = {}
            for i, row in enumerate(rows[2:], 2):
                cells = row.strip('|').split('|')
                identity = ' '.join(cells[:2])
                key = next((k for k in keys if k not in matched and k not in FORCE_BLOCKS.get(number, set()) and re.search(r'(?<![\w/-])' + re.escape(k) + r'(?![\w.-])', identity, re.I)), None)
                if key:
                    hits[i] = key
                    matched.add(key)
            if not hits:
                return match[0]
            result = []
            for i, row in enumerate(rows):
                value = 'Oferta' if i == 0 else ':---' if i == 1 else f'[Ver precio →]({url(hits[i])})' if i in hits else '—'
                result.append(row.rstrip() + ' ' + value + ' |')
            return '\n'.join(result) + '\n'
        # Transposed comparisons get a CTA row directly under their columns.
        if number in {4, 21}:
            def transposed(m):
                rows = m[0].splitlines()
                headers = rows[0].strip('|').split('|')
                values = []
                for cell in headers:
                    key = next((k for k in keys if k in cell), None)
                    values.append(f'[Ver precio →]({url(key)})' if key else 'Oferta' if not values else '—')
                    if key:
                        matched.add(key)
                return m[0] + ('| ' + ' | '.join(values) + ' |\n' if len(matched) else '')
            text = re.sub(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', transposed, text, count=1)
        else:
            text = re.sub(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', table, text)
        extras = []
        for key in keys:
            if key in matched:
                continue
            heading, note = NOTES[key]
            extras.append(f'### {heading}\n\n{note}\n\n[{cta(key)}]({url(key)})')
        for previous in previous_extras:
            old_urls = set(re.findall(r'https://meli\.la/[A-Za-z0-9]+', previous))
            new_urls = {url(k) for k in keys if k not in matched}
            if old_urls and old_urls == new_urls:
                extras = [previous]
                break
        if number == 15:
            extras.append('### Generadores chicos: referencia breve\n\nSi buscás un equipo de baja potencia como el Konan KGE/800 o el Lüsqtoff LG950P, consultá la [comparativa de generadores chicos](/generadores/chicos/) para ver potencias, dimensiones y límites de los datos publicados.')
        if extras:
            # Situar las alternativas tras la tabla de modelos pertinente.
            candidates = list(re.finditer(r'(?m)^## [^\n]+\n(?:(?!^## ).*\n)*', text))
            section = next((m for m in candidates if re.search(r'comparativa|modelos|gama|opciones|versiones', m[0].splitlines()[0], re.I)), candidates[0])
            position = section.end()
            text = text[:position].rstrip() + '\n\n<!-- GENERADORES-EXTRAS -->\n\n' + '\n\n'.join(extras) + '\n\n<!-- /GENERADORES-EXTRAS -->\n\n' + text[position:].lstrip('\n')
        if keys:
            file.write_text(text, encoding='utf-8')
        configs[path] = dict(file=file.name, models=keys, offers=[dict(model=k, url=url(k), cta=cta(k)) for k in keys])
    (ROOT / 'generadores-ofertas.json').write_text(json.dumps(configs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{sum(bool(k) for k in PLACEMENTS.values())} guías; {sum(map(len, PLACEMENTS.values()))} asociaciones; {len(OFFERS)-len(PENDING)} productos; {len(PENDING)} pendiente')

if __name__ == '__main__':
    main()
