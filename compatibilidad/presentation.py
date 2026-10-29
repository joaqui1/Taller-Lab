"""Citable answers with explicit scope, authorship and primary sources."""
from datetime import date, datetime
from html import escape
from compatibilidad import catalog
from compatibilidad.search import normalize_code, GLOBAL_SEARCH_INDEX
from compatibilidad.rules import evaluate_compatibility

def product_path(product):
    prefix={'bateria':'baterias','herramienta':'herramientas-bateria','cargador':'cargadores','adaptador':'cargadores'}[product.product_type]
    return '/'+prefix+'/'+product.slug+'/'

def model_picker_options():
    return '<datalist id="compat-models">'+''.join(f'<option value="{escape(p.mpn)}">{escape(p.brand)} · {escape(p.model_name)}</option>' for p in catalog.CATALOG_PRODUCTS if p.status=='publicado')+'</datalist>'

def verified_directory():
    groups=[]
    for kind,label in [('bateria','Baterías'),('cargador','Cargadores'),('herramienta','Herramientas')]:
        products=sorted((p for p in catalog.CATALOG_PRODUCTS if p.status=='publicado' and p.product_type==kind),key=lambda p:(p.brand,p.model_name))
        links=''.join(f'<li><a href="{product_path(p)}"><span>{escape(p.brand)} · {escape(p.model_name)}</span><code>{escape(p.mpn)}</code></a></li>' for p in products)
        groups.append(f'<div><h3>{label} <span>({len(products)})</span></h3><ul>{links}</ul></div>')
    return '<section class="compat-directory"><h2>Elegí un modelo verificado</h2><p>Entrá a su ficha para ver las baterías, herramientas o cargadores documentados para ese código.</p><div class="compat-directory-grid">'+''.join(groups)+'</div></section>'

def related_combinations(source,target,current_path):
    related_products=[]
    seen=set()
    for relation in catalog.RELATIONS:
        a=catalog.PRODUCTS_BY_ID[relation['source_product_id']];b=catalog.PRODUCTS_BY_ID[relation['target_product_id']]
        path=relation_path(a,b)
        if path==current_path or not {a.id,b.id}.intersection({source.id,target.id}):continue
        if evaluate_compatibility(a,b).is_compatible:
            for product in (a,b):
                if product.id in {source.id,target.id} or product.id in seen:
                    continue
                seen.add(product.id)
                related_products.append(product)
                if len(related_products)==3:
                    break
        if len(related_products)==3:
            break
    rows=''.join(f'<li><a href="{product_path(product)}">{escape(product.brand)} {escape(product.model_name)} ({escape(product.mpn)})</a></li>' for product in related_products)
    return '<section><h2>Otras combinaciones documentadas de estos modelos</h2><ul>'+rows+'</ul></section>' if rows else ''

def relation_path(source,target):
    return '/compatibilidad/'+normalize_code(source.mpn).lower()+'-con-'+normalize_code(target.mpn).lower()+'/'

def relationship_paths():
    return tuple(relation_path(catalog.PRODUCTS_BY_ID[r['source_product_id']],catalog.PRODUCTS_BY_ID[r['target_product_id']]) for r in catalog.RELATIONS)

def relationship_is_indexable(evaluation):
    """Las relaciones solo pueden indexarse si declaran alcance propio explícito."""
    return bool(evaluation.conditions or evaluation.exclusions)

def coverage_summary():
    active=sum(p.status=='publicado' for p in catalog.CATALOG_PRODUCTS)
    checked=catalog.CURRENT_METADATA.get('last_checked_at','')
    return f'<aside class="compat-coverage"><strong>{active} modelos verificados · {len(catalog.RELATIONS)} relaciones documentadas · {len(catalog.CATALOG_PRODUCTS)-active} referencias pendientes</strong><p>Última comprobación: {escape(checked[:10] or "sin fecha")} (UTC). Autor de la recopilación: <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a>. <a href="/compatibilidad/cambios/">Historial de cambios</a>.</p></aside>'

def _date_es(value):
    try:
        return date.fromisoformat(str(value)[:10]).strftime('%d/%m/%Y')
    except (TypeError, ValueError):
        return str(value or '')

def source_check_text(evidence):
    checked=evidence.date_reviewed
    checked_label=_date_es(checked)
    result=(f'Comprobado automáticamente contra la ficha oficial de {escape(evidence.manufacturer)} '
            f'el <time datetime="{escape(checked)}">{escape(checked_label)}</time>.')
    reviewer=getattr(evidence,'source_approved_by',None)
    approved_at=getattr(evidence,'source_approved_at',None)
    if reviewer and approved_at:
        result+=(f' <span>Cambio de fuente aprobado por {escape(reviewer)} el '
                 f'<time datetime="{escape(approved_at)}">{escape(_date_es(approved_at))}</time>.</span>')
    return result

