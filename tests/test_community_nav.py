import re
import unittest
from unittest.mock import patch

from servidor_local import HTML_SHELL


class CommunityNavTests(unittest.TestCase):
    def render_shell(self):
        return HTML_SHELL.format(
            PAGE_TITLE="Prueba | TallerLab",
            CANONICAL_TAG="",
            PAGE_DESC="",
            PORT=8080,
            CONTENT="",
            LOGO_SRC="/assets/logo_cropped.webp",
        )

    def menus(self, html):
        mobile = re.search(r'<nav aria-label="Menú de navegación">(.*?)</nav>', html, re.S).group(1)
        desktop = re.search(r'<nav class="nav-links">(.*?)</nav>', html, re.S).group(1)
        return mobile, desktop

    def test_community_closed_is_absent_from_both_menus(self):
        with patch("comunidad.storage.enabled", return_value=False):
            html = self.render_shell()
        mobile, desktop = self.menus(html)
        self.assertNotIn("Comunidad", mobile)
        self.assertNotIn("Comunidad", desktop)
        self.assertNotIn('<a href="/comunidad/">Comunidad</a>', html.split("<footer>", 1)[1])

    def test_community_open_appears_between_prices_and_working_method(self):
        with patch("comunidad.storage.enabled", return_value=True):
            html = self.render_shell()
        mobile, desktop = self.menus(html)
        for menu in (mobile, desktop):
            with self.subTest(menu=menu):
                self.assertIn("Comunidad", menu)
                self.assertLess(menu.index("Precios"), menu.index("Comunidad"))
                self.assertLess(menu.index("Comunidad"), menu.index("Cómo trabajamos"))
        self.assertIn('<a href="/comunidad/">Comunidad</a>', html.split("<footer>", 1)[1])

    def test_community_status_error_is_treated_as_closed(self):
        with patch("comunidad.storage.enabled", side_effect=RuntimeError("estado no disponible")):
            html = self.render_shell()
        mobile, desktop = self.menus(html)
        self.assertNotIn("Comunidad", mobile)
        self.assertNotIn("Comunidad", desktop)


if __name__ == "__main__":
    unittest.main()
