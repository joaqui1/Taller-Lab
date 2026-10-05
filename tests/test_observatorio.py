"""Batería de pruebas unitarias y de integración para el Observatorio de Precios."""

import csv
import io
import os
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from observatorio.analytics import (
    analyze_seller_discount,
    get_experimental_tool_basket_index,
    get_product_current_stats,
    get_product_price_history_series,
)
from observatorio.catalog import CATALOG_PRODUCTS, PRODUCTS_BY_ID
from observatorio.collector import CollectorLockError, run_collection_batch
from observatorio.config import (
    FRESHNESS_HOURS_LIMIT,
    PRICE_JUMP_THRESHOLD_PERCENT,
)
from observatorio.db import execute_stmt, init_db, query_all, query_one
from observatorio.export_csv import export_observations_to_csv, sanitize_csv_field
from observatorio.extractors.base import BaseExtractor, ExtractionResult
from observatorio.extractors.feed_importer import FeedImporter
from observatorio.extractors.fixtures import (
    FIXTURE_BULONERA_HTML_VALID,
    FIXTURE_EASY_HTML_WITH_INSTALLMENTS,
    FIXTURE_FEED_CATALOG_JSON,
    FIXTURE_HTML_MISSING_PRICE,
    FIXTURE_HTML_NON_ARS_CURRENCY,
    FIXTURE_HTML_OUT_OF_STOCK,
    FIXTURE_HTML_PRICE_JUMP,
    FIXTURE_HTML_VARIANT_MISMATCH,
)
from observatorio.extractors.store_adapters import EasyStoreAdapter, VtexStoreAdapter
from observatorio.extractors.structured_data import StructuredDataExtractor
from observatorio.sources import CONFIGURED_OFFERS, OFFERS_BY_ID
from observatorio.validation import is_observation_fresh, validate_observation
from observatorio.views import (
    get_dataset_schema_json,
    render_model_price_widget,
    render_observatory_category_html,
    render_observatory_hub_html,
    render_observatory_methodology_html,
)


