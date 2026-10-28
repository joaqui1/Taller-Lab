import copy
import json
import re
import unittest
from contextlib import contextmanager
from xml.etree import ElementTree
from urllib.parse import urlparse
from unittest.mock import patch

from compatibilidad import catalog
from compatibilidad.content_dates import product_content_signature
from compatibilidad.editorial import EDITORIAL_FICHAS, validate_fichas_editorial
from compatibilidad.presentation import compatibility_lastmod, product_path
from compatibilidad.storage import StateStore, clear_migration_cache
from compatibilidad.views import get_product_schema_json


def _schema_date_modified(markup):
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', markup)
    return json.loads(match.group(1)).get('dateModified')


def _sitemap_lastmod(markup, path):
    root = ElementTree.fromstring(markup)
    for entry in root.findall('.//{*}url'):
        location = entry.find('{*}loc')
        if location is not None and urlparse(location.text or '').path == path:
            modified = entry.find('{*}lastmod')
            return modified.text if modified is not None else None
    return None


class _Cursor:
    def __init__(self, row=None, rows=None):
        self.row = row
        self.rows = rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class _ThirtyVersionConnection:
    def __init__(self, active_payload):
        self.active_payload = active_payload
        self.versions = [f'version-{index}' for index in range(30)]
        self.queries = []

    def execute(self, query, params=()):
        self.queries.append(query)
        if 'sqlite_master' in query:
            return _Cursor(('compatibility_current',))
        if 'JOIN compatibility_current' in query:
            return _Cursor(('active-version', json.dumps(self.active_payload)))
        if 'json_each' in query:
            return _Cursor(rows=[])
        if 'ORDER BY created_at,version' in query:
            return _Cursor(rows=[(json.dumps({}), '2026-10-01') for _ in self.versions])
        raise AssertionError(f'Consulta inesperada: {query}')


class CompatibilityDatesC2Tests(unittest.TestCase):
    def setUp(self):
        clear_migration_cache()
        self.addCleanup(clear_migration_cache)

    def test_active_payload_with_dates_does_not_scan_thirty_historical_versions(self):
        payload = {
            'products': [{'id': 'BAT-BOSCH-PROCORE-4AH', 'status': 'publicado', 'content_changed_at': '2026-10-04'}],
            'relations': [{'id': 'pair-1', 'content_changed_at': '2026-10-04'}],
            'evidences': [],
        }
        store = StateStore(path='unused.sqlite3', database_url='')
        conn = _ThirtyVersionConnection(payload)

        @contextmanager
        def connection(write=False):
            yield conn, '?'

        with patch.object(store, 'connection', side_effect=connection):
            state = store.current()

        self.assertEqual(state['products'][0]['content_changed_at'], '2026-10-04')
        version_queries = [query for query in conn.queries if 'FROM compatibility_versions' in query]
        self.assertEqual(len(version_queries), 1)
        self.assertIn('JOIN compatibility_current', version_queries[0])
        self.assertNotIn('ORDER BY created_at,version', '\n'.join(conn.queries))

    def test_legacy_migration_is_cached_for_the_active_version(self):
        payload = {
            'metadata': {'published_at': '2026-10-04'},
            'products': [{'id': 'BAT-BOSCH-PROCORE-4AH', 'status': 'publicado'}],
            'relations': [],
            'evidences': [],
        }
        store = StateStore(path='unused.sqlite3', database_url='')
        conn = _ThirtyVersionConnection(payload)

        @contextmanager
        def connection(write=False):
            yield conn, '?'

        with patch.object(store, 'connection', side_effect=connection):
            first = store.current()
            second = store.current()

        self.assertEqual(first['products'][0]['content_changed_at'], '2026-10-04')
        self.assertEqual(second['products'][0]['content_changed_at'], '2026-10-04')
        history_queries = [query for query in conn.queries if 'json_each' in query]
        self.assertEqual(len(history_queries), 1)

    def test_published_editorial_date_moves_only_its_product_sitemap_and_schema(self):
        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        other = catalog.PRODUCTS_BY_ID['TOOL-BOSCH-GWS-18V-10']
        path = product_path(product)
        other_path = product_path(other)
        before = compatibility_lastmod()
        approved_ficha = copy.deepcopy(EDITORIAL_FICHAS[product.id])
        approved_ficha.update(publicado=True, last_approved_modified_at='2026-10-26')

        with patch.dict(EDITORIAL_FICHAS, {product.id: approved_ficha}):
            after = compatibility_lastmod()
            from servidor_local import render_sitemap
            sitemap_first = render_sitemap()
            sitemap_second = render_sitemap()
            schema = get_product_schema_json(product, 'https://www.tallerlab.com.ar')

        self.assertEqual(after[path], '2026-10-26')
        self.assertEqual(after[other_path], before[other_path])
        self.assertEqual(_sitemap_lastmod(sitemap_first, path), '2026-10-26')
        self.assertEqual(_sitemap_lastmod(sitemap_second, path), '2026-10-26')
        self.assertEqual(_schema_date_modified(schema), '2026-10-26')

    def test_seed_integer_capacity_has_same_signature_as_stored_float(self):
        import pathlib

        seed_path = pathlib.Path(__file__).parents[1] / 'compatibilidad' / 'data' / 'verified_seed.json'
        seed = json.loads(seed_path.read_text(encoding='utf-8'))
        seed_product = next(item for item in seed['products'] if item['id'] == 'BAT-BOSCH-PROCORE-4AH')
        stored_product = copy.deepcopy(seed_product)
        stored_product['capacity_ah'] = 4.0
        evidences = {item['id']: item for item in seed.get('evidences', [])}
        self.assertEqual(seed_product['capacity_ah'], 4)
        self.assertEqual(product_content_signature(seed_product, evidences),
                         product_content_signature(stored_product, evidences))

    def test_published_editorial_signature_includes_approval_date(self):
        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH'].to_dict()
        evidence = catalog.EVIDENCES_BY_ID[product['evidence_identity_id']].to_dict()
        evidences = {evidence['id']: evidence}
        ficha = copy.deepcopy(EDITORIAL_FICHAS[product['id']])
        ficha.update(publicado=True, last_approved_modified_at='2026-10-26')
        with patch.dict(EDITORIAL_FICHAS, {product['id']: ficha}):
            first = product_content_signature(product, evidences)
            ficha['last_approved_modified_at'] = '2026-10-27'
            second = product_content_signature(product, evidences)
        self.assertNotEqual(first, second)

    def test_ficha_approval_date_validation_requires_iso_date_when_published(self):
        product_id = 'BAT-BOSCH-PROCORE-4AH'
        draft = {'publicado': False, 'last_approved_modified_at': None}
        self.assertEqual(validate_fichas_editorial({product_id: draft}, product_ids={product_id}), [])
        published = {'publicado': True, 'last_approved_modified_at': '26/10/2026'}
        errors = validate_fichas_editorial({product_id: published}, product_ids={product_id})
        self.assertTrue(any('last_approved_modified_at' in error for error in errors))

    def test_public_compatibility_page_has_no_outdated_automatic_review_phrasing(self):
        from compatibilidad.views import render_tool_detail

        product = catalog.PRODUCTS_BY_ID['BAT-BOSCH-PROCORE-4AH']
        html = render_tool_detail(product)
        self.assertNotIn('Fecha más antigua de la cadena', html)
        self.assertNotIn('comprobación automática de afirmaciones configuradas', html)


if __name__ == '__main__':
    unittest.main()
