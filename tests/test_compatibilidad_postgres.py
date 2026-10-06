"""Contrato real de versiones en un esquema PostgreSQL desechable de pruebas."""
import os
import unittest
import uuid
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit


@unittest.skipUnless(os.environ.get('TALLERLAB_TEST_DATABASE_URL'), 'Falta PostgreSQL aislado de pruebas')
class CompatibilityPostgresTests(unittest.TestCase):
    def test_publication_conflict_and_rollback_are_persistent(self):
        import psycopg
        from psycopg import sql
        from compatibilidad.catalog import baseline_state
        from compatibilidad.storage import ConcurrentUpdate, StateStore

        url = os.environ['TALLERLAB_TEST_DATABASE_URL']
        parsed = urlsplit(url)
        if 'test' not in parsed.path.lower():
            self.fail('Usar exclusivamente una base identificada como test')
        schema = 'compat_test_' + uuid.uuid4().hex
        with psycopg.connect(url, autocommit=True) as admin:
            admin.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
            try:
                query = dict(parse_qsl(parsed.query))
                query['options'] = '-c search_path=' + schema
                isolated = urlunsplit(parsed._replace(query=urlencode(query, quote_via=quote)))
                store = StateStore(database_url=isolated)
                self.assertIsNone(store.current())
                first = store.publish(baseline_state())
                version = first['metadata']['version']
                self.assertEqual(StateStore(database_url=isolated).current(), first)
                with self.assertRaises(ConcurrentUpdate):
                    store.publish(baseline_state())
                second = store.publish(first, expected_version=version)
                self.assertNotEqual(second['metadata']['version'], version)
                store.rollback(version)
                self.assertEqual(StateStore(database_url=isolated).current(), first)
            finally:
                admin.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))
