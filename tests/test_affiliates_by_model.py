import unittest

from tallerlab_data.affiliates_by_model import _tools, build_files


class AffiliateCatalogSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table, cls.review = build_files()

    def test_catalog_offers_cover_exact_model_records(self):
        expected = {
            "bosch-gbh-220": "https://meli.la/2cRLSJx",
            "bosch-gbh-2-26-dre": "https://meli.la/16mozwd",
            "bosch-gbh-180-li": "https://meli.la/29WzeN7",
            "bosch-gsb-550-re": "https://meli.la/18iubWD",
            "karcher-k3-black-edition": "https://meli.la/1LYmDeG",
            "karcher-k4-power-control": "https://meli.la/149NjG2",
            "karcher-k4-standard": "https://meli.la/2SvkJCm",
            "karcher-k5-power-control": "https://meli.la/1wCKV4R",
            "bosch-ghp-180": "https://meli.la/1wNMwSL",
            "bosch-ghp-200": "https://meli.la/1zrcYor",
            "stihl-re-80-x": "https://meli.la/1wzSW2u",
            "gamma-inverter-2kw": "https://meli.la/1B4sjDN",
            "bta-25-litros": "https://meli.la/14USeGB",
        }
        for slug, url in expected.items():
            with self.subTest(slug=slug):
                self.assertEqual(self.table["models"][slug]["url"], url)
                self.assertIn("catalog_snapshot.commercial_offers", self.table["models"][slug]["sources"])

    def test_wrong_karcher_k2_mpn_is_not_attached_to_catalog_tool(self):
        entry = self.table["models"].get("karcher-k2-basic")
        if entry:
            self.assertNotEqual(entry["url"], "https://meli.la/1LYmDeG")
            self.assertNotIn("1.994-322.0", entry["mpn"])

    def test_model_name_without_exact_mpn_stays_in_review(self):
        self.assertEqual(self.table["models"]["einhell-te-cd-18-40"]["url"], "https://meli.la/2EINHTECD")
        self.assertTrue(any(row.get("tool_slug") == "einhell-te-cd-18-40"
                            and row.get("candidato") == "https://meli.la/2A1rX5b"
                            for row in self.review))

    def test_table_is_covered_only_by_unambiguous_or_curated_matches(self):
        accepted = {tool["slug"] for tool in _tools()}
        self.assertEqual(len(accepted), 100)
        self.assertEqual(len(self.table["models"]), 100)
        self.assertLessEqual(set(self.table["models"]), accepted)


if __name__ == "__main__":
    unittest.main()
