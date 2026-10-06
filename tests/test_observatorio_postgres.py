"""Integración opcional en un esquema desechable de una instancia PostgreSQL de pruebas."""
import os
import unittest
import uuid
from urllib.parse import urlsplit, urlunsplit, parse_qsl, quote, urlencode
from unittest.mock import patch

@unittest.skipUnless(os.environ.get('OBSERVATORY_TEST_DATABASE_URL'), 'Falta una instancia PostgreSQL de pruebas')
class TestPostgresObservatorio(unittest.TestCase):
    def test_schema_migration_lock_and_idempotent_capture(self):
        import psycopg
        from psycopg import sql
        from observatorio import config
        from observatorio.db import init_db, query_one, execute_stmt
        from observatorio.cli import cmd_seed_catalog
        from observatorio.collector import run_collection_batch, _acquire_run_lock, _now
        from observatorio.extractors.fixtures import FIXTURE_BULONERA_HTML_VALID
        url=os.environ['OBSERVATORY_TEST_DATABASE_URL']
        schema='obs_test_'+uuid.uuid4().hex
        old=config.DATABASE_URL,config.STORAGE_MODE
        with psycopg.connect(url,autocommit=True) as admin:
            admin.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
            try:
                parsed=urlsplit(url)
                parameters=dict(parse_qsl(parsed.query))
                parameters['options']=parameters.get('options','')+' -c search_path='+schema
                config.DATABASE_URL=urlunsplit((parsed.scheme,parsed.netloc,parsed.path,urlencode(parameters, quote_via=quote),parsed.fragment))
                config.STORAGE_MODE='postgres'
                init_db(); init_db(); cmd_seed_catalog(None)
                self.assertTrue(_acquire_run_lock('one',_now()))
                self.assertFalse(_acquire_run_lock('two',_now()))
                execute_stmt("UPDATE collector_runs SET status='completed' WHERE id='one'")
                execute_stmt('UPDATE collector_lease SET owner=NULL WHERE id=1')
                execute_stmt("UPDATE sources SET status='habilitada',capture_allowed=1,redistribution_allowed=1,terms_verified_date='test-only' WHERE id='tienda_bulonera_vtex'")
                class Response:
                    status_code=200
                    text=FIXTURE_BULONERA_HTML_VALID
                    headers={}
                with patch('observatorio.collector.requests.get',return_value=Response()):
                    for _ in range(2):
                        run_collection_batch(batch_size=1,offer_ids_subset=['OFF-COMP-LUSQ-LC2550B-BULO'])
                self.assertEqual(query_one('SELECT COUNT(*) AS c FROM observations')['c'],1)
            finally:
                config.DATABASE_URL,config.STORAGE_MODE=old
                admin.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))
