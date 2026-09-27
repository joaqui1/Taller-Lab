from pathlib import Path
import csv, unicodedata, re, json
from collections import defaultdict, Counter

ROOT = Path(r'C:\Users\joaqu\Desktop\keywords')
OUT = Path(__file__).parent
def norm(s):
    return re.sub(r'\s+', ' ', ''.join(c for c in unicodedata.normalize('NFKD', s.lower()) if not unicodedata.combining(c))).strip()
def number(s):
    try: return float(s)
    except (ValueError,TypeError): return None
def slug(s): return re.sub(r'[^a-z0-9]+', '-', norm(s)).strip('-')
original = defaultdict(list)
raw_count=0
for p in ROOT.glob('*.csv'):
    with p.open(encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            original[norm(r['Keyword'])].append((p.name,r)); raw_count+=1
measured=[]
for p in sorted((ROOT/'semrush').glob('*.csv')):
    with p.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            r['family']=p.stem.replace('semrush_',''); r['file']=p.name
            measured.append(r)
known={norm(r['keyword']):r for r in measured if number(r['kd']) is not None}
all_sem={norm(r['keyword']):r for r in measured}
selected=[]
for i,line in enumerate((OUT/'seo-prioridades-100-base.txt').read_text(encoding='utf-8').splitlines(),1):
    kw,page,reason=line.split('|')
    assert norm(kw) in original,kw
    assert norm(kw) not in known,kw
    selected.append(dict(rank=i,keyword=kw,page=page,reason=reason,sem=all_sem.get(norm(kw))))
assert len(selected)==100 and len({norm(r['keyword']) for r in selected})==100

# Manual intent mapping: provisional editorial pages, not SERP-confirmed clusters.
alias={norm(r['keyword']):r['page'] for r in selected}
groups={
'compresores/lusqtoff-50-litros':['compresor lusqtoff 50 litros opiniones'],
'compresores/50-litros':['compresor 50 litros','mejor compresor de aire 50 litros'],
'compresores/para-auto':['mejor compresor de aire para auto'],
'compresores/silenciosos':['mejor compresor de aire silencioso'],
'compresores/para-aerografo':['mejor compresor para aerografo','compresor para aerografo silencioso'],
'compresores/sin-aceite':['compresor sin aceite opiniones'],
'compresores/para-pintar-autos':['mejor compresor para pintar autos'],
'compresores/einhell-tc-ac-190-24-8':['compresor einhell tc ac 190 24 8','compresor einhell 24 litros opiniones'],
'hidrolavadoras/para-autos':['mejores hidrolavadoras para autos'],
'hidrolavadoras/para-lavadero':['que hidrolavadora comprar para lavadero de autos'],
'hidrolavadoras/gamma':['hidrolavadora gamma opiniones'],
'hidrolavadoras/niwa':['hidrolavadora niwa opiniones'],
'hidrolavadoras/lusqtoff-hl-120':['hidrolavadora lusqtoff hl 120 opiniones'],
'hidrolavadoras/lusqtoff-hl-150':['hidrolavadora lusqtoff hl 150 opiniones'],
'hidrolavadoras/daewoo-1600w':['hidrolavadora daewoo 1600w opiniones'],
'hidrolavadoras/black-decker-1300w':['hidrolavadora black decker 1300w','hidrolavadora black decker 1300w opiniones'],
'hidrolavadoras/inalambricas':['hidrolavadora inalambrica','mejor hidrolavadora inalambrica'],
'hidrolavadoras/profesionales':['hidrolavadora profesional'],
'sierras/circulares':['mejor sierra circular calidad precio'],
'sierras/de-banco':['mejor sierra de mesa calidad precio'],
'sierras/caladoras':['mejor sierra caladora calidad precio'],
'sierras/circulares-lusqtoff':['sierra circular lusqtoff opiniones'],
'sierras/ingletadoras-einhell':['ingletadora einhell opiniones'],
'sierras/ingletadoras-lusqtoff':['ingletadora lusqtoff opiniones'],
'sierras/de-banco-einhell':['sierra de banco einhell opiniones'],
'sierras/bosch-gks-150':['sierra circular bosch gks 150','bosch gks 150 opiniones'],
'sierras/bosch-gts-254':['sierra de banco bosch gts 254','sierra de banco bosch gts 254 opiniones'],
'sierras/stanley-sc16':['sierra circular stanley sc16','sierra circular stanley 1600w opiniones'],
'sierras/ingletadoras-telescopicas':['ingletadora telescopica','mejor ingletadora telescopica calidad precio'],
'amoladoras/black-decker-g720':['amoladora g720 black decker opiniones'],
'amoladoras/inalambricas':['mejor amoladora a bateria'],
'amoladoras/stanley':['amoladora stanley opiniones'],
'amoladoras/discos-porcelanato':['mejor disco para cortar porcelanato'],
'amoladoras/discos-ceramica':['mejor disco para cortar ceramica'],
'amoladoras/discos-metal':['mejores discos de corte para metal'],
'amoladoras/lusqtoff-850w':['amoladora lusqtoff 850w opiniones'],
'amoladoras/comparativa-general':['mejor amoladora calidad precio'],
'taladros/inalambricos':['mejor taladro inalambrico'],
'taladros/percutores':['mejor taladro percutor','mejor taladro percutor profesional'],
'taladros/atornilladores-de-impacto':['mejor atornillador de impacto'],
'taladros/para-durlock':['que atornillador comprar para durlock'],
'taladros/stanley':['taladro stanley opiniones'],
'taladros/para-casa':['taladro para casa','mejor taladro calidad precio'],
'soldadoras/tig':['mejor soldadora tig'],
'soldadoras/lusqtoff':['soldadora lusqtoff opiniones'],
'soldadoras/esab-handy-arc-160i':['esab handy arc 160i opiniones'],
'soldadoras/dogo-mig-150':['soldadora dogo mig 150 opiniones'],
'soldadoras/lusqtoff-iron-250':['soldadora lusqtoff iron 250','iron 250 lusqtoff opiniones'],
'soldadoras/guantes':['mejores guantes para soldar'],
'soldadoras/alambre-flux':['alambre flux 0.8','mejor alambre flux'],
'soldadoras/mig-sin-gas':['soldadora mig sin gas','mejor soldadora mig sin gas'],
'soldadoras/mascaras-fotosensibles':['mascara de soldar fotosensible','mejor mascara de soldar fotosensible'],
'generadores/comparativa-general':['grupo electrogeno','generador electrico','grupo electrogeno precio','mejor generador eléctrico calidad precio'],
'generadores/para-casa':['generador electrico para casa'],
'generadores/dimensionamiento-casa':['que generador necesito para una casa'],
'generadores/inverter':['generador inverter','mejores generadores inverter','mejor generador inverter calidad precio'],
'generadores/silenciosos':['generador eléctrico silencioso','mejor generador silencioso'],
'generadores/portatiles':['mejores generadores electricos portatiles'],
'generadores/lusqtoff':['generador lusqtoff','generador lusqtoff opiniones'],
'generadores/hyundai':['generador hyundai','generadores hyundai opiniones'],
'generadores/a-gas':['generador electrico a gas','generador a gas natural domiciliario','generador nafta o gas'],
'generadores/solar-portatil':['generador solar portatil','mejores generadores solares','generador solar portatil con placa solar'],
'generadores/aire-acondicionado':['generador electrico para aire acondicionado','grupo electrogeno para aire acondicionado de 3000 frigorias','grupo electrogeno para aire acondicionado y heladera'],
'generadores/3000w':['generador 3000w','que puedo conectar a un generador de 3000 watts'],
'generadores/consumo':['consumo de generador electrico','cuanto consume un generador de 5000 watts'],
}
for page,terms in groups.items():
    for t in terms: alias[norm(t)]=page
def page_for(r):
    k=norm(r['keyword'])
    if k in alias:return alias[k]
    # Unmerged topics retain a provisional page instead of imposing false equivalence.
    return r['family']+'/'+slug(r['keyword'])
page_groups=defaultdict(list)
for r in measured: page_groups[page_for(r)].append(r)
for r in selected:r['related']=page_groups.get(r['page'],[])

(OUT/'semrush-100-pendientes-kd.txt').write_text('\n'.join(r['keyword'] for r in selected)+'\n',encoding='utf-8')
stats=[]
for family in sorted({r['family'] for r in measured}):
    rows=[r for r in measured if r['family']==family]
    stats.append(dict(family=family,rows=len(rows),known_kd=sum(number(r['kd']) is not None for r in rows),unknown_volume=sum(number(r['volume']) is None for r in rows),zero_volume=sum(number(r['volume'])==0 for r in rows)))

lines=['# Próximas 100 consultas de KD — afiliación Mercado Libre', '',
'Fecha de análisis: 23/09/2026. Fuente: siete CSV originales y siete CSV de Semrush suministrados. Mercado objetivo asumido: Argentina; los CSV de Semrush no incluyen país, dispositivo ni fecha absoluta de actualización.', '',
f'Se cruzaron {raw_count:,} filas originales con {len(measured)} filas Semrush. Hay {len(known)} consultas normalizadas con KD numérico. Se normalizaron tildes, mayúsculas y espacios para evitar duplicados. No se infirió el KD de sinónimos ni de modelos.', '',
'La selección contiene 98 consultas ausentes de Semrush y 2 reintentos con KD n/d. Ninguna de las 100 tiene KD conocido en los archivos. Las 100 aparecen en los originales. El orden es una prioridad editorial de investigación, no una predicción de tráfico o ingresos ni un orden definitivo de publicación.', '',
'Criterios: utilidad para decidir una compra, señal de demanda en los originales, evidencia de páginas relacionadas en Semrush, posibilidad de aportar una comparación útil, y cuánto cambia una medición la decisión de crear o ampliar una página. Se penalizaron sinónimos redundantes, términos de alquiler/reparación, intención académica y expansiones industriales alejadas de compras afiliadas. No se forzaron cupos iguales por familia.', '',
'Los valores 50/500/5000/50000 de los originales se usan como señales gruesas, no como volumen exacto. No se suman volúmenes de variantes. n/d en volumen no equivale a KD ausente ni a cero búsquedas. Las prioridades no incorporan comisión, elegibilidad ni stock, datos todavía no aportados.', '',
'## Estado de los archivos', '', '| Familia | Filas | KD conocido | Volumen n/d | Volumen 0 |','|---|---:|---:|---:|---:|']
for s in stats:lines.append(f"| {s['family']} | {s['rows']} | {s['known_kd']} | {s['unknown_volume']} | {s['zero_volume']} |")
lines += ['', '## Lectura de los datos', '',
'La primera tanda sobreponderó modificadores como mejor y opiniones. Los resultados justifican probar las consultas de producto y categoría antes de descartarlas por supuesta dificultad. Ejemplos medidos: generador eléctrico para casa 390/KD6, generador inverter 480/KD9, compresor 50 litros 1000/KD15, amoladora de banco 3600/KD13, soldadora MIG con gas 1000/KD11 y sierra sin fin para madera 720/KD8. Son volumen/KD reportados, no tráfico asegurado.', '',
'Generadores ya tiene 80 consultas medidas: recibe cinco nuevas para cubrir huecos, no otra tanda de sinónimos. Taladros y parte de hidrolavadoras muestran más incertidumbre; medir sus consultas comerciales principales ayuda a decidir cuánto invertir.', '',
'Soldadora para aluminio tiene volumen 210 pero KD n/d. Mejor hidrolavadora calidad precio tiene volumen 20 pero KD n/d. Diferencias entre soldadura TIG y MIG no aparece en la exportación de soldadoras, aunque estaba en la lista anterior.', '',
'## Lista priorizada por página propuesta', '',
'La página es un destino editorial provisional. Una fila puede ampliar una página ya investigada. Las URLs son propuestas relativas; no son páginas existentes. El solapamiento debe verificarse en SERP antes de decidir separación. Las filas 1–40 son la primera tanda, 41–80 la segunda y 81–100 la ampliación.', '',
'| # | Keyword | Página propuesta | Evidencia Semrush en esa página | Por qué medir |','|---:|---|---|---|---|']
for r in selected:
    evidence='; '.join(f"{x['keyword']} (vol. {x['volume']}, KD {x['kd']})" for x in r['related']) or 'Sin consulta asignada medida; señal solo del original.'
    lines.append(f"| {r['rank']} | {r['keyword']} | /{r['page']}/ | {evidence} | {r['reason']} |")
lines += ['', '## Reglas de publicación y medición', '',
'1. Consultar las 100 en la misma base Argentina. Exportar keyword, volumen, KD, intención y fecha.',
'2. Antes de escribir, revisar formato y URLs de los diez resultados orgánicos. KD bajo por sí solo no significa que una guía de afiliación satisfaga la intención.',
'3. Unificar modelo, precio y opiniones cuando resuelvan la misma decisión. Mantener separadas una gama y un modelo solo si cada página aporta una comparación propia.',
'4. Validar especialmente: compresor auto/moto/inalámbrico; compresor 24/25 litros; hidrolavadora profesional/para lavadero; cerámica/porcelanato; generador inverter/silencioso/portátil; taladro inalámbrico/percutor. No publicar cruces automáticos de marca × potencia × uso.',
'5. En las guías, comparar fichas y versiones verificadas, explicar compatibilidad y limitaciones, y actualizar ofertas. No atribuir pruebas propias cuando solo hay investigación documental.',
'6. Confirmar stock, elegibilidad para referidos y condiciones de cada producto en ML. Medir clics salientes y conversiones atribuibles antes de ampliar masivamente.', '',
'## Fuentes metodológicas', '',
'- Semrush, significado de N/A y volumen cero: https://www.semrush.com/kb/129-keywords-show-n-a',
'- Semrush, análisis en lote: https://www.semrush.com/kb/257-keyword-overview',
'- Google, afiliación y valor añadido: https://developers.google.com/search/docs/essentials/spam-policies',
]
(OUT/'analisis-semrush-prioridades.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

page_lines=['# Mapa provisional de las 319 consultas Semrush', '',
'Todas las filas de los siete archivos están incluidas una sola vez. Las agrupaciones son hipótesis editoriales para decidir qué medir y qué unificar, no clusters validados por coincidencia de resultados. Cuando la equivalencia no es clara se conserva un tema provisional separado. No constituye autorización ni recomendación de crear una URL por cada grupo.', '',
'Los modelos Einhell de 24 litros y las gamas Stanley de 1600 W requieren comprobar versión exacta antes de integrar opiniones genéricas en una ficha específica. No se suman volúmenes de variantes.', '',
'| Página propuesta | Keyword medida | Volumen Semrush | KD |','|---|---|---:|---:|']
for page,rows in sorted(page_groups.items()):
    for r in rows:page_lines.append(f"| /{page}/ | {r['keyword']} | {r['volume']} | {r['kd']} |")
(OUT/'mapa-paginas-semrush.md').write_text('\n'.join(page_lines)+'\n',encoding='utf-8')
print(json.dumps(dict(original_rows=raw_count,original_unique_normalized=len(original),semrush_rows=len(measured),kd_known=len(known),kd_missing=[r['keyword'] for r in measured if number(r['kd']) is None],volume_missing=sum(number(r['volume']) is None for r in measured),selected=len(selected),selected_retries=sum(r['sem'] is not None for r in selected),selected_by_family=dict(Counter(r['page'].split('/')[0] for r in selected)),page_groups=len(page_groups),checks='100 únicas, originales presentes, ningún KD conocido repetido, 319 filas incluidas en mapa'),ensure_ascii=False))
