import re
import unittest

from tallerlab_data.research_study import (
    get_research_study_data,
    has_epta_energy,
    has_output_flow,
    has_work_pressure,
)
from tallerlab_data.selection import family
from tallerlab_data.storage import list_tools
from tallerlab_data.views import render_research_study_page


class ResearchStudyDetailsTests(unittest.TestCase):
    def test_listed_models_with_data_match_each_table_numerator(self):
        page = render_research_study_page()
        metrics = get_research_study_data()["metrics"]
        all_tools = list_tools()
        groups = {
            "output_tank": ([t for t in all_tools if t.category == "compresores" and family(t) == "compresor-tanque"], has_output_flow,
                            metrics["compresores_por_familia"]["compresor-tanque"]["output_flow_count"]),
            "output_inflator": ([t for t in all_tools if t.category == "compresores" and family(t) == "inflador"], has_output_flow,
                                 metrics["compresores_por_familia"]["inflador"]["output_flow_count"]),
            "output_airbrush": ([t for t in all_tools if t.category == "compresores" and family(t) == "aerografo"], has_output_flow,
                                metrics["compresores_por_familia"]["aerografo"]["output_flow_count"]),
            "work_pressure": ([t for t in all_tools if t.category == "hidrolavadoras"], has_work_pressure,
                              metrics["hidro_trabajo_separada_count"]),
            "epta_energy": ([t for t in all_tools if family(t) == "rotomartillo"], has_epta_energy,
                            metrics["rotary_hammers_epta_count"]),
            "contradictions": (all_tools, lambda t: bool(t.contradictions), metrics["contradictions_count"]),
        }

        for group, (tools, predicate, numerator) in groups.items():
            with self.subTest(group=group):
                self.assertEqual(sum(bool(predicate(tool)) for tool in tools), numerator)
                details = re.search(
                    rf'<details data-group="{group}"[^>]*>(.*?)</details>', page, re.DOTALL
                )
                self.assertIsNotNone(details, f"No se encontró el desplegable {group}")
                listed_with_data = len(re.findall(r'data-status="dato"', details.group(1)))
                self.assertEqual(listed_with_data, numerator)

    def test_karcher_pressure_range_is_disclosed_as_non_comparable(self):
        page = render_research_study_page()
        self.assertIn("rango declarado, no comparable como valor único", page)
        self.assertIn("20 a 130 bar", page)
        pressure_details = re.search(
            r'<details data-group="work_pressure"[^>]*>(.*?)</details>', page, re.DOTALL
        )
        self.assertIsNotNone(pressure_details)
        karcher_item = re.search(r'<li[^>]*>.*?/herramientas/karcher-k4-power-control/.*?</li>', pressure_details.group(1))
        self.assertIsNotNone(karcher_item)
        self.assertIn('data-status="sin-dato"', karcher_item.group(0))


if __name__ == "__main__":
    unittest.main()
