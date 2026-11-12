"""Catálogo documental sintético con vigencia relativa a la ejecución de pruebas."""
from datetime import datetime, timezone
from unittest.mock import patch

from compatibilidad import catalog


def use_fresh_compatibility_catalog(test_case):
    """Renueva solo la revisión de la fixture y restaura el catálogo al terminar."""
    baseline = catalog.baseline_state

    def fresh_baseline():
        state = baseline()
        today = datetime.now(timezone.utc).date().isoformat()
        for evidence in state['evidences']:
            evidence['date_reviewed'] = today
        return state

    test_case.addCleanup(catalog.apply_state, baseline())
    patcher = patch.object(catalog, 'baseline_state', side_effect=fresh_baseline)
    test_case.addCleanup(patcher.stop)
    patcher.start()
    catalog.apply_state(catalog.baseline_state())
