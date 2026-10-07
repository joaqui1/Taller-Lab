import unittest
import json
import tempfile
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from observatorio.publication_health import publication_warning, verify_live_publication
from observatorio.estatico import build_site
from observatorio.gratuito import DEFAULT_HISTORY


class PublicationHealthTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.finished = self.now.isoformat()
        self.report = {'unverified': 0, 'stale': 0,
                       'run': {'finished_at': self.finished, 'status': 'ok',
                               'captured': 44, 'already_captured': 0}}

    def test_success_and_daily_repeat_need_no_action(self):
        self.assertIsNone(publication_warning(self.report, self.finished, self.now))
        self.report['run'].update(captured=0, already_captured=44)
        self.assertIsNone(publication_warning(self.report, self.finished, self.now))

    def test_isolated_source_failure_is_warning(self):
        self.report['run'].update(status='degraded', captured=43)
        self.report['unverified'] = 1
        self.assertIn('1 productos sin verificación', publication_warning(self.report, self.finished, self.now))

    def test_old_publication_is_not_mistaken_for_current_run(self):
        with self.assertRaises(ValueError):
            publication_warning(self.report, (self.now-timedelta(minutes=5)).isoformat(), self.now)

    def test_total_failure_unfinished_expired_and_future_are_errors(self):
        for delta, status, captured in [(0, 'degraded', 0), (0, 'running', 44),
                                         (-49, 'ok', 44), (1, 'ok', 44)]:
            with self.subTest(delta=delta, status=status, captured=captured):
                report = deepcopy(self.report)
                finished = (self.now+timedelta(hours=delta)).isoformat()
                report['run'].update(finished_at=finished, status=status, captured=captured)
                with self.assertRaises(ValueError):
                    publication_warning(report, finished, self.now)

    def test_live_verification_requires_all_routes_canonical_and_matching_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history = json.loads(DEFAULT_HISTORY.read_text(encoding='utf-8'))
            now = datetime.fromisoformat(history['run']['finished_at']) + timedelta(minutes=1)
            summary = build_site(DEFAULT_HISTORY, root, now=now)
            expected = summary['run']['finished_at']
            def fetch(url):
                path = root / url.removeprefix('https://www.tallerlab.com.ar/')
                if path.is_dir(): path /= 'index.html'
                return path.read_text(encoding='utf-8')
            result = verify_live_publication('https://www.tallerlab.com.ar', expected, fetch, now)
            self.assertEqual(result['routes'], 53)
            path = root / summary['routes'][-1].strip('/') / 'index.html'
            html = path.read_text(encoding='utf-8')
            path.write_text('<html><h1>No encontrado</h1></html>', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Canonical'):
                verify_live_publication('https://www.tallerlab.com.ar', expected, fetch, now)
            path.write_text(html.replace('data-publication="'+expected, 'data-publication="2000-01-01'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'publicaciones distintas'):
                verify_live_publication('https://www.tallerlab.com.ar', expected, fetch, now)
            path.unlink()
            with self.assertRaises(OSError):
                verify_live_publication('https://www.tallerlab.com.ar', expected, fetch, now)
