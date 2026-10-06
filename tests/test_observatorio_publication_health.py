import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone

from observatorio.publication_health import publication_warning


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
