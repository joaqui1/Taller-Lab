"""Regression checks for evidence exclusions and deployable snapshots."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tallerlab_data import storage
from tallerlab_data.documentary import export_snapshot
from tallerlab_data.pipeline import normalize_unit_value, resolve_candidate
from tallerlab_data.comparator import analyze_spec_comparability


class DocumentaryChecks(unittest.TestCase):
    def spec(self, condition, **extra):
        return dict(name='Caudal', condition=condition, normalized_unit='L/min',
                    normalized_value=100, status='declarado', **extra)

    def test_ambiguous_scalars_remain_original(self):
        for raw, key in [('20 a 130 bar', 'presion'), ('100–200 L/min', 'caudal'), ('50/28 Nm', 'torque')]:
            self.assertIsNone(normalize_unit_value(raw, key)[0])

    def test_semantics_and_evidence_exclusions(self):
        pairs = [
            (self.spec('No documentado'), self.spec('Aspiración')),
            (self.spec('Salida a 7 bar', documentary_status='sin_respaldo'), self.spec('Salida a 7 bar')),
            (self.spec('Salida a 7 bar', condition_status='sin_respaldo'), self.spec('Salida a 7 bar')),
            (self.spec('Salida máxima a 7 bar'), self.spec('Salida nominal a 7 bar')),
        ]
        for pair in pairs:
            self.assertFalse(analyze_spec_comparability('caudal', list(pair))['is_comparable'])
        self.assertTrue(analyze_spec_comparability('caudal', [self.spec('Salida a 7 bar'), self.spec('Salida a 101.52639 psi')])['is_comparable'])

    def test_public_version_is_reproducible(self):
        payload = export_snapshot()
        version = payload.pop('version')
        payload.pop('candidates')
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), version)

    def test_cold_bootstrap_preserves_closed_catalog(self):
        snapshot = json.loads((storage.DATA_DIR / 'catalog_snapshot.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as folder:
            target = Path(folder) / 'cold.db'
            with patch.object(storage, 'DB_PATH', target):
                self.assertEqual(len(storage.list_tools()), len(snapshot['tools']))
                self.assertEqual(len(storage.list_corrections()), len(snapshot['corrections']))
                self.assertFalse(any(c['status'] in {'pendiente', 'validado_para_revision'} for c in storage.list_candidates()))
                self.assertTrue(all(s.documentary_status for t in storage.list_tools() for s in t.specs.values()))

    def test_candidate_exclusion_has_terminal_decision(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as folder:
            with patch.object(storage, 'DB_PATH', Path(folder) / 'decision.db'), patch('tallerlab_data.documentary.write_snapshot', return_value='isolated'):
                storage.add_candidate('TEST-CODE', 'Marca', 'Modelo', 'taladros', {}, 'Sin identidad documental')
                decision = resolve_candidate('TEST-CODE', 'excluir', 'Excluido: documento sin código de producto')
                self.assertEqual(decision['status'], 'excluido')
                self.assertFalse(decision['accepted'])
                self.assertEqual(next(c['status'] for c in storage.list_candidates(include_test=True) if c['candidate_code'] == 'TEST-CODE'), 'excluido')


if __name__ == '__main__':
    unittest.main()
