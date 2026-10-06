"""SEO/authority rules for TallerLab Data pages."""
import re
import unittest
from types import SimpleNamespace

from tallerlab_data.comparator import analyze_spec_comparability
from tallerlab_data.documentary import evidence_source_label
from tallerlab_data.quality import MIN_INDEXABLE_BACKED_SPECS, tool_is_indexable
from tallerlab_data.storage import get_all_tools


def _spec(**kw):
    base = dict(status='declarado', condition='Máximo', name='Caudal máximo', source_type='ficha_fabricante',
                documentary_status='concordancia_textual', condition_status='sin_protocolo_especifico')
    base.update(kw)
    return base


class TestTallerLabDataSeo(unittest.TestCase):
    def test_indexability_threshold(self):
        backed = SimpleNamespace(documentary_status='concordancia_textual')
        loose = SimpleNamespace(documentary_status='sin_respaldo')
        self.assertFalse(tool_is_indexable(SimpleNamespace(specifications=[backed] * (MIN_INDEXABLE_BACKED_SPECS - 1) + [loose])))
        self.assertTrue(tool_is_indexable(SimpleNamespace(specifications=[backed] * MIN_INDEXABLE_BACKED_SPECS)))

    def test_label_follows_evidence_not_seed(self):
        spec = SimpleNamespace(source_name='Manual Bosch GHP 220 (pág. 14)', source_url='x')
        web = {'status': 'recuperado', 'format': 'html', 'title': 'GHP 220 Hidrolavadora | Bosch Professional'}
        self.assertEqual(evidence_source_label(spec, web), 'GHP 220 Hidrolavadora — Bosch Professional (página web)')
        self.assertEqual(evidence_source_label(spec, {'status': 'recuperado', 'format': 'pdf'}), 'Manual Bosch GHP 220')

    def test_flow_units_are_converted_before_comparing(self):
        a = _spec(normalized_value=420.0, normalized_unit='L/h')
        b = _spec(normalized_value=7.4, normalized_unit='L/min')
        result = analyze_spec_comparability('caudal_maximo', [a, b])
        self.assertNotIn('Unidades normalizadas distintas', result['warning'] or '')

    def test_sitemap_and_robots_agree(self):
        import app as A
        import servidor_local as S
        client = A.app.test_client()
        sitemap = client.get('/sitemap.xml').data.decode()
        listed = {re.sub(r'^https?://[^/]+', '', loc) for loc in re.findall(r'<loc>([^<]+)</loc>', sitemap)}
        for tool in get_all_tools():
            path = f'/herramientas/{tool.slug}/'
            html = client.get(path).data.decode()
            noindex = 'content="noindex, follow"' in html
            self.assertEqual(noindex, not tool_is_indexable(tool), path)
            self.assertEqual(path in listed, tool_is_indexable(tool), path)
        for path in S.TALLERLAB_DATA_EDITORIAL_PATHS:
            html = client.get(path).data.decode()
            self.assertEqual('content="noindex, follow"' in html, path not in listed, path)


if __name__ == '__main__':
    unittest.main()


class TestStructuredMatching(unittest.TestCase):
    def test_label_column_and_ranges(self):
        from tallerlab_data.documentary import _structured_match
        self.assertTrue(_structured_match('20 a 130 bar', 'presion (bar) 20 - max. 130 caudal'))
        self.assertTrue(_structured_match('420 L/h (7 L/min)', 'caudal (l/h) max. 420 rendimiento'))
        self.assertTrue(_structured_match('8 bar (115 PSI)', 'presion maxima: 115 psi'))
        self.assertTrue(_structured_match('2.800–11.000 rpm', 'en vacio 2.800 – 11.000 r. p. m.'))

    def test_every_figure_must_be_present(self):
        from tallerlab_data.documentary import _structured_match
        self.assertIsNone(_structured_match('42 / 27 Nm', 'torque suave 27 n·m'))
        self.assertIsNone(_structured_match('2,5 HP / 1750 W', 'potencia 2.5 hp'))
        self.assertIsNone(_structured_match('130 bar', 'presion 130 caudal 7 bar'))