def source_panel(product):
    eid=product.evidence_identity_id
    evidence=catalog.EVIDENCES_BY_ID.get(eid)
    if product.status!='publicado' or not evidence:
        return ''
    supporting=''.join(f'<li><a data-compat-event="clic_fuente" href="{escape(url)}">Manual oficial complementario</a></li>' for url in evidence.supporting_urls)
    return f'<section class="compat-source"><h2>Fuente y comprobación documental</h2><p>{escape(evidence.document_title)} · {escape(evidence.manufacturer)}. {source_check_text(evidence)}</p><blockquote>{escape(evidence.excerpt)}</blockquote><p>{escape(evidence.section_or_page)}.</p><ul><li><a data-compat-event="clic_fuente" href="{escape(evidence.official_url)}">Consultar ficha oficial</a></li>{supporting}</ul><p>Recopilación de <a href="/autor/joaquin-vallasciani/">Joaquín Vallasciani</a>. <a href="/compatibilidad/metodologia/">Método y límites</a> · <a href="/contacto/">Reportar una corrección con modelo y fuente</a>.</p></section>'

def relation_table(printable=False):
    rows=[]
    for r in catalog.RELATIONS:
        source=catalog.PRODUCTS_BY_ID[r['source_product_id']];target=catalog.PRODUCTS_BY_ID[r['target_product_id']]
        evaluation=evaluate_compatibility(source,target)
        if not evaluation.is_compatible:continue
        label=source.brand+' '+source.model_name+' → '+target.model_name
        urls='; '.join(e.official_url for e in evaluation.evidence_chain)
        source_links=''.join(f'<a data-compat-event="clic_fuente" href="{escape(e.official_url)}">{escape(e.manufacturer)}: {escape(e.source_id.split("-")[-1])}</a> ' for e in evaluation.evidence_chain)
        source_link=f'<a href="{product_path(source)}">{escape(source.brand)} {escape(source.model_name)} ({escape(source.mpn)})</a>'
        target_link=f'<a href="{product_path(target)}">{escape(target.brand)} {escape(target.model_name)} ({escape(target.mpn)})</a>'
        rows.append(f'<tr><td>{source_link} → {target_link}</td><td>{escape(evaluation.verdict)}</td><td>{escape(r["date_reviewed"])} (UTC)</td><td>{escape(urls) if printable else source_links}</td></tr>')
    return '<div class="compat-table-scroll" tabindex="0" aria-label="Relaciones documentadas; tabla desplazable"><table class="compat-table"><caption>Compatibilidades documentadas entre modelos exactos</caption><thead><tr><th scope="col">Modelos y códigos</th><th scope="col">Respuesta</th><th scope="col">Fecha</th><th scope="col">Fuentes oficiales</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>' if rows else '<p>No hay relaciones con evidencia vigente. Consultá el historial y la metodología.</p>'

def resolve_relationship(path):
    part=path.removeprefix('/compatibilidad/').strip('/')
    if '-con-' not in part:return None
    a,b=part.split('-con-',1)
    source=GLOBAL_SEARCH_INDEX.find_one(a);target=GLOBAL_SEARCH_INDEX.find_one(b)
    if not source or not target:return None
    return source,target,evaluate_compatibility(source,target)

def guide_links(*products):
    urls=[]
    for p in products:
        if p.guide_url and p.guide_url not in [u for u,_ in urls]:
            urls.append((p.guide_url,p))
    if not urls:return ''
    def label(p):
        noun=product_kind(p)[0]
        return f'Cómo elegir {noun} a batería' if p.product_type=='herramienta' else 'Guía relacionada de TallerLab'
    return '<p>Para seguir: '+' · '.join(f'<a href="{escape(u)}">{escape(label(p))}</a>' for u,p in urls)+'.</p>'

