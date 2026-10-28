"""Regression checks for content-change dates and legacy snapshot migration."""
import copy
import hashlib
import json
import os
import pathlib
import re
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from html import unescape
from unittest.mock import patch
from xml.etree import ElementTree

from compatibilidad import catalog
from compatibilidad.content_dates import stamp_content_changed_at
from compatibilidad.pipeline import CompatibilityPipeline
from compatibilidad.presentation import compatibility_lastmod, relation_path, relation_schema
from compatibilidad.rules import evaluate_compatibility
from compatibilidad.storage import StateStore, clear_migration_cache
from compatibilidad.views import get_product_schema_json

ROOT = pathlib.Path(__file__).resolve().parents[1]
CAPTURE = json.loads((ROOT / 'compatibilidad/data/verified_seed.json').read_text(encoding='utf-8'))
SITEMAP_NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


def _schema_json(markup):
    start = markup.index('>') + 1
    end = markup.rindex('</script>')
    return json.loads(markup[start:end])


def _plain_text(markup):
    return unescape(re.sub(r'<[^>]*>', '', markup))


def _sitemap_lastmod(sitemap, path):
    root = ElementTree.fromstring(sitemap)
    for entry in root.findall(f'{SITEMAP_NS}url'):
        location = entry.find(f'{SITEMAP_NS}loc')
        if location is not None and location.text and location.text.rstrip('/').endswith(path.rstrip('/')):
            lastmod = entry.find(f'{SITEMAP_NS}lastmod')
            return lastmod.text if lastmod is not None else None
    return None


