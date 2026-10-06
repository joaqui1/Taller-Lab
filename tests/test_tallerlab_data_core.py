"""
Suite unitaria hermética para el núcleo de TallerLab Data.
Se ejecuta de forma aislada y no muta la base de datos de producción.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for folder in ['.qa-deps', '.consultor-seo-deps', '.publication-qa-deps', '.integration-qa-deps', '.seo-qa-deps', '.taladros-qa-deps']:
    sys.path.insert(0, str(ROOT / folder))

from tallerlab_data.pipeline import (
    normalize_unit_value,
    validate_candidate,
    check_grid_compatibility,
    HP_TO_W,
    BAR_TO_PSI,
)
from tallerlab_data.comparator import analyze_spec_comparability, compare_tools
from tallerlab_data.storage import get_tool, list_tools, TOOL_SLUGS_ALIAS_MAP
from tallerlab_data.guide_links import GUIDE_TOOL_MAPPINGS
from tallerlab_data.research_study import generate_research_study_metrics, get_research_study_data


class TestTallerLabDataCore(unittest.TestCase):

    def test_normalizer_composite_and_locale_units(self):
        """Verifica que el normalizador no sea engañado por dobles unidades o locales hispanos."""
        cases = [
            ("8 bar (115 PSI)", "presion", 8.0, "bar"),
            ("1.750 W", "potencia", 1750.0, "W"),
            ("2 kW", "potencia", 2000.0, "W"),
            ("2,5 HP / 1750 W", "potencia", 1750.0, "W"),
            ("1500g", "peso", 1.5, "kg"),
            ("2.5 HP", "potencia", round(2.5 * HP_TO_W, 1), "W"),
            ("115 PSI", "presion", round(115.0 / BAR_TO_PSI, 2), "bar"),
            ("360 l/h", "caudal", 6.0, "L/min"),
        ]
        for raw, unit_type, expected_val, expected_unit in cases:
            val, unit = normalize_unit_value(raw, unit_type)
            self.assertEqual(unit, expected_unit, f"Unidad errónea para '{raw}': esperado {expected_unit}, obtenido {unit}")
            self.assertAlmostEqual(val, expected_val, places=1, msg=f"Valor erróneo para '{raw}': esperado {expected_val}, obtenido {val}")
        self.assertEqual(normalize_unit_value('0–2.800 rpm', 'rpm'), (None, 'rpm'))

    def test_grid_compatibility_validation(self):
        """Verifica que el validador regional rechace redes extranjeras fijas y admita 220V/50Hz, baterías y combustión."""
        # Redes incompatibles con Argentina
        for incompatible in ["220 V / 60 Hz", "110 V / 50 Hz", "110 V / 60 Hz", "127 V / 60 Hz"]:
            is_compat, err = check_grid_compatibility(incompatible)
            self.assertFalse(is_compat, f"Debería rechazar '{incompatible}'")
            self.assertIsNotNone(err)

        # Redes y alimentaciones válidas
        for compatible in ["220 V / 50 Hz", "220-240 V / 50 Hz", "220 V / 50-60 Hz", "18 V CC", "20 V MAX Li-Ion", "Nafta 4 tiempos"]:
            is_compat, err = check_grid_compatibility(compatible)
            self.assertTrue(is_compat, f"Debería admitir '{compatible}': {err}")
            self.assertIsNone(err)

    def test_candidate_validator_payload(self):
        """Verifica la validación formal de candidatos a ingreso."""
        base = {
            "brand": "Prueba",
            "commercial_name": "Herramienta Test",
            "mpn": "TEST-123",
            "category": "taladros",
            "primary_sources": [{"url": "https://example.com/manual.pdf"}],
            "specs": {"potencia": "800 W", "peso": "2 kg"}
        }
        # Con red incompatible
        valido, errores = validate_candidate({**base, "voltage": "110 V / 60 Hz"})
        self.assertFalse(valido)
        self.assertTrue(any("incompatible" in e for e in errores))

        # Con red compatible y specs suficientes
        valido, errores = validate_candidate({**base, "voltage": "220 V / 50 Hz"})
        self.assertFalse(valido)
        self.assertTrue(any("procedencia" in error for error in errores))

    def test_comparability_strict_rules(self):
        """Verifica el análisis de comparabilidad física y dimensional."""
        def mk_spec(name, condition, unit, val, status="declarado"):
            return {
                "name": name,
                "condition": condition,
                "normalized_unit": unit,
                "normalized_value": val,
                "status": status,
            }

        # 1. Caudales a presiones dispares (4 bar vs 7 bar)
        diff_press = analyze_spec_comparability(
            "caudal",
            [mk_spec("Caudal", "Caudal de salida a 4 bar", "L/min", 135),
             mk_spec("Caudal", "Caudal de salida a 7 bar", "L/min", 98)]
        )
        self.assertFalse(diff_press["is_comparable"])
        self.assertEqual(diff_press["status_badge"], "incomparable")

        # 2. Pesos con bases distintas (Balanza vs Sin batería)
        diff_weight = analyze_spec_comparability(
            "peso",
            [mk_spec("Peso", "Balanza", "kg", 1.8),
             mk_spec("Peso", "Sin batería", "kg", 1.1)]
        )
        self.assertFalse(diff_weight["is_comparable"])

        # 3. Magnitudes físicas dispares (kVA vs kW)
        diff_units = analyze_spec_comparability(
            "potencia",
            [mk_spec("Potencia", "Nominal", "kVA", 2.2),
             mk_spec("Potencia", "Nominal", "kW", 2.0)]
        )
        self.assertFalse(diff_units["is_comparable"])

        # 4. Estado contradictorio
        contradictory = analyze_spec_comparability(
            "potencia",
            [mk_spec("Potencia", "Nominal", "W", 1750, status="contradictorio"),
             mk_spec("Potencia", "Nominal", "W", 1500)]
        )
        self.assertFalse(contradictory["is_comparable"])
        self.assertEqual(contradictory["status_badge"], "contradictorio")

        # 5. Modelo faltante en comparación múltiple
        missing_spec = analyze_spec_comparability(
            "peso",
            [mk_spec("Peso", "Sin batería", "kg", 1.1),
             mk_spec("Peso", "Sin batería", "kg", 1.2),
             None]
        )
        self.assertFalse(missing_spec["is_comparable"])
        self.assertEqual(missing_spec["status_badge"], "incompleto")

    def test_cross_category_comparison_warning(self):
        """Verifica que comparar herramientas de categorías diferentes dispare advertencia crítica."""
        res = compare_tools(["bosch-gsb-18v-50", "gamma-g2802ar"])
        self.assertTrue(res.category_mismatch)
        self.assertIn("distintas categorías", res.category_warning)

    def test_strict_slug_resolution(self):
        """Verifica que get_tool resuelva con coincidencia exacta y devuelva None ante slugs vacíos o inexistentes."""
        self.assertIsNone(get_tool(""))
        self.assertIsNone(get_tool("   "))
        self.assertIsNone(get_tool("no-existe-en-db-12345"))
        self.assertIsNone(get_tool("bosch-gsb"))  # No debe resolver por coincidencia parcial

        tool = get_tool("bosch-gsb-18v-50")
        self.assertIsNotNone(tool)
        self.assertEqual(tool.slug, "bosch-gsb-18v-50")

    def test_all_guide_mappings_strictly_resolve(self):
        """Verifica que el 100% de los mapeos de guías resuelvan a herramientas existentes sin prefijos laxos."""
        unresolved = []
        prefix_mismatches = []
        for guide_url, slugs in GUIDE_TOOL_MAPPINGS.items():
            for slug in slugs:
                tool = get_tool(slug)
                if tool is None:
                    unresolved.append((guide_url, slug))
                elif tool.slug != slug:
                    prefix_mismatches.append((guide_url, slug, tool.slug))

        self.assertEqual(len(unresolved), 0, f"Mapeos no resueltos: {unresolved}")
        self.assertEqual(len(prefix_mismatches), 0, f"Mapeos con discrepancia de slug: {prefix_mismatches}")

    def test_research_study_factual_calculations(self):
        """Verifica que las métricas del estudio documental provengan de cálculos reales sin números mágicos."""
        metrics = generate_research_study_metrics()
        self.assertEqual(metrics["sample_size"], 100)
        self.assertEqual(metrics["compresores_total"], 25)
        self.assertEqual(metrics["hidro_total"], 25)
        self.assertEqual(metrics["compresores_sin_fad_count"], len(metrics["compresores_sin_fad_slugs"]))
        self.assertEqual(metrics["hidro_solo_max_count"], len(metrics["hidro_solo_max_slugs"]))
        self.assertEqual(metrics["contradictions_count"], len(metrics["contradictions_slugs"]))

        # Verificar consistencia matemática de porcentajes
        self.assertAlmostEqual(metrics["pct_compresores_solo_teorico"], round(metrics["compresores_sin_fad_count"] / metrics["compresores_total"] * 100, 1))
        self.assertAlmostEqual(metrics["pct_hidro_solo_max"], round(metrics["hidro_solo_max_count"] / metrics["hidro_total"] * 100, 1))
        self.assertAlmostEqual(metrics["pct_contradictions"], round(3 / 100 * 100, 1))


if __name__ == "__main__":
    unittest.main()
