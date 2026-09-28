import csv, json, re, unicodedata
from pathlib import Path
from collections import Counter, defaultdict

ROOT=Path(__file__).parent
SOURCE=Path(r'C:\Users\joaqu\Desktop\keywords')
def norm(s):
    return re.sub(r'\s+', ' ', ''.join(c for c in unicodedata.normalize('NFKD',s.lower()) if not unicodedata.combining(c))).strip()
def num(s):
    try:return float(s.replace(',','.'))
    except (ValueError,AttributeError):return None
raw=[]
original_rows=0
original_keywords=set()
for p in SOURCE.glob('*.csv'):
    with p.open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            original_rows+=1
            original_keywords.add(norm(r['Keyword']))
for p in sorted((SOURCE/'semrush').glob('*.csv')):
    with p.open(encoding='utf-8-sig',newline='') as f:
        for line,r in enumerate(csv.DictReader(f,delimiter=';' if 'adicional' in p.name else ','),2):
            if 'Palabra clave' in r:
                r=dict(keyword=r['Palabra clave'],intent=r['Intención'],volume=r['Volumen'],kd=r['KD %'],cpc=r['CPC (USD)'])
            raw.append(dict(keyword=r['keyword'],intent=r['intent'],volume=num(r['volume']),kd=num(r['kd']),cpc=num(r['cpc']),source=p.name,line=line))
groups=defaultdict(list)
for r in raw:groups[norm(r['keyword'])].append(r)
rows={}
conflicts=[]
for k,rs in groups.items():
    # The additional export completes older measurements; use it for duplicate queries.
    rs.sort(key=lambda r: ('adicional' in r['source'],r['kd'] is not None,r['volume'] is not None))
    rows[k]=rs[-1]
    if len({(r['volume'],r['kd'],r['intent']) for r in rs})>1:conflicts.append(dict(keyword=k,records=rs))
pages=json.loads((ROOT/'inventario-afiliacion-analisis.json').read_text(encoding='utf-8'))
by_url={p['url']:p for p in pages}
aliases={
    'grupo electrogeno':'/generadores/comparativa-general/',
    'generador electrico':'/generadores/comparativa-general/',
    'grupo electrogeno precio':'/generadores/precios/',
    'grupo electrogeno chico':'/generadores/chicos/',
    'generador lusqtoff':'/generadores/lusqtoff/',
    'grupo electrogeno honda':'/generadores/honda/',
    'compresor 100 litros':'/compresores/100-litros/',
    'compresor 24 litros':'/compresores/24-litros/',
    'generador electrico silencioso':'/generadores/silenciosos/',
    'generador solar portatil':'/generadores/estacion-de-energia-portatil/',
    'filtro de aire compresor':'/compresores/filtros/',
    'como elegir una amoladora':'/amoladoras/',
    'soldadora mig sin gas':'/soldadoras/mig-sin-gas/',
    'soldadora de punto':'/soldadoras/soldadora-de-punto/',
    'soldadora tig ac dc':'/soldadoras/soldadora-tig-ac-dc/',
}
matches=defaultdict(list)
unmatched=[]
for k,r in rows.items():
    candidates=[p for p in pages if k in [norm(v) for v in p['keywords']]]
    if k in aliases:candidates=[by_url[aliases[k]]]
    if not candidates:
        # Match exact filename phrase as another explicitly authored page target.
        candidates=[p for p in pages if k==norm(re.sub(r'^\d+-','',Path(p['file']).stem).replace('-',' '))]
    if not candidates:
        unmatched.append(r)
        continue
    candidates.sort(key=lambda p:(k!=norm(p['keywords'][0]), len(p['url'])))
    p=candidates[0]
    matches[p['url']].append(r)

ranked=[]
linked_audit=[]
for p in pages:
    all_rs=matches.get(p['url'],[])
    commercial=[r for r in all_rs if {'C','T'} & set(re.findall(r'[ICTN]',r['intent']))]
    measured=[r for r in commercial if r['volume'] is not None and r['kd'] is not None and r['volume']>0]
    qualified=[r for r in measured if r['volume']>=100 and r['kd']<=25]
    if p['rendered_links']: linked_audit.append(dict(url=p['url'],keywords=all_rs,qualified=bool(qualified),links=p['rendered_links']))
    if not p['published'] or not qualified:continue
    for r in qualified:r['priority_index']=r['volume']/(r['kd']+10)
    r=max(qualified,key=lambda r:r['priority_index'])
    ranked.append(dict(**p,main=r,other_queries=[x for x in all_rs if x is not r],index=round(r['priority_index'],3),affiliate=bool(p['rendered_links'])))
