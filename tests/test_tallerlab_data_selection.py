import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
for folder in ['', '.qa-deps', 'tmp/auditoria-observatorio-deps']:
    sys.path.insert(0, str(ROOT / folder))
from tallerlab_data.storage import get_tool, list_tools
from tallerlab_data.selection import family, documentary_order
from tallerlab_data.comparator import compare_tools
from tallerlab_data.affiliates import DISCLOSURE, LINKS, affiliate_for, render_affiliate_options
from tallerlab_data.views import render_tool_comparator_page, render_tool_detail_page
from tallerlab_data.documentary import assess


class SelectionChecks(unittest.TestCase):
    def test_distinct_drilling_mechanisms_cannot_compare_numbers(self):
        tools = [get_tool(slug) for slug in ['bosch-gsb-18v-50', 'bosch-gbh-180-li', 'bosch-gdr-120-li', 'omaha-ab550161k']]
        self.assertEqual(len({family(t) for t in tools}), 4)
        result = compare_tools(tools)
        self.assertTrue(result.rows)
        self.assertFalse(any(row.is_comparable for row in result.rows))
        self.assertTrue(all('Aplicaciones distintas' in row.warning for row in result.rows))

    def test_single_model_default_chooses_same_family(self):
        html = render_tool_comparator_page(['bosch-gdr-120-li'])
        self.assertIn('value="dewalt-dcf887" selected', html)
        self.assertNotIn('value="bosch-gbh-180-li" selected', html)
        for category, segment in [('amoladoras', 'amoladora-banco'), ('compresores', 'aerografo')]:
            html = render_tool_comparator_page(category=category, segment=segment)
            self.assertIn('Esta familia tiene un solo modelo', html)

    def test_affiliates_require_explicit_model_identity(self):
        for slug, entry in LINKS.items():
            tool = get_tool(slug)
            self.assertEqual(affiliate_for(tool), entry)
            altered = copy.deepcopy(tool)
            altered.mpn += '-OTHER'
            self.assertIsNone(affiliate_for(altered))
        makita_options = render_affiliate_options([get_tool('makita-dmp180')])
        self.assertIn('https://meli.la/2uRPKYD', makita_options)
        self.assertIn('rel="sponsored nofollow noopener"', makita_options)
        self.assertIn(DISCLOSURE, makita_options)
        html = render_affiliate_options([get_tool('ingco-cidli20668-4')])
        self.assertIn('rel="sponsored nofollow noopener"', html)
        self.assertIn(DISCLOSURE, html)
        self.assertNotIn('274KM8a', html)

    def test_tool_ficha_shows_only_exact_affiliate_button(self):
        html = render_tool_detail_page(get_tool('ingco-cidli20668-4'))
        self.assertIn('href="https://meli.la/2xvJRJp"', html)
        self.assertIn('rel="sponsored nofollow noopener"', html)
        self.assertIn('data-affiliate-placement="tallerlab-data"', html)
        self.assertIn(DISCLOSURE, html)
        self.assertIn('https://meli.la/2uRPKYD', render_tool_detail_page(get_tool('makita-dmp180')))

        from servidor_local import validate_affiliate_click
        event = validate_affiliate_click({
            'product': 'https://meli.la/1qPbvWX',
            'page': '/herramientas/lusqtoff-hl-120/',
            'placement': 'tallerlab-data',
        })
        self.assertEqual(event['product'], 'https://meli.la/1qPbvWX')

    def test_affiliate_disclosure_survives_final_public_renderer(self):
        from app import app
        response = app.test_client().get('/herramientas/ingco-cidli20668-4/')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn(DISCLOSURE, html)
        self.assertIn('https://meli.la/2xvJRJp', html)

    def test_documentary_order_does_not_depend_on_affiliate_registry(self):
        tools = list_tools()
        order = [t.slug for t in sorted(tools, key=documentary_order)]
        with patch.dict(LINKS, {}, clear=True):
            self.assertEqual(order, [t.slug for t in sorted(tools, key=documentary_order)])

    def test_evidence_cannot_mix_original_number_with_converted_unit(self):
        tool = get_tool('makita-dmp180')
        spec = copy.deepcopy(next(iter(tool.specs.values())))
        spec.raw_value, spec.raw_unit = '360 L/h', 'L/h'
        spec.normalized_value, spec.normalized_unit = 6, 'L/min'
        spec.condition, spec.notes = 'Declarado', ''
        spec.source_url = 'https://makita.com.ar/ficha'
        record = dict(status='recuperado', format='html', text_sha256='fixture', checked_at='2026-10-04')
        with patch('tallerlab_data.documentary.source_record', return_value=record):
            with patch('tallerlab_data.documentary.text_for_code', return_value=('DMP180: caudal 360 L/min', True)):
                assess(tool, spec)
                self.assertEqual(spec.documentary_status, 'sin_respaldo')
            with patch('tallerlab_data.documentary.text_for_code', return_value=('DMP180: caudal 360 L/h', True)):
                assess(tool, spec)
                self.assertEqual(spec.documentary_status, 'concordancia_textual')


if __name__ == '__main__':
    unittest.main()
