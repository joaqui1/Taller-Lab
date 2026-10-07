"""Regresiones de la auditoría pública del 2026-10-06."""
import json
import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class RegistrosDePrueba(unittest.TestCase):
    def test_snapshot_publicado_sin_candidatos_de_prueba(self):
        from tallerlab_data.storage import is_test_candidate
        data = json.loads((ROOT / 'tallerlab_data' / 'data' / 'catalog_snapshot.json').read_text(encoding='utf-8'))
        self.assertFalse([c['model_name'] for c in data['candidates'] if is_test_candidate(c)])

    def test_detector_de_registros_de_prueba(self):
        from tallerlab_data.storage import is_test_candidate
        for c in ({'brand': 'Modelo Incompleto', 'model_name': 'Test100'}, {'brand': 'Test', 'model_name': 'Test'},
                  {'brand': 'X', 'model_name': 'y', 'candidate_code': 'TEST-Q'}):
            self.assertTrue(is_test_candidate(c), c)
        self.assertFalse(is_test_candidate({'brand': 'Black+Decker', 'model_name': 'BES603 Caladora', 'candidate_code': 'BLACK-DECKER-BES603-B2'}))

    def test_metodologia_no_muestra_pruebas_aunque_esten_en_la_base(self):
        import tempfile
        import tallerlab_data.storage as storage
        from tallerlab_data.views import render_data_methodology_page
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / 'catalog.db'
            with patch.object(storage, 'DB_PATH', db):
                storage.add_candidate('SIN-CODIGO', 'Modelo Incompleto', 'Test100', 'compresores', {}, 'prueba', status='excluido')
                html = render_data_methodology_page()
                self.assertNotIn('Test100', html)
                self.assertIn('BES603', html)
                self.assertTrue(any(c['model_name'] == 'Test100' for c in storage.list_candidates(include_test=True)))


class Contacto(unittest.TestCase):
    def test_no_promete_un_buzon_deshabilitado(self):
        from paginas_institucionales import contact_markdown
        texto = contact_markdown(email='', mailbox=False)
        self.assertNotIn('/comunidad/contacto/', texto)
        self.assertNotIn('Recibimos el correo', texto)
        self.assertIn('no hay un canal privado habilitado', texto)

    def test_muestra_correo_editorial_si_esta_configurado(self):
        from paginas_institucionales import contact_markdown, contact_email
        self.assertIn('mailto:editor@example.com', contact_markdown(email='editor@example.com', mailbox=False))
        with patch.dict(os.environ, {'CONTACT_EMAIL': 'editor@example.com'}):
            self.assertEqual(contact_email(), 'editor@example.com')
        with patch.dict(os.environ, {'CONTACT_EMAIL': 'no es un correo'}):
            self.assertNotEqual(contact_email(), 'no es un correo')

    def test_buzon_solo_si_puede_guardar(self):
        from paginas_institucionales import contact_markdown
        self.assertIn('/comunidad/contacto/', contact_markdown(email='', mailbox=True))


class IngcoSinDestacado(unittest.TestCase):
    def test_guia_inalambricos_sin_nota_de_compra_ingco(self):
        from recursos_compra import BUYING_NOTES
        self.assertNotIn('/taladros/inalambricos/', BUYING_NOTES)

    def test_fuente_ingco_no_se_presenta_como_oficial(self):
        data = json.loads((ROOT / 'tallerlab_data' / 'data' / 'catalog_snapshot.json').read_text(encoding='utf-8'))
        tool = next(t for t in data['tools'] if t['slug'] == 'ingco-cidli20668-4')
        texto = json.dumps(tool, ensure_ascii=False)
        self.assertNotIn('Ficha oficial', texto)
        self.assertNotIn('ficha del fabricante"', texto)
        self.assertNotIn('2.0 Ah', texto)
        self.assertIn('Ah sin confirmar', texto)


class IndexacionDeSeccionesCerradas(unittest.TestCase):
    def setUp(self):
        import servidor_local as site
        self.site = site

    def locs(self):
        return re.findall(r'<loc>https?://[^/<]+(/[^<]*)</loc>', self.site.render_sitemap())

    def test_relevamiento_cerrado_fuera_del_sitemap_y_noindex(self):
        with patch.object(self.site, 'relevamiento_abierto', return_value=False):
            locs = self.locs()
            self.assertFalse([p for p in locs if p.startswith('/relevamiento-2027/')])
            for path in self.site.RELEVAMIENTO_PATHS:
                self.assertIn('noindex', self.site.canonical_tag(path))
        with patch.object(self.site, 'relevamiento_abierto', return_value=True):
            self.assertIn('/relevamiento-2027/', self.locs())
            self.assertNotIn('noindex', self.site.canonical_tag('/relevamiento-2027/'))

    def test_portada_comunidad_fuera_del_sitemap_si_no_se_confirma_indexable(self):
        from comunidad import components as cc, storage as db
        with patch.object(db, 'overview_or_none', return_value=None):
            self.assertEqual(cc.community_sitemap_excluded(), {'/comunidad/'})
        with patch.object(cc, 'community_sitemap_lastmod', side_effect=RuntimeError('caída')):
            self.assertNotIn('/comunidad/', self.locs())

    def test_menu_sin_comunidad_mientras_esta_cerrada(self):
        import contenido_publico
        link = contenido_publico.COMMUNITY_NAV_LINK
        with patch.object(contenido_publico, 'community_open', return_value=False):
            html = self.site.render_editorial_page('contacto')
            self.assertNotIn(link, html)
            self.assertIn('<a href="/comunidad/">Comunidad</a>', html)  # sigue en el pie
        with patch.object(contenido_publico, 'community_open', return_value=True):
            self.assertIn(link, self.site.render_editorial_page('contacto'))


class PerfilDeAutor(unittest.TestCase):
    def test_pagina_de_autor_declara_un_solo_person(self):
        import servidor_local as site
        html = site.render_editorial_page('equipo')
        bloques = [json.loads(m) for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
        perfiles = [b for b in bloques if b.get('@type') == 'ProfilePage']
        self.assertEqual(len(perfiles), 1)
        self.assertEqual(perfiles[0]['mainEntity']['@type'], 'Person')
        self.assertEqual(perfiles[0]['mainEntity']['name'], site.AUTHOR_NAME)
        self.assertTrue(perfiles[0]['mainEntity']['knowsAbout'])


if __name__ == '__main__':
    unittest.main()