ranked.sort(key=lambda p:p['index'],reverse=True)
strict=[p for p in ranked if p['affiliate']]
result=dict(source_rows=len(raw),unique_keywords=len(rows),duplicate_keywords=sum(len(rs)>1 for rs in groups.values()),conflicts=conflicts,pages=len(pages),linked_pages=len(linked_audit),qualified_pages=len(ranked),strict_pages=len(strict),strict=strict,ranked=ranked,linked_audit=linked_audit,unmatched_commercial=[r for r in unmatched if re.search(r'[CT]',r['intent']) and (r['volume'] or 0)>=100])
result.update(original_rows=original_rows,original_unique=len(original_keywords),semrush_missing_original=[r['keyword'] for k,r in rows.items() if k not in original_keywords])
(ROOT/'resultado-potencial-paginas.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
pending=[p for p in ranked if not p['affiliate']][:21]
selected=strict+pending
assert len(selected)==30 and len({p['url'] for p in selected})==30
assert all(p['main']['volume']>=100 and p['main']['kd']<=25 for p in selected)
assert all(p['published'] for p in selected)
assert all(bool(p['rendered_links'])==p['affiliate'] for p in selected)
lines=[
    '# 30 oportunidades comerciales de TallerLab',
    '',
    'Análisis: 27/09/2026. Alcance: archivos de keywords del Escritorio y HTML generado por la copia local actual de TallerLab. No se verificó el despliegue público ni el stock, redirección o elegibilidad vigente de las ofertas.',
    '',
    f'Se revisaron {original_rows:,} filas de siete CSV originales, {len(raw)} filas de ocho CSV de Semrush (140 de consultas adicionales), {len(rows)} consultas Semrush únicas y {len(pages)} páginas publicables en el sitio local. Los originales de Google Keyword Planner usan rangos gruesos; su Competition es competencia publicitaria y no KD orgánico. Se usaron volumen y KD de Semrush para la selección.',
    '',
    'Hay 26 páginas con al menos un enlace meli.la realmente presente en una etiqueta <a> del HTML. Solo 9 cumplen además los filtros elegidos de intención C o T (incluye I,C e I,T), volumen >=100/mes y KD <=25. El corte de volumen es una decisión de este análisis, no una definición universal de buen volumen.',
    '',
    'Por lo tanto, no existen 30 páginas que cumplan todos esos criterios en los datos y código revisados. La lista reúne las 9 elegibles actuales y las 21 mejores ampliaciones que necesitan incorporar enlaces de afiliado. Las dos listas se ordenan por volumen/(KD+10), un índice propio y orientativo para equilibrar demanda y dificultad, no una métrica Semrush ni una estimación de ingresos. No se suman variantes de una misma página.',
    '',
    'Argentina es el mercado asumido por el contenido y los enlaces. Los CSV Semrush no registran país ni dispositivo ni fecha absoluta de consulta. Los valores se conservan tal como fueron exportados; no son una actualización de métricas en vivo. La exportación adicional completa KD e intención ausentes en dos consultas duplicadas. No se transfirió KD entre modelos distintos.',
    '',
    '## 9 páginas con enlace y métricas suficientes',
    '',
    '| # | Página existente | Keyword medida | Volumen/mes | KD | Intención | Enlace de afiliado | Fuente, fila |',
    '|---:|---|---|---:|---:|---|---|---|',
]
for i,p in enumerate(strict,1):
    r=p['main']; links='; '.join(p['rendered_links'])
    lines.append(f"| {i} | {p['url']} | {r['keyword']} | {r['volume']:,.0f} | {r['kd']:.0f} | {r['intent']} | {links} | {r['source']}:{r['line']} |")
lines += ['', '**Compresores de 50 litros:** el enlace https://meli.la/32SJoX7 corresponde al kit Lüsqtoff AA-5000K de accesorios, no a un compresor. Cumple presencia de afiliación, pero su monetización del producto principal está incompleta. La prioridad práctica de la guía de taladro percutor inalámbrico es mayor para vender el producto buscado.', '', '## 21 ampliaciones para completar 30 oportunidades', '', 'Todas estas páginas existen y tienen métricas comerciales suficientes, pero no muestran un enlace meli.la en el HTML actual.', '', '| # | Página existente | Keyword medida | Volumen/mes | KD | Intención | Fuente, fila |', '|---:|---|---|---:|---:|---|---|']
for i,p in enumerate(pending,10):
    r=p['main']
    lines.append(f"| {i} | {p['url']} | {r['keyword']} | {r['volume']:,.0f} | {r['kd']:.0f} | {r['intent']} | {r['source']}:{r['line']} |")
lines += ['', '## Acciones concretas', '',
    '- Mejorar primero las guías generales de hidrolavadoras, generadores y amoladoras Bosch: comparar modelos exactos y facilitar el paso desde la decisión al precio de cada modelo.',
    '- Para abrir nuevas oportunidades de monetización, comenzar por taladro inalámbrico, rotomartillo, taladro percutor, amoladora de banco y disco flap. Tienen el mayor índice entre las páginas sin enlace.',
    '- Compresor para auto ya tiene una oferta vinculada a esa ruta en AFFILIATE_PRODUCTS (Nictom IE01), pero el artículo no contiene el referido y el renderizador no lo agrega. Taladro de banco presenta la misma situación con Omaha AB550161K. Hidrolavadora Lüsqtoff y su HL100-7 también tienen una oferta configurada que no aparece en la guía. Son oportunidades concretas de integración; tener una oferta en la configuración no equivale a mostrarla en la página.',
    '- Mantener diferenciadas la guía general de generadores y la guía de precios; la segunda necesita resolver presupuesto y costo del equipo. El volumen 6.600 de grupo electrogeno y el 5.400 de generador electrico pertenecen a una misma página y no se sumaron.',
    '- No incluir sierra circular (8.100/KD23), sensitiva (3.600/KD13) o sierra sable (1.900/KD10) como comerciales confirmadas: Semrush las etiqueta I. Pueden ser futuras candidatas si una revisión de resultados y conversiones demuestra intención de compra.',
    '- Hidrolavadora Karcher (5.400/KD32) quedó fuera del umbral KD<=25; no carece de demanda, pero requiere más esfuerzo según esta métrica.',
    '', '## Otras 17 páginas con afiliación fuera del filtro', '', '| Página | Métricas asignadas disponibles | Motivo |', '|---|---|---|']
strict_urls={p['url'] for p in strict}
for p in linked_audit:
    if p['url'] in strict_urls:continue
    metrics='; '.join(f"{r['keyword']}: vol. {r['volume'] if r['volume'] is not None else 'n/d'}, KD {r['kd'] if r['kd'] is not None else 'n/d'}, {r['intent']}" for r in p['keywords'])
    reason='Sin consulta Semrush equivalente identificada; no asignar KD de otro modelo' if not p['keywords'] else 'Volumen inferior a 100 o intención únicamente I'
    lines.append(f"| {p['url']} | {metrics or 'Sin medición equivalente'} | {reason} |")
lines += ['', '## Fuentes y validación', '',
    '- Datos: C:/Users/joaqu/Desktop/keywords/*.csv y C:/Users/joaqu/Desktop/keywords/semrush/*.csv. La columna Fuente, fila ubica cada medición.',
    '- Páginas: paginas/**/*.md; afiliación y HTML: servidor_local.py, AFFILIATE_PRODUCTS y render_article_page. Se inspeccionaron los enlaces <a href> después de generar cada una de las 178 páginas.',
    '- Definiciones de intención, volumen y KD: [Semrush Keyword Overview](https://www.semrush.com/kb/257-keyword-overview).',
    '- Comprobaciones: 30 URLs únicas, todas publicables, intención C/T, volumen numérico >=100, KD numérico <=25; 9 con href de afiliado y 21 sin él.',
    '- El potencial económico sigue dependiendo de comisiones, conversión, precio, oferta y tráfico real. Estos datos no se aportaron; el orden refleja oportunidad SEO y estado de afiliación.',
]
(ROOT/'30-paginas-potencial-comercial-2026-09-27.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['source_rows','unique_keywords','duplicate_keywords','pages','linked_pages','qualified_pages','strict_pages']},ensure_ascii=False))
print('STRICT')
for p in strict:print(p['url'],p['main'],p['rendered_links'])
print('TOP 40')
for i,p in enumerate(ranked[:40],1): print(i,p['url'],p['main']['keyword'],p['main']['volume'],p['main']['kd'],p['main']['intent'],p['affiliate'],p['index'])
print('LINKED AUDIT')
for p in linked_audit:print(p['url'],[(r['keyword'],r['volume'],r['kd'],r['intent']) for r in p['keywords']])
print('UNMATCHED COMMERCIAL',result['unmatched_commercial'])