def relationship_page(path):
    from compatibilidad.commercial import render_pair_commercial
    resolved=resolve_relationship(path)
    if not resolved:return None
    source,target,evaluation=resolved
    title=f'¿{display_name(source,True)} sirve con {display_name(target,True)}?'
    title=title[0]+title[1].upper()+title[2:]
    answer=f'Sí{", bajo las condiciones indicadas" if evaluation.requires_conditions else ""}. {source.brand} {source.model_name} ({source.mpn}) es compatible con {target.brand} {target.model_name} ({target.mpn}), según las fuentes oficiales indicadas abajo.' if evaluation.is_compatible else 'No se confirma esta combinación: '+evaluation.summary_text
    limits=''.join('<li>'+escape(text)+'</li>' for text in evaluation.conditions+evaluation.exclusions)
    conditions='<section class="compat-conditions"><h2>Condiciones y límites documentados</h2><ul>'+limits+'</ul></section>' if limits else ''
    scope='La cadena comprueba el código de cada producto, su sistema de baterías y una declaración de compatibilidad del fabricante.' if evaluation.is_compatible else 'Esta combinación no tiene una confirmación documental vigente en la base. Las fichas individuales no prueban por sí solas la relación entre ambos productos.'
    # Robots directives live in the document head, where the renderer emits them once.
    noindex=''
    return f'{noindex}<article class="compat-answer"><nav aria-label="Migas de pan"><a href="/compatibilidad/">Base de compatibilidad</a> / Consulta por modelo</nav><h1>{escape(title)}</h1><p class="compat-direct-answer">{escape(answer)}</p><p><strong>{escape(evaluation.verdict)}</strong></p>{conditions}<h2>Qué demuestra esta respuesta</h2><p>{scope} Se refiere a las variantes identificadas; no acredita stock, adaptadores externos ni ensayo físico.</p><p>Fichas de los modelos: <a href="{product_path(source)}">{escape(source.brand)} {escape(source.model_name)} ({escape(source.mpn)})</a> · <a href="{product_path(target)}">{escape(target.brand)} {escape(target.model_name)} ({escape(target.mpn)})</a>.</p>{guide_links(source,target)}{source_panel(source)}{source_panel(target)}{render_pair_commercial(source,target)}{related_combinations(source,target,path)}<h2>Consultar otra combinación</h2><p><a href="/compatibilidad/">Buscador y tabla completa</a> · <a href="/datos/compatibilidad/baterias.json">Descargar datos con fuentes y fechas</a>.</p></article>'


# --- SEO: nombres legibles, enlaces entre fichas y datos estructurados por respuesta ---
_TOOL_KINDS=(('gws','amoladora','la'),('amoladora','amoladora','la'),('gdx','llave de impacto','la'),('taladro','taladro','el'),('multitool','multiherramienta oscilante','la'),('pintar','equipo para pintar','el'),('sierra','sierra','la'),('atornillador','atornillador','el'),('llave','llave de impacto','la'))

def product_kind(product):
    """Sustantivo y artículo en español para titular respuestas sin repetir el tipo."""
    if product.product_type=='bateria':return 'batería','la'
    if product.product_type in ('cargador','adaptador'):return 'cargador','el'
    text=(product.model_name+' '+product.slug).lower()
    for key,noun,article in _TOOL_KINDS:
        if key in text:return noun,article
    return 'herramienta','la'

def display_name(product,with_article=False):
    """'la batería Bosch ProCORE18V 4.0Ah'; omite el tipo si el nombre comercial ya lo incluye."""
    noun,article=product_kind(product)
    name=f'{product.brand} {product.model_name}'
    if noun.split()[0] in product.model_name.lower():
        return name
    return f'{article+" " if with_article else ""}{noun} {name}'

def compatible_counterparts(product):
    """Modelos con relación compatible vigente y la URL de su respuesta."""
    items=[]
    for relation in catalog.RELATIONS:
        a=catalog.PRODUCTS_BY_ID.get(relation['source_product_id']);b=catalog.PRODUCTS_BY_ID.get(relation['target_product_id'])
        if not a or not b or product.id not in (a.id,b.id):continue
        if not evaluate_compatibility(a,b).is_compatible:continue
        items.append((b if a.id==product.id else a,relation_path(a,b)))
    return items

def compatible_counterpart_pages(product):
    """Modelos relacionados con sus fichas indexables, sin cambiar la API existente."""
    return [(counterpart,product_path(counterpart)) for counterpart,_ in compatible_counterparts(product)]

def relation_meta(source,target,evaluation):
    noun_a=display_name(source);noun_b=display_name(target)
    codes=[c for c,p in ((source.mpn,source),(target.mpn,target)) if c.lower() not in p.model_name.lower()]
    title=f'¿{noun_a} sirve con {noun_b}?'+(f' ({" + ".join(codes)})' if codes else '')
    title='¿'+title[1].upper()+title[2:]
    date=min((e.date_reviewed for e in evaluation.evidence_chain),default='')
    if evaluation.is_compatible:
        cond=' bajo condiciones' if evaluation.requires_conditions else ''
        desc=f'Sí{cond}: {display_name(source,True)} ({source.mpn}) es compatible con {display_name(target,True)} ({target.mpn}) según la documentación oficial de {source.brand}. Extracto, enlace a la fuente y fecha de verificación{" ("+date+")" if date else ""}.'
    else:
        desc=f'No se confirma que {display_name(source,True)} ({source.mpn}) sirva con {display_name(target,True)} ({target.mpn}): no hay evidencia documental vigente.'
    return title,desc