class CompatibilityContentDates(unittest.TestCase):
    def setUp(self):
        clear_migration_cache()
        self.addCleanup(clear_migration_cache)
        temp_root = ROOT / 'tmp'
        temp_root.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=temp_root)
        self.store = StateStore(path=pathlib.Path(self.temp.name) / 'state.db', database_url='')
        self.environment = patch.dict(os.environ, {
            'COMPATIBILITY_STATE_PATH': str(self.store.path), 'COMPATIBILITY_DATABASE_URL': '',
            'DATABASE_URL': '', 'VERCEL': '', 'CRON_SECRET': 'test-private-secret',
            'COMPATIBILITY_MAINTENANCE_TOKEN': 'test-private-secret',
        })
        self.environment.start()
        catalog.apply_state(catalog.baseline_state())
        self.documents = {
            evidence['official_url']: {
                'url': evidence['official_url'], 'http_status': 200,
                'text': evidence.get('primary_text') or evidence['content_text'],
                'hash': evidence['evidence_hash'],
                'fetched_at': datetime.now(timezone.utc).isoformat(),
            }
            for evidence in CAPTURE['evidences']
        }
        for evidence in CAPTURE['evidences']:
            self.documents.update(copy.deepcopy(evidence.get('supporting_documents', {})))
        self.pipeline = CompatibilityPipeline(self.store, lambda url: copy.deepcopy(self.documents[url]))

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()
        catalog.apply_state(catalog.baseline_state())

    def test_legacy_sqlite_versions_gain_first_publication_dates_without_rewrites(self):
        legacy_path = pathlib.Path(self.temp.name) / 'legacy.db'
        first = {
            'metadata': {'version': 'legacy-1', 'engine_version': '2', 'published_at': '2026-08-11T12:00:00+00:00'},
            'products': [{'id': 'P-1', 'status': 'publicado'}, {'id': 'P-2', 'status': 'pendiente'}],
            'relations': [{'id': 'R-1'}], 'evidences': [], 'changelog': [],
        }
        second = copy.deepcopy(first)
        second['metadata'].update(version='legacy-2', published_at='2026-08-19T12:00:00+00:00')
        conn = sqlite3.connect(legacy_path)
        try:
            conn.execute('CREATE TABLE compatibility_versions (version TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
            conn.execute('CREATE TABLE compatibility_current (id INTEGER PRIMARY KEY, version TEXT NOT NULL)')
            conn.execute('INSERT INTO compatibility_versions VALUES (?,?,?)', ('legacy-1', json.dumps(first), first['metadata']['published_at']))
            conn.execute('INSERT INTO compatibility_versions VALUES (?,?,?)', ('legacy-2', json.dumps(second), second['metadata']['published_at']))
            conn.execute('INSERT INTO compatibility_current VALUES (1,?)', ('legacy-2',))
            conn.commit()
        finally:
            conn.close()

        store = StateStore(path=legacy_path, database_url='')
        current = store.current()
        self.assertEqual(current['products'][0]['content_changed_at'], '2026-08-11')
        self.assertEqual(current['products'][1]['content_changed_at'], '2026-10-04')
        self.assertEqual(current['relations'][0]['content_changed_at'], '2026-08-11')
        self.assertEqual(store.get('legacy-1')['relations'][0]['content_changed_at'], '2026-08-11')
        conn = sqlite3.connect(legacy_path)
        try:
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM compatibility_versions').fetchone()[0], 2)
            stored = json.loads(conn.execute('SELECT payload FROM compatibility_versions WHERE version=?', ('legacy-2',)).fetchone()[0])
        finally:
            conn.close()
        self.assertNotIn('content_changed_at', stored['products'][0])

    def test_content_comparison_updates_product_and_relation_dates(self):
        previous = catalog.baseline_state()
        changed = copy.deepcopy(previous)
        product = next(p for p in changed['products'] if p['id'] == 'BAT-BOSCH-PROCORE-4AH')
        relation = next(r for r in changed['relations'] if r['source_product_id'] == product['id'])
        product['capacity_ah'] = 5.0
        relation['verdict'] = 'Compatible bajo condiciones'
        relation['conditions'] = ['Condición de prueba documentada']
        stamp_content_changed_at(changed, previous, '2026-10-26')
        self.assertEqual(product['content_changed_at'], '2026-10-26')
        self.assertEqual(relation['content_changed_at'], '2026-10-26')

    def test_second_check_on_a_later_day_keeps_lastmod_and_product_date_modified(self):
        self.pipeline.execute_maintenance()
        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        path = '/baterias/' + product.slug + '/'
        first_lastmod = compatibility_lastmod()[path]
        first_schema_modified = _schema_json(get_product_schema_json(product, 'https://www.tallerlab.com.ar'))['dateModified']
        relation = next(r for r in catalog.RELATIONS if r['source_product_id'] == product.id)
        source = catalog.PRODUCTS_BY_ID[relation['source_product_id']]
        target = catalog.PRODUCTS_BY_ID[relation['target_product_id']]
        relation_url = relation_path(source, target)
        first_relation_modified = _schema_json(relation_schema(
            source, target, evaluate_compatibility(source, target), relation_url,
            'https://www.tallerlab.com.ar'))['dateModified']
        first_reviewed = catalog.EVIDENCES_BY_ID[product.evidence_identity_id].date_reviewed

        class NextDay(datetime):
            @classmethod
            def now(cls, tz=None):
                return datetime.now(tz) + timedelta(days=1)

        with patch('compatibilidad.pipeline.datetime', NextDay), patch('compatibilidad.sources.datetime', NextDay):
            self.pipeline.execute_maintenance()
            from servidor_local import render_sitemap
            sitemap = render_sitemap()

        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        self.assertNotEqual(catalog.EVIDENCES_BY_ID[product.evidence_identity_id].date_reviewed, first_reviewed)
        self.assertEqual(product.content_changed_at, first_lastmod)
        self.assertEqual(compatibility_lastmod()[path], first_lastmod)
        self.assertEqual(_schema_json(get_product_schema_json(product, 'https://www.tallerlab.com.ar'))['dateModified'], first_schema_modified)
        relation = next(r for r in catalog.RELATIONS if r['source_product_id'] == product.id)
        source = catalog.PRODUCTS_BY_ID[relation['source_product_id']]
        target = catalog.PRODUCTS_BY_ID[relation['target_product_id']]
        self.assertEqual(_schema_json(relation_schema(
            source, target, evaluate_compatibility(source, target), relation_url,
            'https://www.tallerlab.com.ar'))['dateModified'], first_relation_modified)
        self.assertEqual(_sitemap_lastmod(sitemap, path), first_lastmod)

    def test_approval_copy_uses_only_explicit_source_approval(self):
        from compatibilidad.presentation import source_check_text

        self.pipeline.execute_maintenance()
        product_id = 'BAT-BOSCH-PROCORE-4AH'
        product = catalog.PRODUCTS_BY_ID[product_id]
        evidence = catalog.EVIDENCES_BY_ID[product.evidence_identity_id]
        automatic_text = source_check_text(evidence)
        today_es = datetime.now(timezone.utc).strftime('%d/%m/%Y')
        automatic_plain = _plain_text(automatic_text)
        self.assertIn(f'Comprobado automáticamente contra la ficha oficial de Bosch el {today_es}', automatic_plain)
        self.assertNotIn('Cambio de fuente aprobado por', automatic_plain)

        url = product.official_url
        self.documents[url]['text'] = self.documents[url]['text'].replace(
            'Número de pedido', 'Cambio técnico revisado. Número de pedido', 1)
        self.pipeline.execute_maintenance()
        text_hash = hashlib.sha256(self.documents[url]['text'].encode('utf-8')).hexdigest()
        self.pipeline.approve_source_change(product_id, text_hash, 'Revisor de prueba',
            'Se comparó el cambio con las afirmaciones configuradas para el modelo.')
        evidence = catalog.EVIDENCES_BY_ID[product.evidence_identity_id]
        approved_text = _plain_text(source_check_text(evidence))
        self.assertIn(f'Cambio de fuente aprobado por Revisor de prueba el {today_es}', approved_text)

    def test_thirty_day_evidence_expiry_still_uses_date_reviewed(self):
        from dataclasses import replace
        from compatibilidad.sources import proof_valid

        evidence = next(iter(catalog.EVIDENCES_BY_ID.values()))
        stale = replace(evidence, date_reviewed=(datetime.now(timezone.utc) - timedelta(days=31)).date().isoformat())
        self.assertFalse(proof_valid(stale))
        self.assertTrue(proof_valid(stale, check_age=False))

    def test_current_reuses_migrated_payload_across_store_instances(self):
        """Las lecturas públicas crean un StateStore por visita: la migración corre una vez."""
        legacy_path = pathlib.Path(self.temp.name) / 'cache.db'
        payloads = []
        for number in range(1, 31):
            payloads.append({
                'metadata': {'version': f'legacy-{number}', 'engine_version': '2',
                             'published_at': f'2026-09-{number:02d}T12:00:00+00:00' if number <= 30 else ''},
                'products': [{'id': 'P-1', 'status': 'publicado'}],
                'relations': [{'id': 'R-1'}], 'evidences': [], 'changelog': [],
            })
        conn = sqlite3.connect(legacy_path)
        try:
            conn.execute('CREATE TABLE compatibility_versions (version TEXT PRIMARY KEY, payload TEXT NOT NULL, created_at TEXT NOT NULL)')
            conn.execute('CREATE TABLE compatibility_current (id INTEGER PRIMARY KEY, version TEXT NOT NULL)')
            for payload in payloads:
                conn.execute('INSERT INTO compatibility_versions VALUES (?,?,?)',
                             (payload['metadata']['version'], json.dumps(payload), payload['metadata']['published_at']))
            conn.execute('INSERT INTO compatibility_current VALUES (1,?)', ('legacy-30',))
            conn.commit()
        finally:
            conn.close()

        original = StateStore._first_publication_dates_for_store
        with patch.object(StateStore, '_first_publication_dates_for_store', autospec=True,
                          side_effect=original) as history_query:
            first = StateStore(path=legacy_path, database_url='').current()
            second = StateStore(path=legacy_path, database_url='').current()
        self.assertEqual(history_query.call_count, 1)
        self.assertEqual(first, second)
        self.assertEqual(first['products'][0]['content_changed_at'], '2026-09-01')

        dated = copy.deepcopy(payloads[-1])
        dated['metadata']['version'] = 'dated-1'
        dated['products'][0]['content_changed_at'] = '2026-09-01'
        dated['relations'][0]['content_changed_at'] = '2026-09-01'
        conn = sqlite3.connect(legacy_path)
        try:
            conn.execute('INSERT INTO compatibility_versions VALUES (?,?,?)', ('dated-1', json.dumps(dated), '2026-10-01T12:00:00+00:00'))
            conn.execute('UPDATE compatibility_current SET version=? WHERE id=1', ('dated-1',))
            conn.commit()
        finally:
            conn.close()
        with patch.object(StateStore, '_first_publication_dates_for_store', autospec=True,
                          side_effect=original) as history_query:
            StateStore(path=legacy_path, database_url='').current()
        self.assertEqual(history_query.call_count, 0)

    def test_publishing_an_editorial_ficha_moves_only_that_lastmod(self):
        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        other = catalog.PRODUCTS_BY_ID['BAT-BOSCH-GBA-4AH']
        path = '/baterias/' + product.slug + '/'
        other_path = '/baterias/' + other.slug + '/'
        before = compatibility_lastmod()

        def published_ficha(product_id):
            if product_id == product.id:
                return {'publicado': True, 'last_approved_modified_at': '2099-01-15'}
            return None

        with patch('compatibilidad.editorial.get_published_ficha', side_effect=published_ficha):
            after = compatibility_lastmod()
            schema_modified = _schema_json(get_product_schema_json(product, 'https://www.tallerlab.com.ar'))['dateModified']
        self.assertEqual(after[path], '2099-01-15')
        self.assertEqual(schema_modified, '2099-01-15')
        self.assertEqual(after[other_path], before[other_path])


if __name__ == '__main__':
    unittest.main()
