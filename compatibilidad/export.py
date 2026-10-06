"""Public documentary ledger. Captured manufacturer documents stay private."""
import csv
import io
import json
from datetime import datetime, timezone
from compatibilidad.catalog import CATALOG_PRODUCTS, EVIDENCES, PLATFORMS, RELATIONS, CURRENT_METADATA, CHANGELOG, refresh_published_state
from compatibilidad.catalog import catalog_read_locked
from compatibilidad.models import CompatibilityRelation
from compatibilidad.rules import evaluate_compatibility

def sanitize_csv_cell(value):
    text='' if value is None else str(value).strip()
    return "'"+text if text and text[0] in '=+-@' else text

def generate_evaluated_relations():
    by_id={p.id:p for p in CATALOG_PRODUCTS}
    relations=[]
    for rel in RELATIONS:
        ev=evaluate_compatibility(by_id[rel['source_product_id']],by_id[rel['target_product_id']])
        if not ev.is_compatible and ev.verdict!='Incompatible documentado':
            continue
        relations.append(CompatibilityRelation(**{**rel,'evidence_ids':[e.id for e in ev.evidence_chain]}))
    return relations

@catalog_read_locked
def export_compatibility_to_json():
    refresh_published_state()
    evidences=[]
    for e in EVIDENCES:
        record=e.to_dict()
        record.pop('content_text')
        record.pop('primary_text',None)
        record.pop('supporting_documents',None)
        record['product_facts'].pop('_technical_text',None)
        evidences.append(record)
    return json.dumps({'metadata':{**CURRENT_METADATA,'title':'Base argentina de compatibilidad',
        'verified_products':sum(p.status=='publicado' for p in CATALOG_PRODUCTS),
        'pending_products':sum(p.status!='publicado' for p in CATALOG_PRODUCTS),
        'generated_at':datetime.now(timezone.utc).isoformat(),
        'license':'CC BY 4.0 para la recopilación y estructura propias; documentos del fabricante conservan sus derechos',
        'license_url':'https://creativecommons.org/licenses/by/4.0/',
        'scope':'Solo las relaciones enumeradas están documentadas. Los registros pendientes no acreditan identidad ni disponibilidad.'},
        'products':[p.to_dict() for p in CATALOG_PRODUCTS], 'platforms':[p.to_dict() for p in PLATFORMS],
        'evidences':evidences,'relations':[r.to_dict() for r in generate_evaluated_relations()],
        'changelog':[c.to_dict() for c in CHANGELOG]},ensure_ascii=False,indent=2)

@catalog_read_locked
def export_compatibility_to_csv():
    refresh_published_state()
    output=io.StringIO(); writer=csv.writer(output,lineterminator='\n')
    writer.writerow(['version','source_product_id','source_mpn','target_product_id','target_mpn',
        'verdict','conditions','required_packs','evidence_ids','source_urls','date_reviewed'])
    by_id={p.id:p for p in CATALOG_PRODUCTS}; by_evi={e.id:e for e in EVIDENCES}
    for relation in generate_evaluated_relations():
        writer.writerow([sanitize_csv_cell(x) for x in [CURRENT_METADATA['version'],relation.source_product_id,
            by_id[relation.source_product_id].mpn,relation.target_product_id,by_id[relation.target_product_id].mpn,
            relation.verdict,' | '.join(relation.conditions),relation.required_packs_count,
            ' | '.join(relation.evidence_ids),' | '.join(dict.fromkeys(url for eid in relation.evidence_ids for url in [by_evi[eid].official_url]+by_evi[eid].supporting_urls)),relation.date_reviewed]])
    return output.getvalue()
