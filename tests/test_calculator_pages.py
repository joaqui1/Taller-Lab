import json
import re
import shutil
import subprocess
import unittest

from app import app
from servidor_local import ALL_ARTICLES, CALCULATOR_PAGES, render_article_page, render_calculator_embed, render_calculator_page, render_sitemap


class CalculatorPagesTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_pages_share_guide_resource_config_and_runtime(self):
        for slug, data in CALCULATOR_PAGES.items():
            with self.subTest(slug=slug):
                guide = render_article_page(next(article for article in ALL_ARTICLES if article["url"] == data["guide"]))
                page = render_calculator_page(f"/calculadoras/{slug}/")
                embed = render_calculator_embed(slug)
                configs = [
                    re.search(r'<script type="application/json" class="resource-config">(.*?)</script>', html, re.S).group(1)
                    for html in (guide, page, embed)
                ]
                self.assertEqual([json.loads(config) for config in configs].count(json.loads(configs[0])), 3)
                for html in (guide, page, embed):
                    self.assertIn('/assets/decision-tools.js?v=5', html)
                self.assertIn("Cómo calcula", page)
                self.assertIn('applicationCategory', page)
                self.assertIn('isAccessibleForFree', page)
                self.assertIn('<meta name="robots" content="noindex,follow">', embed)

    def test_embed_headers_and_sitemap_exclusion(self):
        for slug in CALCULATOR_PAGES:
            response = self.client.get(f"/embed/calculadoras/{slug}/", headers={"Referer": "https://ejemplo.com/articulo"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("X-Robots-Tag"), "noindex, follow")
            self.assertEqual(response.headers.get("Content-Security-Policy"), "frame-ancestors *")
        sitemap = render_sitemap()
        for slug in CALCULATOR_PAGES:
            self.assertNotIn(f"/embed/calculadoras/{slug}/", sitemap)

    def test_indexable_calculator_routes(self):
        routes = ["/calculadoras/"] + [f"/calculadoras/{slug}/" for slug in CALCULATOR_PAGES]
        sitemap = render_sitemap()
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)
                self.assertIn(route, sitemap)

    @unittest.skipUnless(shutil.which("node"), "Node.js no está disponible para probar los cálculos")
    def test_three_input_sets_run_through_shared_decision_function(self):
        script = r'''const {calculate}=require('./assets/decision-tools.js');
const cases=[
 ['house',{},[{name:'heladera',run:300,start:600},{name:'luces',run:100,start:100}]],
 ['air',{supply:98,supplyPressure:7,demand:100,demandPressure:7},[]],
 ['cost',{priceA:1000,shippingA:50,extrasA:25,priceB:900,shippingB:100,extrasB:0},[]],
 ['water',{flow:5.5,minutes:10},[]],
 ['air',{supply:140,supplyPressure:6.3,demand:142,demandPressure:6.3},[]],
 ['cost',{priceA:100000,shippingA:0,extrasA:5000,priceB:99000,shippingB:1500,extrasB:1000},[]],
 ['water',{flow:7.5,minutes:22},[]],
 ['house',{},[{name:'bomba',run:700,start:1200}]],
 ['house',{},[{name:'heladera',run:300,start:750},{name:'bomba',run:500,start:1300},{name:'luces',run:100,start:100}]],
 ['air',{supply:98,supplyPressure:7,demand:98,demandPressure:7},[]],
 ['cost',{priceA:500000,shippingA:20000,extrasA:30000,priceB:510000,shippingB:0,extrasB:0},[]],
 ['water',{flow:6,minutes:5},[]]
]; console.log(JSON.stringify(cases.map(([kind,values,loads])=>calculate(kind,values,loads))));'''
        node = shutil.which("node")
        result = subprocess.run([node, "-e", script], check=True, capture_output=True, text=True)
        values = json.loads(result.stdout)
        self.assertEqual(len(values), 12)
        self.assertIn("Marcha: 400 W", values[0]["title"] + " " + values[0]["body"])
        self.assertIn("Total A: $1.075", values[2]["title"])
        self.assertIn("55 litros teóricos", values[3]["title"])


if __name__ == "__main__":
    unittest.main()