def relation_schema(source,target,evaluation,path,base):
    import json as _json
    title,desc=relation_meta(source,target,evaluation)
    relation=next((r for r in catalog.RELATIONS if r['source_product_id']==source.id and r['target_product_id']==target.id),None)
    latest=(relation or {}).get('content_changed_at') or max((p.content_changed_at for p in (source,target)),default='')
    def thing(p):
        return {'@type':'Thing','name':f'{p.brand} {p.model_name}','identifier':p.mpn,'url':base+product_path(p),'sameAs':p.official_url}
    data={'@context':'https://schema.org','@type':'WebPage','name':title,'description':desc,'url':base+path,'inLanguage':'es-AR',
          'about':[thing(source),thing(target)],
          'author':{'@type':'Person','name':'Joaquín Vallasciani','url':base+'/autor/joaquin-vallasciani/'},
          'publisher':{'@id':base+'/#organization'},
          'isPartOf':{'@type':'Dataset','name':'Base argentina de compatibilidad de baterías, herramientas y cargadores','description':'Dataset técnico y verificación documental de relaciones de compatibilidad para herramientas a batería de 18V y 20V comercializadas en Argentina.','url':base+'/compatibilidad/'},
          'citation':sorted({e.official_url for e in evaluation.evidence_chain}|{u for e in evaluation.evidence_chain for u in e.supporting_urls})}
    if latest:data['dateModified']=latest
    return '<script type="application/ld+json">'+_json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+'</script>'

def guide_compatibility_block(guide_url):
    """Enlaza desde cada guía editorial a las fichas verificadas que la citan como guía."""
    items=[]
    for p in catalog.CATALOG_PRODUCTS:
        if p.status!='publicado' or p.guide_url!=guide_url:continue
        n=len(compatible_counterparts(p))
        if not n:continue
        if p.product_type=='herramienta':
            label=f'Baterías compatibles con {p.brand} {p.model_name} ({p.mpn})'
        elif p.product_type=='bateria':
            label=f'Herramientas y cargadores para la batería {p.brand} {p.model_name} ({p.mpn})'
        else:
            label=f'Baterías que carga {p.brand} {p.model_name} ({p.mpn})'
        items.append(f'<li><a href="{product_path(p)}">{escape(label)}</a> · {n} combinaciones verificadas</li>')
    if not items:return ''
    return '<section class="compat-guide-block"><h2>Compatibilidad de baterías verificada</h2><p>Antes de comprar una batería o un cargador aparte, comprobá el código exacto. Cada ficha enlaza la documentación oficial del fabricante.</p><ul>'+''.join(items)+'</ul><p><a href="/compatibilidad/">Ver la base completa de compatibilidad</a></p></section>'

def product_last_modified(product):
    """Latest approved product-content date, including its published editorial ficha."""
    dates=[]
    raw=getattr(product, 'content_changed_at', '')
    try:
        dates.append(date.fromisoformat(str(raw)[:10]).isoformat())
    except (TypeError, ValueError):
        pass
    try:
        from compatibilidad.editorial import get_published_ficha
        ficha=get_published_ficha(product.id)
        raw=ficha.get('last_approved_modified_at') if ficha else None
        if raw:
            try:
                normalized=date.fromisoformat(str(raw)[:10]).isoformat()
            except ValueError:
                normalized=datetime.strptime(str(raw), '%d/%m/%Y').date().isoformat()
            dates.append(normalized)
    except (ImportError, AttributeError, TypeError, ValueError):
        pass
    return max(dates, default='')

def compatibility_lastmod():
    """Fecha del último cambio de contenido por URL pública de compatibilidad."""
    dates={}
    def put(path,date):
        if date and (path not in dates or date>dates[path]):dates[path]=date[:10]
    for p in catalog.CATALOG_PRODUCTS:
        if p.status!='publicado':continue
        latest=product_last_modified(p)
        put(product_path(p),latest)
        put('/plataformas/'+p.platform_id+'/',latest)
    for r in catalog.RELATIONS:
        a=catalog.PRODUCTS_BY_ID.get(r['source_product_id']);b=catalog.PRODUCTS_BY_ID.get(r['target_product_id'])
        if a and b:put(relation_path(a,b),r.get('content_changed_at',''))
    latest=max(dates.values(),default='')
    for path in ('/compatibilidad/','/compatibilidad/matriz-imprimible/','/compatibilidad/cambios/'):
        if latest:dates[path]=latest
    return dates

def latest_content_changed_at():
    dates=[product_last_modified(p) for p in catalog.CATALOG_PRODUCTS if p.status=='publicado']
    dates.extend(r.get('content_changed_at','') for r in catalog.RELATIONS if r.get('content_changed_at'))
    return max(dates,default='')