class TestObservatorio(unittest.TestCase):
    _temp_dir = None

    @classmethod
    def setUpClass(cls):
        import tempfile
        from pathlib import Path
        import observatorio.config as cfg
        from observatorio.cli import cmd_seed_catalog

        # Barrera de seguridad contra base de datos no-test
        db_url = os.environ.get("DATABASE_URL", "")
        if db_url and "test" not in db_url.lower():
            raise RuntimeError("DATABASE_URL configurada no contiene 'test'. Abortando para proteger base productiva.")

        cls._orig_sqlite_path = cfg.SQLITE_PATH
        cls._orig_storage_mode = cfg.STORAGE_MODE

        cls._temp_dir = tempfile.TemporaryDirectory(prefix="test-observatorio-")
        test_db_path = Path(cls._temp_dir.name) / "test.db"
        cfg.STORAGE_MODE = "sqlite"
        cfg.SQLITE_PATH = test_db_path

        from observatorio.db import get_db
        with get_db() as conn:
            actual_path = Path(conn.execute('PRAGMA database_list').fetchone()[2]).resolve()
        if actual_path != test_db_path.resolve():
            raise RuntimeError('La conexión efectiva no corresponde a la base temporal.')

        init_db()
        cmd_seed_catalog(None)

    @classmethod
    def tearDownClass(cls):
        import observatorio.config as cfg
        if hasattr(cls, "_orig_sqlite_path"):
            cfg.SQLITE_PATH = cls._orig_sqlite_path
        if hasattr(cls, "_orig_storage_mode"):
            cfg.STORAGE_MODE = cls._orig_storage_mode
        if cls._temp_dir:
            cls._temp_dir.cleanup()

    def setUp(self):
        # Limpiar corridas y observaciones previas para pruebas deterministas
        execute_stmt("DELETE FROM collector_attempts;")
        execute_stmt("DELETE FROM collector_lease;")
        execute_stmt("DELETE FROM incidents;")
        execute_stmt("DELETE FROM observations;")
        execute_stmt("DELETE FROM collector_runs;")
        execute_stmt("UPDATE sources SET status = 'habilitada', capture_allowed=1, redistribution_allowed=1,terms_verified_date='test-only';")
        execute_stmt("UPDATE offers SET enabled = 1, last_checked_at = NULL,next_attempt_at=NULL;")

    def test_parse_money_exact_decimals(self):
        """El dinero debe manejarse exclusivamente con Decimal exacto y sin pérdida por float."""
        self.assertEqual(BaseExtractor.parse_money("289.900,50"), Decimal("289900.50"))
        self.assertEqual(BaseExtractor.parse_money("289,900.50"), Decimal("289900.50"))
        self.assertEqual(BaseExtractor.parse_money("$ 315.000"), Decimal("315000.00"))
        self.assertEqual(BaseExtractor.parse_money(125000), Decimal("125000.00"))
        self.assertEqual(BaseExtractor.parse_money(125000.75), Decimal("125000.75"))
        self.assertIsNone(BaseExtractor.parse_money(""))
        self.assertIsNone(BaseExtractor.parse_money(None))
        self.assertIsNone(BaseExtractor.parse_money("Consultar"))

    def test_structured_data_extractor_valid(self):
        """Prueba extracción correcta con JSON-LD schema.org/Product, transferencia y precio tachado."""
        target = PRODUCTS_BY_ID["COMP-LUSQ-LC2550B"]
        extractor = StructuredDataExtractor()
        res = extractor.extract(FIXTURE_BULONERA_HTML_VALID, "https://ejemplo.com", target)

        self.assertTrue(res.success)
        self.assertEqual(res.price_single_payment, Decimal("298500.00"))
        self.assertEqual(res.currency, "ARS")
        self.assertEqual(res.availability, "disponible")
        self.assertEqual(res.price_transfer, Decimal("268650.00"))
        self.assertEqual(res.price_reference_shown, Decimal("355000.00"))
        self.assertIsNotNone(res.raw_evidence_hash)
        self.assertTrue(len(res.raw_evidence_hash) == 64)

    def test_installments_distinct_from_single_payment(self):
        """Una cuota financiada nunca debe confundirse con el precio de pago único total."""
        target = PRODUCTS_BY_ID["COMP-LUSQ-LC2550B"]
        extractor = EasyStoreAdapter()
        res = extractor.extract(FIXTURE_EASY_HTML_WITH_INSTALLMENTS, "https://easy.com.ar", target)

        self.assertTrue(res.success)
        # El precio total es 312000.00, no la cuota de 42120 ni el total financiado de 505440
        self.assertEqual(res.price_single_payment, Decimal("312000.00"))
        self.assertNotEqual(res.price_single_payment, Decimal("42120.00"))
        self.assertNotEqual(res.price_single_payment, Decimal("505440.00"))

    def test_out_of_stock_handling(self):
        """Un producto agotado debe registrarse como agotado y NO publicarse como mínimo activo."""
        target = PRODUCTS_BY_ID["COMP-GAMMA-G2802"]
        extractor = StructuredDataExtractor()
        res = extractor.extract(FIXTURE_HTML_OUT_OF_STOCK, "https://ejemplo.com", target)

        self.assertTrue(res.success)
        self.assertEqual(res.availability, "agotado")

        report = validate_observation(res, target, OFFERS_BY_ID["OFF-COMP-GAMMA-G2802-BULO"])
        self.assertEqual(report.status, "valido")
        # REGLA OBLIGATORIA: Nunca publicar como mínimo activo un producto agotado
        self.assertFalse(report.is_published)
        self.assertEqual(report.incident_type, "out_of_stock")

    def test_variant_mismatch_detected(self):
        """Una página que ofrece un repuesto/accesorio en lugar del equipo debe ser rechazada."""
        target = PRODUCTS_BY_ID["HIDRO-KARCH-K2"]
        extractor = StructuredDataExtractor()
        res = extractor.extract(FIXTURE_HTML_VARIANT_MISMATCH, "https://ejemplo.com", target)

        self.assertFalse(res.success)
        self.assertIn("repuesto", res.error_message.lower())

    def test_missing_price_never_zero(self):
        """Un campo de precio ausente debe dar None, NUNCA inferirse como cero."""
        target = PRODUCTS_BY_ID["COMP-LUSQ-LC2550B"]
        extractor = StructuredDataExtractor()
        res = extractor.extract(FIXTURE_HTML_MISSING_PRICE, "https://ejemplo.com", target)

        self.assertFalse(res.success)
        self.assertIsNone(res.price_single_payment)
        self.assertNotEqual(res.price_single_payment, Decimal("0.00"))

        report = validate_observation(res, target, OFFERS_BY_ID["OFF-COMP-LUSQ-LC2550B-BULO"])
        self.assertEqual(report.status, "rechazado")

    def test_non_ars_currency_rejected(self):
        """Cualquier moneda que no sea ARS debe ser rechazada sin conjeturas de cambio."""
        target = PRODUCTS_BY_ID["GEN-HONDA-EU22I"]
        extractor = StructuredDataExtractor()
        res = extractor.extract(FIXTURE_HTML_NON_ARS_CURRENCY, "https://ejemplo.com", target)

        self.assertFalse(res.success)
        self.assertEqual(res.currency, "USD")

    def test_anomalous_price_jump_triggers_incident(self):
        """Un salto de precio superior al 35% respecto a la mediana previa debe marcarse anómalo."""
        target = PRODUCTS_BY_ID["COMP-LUSQ-LC2550B"]
        offer = OFFERS_BY_ID["OFF-COMP-LUSQ-LC2550B-BULO"]
        
        # Historial previo con mediana de ~290.000 ARS
        previous_obs = [
            {"price_single_payment": Decimal("290000.00"), "observed_at": "2026-10-01T10:00:00Z"},
            {"price_single_payment": Decimal("295000.00"), "observed_at": "2026-10-02T10:00:00Z"},
        ]

        # Nueva observación con caída o salto brusco (ej. 28.990 ARS por error de tipeo)
        anomalous_extraction = ExtractionResult(
            success=True,
            price_single_payment=Decimal("28990.00"),
            currency="ARS",
            availability="disponible",
        )

        report = validate_observation(anomalous_extraction, target, offer, previous_obs)
        self.assertEqual(report.status, "anomalo")
        self.assertFalse(report.is_published)
        self.assertEqual(report.incident_type, "price_jump")
        self.assertEqual(report.incident_severity, "critical")

    def test_freshness_policy(self):
        """Una observación con más de 48 horas queda fuera de la frescura activa."""
        now = datetime.now(timezone.utc)
        fresh_date = now - timedelta(hours=24)
        stale_date = now - timedelta(hours=50)

        self.assertTrue(is_observation_fresh(fresh_date))
        self.assertFalse(is_observation_fresh(stale_date))

    def test_feed_importer_catalog(self):
        """El importador de feed procesa correctamente catálogo JSON y mapea disponibilidad."""
        target = PRODUCTS_BY_ID["COMP-LUSQ-LC2550B"]
        importer = FeedImporter()
        res = importer.extract(FIXTURE_FEED_CATALOG_JSON, "https://feed.ejemplo.com", target)

        self.assertTrue(res.success)
        self.assertEqual(res.price_single_payment, Decimal("289900.00"))
        self.assertEqual(res.price_transfer, Decimal("260910.00"))
        self.assertEqual(res.price_reference_shown, Decimal("340000.00"))
        self.assertEqual(res.availability, "disponible")

    def test_collector_concurrency_exclusion(self):
        """Dos corridas simultáneas deben ser bloqueadas mediante exclusión mutua."""
        # Simular una corrida en ejecución
        now_utc = datetime.now(timezone.utc).isoformat()
        execute_stmt(
            "INSERT INTO collector_runs (id, started_at, status) VALUES ('run-lock-test', ?, 'running');",
            (now_utc,)
        )

        with self.assertRaises(CollectorLockError):
            run_collection_batch(batch_size=5, use_fixtures=True)

        # Liberar la corrida
        execute_stmt("UPDATE collector_runs SET status = 'completed' WHERE id = 'run-lock-test';")

    def test_collector_partial_failure_isolation(self):
        """El fallo en la extracción de un producto o tienda no interrumpe el resto del lote."""
        res = run_collection_batch(batch_size=5, use_fixtures=True)
        self.assertIn(res["status"], ("completed", "partial_failure"))
        self.assertGreater(res["successful_offers"], 0)
        self.assertGreater(res["total_offers"], 0)
        self.assertLessEqual(res["total_offers"], 5)

    def test_csv_sanitization_against_formula_injection(self):
        """Los caracteres executables (=, +, -, @) deben sanitizarse para proteger hojas de cálculo."""
        self.assertEqual(sanitize_csv_field("=SUM(A1:A10)"), "'=SUM(A1:A10)")
        self.assertEqual(sanitize_csv_field("+cmd|' /C calc'!A0"), "'+cmd|' /C calc'!A0")
        self.assertEqual(sanitize_csv_field("-123"), "'-123")
        self.assertEqual(sanitize_csv_field("@HYPERLINK"), "'@HYPERLINK")
        self.assertEqual(sanitize_csv_field("Compresor 50L"), "Compresor 50L")
        self.assertEqual(sanitize_csv_field(None), "")

    def test_csv_export_format_and_metadata(self):
        """El CSV exportado debe ser UTF-8, con comentarios de encabezado y columnas inequívocas."""
        now_utc = datetime.now(timezone.utc).isoformat()
        execute_stmt(
            "INSERT INTO collector_runs (id, started_at, status) VALUES ('run-test', ?, 'completed');",
            (now_utc,)
        )
        execute_stmt(
            """
            INSERT INTO observations (
                id, run_id, offer_id, product_id, observed_at,
                price_single_payment, currency, availability, validation_status,
                is_published, is_synthetic, extractor_version, created_at
            ) VALUES ('obs-csv-test', 'run-test', 'OFF-COMP-LUSQ-LC2550B-BULO', 'COMP-LUSQ-LC2550B',
                      ?, '289900.00', 'ARS', 'disponible', 'valido', 1, 0, '1.0.0', ?);
            """,
            (now_utc, now_utc)
        )

        csv_output = export_observations_to_csv(category="compresores")
        self.assertTrue(csv_output.startswith('observacion_id,'))
        self.assertIn("precio_pago_unico_ars", csv_output)
        self.assertIn("289900.00", csv_output)
        self.assertIn("Lüsqtoff", csv_output)

    def test_selection_picks_latest_observation_not_lowest(self):
        """Con una observación antigua de $100k y una nueva de $120k, debe publicar $120k."""
        pid = "COMP-LUSQ-LC2550B"
        oid = "OFF-COMP-LUSQ-LC2550B-BULO"
        older_dt = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        newer_dt = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        execute_stmt(
            """
            INSERT INTO observations (id, offer_id, product_id, observed_at, price_single_payment, currency, availability, validation_status, is_published, is_synthetic, extractor_version, created_at)
            VALUES ('obs-old', ?, ?, ?, '100000.00', 'ARS', 'disponible', 'valido', 1, 0, 'test', ?);
            """,
            (oid, pid, older_dt, older_dt)
        )
        execute_stmt(
            """
            INSERT INTO observations (id, offer_id, product_id, observed_at, price_single_payment, currency, availability, validation_status, is_published, is_synthetic, extractor_version, created_at)
            VALUES ('obs-new', ?, ?, ?, '120000.00', 'ARS', 'disponible', 'valido', 1, 0, 'test', ?);
            """,
            (oid, pid, newer_dt, newer_dt)
        )
        stats = get_product_current_stats(pid)
        self.assertEqual(stats["min_current_price"], Decimal("120000.00"))
        self.assertEqual(stats["active_offers_count"], 1)

    def test_sold_out_does_not_revive_older_available(self):
        """Si la última observación dice 'agotado', no debe revivir una captura previa con stock."""
        pid = "COMP-LUSQ-LC2550B"
        oid = "OFF-COMP-LUSQ-LC2550B-BULO"
        older_dt = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        newer_dt = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        execute_stmt(
            """
            INSERT INTO observations (id, offer_id, product_id, observed_at, price_single_payment, currency, availability, validation_status, is_published, is_synthetic, extractor_version, created_at)
            VALUES ('obs-avail', ?, ?, ?, '100000.00', 'ARS', 'disponible', 'valido', 1, 0, 'test', ?);
            """,
            (oid, pid, older_dt, older_dt)
        )
        execute_stmt(
            """
            INSERT INTO observations (id, offer_id, product_id, observed_at, price_single_payment, currency, availability, validation_status, is_published, is_synthetic, extractor_version, created_at)
            VALUES ('obs-soldout', ?, ?, ?, '100000.00', 'ARS', 'agotado', 'valido', 0, 0, 'test', ?);
            """,
            (oid, pid, newer_dt, newer_dt)
        )
        stats = get_product_current_stats(pid)
        self.assertEqual(stats["active_offers_count"], 0)
        self.assertIsNone(stats["min_current_price"])

    def test_empty_state_honest_presentation(self):
        """Cuando no hay observaciones válidas, se presenta un estado honesto sin inventar precios."""
        stats = get_product_current_stats("COMP-NICTOM-IE01")
        self.assertIsNone(stats["min_current_price"])
        self.assertEqual(stats["active_offers_count"], 0)
        self.assertFalse(stats["is_fresh"])

        # El widget de guía retorna cadena vacía cuando no hay datos
        widget_html = render_model_price_widget("COMP-NICTOM-IE01")
        self.assertEqual(widget_html, "")

    def test_no_secrets_in_public_outputs(self):
        """Garantizar que ningún secreto, token o credencial se filtre en HTML, CSV ni esquemas."""
        hub_html = render_observatory_hub_html()
        cat_html = render_observatory_category_html("compresores")
        met_html = render_observatory_methodology_html()
        csv_data = export_observations_to_csv()

        secret_indicators = ("password", "token", "secret", "bearer", "DATABASE_URL", "apikey")
        for text in (hub_html, cat_html, met_html, csv_data):
            for sec in secret_indicators:
                self.assertNotIn(f"{sec}=", text)
                self.assertNotIn(f"{sec}:", text.lower())

    def test_connection_really_uses_temporary_database(self):
        from pathlib import Path
        from observatorio import config
        from observatorio.db import get_db
        with get_db() as conn:
            actual = Path(conn.execute('PRAGMA database_list').fetchone()[2]).resolve()
        self.assertEqual(actual,config.SQLITE_PATH.resolve())
        self.assertEqual(actual.parent,Path(self._temp_dir.name).resolve())

    def test_unverified_source_is_not_requested(self):
        from unittest.mock import patch
        execute_stmt('UPDATE sources SET capture_allowed=0')
        with patch('observatorio.collector.requests.get') as request:
            result=run_collection_batch()
        self.assertEqual(request.call_count,0)
        self.assertEqual(result['status'],'no_sources')

    def test_verified_source_can_be_enabled_without_reactivating_paused_offers(self):
        from dataclasses import replace
        from unittest.mock import patch
        from observatorio.cli import cmd_seed_catalog
        from observatorio.sources import SOURCES_BY_ID
        source_id='tienda_bulonera_vtex'
        approved=replace(SOURCES_BY_ID[source_id],status='habilitada',capture_allowed=True,
                         redistribution_allowed=True,terms_verified_date='test-only')
        execute_stmt("UPDATE sources SET status='pendiente_evaluacion' WHERE id=?",(source_id,))
        execute_stmt("UPDATE offers SET enabled=0 WHERE id='OFF-COMP-LUSQ-LC2550B-BULO'")
        with patch('observatorio.cli.SOURCES_REGISTRY',[approved]):
            cmd_seed_catalog(None)
            self.assertEqual(query_one('SELECT status FROM sources WHERE id=?',(source_id,))['status'],'habilitada')
            self.assertEqual(query_one("SELECT enabled FROM offers WHERE id='OFF-COMP-LUSQ-LC2550B-BULO'")['enabled'],0)
            execute_stmt("UPDATE sources SET status='pausada' WHERE id=?",(source_id,))
            cmd_seed_catalog(None)
            self.assertEqual(query_one('SELECT status FROM sources WHERE id=?',(source_id,))['status'],'pausada')

    def test_sqlite_is_rejected_in_production(self):
        from unittest.mock import patch
        from observatorio.db import get_db
        with patch.dict(os.environ,{'VERCEL_ENV':'production'}):
            with self.assertRaises(RuntimeError):
                with get_db(): pass

    def test_http_empty_categories_sitemap_and_fixture_rejection(self):
        import app as module
        from unittest.mock import patch
        # Este contrato corresponde al modo SQLite legado, aislado del nuevo
        # piloto estático que tiene observaciones reales independientes.
        with patch('observatorio.estatico.static_observatory_file', return_value=None), patch('observatorio.estatico.published_observatory_paths', return_value=[]), patch.object(module,'OBSERVATORY_SECRET','test-only'), patch.dict(os.environ,{'CRON_SECRET':''}):
            with module.app.test_client() as client:
                self.assertEqual(client.get('/datos/precios/no-existe/descargar-csv').status_code,404)
                empty=client.get('/datos/precios/compresores/').get_data(as_text=True)
                self.assertIn('noindex',empty)
                self.assertNotIn('"@type": "Dataset"',empty)
                self.assertNotIn('/datos/precios/compresores/',client.get('/sitemap.xml').get_data(as_text=True))
                self._insert_probe('http-real')
                sitemap=client.get('/sitemap.xml').get_data(as_text=True)
                self.assertIn('/datos/precios/compresores/',sitemap)
                self.assertNotIn('/datos/precios/hidrolavadoras/',sitemap)
                self.assertEqual(client.get('/api/observatorio/ejecutar?fixtures=true',headers={'Authorization':'Bearer test-only'}).status_code,400)
                state=client.get('/api/observatorio/estado',headers={'Authorization':'Bearer test-only'}).get_json()
                self.assertNotEqual(state['status'],'ok')

    def test_atomic_lease_allows_one_concurrent_owner(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from observatorio.collector import _acquire_run_lock
        barrier=Barrier(2)
        def acquire(name):
            barrier.wait(timeout=10)
            return _acquire_run_lock(name,datetime.now(timezone.utc).isoformat())
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(acquire,['first','second']))
        self.assertEqual(sorted(results),[False,True])

    def test_backup_restores_sqlite_observations(self):
        from pathlib import Path
        from argparse import Namespace
        from contextlib import closing
        import sqlite3
        from observatorio.cli import cmd_backup
        self._insert_probe('backup-sentinel',price=123456)
        destination=Path(self._temp_dir.name)/'backup.db'
        cmd_backup(Namespace(dest=str(destination)))
        with closing(sqlite3.connect(destination)) as conn:
            self.assertEqual(conn.execute("SELECT price_single_payment FROM observations WHERE id='backup-sentinel'").fetchone()[0],123456)
            self.assertEqual(conn.execute('PRAGMA integrity_check').fetchone()[0],'ok')

    def _insert_probe(self, ident, price=100000, status='valido', published=1, synthetic=0, when=None):
        dt=when or datetime.now(timezone.utc).isoformat()
        execute_stmt('INSERT INTO observations(id,offer_id,product_id,observed_at,created_at,price_single_payment,currency,availability,validation_status,is_published,is_synthetic,extractor_version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                     (ident,'OFF-COMP-LUSQ-LC2550B-BULO','COMP-LUSQ-LC2550B',dt,dt,str(price),'ARS','disponible',status,published,synthetic,'test'))

    def test_all_public_outputs_exclude_synthetic_and_unpublished(self):
        for ident, synthetic, published in [('synthetic',1,1),('retained',0,0)]:
            self._insert_probe(ident,synthetic=synthetic,published=published)
        self.assertEqual(get_product_price_history_series('COMP-LUSQ-LC2550B'),[])
        self.assertNotIn('synthetic,',export_observations_to_csv())
        self.assertNotIn('retained,',export_observations_to_csv())
        self.assertIsNone(get_product_current_stats('COMP-LUSQ-LC2550B')['historical_min_price'])

    def test_rights_gate_csv_and_current_prices(self):
        self._insert_probe('real')
        execute_stmt("UPDATE sources SET redistribution_allowed=0 WHERE id='tienda_bulonera_vtex'")
        self.assertNotIn('real,',export_observations_to_csv())
        self.assertEqual(get_product_current_stats('COMP-LUSQ-LC2550B')['active_offers_count'],0)

    def test_new_anomaly_does_not_revive_old_price(self):
        self._insert_probe('old',when=(datetime.now(timezone.utc)-timedelta(hours=2)).isoformat())
        self._insert_probe('new',price=200000,status='anomalo',published=0)
        self.assertIsNone(get_product_current_stats('COMP-LUSQ-LC2550B')['min_current_price'])

    def test_timestamp_tie_counts_one_offer(self):
        stamp=datetime.now(timezone.utc).isoformat()
        self._insert_probe('a',when=stamp)
        self._insert_probe('b',price=120000,when=stamp)
        self.assertEqual(get_product_current_stats('COMP-LUSQ-LC2550B')['active_offers_count'],1)

    def test_expired_run_recovers_and_daily_capture_is_idempotent(self):
        stamp=(datetime.now(timezone.utc)-timedelta(hours=2)).isoformat()
        execute_stmt("INSERT INTO collector_runs(id,started_at,status) VALUES ('expired',?,'running')",(stamp,))
        kwargs={'batch_size':1,'use_fixtures':True,'offer_ids_subset':['OFF-COMP-LUSQ-LC2550B-BULO']}
        run_collection_batch(**kwargs)
        run_collection_batch(**kwargs)
        self.assertEqual(query_one('SELECT COUNT(*) AS c FROM observations')['c'],1)
        self.assertEqual(query_one("SELECT status FROM collector_runs WHERE id='expired'")['status'],'failed')

    def test_retry_after_is_never_shortened(self):
        from unittest.mock import patch
        from observatorio import config
        class Response:
            status_code=429
            headers={'Retry-After':'600'}
        with patch('observatorio.collector.requests.get',return_value=Response()) as request, patch('observatorio.collector.time.sleep') as sleep:
            run_collection_batch(batch_size=1,offer_ids_subset=['OFF-COMP-LUSQ-LC2550B-BULO'])
        self.assertEqual(request.call_count,1)
        self.assertFalse(any(call.args and call.args[0]<600 for call in sleep.call_args_list))
        with patch('observatorio.collector.requests.get') as request:
            run_collection_batch(batch_size=1,offer_ids_subset=['OFF-COMP-LUSQ-LC2550B-BULO'])
        self.assertEqual(request.call_count,0)

    def test_strict_variant_feed_and_visible_price(self):
        import json
        target=PRODUCTS_BY_ID['COMP-LUSQ-LC2550B']
        base={'@type':'Product','name':target.brand+' '+target.model_name,'mpn':target.mpn,
              'offers':{'@type':'Offer','price':'120000','priceCurrency':'ARS','availability':'https://schema.org/InStock'}}
        for changes in ({'mpn':target.mpn+'-OTHER'},{'voltage':'110 V'}):
            content='<script type="application/ld+json">'+json.dumps(dict(base,**changes))+'</script>'
            self.assertFalse(StructuredDataExtractor().extract(content,'https://example.invalid',target).success)
        content='<script type="application/ld+json">'+json.dumps(base)+'</script><div class="product-price">$180.000</div><del>$120.000</del>'
        self.assertFalse(StructuredDataExtractor().extract(content,'https://example.invalid',target).success)
        feed=FeedImporter()
        for item in ({'mpn':target.mpn,'price':120000,'stock':1},{'mpn':'OTHER','title':base['name'],'price':120000,'currency':'ARS','stock':1}):
            self.assertFalse(feed.extract(json.dumps([item]),'https://example.invalid',target).success)
        result=feed.extract(json.dumps([{'mpn':target.mpn,'price':120000,'currency':'ARS','stock':0}]),'https://example.invalid',target)
        self.assertEqual(result.availability,'agotado')

    def test_chart_has_explicit_gaps_and_vendor_links(self):
        self._insert_probe('older',when=(datetime.now(timezone.utc)-timedelta(days=2)).isoformat())
        self._insert_probe('today',price=120000)
        series=get_product_price_history_series('COMP-LUSQ-LC2550B')
        self.assertTrue(any(row['price'] is None for row in series))
        content=render_observatory_category_html('compresores')
        self.assertIn('<svg',content)
        self.assertIn('https://www.buloneragrupo.com.ar/',content)
        self.assertNotIn('<polyline',content)

    def test_upgrade_quarantines_legacy_observations(self):
        import sqlite3
        from contextlib import closing
        from pathlib import Path
        from observatorio import config
        original=config.SQLITE_PATH
        legacy=Path(self._temp_dir.name)/'legacy.db'
        schema=(Path(__file__).resolve().parents[1]/'observatorio/schema.sql').read_text(encoding='utf-8')
        schema=schema.replace('    is_synthetic INTEGER NOT NULL DEFAULT 0,','')
        schema=schema.replace('    capture_key TEXT,','')
        schema=';'.join(s for s in schema.split(';') if 'idx_obs_synthetic' not in s and 'idx_obs_capture_key' not in s)
        with closing(sqlite3.connect(legacy)) as conn: conn.executescript(schema)
        try:
            config.SQLITE_PATH=legacy
            init_db()
            with closing(sqlite3.connect(legacy)) as conn:
                columns={r[1]:r for r in conn.execute('PRAGMA table_info(observations)')}
                self.assertIn('capture_key',columns)
                self.assertEqual(columns['is_synthetic'][4],'1')
        finally:
            config.SQLITE_PATH=original


if __name__ == "__main__":
    unittest.main()
