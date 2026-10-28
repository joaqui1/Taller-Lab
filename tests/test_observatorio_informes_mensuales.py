import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from bs4 import BeautifulSoup

from observatorio.informes_mensuales import (
    calculate_report, editorial_reports, load_ipc, report_csv,
)


def observation(model_id, day, price, availability='disponible', reference=None):
    return {
        'model_id': model_id,
        'day_art': f'2026-03-{day:02d}',
        'observed_at': f'2026-03-{day:02d}T12:00:00+00:00',
        'price_ars': None if price is None else f'{price:.2f}',
        'reference_ars': None if reference is None else f'{reference:.2f}',
        'availability': availability,
        'currency': 'ARS',
        'evidence_sha256': 'a' * 64,
    }


def small_manifest():
    models = [
        {'id': 'a', 'brand': 'Bosch', 'model': 'GWS 25-230', 'variant': '230 mm', 'category': 'compresores', 'source': 'tienda', 'url': 'https://tienda.example/a'},
        {'id': 'b', 'brand': 'Bosch', 'model': 'GBH 2-26', 'variant': '220 V', 'category': 'compresores', 'source': 'tienda', 'url': 'https://tienda.example/b'},
        {'id': 'c', 'brand': 'Bosch', 'model': 'GWS 770', 'variant': '115 mm', 'category': 'compresores', 'source': 'tienda', 'url': 'https://tienda.example/c'},
        {'id': 'd', 'brand': 'Bosch', 'model': 'GWS 850', 'variant': '115 mm', 'category': 'compresores', 'source': 'tienda', 'url': 'https://tienda.example/d'},
        {'id': 'e', 'brand': 'Bosch', 'model': 'GWS 900', 'variant': '125 mm', 'category': 'compresores', 'source': 'tienda', 'url': 'https://tienda.example/e'},
    ]
    return {
        'selection': 'Modelos sintéticos para pruebas.',
        'models': models,
        'sources': {'tienda': {'name': 'Tienda de prueba', 'domain': 'tienda.example', 'official': False}},
    }


