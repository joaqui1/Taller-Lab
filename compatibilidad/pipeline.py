"""Fetch, validate, publish and restore documentary state without AI inference."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from compatibilidad import catalog
from compatibilidad.models import Evidence, Verdict
from compatibilidad.sources import PROFILES, PROFILE_NAMES, OFFICIAL_DOMAINS, official_url, contains, fetch_source, technical_text, documented_facts
from compatibilidad.storage import StateStore

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
CANDIDATES_FILE = DATA_DIR / 'candidates.json'
SNAPSHOTS_DIR = DATA_DIR / 'snapshots'
ALERTS_FILE = DATA_DIR / 'pipeline_alerts.json'
OFFICIAL_SOURCES_REGISTRY = PROFILES

def relation(source, target, evidence_ids):
    return {'id':f'REL-{source}-{target}', 'source_product_id':source, 'target_product_id':target,
            'relation_type':'cargador_hacia_bateria' if source.startswith('CHG-') else 'bateria_hacia_herramienta',
            'verdict':Verdict.COMPATIBLE_DOCUMENTADO.value, 'conditions':[], 'exclusions':[],
            'required_packs_count':1, 'evidence_ids':evidence_ids, 'derivation_method':'documentacion_primaria',
            'notes':'Identidad, pertenencia y declaración oficial comprobadas.', 'recommendations':[],
            'date_reviewed':datetime.now(timezone.utc).date().isoformat()}

def configured_relations(products):
    published={p['id'] for p in products if p['status']=='publicado'}
    result=[]
    profiles={p['product_id']:p for p in PROFILES}
    for source in products:
        if source['id'] not in published or source['id'] not in profiles:
            continue
        for target in products:
            if target['id'] not in published or target['id'] not in profiles or source['platform_id']!=target['platform_id']:
                continue
            if (source['product_type'],target['product_type']) not in (('bateria','herramienta'),('cargador','bateria')):
                continue
            # Scope is explicit in reviewed profiles; no relation by voltage/brand.
            allowed=profiles[source['id']].get('compatible_target_types', ['herramienta'] if source['id']=='BAT-BOSCH-PROCORE-4AH' else ['bateria'] if source['id'].startswith('CHG-GAMMA-') else [])
            if target['product_type'] in allowed:
                result.append(relation(source['id'],target['id'],['DOC-'+source['id'],'DOC-'+target['id']]))
    return result

class CompatibilityPipeline:
    def __init__(self, store=None, fetcher=None):
        self.store=store
        self.fetcher=fetcher or fetch_source
        self.documents={}

    def load_candidates(self):
        if not CANDIDATES_FILE.exists():
            return []
        data=json.loads(CANDIDATES_FILE.read_text(encoding='utf8'))
        if not isinstance(data,list):
            raise ValueError('La cola de candidatos debe ser una lista')
        return data

    def run_check_sources(self, check_online=True):
        self.documents={}
        def check(profile):
            url=catalog.PRODUCTS_BY_ID[profile['product_id']].official_url
            report={'source_id':profile['product_id'],'url':url,'http_status':None,
                    'status':'no_comprobado','last_fetched_at':None}
            if not check_online:
                return report,None
            try:
                doc=self.fetcher(url)
                doc=dict(doc)
                doc['primary_text']=doc['text']
                doc['supporting_documents']={}
                doc['supporting_urls']=profile.get('supporting_urls',[])
                doc['technical_text']=technical_text(doc['text'],url)
                for supporting_url in doc['supporting_urls']:
                    support=self.fetcher(supporting_url)
                    if support['http_status']!=200 or not official_url(support['url']):
                        raise ValueError('Documento complementario no verificado')
                    doc['text']+=' '+support['text']
                    doc['supporting_documents'][supporting_url]=support
                    doc['technical_text']+=' '+technical_text(support['text'],supporting_url)
                if doc['http_status']!=200 or not official_url(doc['url']):
                    raise ValueError('Respuesta o dominio final inválidos')
                report.update(status='accesible',http_status=200,content_hash=doc['hash'],
                              text_hash=hashlib.sha256(doc['text'].encode('utf8')).hexdigest(),
                              last_fetched_at=doc['fetched_at'],url=doc['url'])
                return report,doc
            except Exception as exc:
                report.update(status='inaccesible',error=type(exc).__name__)
                return report,None
        with ThreadPoolExecutor(max_workers=4) as executor:
            entries=list(executor.map(check,PROFILES))
        for report,doc in entries:
            if doc:
                self.documents[report['source_id']]=doc
        return [report for report,_ in entries]

    def validate_candidate(self,candidate):
        errors=[]
        pid=candidate.get('id') or candidate.get('product_id')
        profile=next((p for p in PROFILES if p['product_id']==pid),None)
        product=catalog.PRODUCTS_BY_ID.get(pid)
        if not profile or not product:
            errors.append('Modelo sin perfil documental revisado; queda pendiente')
        if not official_url(candidate.get('official_url','')):
            errors.append('Dominio oficial inválido')
        if product and candidate.get('official_url')!=product.official_url:
            errors.append('URL no corresponde al perfil de este producto')
        if product and candidate.get('mpn')!=product.mpn:
            errors.append('MPN no corresponde al producto configurado')
        if candidate.get('product_type') not in ('bateria','herramienta','cargador','adaptador'):
            errors.append('Tipo de producto inválido')
        if candidate.get('platform_id') not in catalog.PLATFORMS_BY_ID:
            errors.append('Plataforma desconocida')
        if profile and candidate.get('platform_id')!=profile['platform']:
            errors.append('Pertenencia no corresponde al perfil')
        try:
            reviewed=datetime.fromisoformat(candidate.get('date_reviewed','')).date()
            if reviewed>datetime.now(timezone.utc).date():
                errors.append('Fecha futura')
        except (ValueError,TypeError):
            errors.append('Fecha de revisión inválida')
        if candidate.get('review_method')!='declaracion_sistema_oficial':
            errors.append('Método no soportado por este extractor')
        doc=self.documents.get(pid)
        if not doc:
            errors.append('Fuente no obtenida en este ciclo')
        elif profile:
            if not all(contains(doc.get('technical_text',doc['text']),v) for v in profile['assertions']):
                errors.append('La fuente cambió o no sostiene identidad/pertenencia')
            if not candidate.get('excerpt') or not contains(doc.get('technical_text',doc['text']),candidate['excerpt']):
                errors.append('Extracto no localizado en el documento')
        return not errors,errors

    def execute_maintenance(self,dry_run=False,check_online=True):
        if not isinstance(dry_run,bool) or not isinstance(check_online,bool):
            raise ValueError('dry_run y check_online deben ser booleanos')
        store=self.store or StateStore()
        previous=store.current()
        state=json.loads(json.dumps(previous or catalog.baseline_state()))
        expected=previous['metadata']['version'] if previous else None
        reports=self.run_check_sources(check_online)
        if not check_online:
            return {'status':'NO_EJECUTADO_OFFLINE','dry_run':dry_run,'sources_monitored':len(reports),
                    'sources_operational':0,'snapshot_file':None,'sources':reports,'version':state['metadata']['version']}
        products={p['id']:p for p in state['products']}
        for profile in PROFILES:
            if profile.get('product') and profile['product_id'] not in products:
                products[profile['product_id']]=dict(profile['product'])
        evidences={e['id']:e for e in state['evidences']}
        candidates=[]; alerts=[]; approved=0
        for profile in PROFILES:
            pid=profile['product_id']; product=products[pid]
            candidate={'id':pid,'mpn':product['mpn'],'product_type':product['product_type'],
                'platform_id':profile['platform'],'official_url':product['official_url'],
                'excerpt':profile['excerpt'],'date_reviewed':datetime.now(timezone.utc).date().isoformat(),
                'review_method':'declaracion_sistema_oficial'}
            valid,errors=self.validate_candidate(candidate)
            doc=self.documents.get(pid)
            old=evidences.get('DOC-'+pid)
            if valid and old and old.get('content_text'):
                from compatibilidad.sources import normalize
                old_technical=technical_text(old['content_text'],old['official_url'])
                if old.get('supporting_urls'):
                    # Supporting manuals are included after the primary text.
                    old_technical=normalize(old.get('product_facts',{}).get('_technical_text',old['content_text']))
                if normalize(doc.get('technical_text',doc['text'])) != old_technical:
                    valid=False
                    errors.append('Contenido documental modificado: requiere revisión del perfil antes de republicar')
            candidate.update(status='aprobado' if valid else 'pendiente',errors=errors)
            candidates.append(candidate)
            if not valid:
                product['status']='conflicto' if pid in self.documents else 'pendiente'
                eid='DOC-'+pid
                if eid in evidences:
                    evidences[eid]['status']='suspendida'
                alerts.append({'product_id':pid,'errors':errors})
                continue
            doc=self.documents[pid]
            product.update(status='publicado',specs={},gtin_ean=None,
                model_name=PROFILE_NAMES[pid],
                is_argentina_catalog=True,
                market_availability_notes='Identidad y sistema comprobados en la ficha oficial argentina; no indica stock.',
                notes='Compatibilidad documentada para las relaciones indicadas abajo.',
                evidence_identity_id='DOC-'+pid,evidence_platform_id='DOC-'+pid)
            if profile.get('facts'):
                product.update(profile['facts'])
            if not profile.get('facts') and product['brand']=='Gamma':
                product['voltage_nominal']=None
                product['voltage_max']='20 V'
                product['capacity_ah']=2.0 if pid=='BAT-GAMMA-G12490AR' else 4.0 if pid=='BAT-GAMMA-G12491AR' else None
            elif not profile.get('facts') and pid=='BAT-BOSCH-PROCORE-4AH':
                product.update(capacity_ah=4.0,voltage_nominal='18 V',voltage_max=None)
            elif not profile.get('facts'):
                product.update(capacity_ah=None,voltage_nominal='18 V',voltage_max=None)
            if not profile.get('facts') and pid=='CHG-GAMMA-G12493AR':
                product['specs']={'tiempo_carga_G12490AR':'40 minutos según fabricante'}
            claims=['identidad','pertenencia']
            if profile.get('compatible_target_types') or pid in ('BAT-BOSCH-PROCORE-4AH','TOOL-BOSCH-GWS-18V-10PSC') or product['brand']=='Gamma':
                claims.append('compatibilidad')
            evidence=Evidence(id='DOC-'+pid,source_id=pid,manufacturer=product['brand'],
                official_url=doc['url'],document_title='Ficha oficial: '+product['model_name'],
                section_or_page='Identificación y declaración de sistema en la ficha de producto',excerpt=profile['excerpt'],
                date_consulted=doc['fetched_at'][:10],date_reviewed=candidate['date_reviewed'],
                verification_method='declaracion_sistema_oficial',reviewer='TallerLab: comprobación automática de afirmaciones configuradas',
                evidence_hash=hashlib.sha256(doc['text'].encode('utf8')).hexdigest(),status='verificada',
                product_ids=[pid],claim_types=claims,text_assertions=profile['assertions'],content_text=doc['text'],
                product_facts={**documented_facts(profile,catalog.PRODUCTS_BY_ID[pid]),'_technical_text':doc.get('technical_text',doc['text'])},
                supporting_urls=doc.get('supporting_urls',[]),primary_text=doc.get('primary_text',doc['text']),
                supporting_documents=doc.get('supporting_documents',{}))
            evidences[evidence.id]=evidence.to_dict(); approved+=1
        state.update(products=list(products.values()),evidences=list(evidences.values()),
                     relations=configured_relations(list(products.values())),sources=reports,candidates=candidates,
                     platforms=[p.to_dict() for p in catalog.PLATFORMS])
        state['observed_documents']={a['product_id']:self.documents[a['product_id']] for a in alerts if a['product_id'] in self.documents}
        state['metadata'].update(engine_version='2',last_checked_at=datetime.now(timezone.utc).isoformat())
        state['changelog'].append({'version':'pendiente_publicacion','date':datetime.now(timezone.utc).date().isoformat(),
            'author':'TallerLab: mantenimiento documental', 'description':f'{approved} perfiles comprobados; {len(alerts)} suspendidos o pendientes.',
            'affected_records':[p['product_id'] for p in PROFILES]})
        catalog.validate_state(state)
        published=None
        if not dry_run:
            published=store.publish(state,expected)
            catalog.apply_state(published)
        queue=[]
        for candidate in self.load_candidates():
            valid,errors=self.validate_candidate(candidate)
            queue.append({'id':candidate.get('id'),'status':'configurado' if valid else 'pendiente','errors':errors})
        return {'status':'REVISION_REQUERIDA' if alerts else 'OK','dry_run':dry_run,'candidate_queue':queue,
                'version':published['metadata']['version'] if published else state['metadata']['version'],
                'snapshot_file':published['metadata']['version'] if published else None,
                'sources_monitored':len(reports),'sources_operational':len(self.documents),
                'published_products':sum(p['status']=='publicado' for p in state['products']),
                'candidates_approved':approved,'candidates_pending':len(alerts),'total_candidates':len(candidates),
                'pending_count':len(alerts),'alerts_generated':alerts,'sources':reports}

    def rollback_to_snapshot(self,version):
        catalog.apply_state((self.store or StateStore()).rollback(version))
        return True

    def approve_source_change(self,product_id,text_hash,reviewer,note):
        """Explicit operator approval of a changed document, not automatic guessing."""
        if not reviewer.strip() or len(note.strip())<15:
            raise ValueError('La aprobación requiere revisor y motivo documentado')
        store=self.store or StateStore()
        previous=store.current()
        state=json.loads(json.dumps(previous or catalog.baseline_state()))
        profile=next((p for p in PROFILES if p['product_id']==product_id),None)
        if not profile:
            raise ValueError('Modelo sin perfil documental')
        product=next(p for p in state['products'] if p['id']==product_id)
        self.run_check_sources()
        doc=self.documents.get(product_id)
        if not doc:
            raise ValueError('No se pudieron obtener todos los documentos del perfil')
        actual=hashlib.sha256(doc['text'].encode('utf8')).hexdigest()
        if actual!=text_hash or not official_url(doc['url']) or doc['http_status']!=200:
            raise ValueError('El documento ya no coincide con el hash revisado')
        if not all(contains(doc['text'],a) for a in profile['assertions']):
            raise ValueError('Las afirmaciones ya no están respaldadas: revisar primero el perfil y sus datos')
        eid='DOC-'+product_id
        evidence=next((e for e in state['evidences'] if e['id']==eid),None)
        if not evidence:
            raise ValueError('Ejecutar mantenimiento inicial antes de aprobar cambios')
        evidence.update(content_text=doc['text'],evidence_hash=actual,status='verificada',
            primary_text=doc.get('primary_text',doc['text']),supporting_documents=doc.get('supporting_documents',{}),
            product_facts={**profile['facts'],'_technical_text':doc.get('technical_text',doc['text'])},
            date_consulted=doc['fetched_at'][:10],date_reviewed=datetime.now(timezone.utc).date().isoformat(),
            reviewer=reviewer+' (aprobación del cambio; afirmaciones comprobadas automáticamente)')
        product['status']='publicado'
        state['relations']=configured_relations(state['products'])
        state.setdefault('observed_documents',{}).pop(product_id,None)
        state['changelog'].append({'version':'pendiente_publicacion','date':datetime.now(timezone.utc).date().isoformat(),
            'author':reviewer,'description':note,'affected_records':[product_id]})
        catalog.validate_state(state)
        published=store.publish(state,previous['metadata']['version'] if previous else None)
        catalog.apply_state(published)
        return {'version':published['metadata']['version'],'product_id':product_id,'text_hash':actual}

GLOBAL_PIPELINE=CompatibilityPipeline()
MaintenancePipeline=CompatibilityPipeline
