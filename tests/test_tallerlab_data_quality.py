"""Regression tests on a disposable SQLite catalog, never the working database."""
import copy
import csv
import io
import json
import math
import sys
import tempfile
import unittest
from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for folder in ['.qa-deps', '.consultor-seo-deps', '.publication-qa-deps', '.integration-qa-deps', '.seo-qa-deps', '.taladros-qa-deps']:
    sys.path.insert(0, str(ROOT / folder))

from tallerlab_data import storage
from tallerlab_data.models import CommercialOffer
from tallerlab_data.catalog_seed import seed_database
from tallerlab_data.pipeline import normalize_unit_value, process_candidate_ingestion, record_price_observation
from tallerlab_data.comparator import analyze_spec_comparability
from tallerlab_data.quality import latest_verified_offer
from tallerlab_data.research_study import generate_research_study_metrics, generate_study_csv
from tallerlab_data.views import render_tool_detail_page, render_tools_hub_page, get_tool_product_schema, render_research_study_page
from tallerlab_data.migrate_quality import migrate_quality_metadata


class TestQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        cls.database = Path(cls.temp.name) / 'catalog.db'
        cls.override = patch.object(storage, 'DB_PATH', cls.database)
        cls.override.start()
        seed_database()

    @classmethod
    def tearDownClass(cls):
        cls.override.stop()
        cls.temp.cleanup()

    def tool(self):
        return storage.get_tool('bosch-gsb-18v-50')

    def test_weights_and_ranges(self):
        self.assertEqual(normalize_unit_value('1500g', 'peso'), (1.5, 'kg'))
        self.assertAlmostEqual(normalize_unit_value('5 lb', 'peso')[0], 2.268, places=3)
        self.assertIsNone(normalize_unit_value('1,3–2,4 kg', 'peso')[0])
        self.assertIsNone(normalize_unit_value('0–500 / 0–2.000 rpm', 'rpm')[0])
        self.assertIsNone(normalize_unit_value('2 kVA', 'potencia')[0])

    def test_pending_and_null_prices_do_not_publish(self):
        tool = self.tool()
        tool.commercial_offers = [offer for offer in tool.offers if offer.verification_status != "verificado"]
        html = render_tool_detail_page(tool)
        self.assertNotIn('419,000', html)
        self.assertNotIn('Stock detectado: disponible', html)
        self.assertNotIn('"offers"', get_tool_product_schema(tool, 'https://example.com/tool'))
        tool.offers[0].observed_price_ars = None
        self.assertIn('TallerLab no vende herramientas: confirmá precio, stock', render_tool_detail_page(tool))
        self.assertNotIn('pendientes de relevamiento', render_tool_detail_page(tool))

    def test_offers_evidence_dates_and_shared_selection(self):
        tool = self.tool()
        today = datetime.now(timezone.utc).date()
        old = CommercialOffer('Old', 'Shop', 'https://example.com/old', 999, (today-timedelta(days=8)).isoformat(), verification_status='verificado', evidence_reference='capture-old')
        valid = CommercialOffer('Shop', 'Shop', 'https://example.com/new', 12345, today.isoformat(), verification_status='verificado', evidence_reference='capture-new')
        future = copy.deepcopy(valid)
        future.observation_date = (today+timedelta(days=1)).isoformat()
        no_evidence = copy.deepcopy(valid)
        no_evidence.evidence_reference = ''
        tool.commercial_offers = [old, future, no_evidence, valid]
        self.assertIs(latest_verified_offer(tool), valid)
        schema = json.loads(get_tool_product_schema(tool, 'https://example.com/tool').split('>',1)[1].rsplit('<',1)[0])
        self.assertNotIn('availability', schema['offers'])
        self.assertNotIn('priceValidUntil', schema['offers'])
        self.assertEqual(schema['offers']['price'], '12345.00')
        self.assertIn('12,345', render_tool_detail_page(tool))

    def test_offer_storage_roundtrip(self):
        self.assertFalse(record_price_observation(self.tool().slug, 'Shop','Shop','https://example.com/price', 500))
        self.assertTrue(record_price_observation(self.tool().slug, 'Shop','Shop','https://example.com/price', 500, evidence_reference='tmp/capture.json', availability='agotado', kit_code='official-kit'))
        offer = latest_verified_offer(self.tool())
        self.assertEqual(offer.evidence_reference, 'tmp/capture.json')
        self.assertEqual(offer.availability, 'agotado')
        self.assertEqual(offer.kit_quoted, 'official-kit')

    def test_sources_classified_and_migration_idempotent(self):
        migrate_quality_metadata()
        migrate_quality_metadata()
        for tool in storage.list_tools():
            for spec in tool.specs.values():
                if 'fravega.com' in spec.source_url or 'supertoolsbd.com' in spec.source_url:
                    self.assertEqual(spec.source_type, 'comercio')
                self.assertNotEqual(spec.document_page, 'pág. 1')

    def test_seed_preserves_review(self):
        tool = self.tool()
        original = tool.specs['torque_maximo'].raw_value
        tool.specs['torque_maximo'].raw_value = 'Reviewed correction'
        storage.save_tool(tool)
        seed_database()
        self.assertEqual(self.tool().specs['torque_maximo'].raw_value, 'Reviewed correction')
        tool.specs['torque_maximo'].raw_value = original
        storage.save_tool(tool)

    def test_ingestion_stages_even_formally_valid_data(self):
        payload = dict(slug='review-only', brand='Test', commercial_name='Test', mpn='TEST-Q', category='taladros', voltage='220 V / 50 Hz', primary_sources=[{'url':'https://example.com/manual.pdf'}], specs={key: spec.to_dict() for key, spec in list(self.tool().specs.items())[:2]})
        result = process_candidate_ingestion(payload)
        self.assertFalse(result['accepted'])
        self.assertEqual(result['status'], 'validado_para_revision')
        self.assertIsNone(storage.get_tool('review-only'))
        self.assertTrue(any(row['candidate_code']=='TEST-Q' for row in storage.list_candidates(include_test=True)))
        payload['primary_sources'] = [{'url':'not-a-url'}]
        self.assertEqual(process_candidate_ingestion(payload)['status'], 'aislado_en_staging')

    def test_comparison_missing_units_and_pressure(self):
        def spec(unit, condition='Neto', status='declarado', value=1):
            return dict(normalized_unit=unit, condition=condition, status=status, normalized_value=value, name='Value')
        for key, values in [
            ('peso', [spec('kg'), spec('g')]),
            ('peso', [spec('kg'), spec('kg', status='no_encontrado', value=None)]),
            ('peso', [spec('kg', 'Balanza'), spec('kg','Sin batería')]),
            ('caudal', [spec('L/min','Salida a 4 bar'), spec('L/min','Salida a 101.5 psi')]),
        ]:
            self.assertFalse(analyze_spec_comparability(key, values)['is_comparable'])
        self.assertTrue(analyze_spec_comparability('caudal', [spec('L/min','Salida a 7 bar'),spec('L/min','Salida a 101.5 psi')])['is_comparable'])

    def test_research_rejects_missing_observations(self):
        for slug, key, metric in [('gamma-g2801ar','caudal_fad','compresores_fad_count'), ('karcher-k2-basic','presion_trabajo','hidro_trabajo_separada_count')]:
            tool = storage.get_tool(slug)
            observation = copy.deepcopy(next(iter(tool.specs.values())))
            observation.status = 'no_encontrado'
            observation.normalized_value = None
            tool.specs = {key: observation}
            with patch('tallerlab_data.research_study.list_tools', return_value=[tool]):
                self.assertEqual(generate_research_study_metrics()[metric], 0)

    def test_csv_reproduces_coverage(self):
        rows = list(csv.DictReader(io.StringIO(generate_study_csv())))
        metrics = generate_research_study_metrics()
        self.assertEqual(len(rows), metrics['total_specs_analyzed'])
        tools = {row['slug']: row for row in rows}
        self.assertEqual(sum(row['caudal_salida_en_base']=='disponible' for row in tools.values()), metrics['compresores_fad_count'])
        self.assertEqual(sum(row['presion_trabajo_en_base']=='disponible' for row in tools.values()), metrics['hidro_trabajo_separada_count'])
        for field in ['condicion','fuente_url','estado','variante']:
            self.assertIn(field, rows[0])

    def test_public_claims(self):
        html = render_tools_hub_page()
        self.assertNotIn('100%</span>', html)
        self.assertNotIn('Manuales Contrastados', html)
        self.assertIn('Batería 18 V CC', html)
        study = render_research_study_page()
        self.assertNotIn('brecha promedio', study)
        self.assertIn('no demuestra que el fabricante lo omita', study)


if __name__ == '__main__':
    unittest.main()
