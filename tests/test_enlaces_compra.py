"""Las acciones de compra requieren afiliación; la documentación sigue enlazada."""
import unittest

from bs4 import BeautifulSoup
from contenido_publico import es_enlace_afiliado, limpiar_contenido_publico


class PurchaseLinkTests(unittest.TestCase):
    def test_purchase_buttons_removed_without_losing_sources_or_affiliates(self):
        html = '''<div class="offer-actions">
          <a class="offer-button" href="https://fabricante.example/producto">Ver ficha</a>
          <a class='buying-link' href='https://listado.mercadolibre.com.ar/taladro'>Buscar</a>
          <a class="btn-mercado-libre" href="https://www.mercadolibre.com.ar/p/MLA123">Comprar</a>
          <a class="offer-button" href="https://meli.la/abc123" rel="nofollow sponsored">Comprar afiliado</a>
          <a class="offer-guide" href="/taladros/">Leer guía</a>
          </div><section id="fuentes-consultadas">
          <a href="https://fabricante.example/producto">Fuente oficial</a>
          <a href="https://fabricante.example/manual.pdf">Manual</a>
          </section>'''
        soup = BeautifulSoup(limpiar_contenido_publico(html), 'html.parser')
        self.assertEqual([a['href'] for a in soup.select('.offer-actions a')],
                         ['https://meli.la/abc123', '/taladros/'])
        self.assertEqual(len(soup.select('#fuentes-consultadas a')), 2)
        self.assertEqual(soup.select_one('[href="https://meli.la/abc123"]')['rel'], ['nofollow', 'sponsored'])

    def test_affiliate_host_is_exact_not_a_label_or_tracking_attribute(self):
        self.assertTrue(es_enlace_afiliado('https://meli.la/abc123'))
        for url in ('https://meli.la.example/abc123', 'https://meli.la@other.example/abc123',
                    'https://www.mercadolibre.com.ar/producto', 'https://meli.la/',
                    'http://meli.la/abc123', 'https://fabricante.example/'):
            with self.subTest(url=url):
                self.assertFalse(es_enlace_afiliado(url))
                html = f'<a class="offer-button" href="{url}" rel="sponsored" data-affiliate-placement="choice">Comprar</a>'
                self.assertNotIn('<a ', limpiar_contenido_publico(html))

    def test_internal_buttons_and_empty_action_containers(self):
        html = '<a class="buying-link" href="/taladros/">Ver guía</a>'
        self.assertIn(html, limpiar_contenido_publico(html))
        html = '<div class="offer-actions"><a class="offer-button" href="https://marca.example/">Comprar</a></div>'
        self.assertEqual(limpiar_contenido_publico(html), '')

    def test_all_published_guides_only_offer_affiliate_purchase_actions(self):
        import servidor_local as site
        commercial_classes = {'offer-button', 'buying-link', 'btn-mercado-libre', 'catalog-link'}
        affiliates = 0
        for article in site.ALL_ARTICLES:
            soup = BeautifulSoup(site.render_article_page(article), 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith(('https://', 'http://', '//')):
                    continue
                if commercial_classes.intersection(link.get('class', [])):
                    self.assertTrue(es_enlace_afiliado(href), (article['url'], href))
                    affiliates += 1
        self.assertGreater(affiliates, 100)
        self.assertTrue(all(es_enlace_afiliado(url) for url in site.AFFILIATE_URLS))

    def test_documented_models_remain_without_purchase_buttons(self):
        import servidor_local as site
        url = 'https://www.einhell.com.ar/p/4010451-te-ac-270-50-silent/'
        html = site.render_affiliate_shelf('compresores',
                  [('compresores', ('Einhell TE-AC 270/50 Silent', 'Uso documentado', url, '/compresores/50-litros/'))])
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIn('TE-AC 270/50 Silent', soup.get_text())
        self.assertIsNone(soup.select_one('.offer-button'))
        self.assertEqual(soup.select_one('.offer-guide')['href'], '/compresores/50-litros/')
        self.assertNotIn('listado.mercadolibre.com.ar', site.render_50l_models())
