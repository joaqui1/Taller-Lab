"""Regression tests for documentary correctness and real state transitions."""
import copy
import csv
import hashlib
import io
import json
import os
import pathlib
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from compatibilidad import catalog
from compatibilidad.models import Evidence
from compatibilidad.rules import evaluate_compatibility
from compatibilidad.search import GLOBAL_SEARCH_INDEX, ProductSearchIndex
from compatibilidad.sources import official_url, proof_valid, OfficialRedirect
from compatibilidad.pipeline import CompatibilityPipeline
from compatibilidad.storage import StateStore, ConcurrentUpdate
from compatibilidad.export import export_compatibility_to_json, export_compatibility_to_csv
from compatibilidad.views import COMPATIBILITY_STATIC_PATHS, render_compatibility_search_results_html

ROOT=pathlib.Path(__file__).resolve().parents[1]
CAPTURE=json.loads((ROOT/'compatibilidad/data/verified_seed.json').read_text(encoding='utf8'))

class CompatibilityRegression(unittest.TestCase):
    def setUp(self):
        test_root=ROOT/'tmp'
        test_root.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=test_root)
        self.store=StateStore(path=pathlib.Path(self.temp.name)/'state.db',database_url='')
        self.environment=patch.dict(os.environ,{'COMPATIBILITY_STATE_PATH':str(self.store.path),
            'COMPATIBILITY_DATABASE_URL':'','DATABASE_URL':'','VERCEL':'','CRON_SECRET':'test-private-secret',
            'COMPATIBILITY_MAINTENANCE_TOKEN':'test-private-secret'})
        self.environment.start()
        catalog.apply_state(catalog.baseline_state())
        self.documents={e['official_url']:{'url':e['official_url'],'http_status':200,
            'text':e.get('primary_text') or e['content_text'],'hash':e['evidence_hash'],
            'fetched_at':datetime.now(timezone.utc).isoformat()} for e in CAPTURE['evidences']}
        for evidence in CAPTURE['evidences']:
            self.documents.update(copy.deepcopy(evidence.get('supporting_documents',{})))
        self.pipeline=CompatibilityPipeline(self.store,lambda url:copy.deepcopy(self.documents[url]))

    def tearDown(self):
        self.environment.stop()
        assert pathlib.Path(self.temp.name).resolve().is_relative_to((ROOT/'tmp').resolve())
        self.temp.cleanup()
        catalog.apply_state(catalog.baseline_state())

    def pair(self,a='1600A016GB',b='06019J40E0'):
        return GLOBAL_SEARCH_INDEX.check_pair(a,b)[2]

    def test_real_documented_example(self):
        ev=self.pair()
        self.assertTrue(ev.is_compatible)
        self.assertEqual(ev.verdict,'Compatible documentado')
        self.assertFalse(ev.conditions)
        self.assertGreaterEqual(len(ev.evidence_chain),2)
        self.assertTrue(all(proof_valid(e) for e in ev.evidence_chain))

    def test_generic_query_requires_selection(self):
        for query in ('Bosch','bosch procore','bateria bosch 18v','DeWalt'):
            a,b,ev=GLOBAL_SEARCH_INDEX.check_pair(query,'06019J40E0')
            self.assertIsNone(a)
            self.assertTrue(ev.is_ambiguous)
            self.assertFalse(ev.is_compatible)
            html=render_compatibility_search_results_html(model_a=query,model_b='06019J40E0')
            self.assertIn('Elegí el modelo exacto',html)
            self.assertIn('b=06019J40E0',html)

    def test_duplicate_mpn_is_not_overwritten(self):
        product=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        index=ProductSearchIndex([product,replace(product,id='variant',slug='variant')])
        resolved,ambiguous,options=index.resolve_product(product.mpn)
        self.assertIsNone(resolved)
        self.assertTrue(ambiguous)
        self.assertEqual(len(options),2)
        self.assertEqual(ProductSearchIndex([]).search('Bosch'),[])

    def test_gamma_charger_identity_and_unreviewed_tool(self):
        self.assertEqual(GLOBAL_SEARCH_INDEX.find_one('G12492AR').product_type,'cargador')
        self.assertFalse(self.pair('G12491AR','G12200AR').is_compatible)
        self.assertFalse(self.pair('G12492AR','G12201AR').is_compatible)
        self.assertTrue(self.pair('G12493AR','G12490AR').is_compatible)

    def test_unreviewed_records_are_not_published_facts(self):
        for product in catalog.CATALOG_PRODUCTS:
            if product.status!='publicado':
                self.assertIsNone(product.capacity_ah)
                self.assertFalse(product.specs)
                self.assertIsNone(product.gtin_ean)
            else:
                self.assertTrue(product.evidence_identity_id)
                self.assertTrue(product.evidence_platform_id)

    def test_missing_evidence_and_cross_brand_abstain(self):
        battery=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        tool=catalog.PRODUCTS_BY_ID['TOOL-BOSCH-GWS-18V-10']
        self.assertFalse(evaluate_compatibility(replace(battery,evidence_identity_id=None),tool).is_compatible)
        self.assertFalse(self.pair('G12491AR','06019J40E0').is_compatible)
        self.assertNotIn('EVI-INTERBRAND-POLICY',catalog.EVIDENCES_BY_ID)

    def test_withdrawn_evidence_blocks_result(self):
        eid=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].evidence_identity_id
        saved=catalog.EVIDENCES_BY_ID.pop(eid)
        try:
            self.assertFalse(self.pair().is_compatible)
        finally:
            catalog.EVIDENCES_BY_ID[eid]=saved

    def test_conflict_blocks_result(self):
        battery=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        tool=catalog.PRODUCTS_BY_ID['TOOL-BOSCH-GWS-18V-10']
        ev=evaluate_compatibility(replace(battery,status='conflicto'),tool)
        self.assertEqual(ev.verdict,'Conflicto en revisión')

    def test_stale_proof_blocks_without_crashing_import_or_restore(self):
        e=next(iter(catalog.EVIDENCES_BY_ID.values()))
        old=replace(e,date_reviewed=(datetime.now(timezone.utc)-timedelta(days=31)).date().isoformat())
        self.assertFalse(proof_valid(old))
        self.assertTrue(proof_valid(old,check_age=False))

    def test_spoofed_domains_and_redirects(self):
        for url in ('https://bosch-professional.com.attacker.example/x','https://bosch-professional.com@attacker.example/x',
                    'http://www.bosch-professional.com/x','https://www.bosch-professional.com:8080/x'):
            self.assertFalse(official_url(url))
        self.assertTrue(official_url('https://www.bosch-professional.com/x'))
        with self.assertRaises(ValueError):
            OfficialRedirect().redirect_request(None,None,302,'',{},'https://attacker.example/')

    def test_fake_candidate_is_rejected(self):
        valid,errors=self.pipeline.validate_candidate({'id':'fake','mpn':'XX','official_url':'https://bosch-professional.com.attacker.example/',
            'date_reviewed':'not-a-date','product_type':'inventado','platform_id':'inventado','excerpt':'texto','review_method':'inventado'})
        self.assertFalse(valid)
        self.assertGreater(len(errors),4)

    def test_publication_is_persisted_and_updates_index(self):
        report=self.pipeline.execute_maintenance()
        self.assertEqual(report['status'],'OK')
        fresh=StateStore(path=self.store.path,database_url='').current()
        self.assertEqual(fresh['metadata']['version'],report['version'])
        self.assertEqual(catalog.CURRENT_METADATA['version'],report['version'])
        self.assertTrue(self.pair().is_compatible)
        self.assertTrue(any(p['id']=='BAT-BOSCH-PROCORE-4AH' and p['status']=='publicado' for p in fresh['products']))

    def test_source_change_suspends_and_rollback_restores_answers(self):
        first=self.pipeline.execute_maintenance()['version']
        url=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].official_url
        self.documents[url]['text']=self.documents[url]['text'].replace('Número de pedido','Cambio técnico: condición pendiente. Número de pedido',1)
        second=self.pipeline.execute_maintenance()
        self.assertEqual(second['status'],'REVISION_REQUERIDA')
        self.assertFalse(self.pair().is_compatible)
        self.assertNotEqual(second['version'],first)
        self.assertTrue(self.pipeline.rollback_to_snapshot(first))
        self.assertEqual(catalog.CURRENT_METADATA['version'],first)
        self.assertTrue(self.pair().is_compatible)
        self.assertEqual(self.store.current()['metadata']['version'],first)
        self.assertEqual(json.loads(export_compatibility_to_json())['metadata']['version'],first)

    def test_removed_fact_suspends_gamma(self):
        self.pipeline.execute_maintenance()
        url=catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12491AR'].official_url
        self.documents[url]['text']=self.documents[url]['text'].replace('4000','3000')
        report=self.pipeline.execute_maintenance()
        self.assertEqual(report['status'],'REVISION_REQUERIDA')
        self.assertFalse(self.pair('G12493AR','G12491AR').is_compatible)

    def test_source_approval_requires_exact_hash_and_is_auditable(self):
        self.pipeline.execute_maintenance()
        pid='BAT-BOSCH-PROCORE-4AH'
        url=catalog.PRODUCTS_BY_ID[pid].official_url
        self.documents[url]['text']=self.documents[url]['text'].replace('Número de pedido','Cambio técnico revisado. Número de pedido',1)
        self.pipeline.execute_maintenance()
        self.assertFalse(self.pair().is_compatible)
        with self.assertRaises(ValueError):
            self.pipeline.approve_source_change(pid,'incorrect','Revisor de prueba','Revisión del cambio editorial en fixture')
        text_hash=hashlib.sha256(self.documents[url]['text'].encode('utf8')).hexdigest()
        result=self.pipeline.approve_source_change(pid,text_hash,'Revisor de prueba','Revisión del cambio editorial en fixture')
        self.assertTrue(self.pair().is_compatible)
        self.assertEqual(self.store.current()['changelog'][-1]['author'],'Revisor de prueba')
        self.assertEqual(self.store.current()['metadata']['version'],result['version'])

    def test_inaccessible_source_is_not_http_200_or_success(self):
        url=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].official_url
        self.documents.pop(url)
        report=self.pipeline.execute_maintenance()
        row=next(s for s in report['sources'] if s['source_id']=='BAT-BOSCH-PROCORE-4AH')
        self.assertIsNone(row['http_status'])
        self.assertEqual(row['status'],'inaccesible')
        self.assertEqual(report['status'],'REVISION_REQUERIDA')
        self.assertFalse(self.pair().is_compatible)

    def test_dry_run_has_no_storage_or_active_state_mutations(self):
        version=catalog.CURRENT_METADATA['version']
        report=self.pipeline.execute_maintenance(dry_run=True)
        self.assertEqual(report['status'],'OK')
        self.assertFalse(self.store.path.exists())
        self.assertEqual(catalog.CURRENT_METADATA['version'],version)

    def test_offline_is_explicit_and_does_not_fetch(self):
        self.pipeline.fetcher=lambda url:self.fail('offline fetched a source')
        result=self.pipeline.execute_maintenance(check_online=False)
        self.assertEqual(result['status'],'NO_EJECUTADO_OFFLINE')
        self.assertFalse(self.store.path.exists())
        self.assertTrue(all(s['http_status'] is None for s in result['sources']))

    def test_concurrent_publication_does_not_overwrite(self):
        first=self.pipeline.execute_maintenance()['version']
        state=self.store.current()
        self.store.publish(state,first)
        with self.assertRaises(ConcurrentUpdate):
            self.store.publish(state,first)

    def test_export_relations_reproduce_verdict_and_keep_documents_private(self):
        dataset=json.loads(export_compatibility_to_json())
        self.assertEqual(len(dataset['relations']),40)
        self.assertTrue(all('content_text' not in e for e in dataset['evidences']))
        self.assertTrue(all('primary_text' not in e and 'supporting_documents' not in e and '_technical_text' not in e['product_facts'] for e in dataset['evidences']))
        for r in dataset['relations']:
            ev=self.pair(r['source_product_id'],r['target_product_id'])
            self.assertEqual(r['verdict'],ev.verdict)
            self.assertTrue(r['evidence_ids'])
        rows=list(csv.DictReader(io.StringIO(export_compatibility_to_csv())))
        self.assertEqual(len(rows),len(dataset['relations']))
        self.assertTrue(all(row['source_urls'].startswith('https://') for row in rows))

    def test_web_routes_pending_noindex_and_readonly_analytics(self):
        from app import app
        client=app.test_client()
        import compatibilidad.telemetry as telemetry
        with patch.object(telemetry.sqlite3,'connect',side_effect=sqlite3.OperationalError('read only')):
            for path in COMPATIBILITY_STATIC_PATHS:
                self.assertEqual(client.get(path).status_code,200,path)
            pending=catalog.PRODUCTS_BY_ID['BAT-DEWALT-DCB203']
            response=client.get('/baterias/'+pending.slug+'/')
            self.assertIn('noindex',response.headers.get('X-Robots-Tag',''))
            self.assertNotIn('"@type": "Product"',response.get_data(as_text=True))

    def test_auth_and_boolean_types_and_cron(self):
        from app import app
        client=app.test_client()
        endpoint='/api/compatibilidad/ejecutar'
        self.assertEqual(client.post(endpoint,headers={'Authorization':'Bearer tallerlab-compat-2026'},json={'dry_run':True}).status_code,401)
        headers={'Authorization':'Bearer test-private-secret'}
        self.assertEqual(client.post(endpoint,headers=headers,json={'dry_run':'false'}).status_code,400)
        with patch('app.MaintenancePipeline',return_value=self.pipeline):
            response=client.post(endpoint,headers=headers,json={'dry_run':True})
            self.assertTrue(response.json['dry_run'])
            self.assertFalse(self.store.path.exists())
            self.assertEqual(client.get(endpoint+'?dry_run=false',headers=headers).status_code,400)
            cron=client.get(endpoint,headers=headers)
            self.assertEqual(cron.status_code,200)
            self.assertFalse(cron.json['dry_run'])
        config=json.loads((ROOT/'vercel.json').read_text())
        self.assertTrue(any(c['path']==endpoint for c in config['crons']))

    def test_serverless_requires_durable_storage(self):
        with patch.dict(os.environ,{'VERCEL':'1','DATABASE_URL':'','COMPATIBILITY_DATABASE_URL':''}):
            with self.assertRaises(RuntimeError):
                StateStore()

    def test_selecting_b_never_overwrites_unknown_a(self):
        from bs4 import BeautifulSoup
        from urllib.parse import urlparse,parse_qs
        html=render_compatibility_search_results_html(model_a='not-a-model',model_b='Bosch')
        links=BeautifulSoup(html,'html.parser').select('.compat-ambiguity a')
        self.assertTrue(links)
        for link in links:
            params=parse_qs(urlparse(link['href']).query)
            self.assertEqual(params['a'],['not-a-model'])
            self.assertNotEqual(params['b'],['Bosch'])

    def test_both_ambiguous_sides_keep_independent_options(self):
        ev=GLOBAL_SEARCH_INDEX.check_pair('Bosch','Gamma')[2]
        self.assertTrue(ev.candidates_by_side['a'])
        self.assertTrue(ev.candidates_by_side['b'])
        html=render_compatibility_search_results_html(model_a='Bosch',model_b='Gamma')
        self.assertIn('Modelo A',html)
        self.assertIn('Modelo B',html)

    def test_warm_worker_expiry_updates_dataset_schema_and_sitemap(self):
        from compatibilidad import sources
        from app import app
        class FutureDate(datetime):
            @classmethod
            def now(cls,tz=None):return datetime.now(tz)+timedelta(days=32)
        with patch.object(sources,'datetime',FutureDate):
            dataset=json.loads(export_compatibility_to_json())
            self.assertEqual(dataset['metadata']['verified_products'],0)
            self.assertFalse(dataset['relations'])
            self.assertEqual(catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].status,'pendiente')
            path='/baterias/'+catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].slug+'/'
            response=app.test_client().get(path)
            self.assertIn('noindex',response.headers['X-Robots-Tag'])
            self.assertNotIn('"@type": "Product"',response.get_data(as_text=True))
            self.assertNotIn(path,app.test_client().get('/sitemap.xml').get_data(as_text=True))

    def test_specification_mutation_is_rejected(self):
        state=copy.deepcopy(catalog.baseline_state())
        next(p for p in state['products'] if p['id']=='BAT-BOSCH-PROCORE-4AH')['capacity_ah']=99
        with self.assertRaises(ValueError):catalog.validate_state(state)

    def test_peripheral_change_does_not_suspend_technical_proof(self):
        url=catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12490AR'].official_url
        self.documents[url]['text']+=' Nueva recomendación en el pie del sitio.'
        report=self.pipeline.execute_maintenance()
        self.assertEqual(report['status'],'OK')
        self.assertTrue(self.pair('G12493AR','G12490AR').is_compatible)

    def test_failed_cron_and_missing_storage_are_not_http_success(self):
        from app import app
        url=catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12490AR'].official_url
        self.documents.pop(url)
        with patch('app.MaintenancePipeline',return_value=self.pipeline):
            response=app.test_client().get('/api/compatibilidad/ejecutar',headers={'Authorization':'Bearer test-private-secret'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json['status'],'REVISION_REQUERIDA')
        health=app.test_client().get('/api/compatibilidad/estado')
        self.assertEqual(health.status_code,503)

    def test_complete_systems_and_regional_codes_are_separate(self):
        for charger,battery,tool in [('1600A028U0','1600A016GB','06019J40E0'),('G12493AR','G12491AR','G12402/1AR')]:
            self.assertTrue(self.pair(charger,battery).is_compatible)
            self.assertTrue(self.pair(battery,tool).is_compatible)
        self.assertFalse(self.pair('1600A019RJ','1600A016GB').is_compatible)

    def test_citable_pages_print_and_accessibility(self):
        from app import app
        from bs4 import BeautifulSoup
        from compatibilidad.presentation import relationship_paths
        client=app.test_client()
        for path in relationship_paths():
            response=client.get(path)
            self.assertEqual(response.status_code,200,path)
            html=response.get_data(as_text=True)
            self.assertIn('Compatible documentado',html)
            self.assertIn('Fuente y comprobación documental',html)
        hub=BeautifulSoup(client.get('/compatibilidad/').get_data(as_text=True),'html.parser')
        self.assertTrue(all(i.get('aria-label') for i in hub.select('input')))
        self.assertIn('18 modelos verificados',hub.get_text())
        matrix=client.get('/compatibilidad/matriz-imprimible/').get_data(as_text=True)
        self.assertIn(catalog.CURRENT_METADATA['version'],matrix)
        self.assertIn('G12402/1AR',matrix)
        self.assertNotIn('Versión 1.0.0',matrix)

    def test_pair_does_not_display_unrelated_empty_search(self):
        from bs4 import BeautifulSoup
        html=render_compatibility_search_results_html(model_a='G12493AR',model_b='G12490AR')
        soup=BeautifulSoup(html,'html.parser')
        message=soup.find(string=lambda s:s and 'No se encontraron modelos' in s)
        self.assertTrue(message is None or message.find_parent('section').has_attr('hidden'))

    def test_verified_directory_and_exact_model_suggestions(self):
        from bs4 import BeautifulSoup
        from compatibilidad.views import render_compatibility_hub_html
        soup=BeautifulSoup(render_compatibility_hub_html(),'html.parser')
        self.assertEqual(len(soup.select('#compat-models option')),18)
        self.assertEqual(len(soup.select('.compat-directory-grid li')),18)
        self.assertNotIn('Cinco sistemas',soup.get_text())
        self.assertIn('2 sistemas con modelos verificados',soup.get_text())
        self.assertTrue(all(i.get('list')=='compat-models' for i in soup.select('input[type="text"]')))

    def test_pair_page_conditions_and_unconfirmed_scope(self):
        from compatibilidad.presentation import relationship_page,relation_path
        source=catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        target=catalog.PRODUCTS_BY_ID['TOOL-BOSCH-GWS-18V-10']
        relation=next(r for r in catalog.RELATIONS if r['source_product_id']==source.id and r['target_product_id']==target.id)
        relation['conditions']=['Condición documental de prueba']
        relation['verdict']='Compatible bajo condiciones'
        html=relationship_page(relation_path(source,target))
        self.assertIn('Sí, bajo las condiciones indicadas',html)
        self.assertIn('Condición documental de prueba',html)
        self.assertIn('Otras combinaciones documentadas',html)
        unknown=relationship_page(relation_path(source,catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12490AR']))
        self.assertIn('no tiene una confirmación documental vigente',unknown)
        self.assertNotIn('La cadena comprueba',unknown)

    def test_csv_includes_supporting_manual_in_evidence_chain(self):
        self.assertIn('o323426v21_160992A51Y_201909.pdf',export_compatibility_to_csv())

    def test_related_kit_cta_is_contextual_and_disclosed(self):
        from bs4 import BeautifulSoup
        from compatibilidad.commercial import render_pair_commercial
        battery=catalog.PRODUCTS_BY_ID['BAT-BOSCH-GBA-4AH']
        tool=catalog.PRODUCTS_BY_ID['TOOL-BOSCH-GWS-18V-10']
        soup=BeautifulSoup(render_pair_commercial(battery,tool),'html.parser')
        link=soup.select_one('.compat-buy-cta')
        self.assertEqual(link['href'],'https://meli.la/1aD8WYE')
        self.assertTrue({'sponsored','nofollow','noopener','noreferrer'} <= set(link['rel']))
        self.assertIn('precio y contenido',link.get_text())
        self.assertNotIn('comisión',soup.get_text())
        self.assertIn('kit distinto',soup.get_text())
        self.assertEqual(render_pair_commercial(battery,catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12490AR']),'')

    def test_commercial_cta_not_shown_for_other_platform_or_pending_model(self):
        from compatibilidad.commercial import render_product_commercial,render_related_kit
        self.assertEqual(render_product_commercial(catalog.PRODUCTS_BY_ID['BAT-GAMMA-G12490AR']),'')
        self.assertEqual(render_related_kit(platform_id='gamma-multienergy'),'')
        pending=next(p for p in catalog.CATALOG_PRODUCTS if p.status!='publicado')
        self.assertEqual(render_product_commercial(pending),'')

    def test_exact_offer_rejects_wrong_sku_and_stale_review(self):
        from compatibilidad.commercial import EXACT_OFFERS,exact_offer
        product=catalog.PRODUCTS_BY_ID['BAT-BOSCH-GBA-4AH']
        offer={'brand':product.brand,'mpn':product.mpn,'url':'https://meli.la/test-fixture',
               'reviewed_at':datetime.now(timezone.utc).isoformat(),'identity_confirmed':True}
        with patch.dict(EXACT_OFFERS,{product.id:offer}):
            self.assertIsNotNone(exact_offer(product))
            offer['mpn']='other-sku'
            self.assertIsNone(exact_offer(product))
            offer['mpn']=product.mpn
            offer['reviewed_at']=(datetime.now(timezone.utc)-timedelta(days=31)).isoformat()
            self.assertIsNone(exact_offer(product))

if __name__=='__main__':
    unittest.main()
