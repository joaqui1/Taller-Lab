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
from tallerlab_data.research_study import generate_research_study_metrics, generate_study_csv, get_research_study_data
from tallerlab_data.views import render_tool_detail_page, render_tools_hub_page, get_tool_product_schema, render_research_study_page, get_research_study_schema
from app import tallerlab_data_json, app as flask_app
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

    def test_research_study_groups_compressors_by_family(self):
        metrics = generate_research_study_metrics()
        families = metrics['compresores_por_familia']
        rows = list(csv.DictReader(io.StringIO(generate_study_csv())))
        compressor_rows = [row for row in rows if row['categoria'] == 'compresores']
        self.assertIn('familia_aplicacion', compressor_rows[0])
        self.assertEqual(len({row['slug'] for row in compressor_rows}), 25)
        expected_counts = {'compresor-tanque': 2, 'inflador': 3, 'aerografo': 0}
        for family_key, expected_count in expected_counts.items():
            family_rows = [row for row in compressor_rows if row['familia_aplicacion'] == family_key]
            self.assertEqual(families[family_key]['total'], len({row['slug'] for row in family_rows}))
            self.assertEqual(families[family_key]['output_flow_count'], expected_count)
        self.assertEqual(sum(item['total'] for item in families.values()), 25)

        page = render_research_study_page()
        self.assertIn(f"De {families['compresor-tanque']['total']} compresores con tanque de la base, 2 tienen caudal de salida a presión de trabajo documentado.", page)
        self.assertLess(page.index('Compresores con tanque</td>'), page.index('Infladores portátiles</td>'))
        self.assertNotIn('el fabricante lo omita', page)

        schema = json.loads(get_research_study_schema('https://example.test/study', 'https://example.test/data.csv').split('>', 1)[1].split('</script>', 1)[0])
        self.assertEqual(len(schema['variableMeasured']), 3)
        self.assertEqual(schema['variableMeasured'][0]['value'], 2)

    def test_press_summary_route_returns_current_counts(self):
        from app import app
        study = get_research_study_data()
        metrics = study['metrics']
        tanks = metrics['compresores_por_familia']['compresor-tanque']
        with app.test_client() as client:
            response = client.get('/herramientas/investigacion/brecha-especificaciones-argentina/#prensa')
            self.assertEqual(response.status_code, 200)
            html = response.get_data(as_text=True)
            self.assertIn(f"{tanks['output_flow_count']} de {tanks['total']} compresores con tanque", html)
            self.assertIn(f"{metrics['hidro_trabajo_separada_count']} tienen presión de trabajo registrada por separado", html)
            self.assertIn(f"{metrics['rotary_hammers_epta_count']} tienen energía de impacto declarada bajo EPTA", html)
            self.assertIn(study['version'][:8], html)

            dataset = client.get('/herramientas/investigacion/descargar-datos.json').get_json()
            self.assertEqual(dataset['version'], study['version'])
            self.assertEqual(dataset['edition_date'], study['edition_date'])

            chart = client.get('/herramientas/investigacion/grafico-cobertura.svg')
            self.assertEqual(chart.status_code, 200)
            self.assertIn(f"{tanks['output_flow_count']} de {tanks['total']}", chart.get_data(as_text=True))

    def test_research_study_edition_matches_downloadable_json(self):
        payload = json.loads(tallerlab_data_json().get_data(as_text=True))
        edition_date = payload['dateModified']
        edition_date_display = f"{edition_date[8:10]}/{edition_date[5:7]}/{edition_date[:4]}"
        edition_version = payload['version'][:8]

        page = render_research_study_page()
        self.assertIn(f"Edición del {edition_date_display} · versión {edition_version}", page)
        self.assertIn(f"TallerLab ({edition_date_display}). Cobertura de especificaciones en el catálogo argentino de TallerLab. Versión {edition_version}.", page)
        self.assertIn('Cómo citar este estudio', page)
        self.assertIn('Copiar cita', page)
        self.assertIn('Historial de cambios', page)
        self.assertIn('Licencia CC BY 4.0', page)

        schema = json.loads(get_research_study_schema('https://example.test/study', 'https://example.test/data.csv').split('>', 1)[1].split('</script>', 1)[0])
        self.assertEqual(schema['dateModified'], payload['dateModified'])
        self.assertEqual(schema['version'], payload['version'])
        self.assertEqual(schema['license'], 'https://creativecommons.org/licenses/by/4.0/')

    def test_public_claims(self):
        html = render_tools_hub_page()
        self.assertNotIn('100%</span>', html)
        self.assertNotIn('Manuales Contrastados', html)
        self.assertIn('Batería 18 V CC', html)
        study = render_research_study_page()
        self.assertNotIn('brecha promedio', study)
        self.assertIn('no presenta una ausencia en la base como una omisión del fabricante', study)

    def test_research_coverage_svg_download_uses_current_metrics(self):
        response = flask_app.test_client().get('/herramientas/investigacion/grafico-cobertura.svg')
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response.content_type)
        svg = response.get_data(as_text=True)
        metrics = get_research_study_data()['metrics']
        families = metrics['compresores_por_familia']
        expected = [
            (families['compresor-tanque']['output_flow_count'], families['compresor-tanque']['total']),
            (families['inflador']['output_flow_count'], families['inflador']['total']),
            (metrics['hidro_trabajo_separada_count'], metrics['hidro_total']),
            (metrics['rotary_hammers_epta_count'], metrics['rotary_hammers_total']),
            (metrics['contradictions_count'], metrics['sample_size']),
        ]
        for count, total in expected:
            self.assertIn(f'>{count} de {total}</text>', svg)
        self.assertIn('<title', svg)
        self.assertIn('<desc', svg)
        self.assertIn('Fuente: TallerLab, edición ', svg)


if __name__ == '__main__':
    unittest.main()
