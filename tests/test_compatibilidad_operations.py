import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from compatibilidad.operations import compare_monitor_states, format_alert


AS_OF = datetime(2026, 10, 26, 12, 0, tzinfo=timezone.utc)


def state(**updates):
    result = {
        'observed_at': '2026-10-26T09:00:00-03:00',
        'status': 'ok',
        'products': [
            {'id': 'TOOL-BOSCH-GWS-18V-10', 'brand': 'Bosch', 'model_name': 'GWS 18V-10',
             'mpn': '06019J40E0', 'status': 'publicado'},
        ],
        'published_products': 18,
        'relation_ids': ['REL-1'],
        'documented_relations': 40,
        'source_failures': [],
        'max_evidence_age_days': 10,
        'oldest_evidence_date': '2026-10-16',
    }
    result.update(updates)
    return result


class CompatibilityOperationsAlertsTests(unittest.TestCase):
    def test_no_changes_produce_no_notice(self):
        previous = state()
        current = state(observed_at='2026-10-27T09:00:00-03:00')

        self.assertEqual(compare_monitor_states(previous, current, as_of=AS_OF), [])

    def test_suspended_product_notice_has_name_reason_and_date(self):
        previous = state()
        current = state(
            status='degradado',
            products=[{'id': 'TOOL-BOSCH-GWS-18V-10', 'brand': 'Bosch', 'model_name': 'GWS 18V-10',
                       'mpn': '06019J40E0', 'status': 'pendiente'}],
            published_products=0,
            relation_ids=[],
            documented_relations=0,
            source_failures=[{'source_id': 'TOOL-BOSCH-GWS-18V-10', 'status': 'inaccesible'}],
        )

        events = compare_monitor_states(previous, current, as_of=AS_OF)
        notice = format_alert(events, current)

        self.assertIn('Producto suspendido: Bosch GWS 18V-10 (MPN 06019J40E0)', notice)
        self.assertIn('Motivo: falló la fuente oficial asociada (inaccesible)', notice)
        self.assertIn('Fecha: 26/10/2026', notice)

    def test_below_baseline_alerts_even_when_previous_snapshot_matches(self):
        previous = state(published_products=17, documented_relations=35)
        current = state(published_products=17, documented_relations=35)

        events = compare_monitor_states(previous, current, as_of=AS_OF)
        notice = format_alert(events, current)

        self.assertEqual(
            {event['type'] for event in events},
            {'products_below_baseline', 'relations_below_baseline'},
        )
        self.assertIn('17 (mínimo 18)', notice)
        self.assertIn('35 (mínimo 40)', notice)

    def test_baseline_minimums_can_be_configured(self):
        with patch.dict('os.environ', {
            'COMPATIBILITY_EXPECTED_PUBLISHED_PRODUCTS': '17',
            'COMPATIBILITY_EXPECTED_DOCUMENTED_RELATIONS': '35',
        }):
            events = compare_monitor_states(
                state(published_products=17, documented_relations=35),
                state(published_products=17, documented_relations=35),
                as_of=AS_OF,
            )

        self.assertEqual(events, [])

    def test_evidence_age_of_21_days_produces_notice(self):
        previous = state(max_evidence_age_days=20, oldest_evidence_date='2026-10-05')
        current = state(max_evidence_age_days=21, oldest_evidence_date='2026-10-05')

        events = compare_monitor_states(previous, current, as_of=AS_OF)
        notice = format_alert(events, current)

        self.assertTrue(any(event['type'] == 'evidence_age' for event in events))
        self.assertIn('Evidencia más antigua: 21 días', notice)
        self.assertIn('revisada el 2026-10-05', notice)
        self.assertIn('Fecha del aviso: 26/10/2026', notice)


if __name__ == '__main__':
    unittest.main()