class MonthlyReportCalculationTests(unittest.TestCase):
    def setUp(self):
        self.manifest = small_manifest()
        self.history = {
            'observations': [
                observation('a', 2, 1000), observation('a', 28, 1200),
                observation('b', 2, 800, reference=1000), observation('b', 28, 1000),
                observation('c', 2, 500), observation('c', 14, 550),
                observation('d', 2, 400), observation('d', 28, None, 'agotado'),
                observation('e', 2, 500), observation('e', 28, 550),
            ],
        }

    def test_median_requires_both_edge_weeks_and_excludes_offer_movements(self):
        report = calculate_report('2026-03', self.history, self.manifest)
        row = report['categories'][0]
        self.assertEqual(row['models_in_sample'], 5)
        self.assertEqual(row['models_with_coverage'], 3)
        self.assertEqual(row['models_in_median'], 2)
        self.assertEqual(row['median_change_pct'], 15.0)
        self.assertEqual(row['out_of_stock'], 1)
        self.assertEqual(row['offers_ended'], 1)
        self.assertEqual({item['model_id'] for item in report['comparisons']}, {'a', 'b', 'e'})
        offer_end = next(item for item in report['comparisons'] if item['model_id'] == 'b')
        self.assertEqual(offer_end['movement_kind'], 'offer_ended')
        self.assertIsNone(report['ipc'])
        self.assertIsNone(row['real_median_change_pct'])
        json.dumps(report)

    def test_ipc_comparison_appears_only_for_a_loaded_month(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ipc.json'
            path.write_text(json.dumps({'meses': {'2026-03': {
                'variacion_mensual_pct': 10,
                'url': 'https://www.indec.gob.ar/archivo-ipc',
            }}}), encoding='utf-8')
            ipc = load_ipc(path)
        report = calculate_report('2026-03', self.history, self.manifest, ipc)
        self.assertEqual(report['ipc']['variacion_mensual_pct'], '10')
        self.assertAlmostEqual(report['categories'][0]['real_median_change_pct'], 4.5455, places=3)
        self.assertIn('variacion_mediana_pct', report_csv(report))

    def test_editorial_month_is_not_published_until_explicitly_enabled_and_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / '2026-03.json'
            path.write_text(json.dumps({'mes': '2026-03', 'publicado': False, 'lectura_del_mes': ''}), encoding='utf-8')
            self.assertEqual(editorial_reports(directory), [])
            path.write_text(json.dumps({'mes': '2026-03', 'publicado': True, 'lectura_del_mes': ''}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'lectura_del_mes'):
                editorial_reports(directory)
            path.write_text(json.dumps({'mes': '2026-03', 'publicado': True, 'lectura_del_mes': 'Lectura editorial.'}), encoding='utf-8')
            self.assertEqual(editorial_reports(directory), [{'month': '2026-03', 'reading': 'Lectura editorial.'}])

    def test_static_report_has_dataset_csv_affiliate_and_no_merchant_links(self):
        from observatorio import estatico

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / 'manifest.json'
            history_path = root / 'history.json'
            editorial_dir = root / 'editorials'
            output = root / 'public'
            affiliate_path = root / 'affiliates.json'
            editorial_dir.mkdir()
            manifest = small_manifest()
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            history = {'version': 1, 'observations': [observation('a', 2, 1000), observation('a', 28, 1200),
                                                       observation('b', 2, 800), observation('b', 28, 900)],
                       'latest_attempts': {}, 'run': {'finished_at': '2026-03-28T12:00:00+00:00'}}
            history_path.write_text(json.dumps(history), encoding='utf-8')
            (editorial_dir / '2026-03.json').write_text(json.dumps({
                'mes': '2026-03', 'publicado': True, 'lectura_del_mes': 'El precio publicado tuvo un aumento en la muestra observada.'
            }), encoding='utf-8')
            model_path = '/datos/precios/compresores/bosch-gws-25-230/'
            affiliate_path.write_text(json.dumps({'models': {'bosch-gws-25-230': {
                'price_path': model_path, 'url': 'https://meli.la/1AbCdEf',
            }}}), encoding='utf-8')
            with patch.object(estatico, 'MANIFEST', manifest_path), \
                 patch.object(estatico, 'EDITORIAL_DIR', editorial_dir), \
                 patch.object(estatico, 'DEFAULT_IPC', root / 'missing-ipc.json'), \
                 patch.object(estatico, 'AFFILIATES_PATH', affiliate_path):
                summary = estatico.build_site(history_path, output, manifest_path=manifest_path)
                estatico.verify_publication(output, summary)

            self.assertIn('/datos/precios/informes/', summary['routes'])
            self.assertIn('/datos/precios/informes/2026-03/', summary['routes'])
            report_html = (output / 'datos/precios/informes/2026-03/index.html').read_text(encoding='utf-8')
            index_soup = BeautifulSoup((output / 'datos/precios/informes/index.html').read_text(encoding='utf-8'), 'html.parser')
            self.assertEqual(index_soup.select_one('meta[name=robots]')['content'], 'index, follow, max-image-preview:large')
            self.assertIn('/datos/precios/informes/', (output / 'sitemap.xml').read_text(encoding='utf-8'))
            report_soup = BeautifulSoup(report_html, 'html.parser')
            types = [json.loads(script.string)['@type'] for script in report_soup.select('script[type="application/ld+json"]')]
            self.assertIn('Dataset', types)
            self.assertTrue(report_soup.select_one('.report-chart'))
            self.assertTrue(report_soup.select_one('.monthly-reading').get_text(strip=True).endswith('El precio publicado tuvo un aumento en la muestra observada.'))
            self.assertTrue((output / 'datos/precios/informes/2026-03.csv').is_file())
            affiliate = report_soup.select_one('a[href="https://meli.la/1AbCdEf"]')
            self.assertEqual(set(affiliate.get('rel', [])), {'sponsored', 'nofollow', 'noopener'})
            self.assertIn('Podemos recibir una comisión si comprás desde este enlace', affiliate.parent.get_text(' ', strip=True))
            no_affiliate_row = next(row for row in report_soup.select('.report-models tbody tr') if 'GBH 2-26' in row.get_text())
            self.assertFalse(no_affiliate_row.select('a[href^="https://meli.la/"]'))
            self.assertIn('Precio publicado por Tienda de prueba', report_soup.get_text(' ', strip=True))
            self.assertFalse(report_soup.select('a[href*="tienda.example"]'))
            self.assertTrue(index_soup.select_one('a[href="/datos/precios/informes/2026-03/"]'))
            hub = BeautifulSoup((output / 'datos/precios-herramientas-argentina/index.html').read_text(encoding='utf-8'), 'html.parser')
            self.assertTrue(hub.select_one('a[href="/datos/precios/informes/2026-03/"]'))
            (editorial_dir / '2026-03.json').write_text(json.dumps({
                'mes': '2026-03', 'publicado': False, 'lectura_del_mes': 'Lectura en revisión.'
            }), encoding='utf-8')
            draft_output = root / 'draft'
            with patch.object(estatico, 'MANIFEST', manifest_path), patch.object(estatico, 'EDITORIAL_DIR', editorial_dir):
                draft_summary = estatico.build_site(history_path, draft_output, manifest_path=manifest_path)
                estatico.verify_publication(draft_output, draft_summary)
                expected_draft_paths = estatico.expected_observatory_paths()
            self.assertFalse((draft_output / 'datos/precios/informes/2026-03/index.html').exists())
            self.assertNotIn('/datos/precios/informes/', draft_summary['routes'])
            self.assertNotIn('/datos/precios/informes/', expected_draft_paths)
            draft_index = BeautifulSoup((draft_output / 'datos/precios/informes/index.html').read_text(encoding='utf-8'), 'html.parser')
            self.assertEqual(draft_index.select_one('meta[name=robots]')['content'], 'noindex, follow')
            self.assertNotIn('/datos/precios/informes/', (draft_output / 'sitemap.xml').read_text(encoding='utf-8'))
            linked_reports_hub = []
            for html_file in draft_output.rglob('*.html'):
                soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
                linked_reports_hub.extend(
                    (html_file, link['href']) for link in soup.select('a[href]')
                    if link['href'] == '/datos/precios/informes/'
                )
            self.assertEqual(linked_reports_hub, [])
            draft_hub = BeautifulSoup((draft_output / 'datos/precios-herramientas-argentina/index.html').read_text(encoding='utf-8'), 'html.parser')
            self.assertFalse(draft_hub.select_one('.latest-report'))


if __name__ == '__main__':
    unittest.main()
