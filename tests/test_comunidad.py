"""Pruebas de recorridos y permisos con almacenamiento temporal, sin datos reales."""
import os
import tempfile
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from app import app
from comunidad import storage as db

SLUG = 'bosch-gsb-18v-50'
URL = '/comunidad/modelos/' + SLUG + '/'


class CommunityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent.parent/'tmp')
        self.path = patch.object(db, 'DB_PATH', Path(self.tmp.name)/'community.db')
        self.path.start()
        self.env = patch.dict(os.environ, {'COMUNIDAD_HABILITADA': '1', 'COMUNIDAD_ADMIN_KEY': 'test-admin-key',
            'COMUNIDAD_DATABASE_URL': '', 'APP_ENV': 'test', 'VERCEL': '', 'VERCEL_ENV': ''})
        self.env.start()
        app.config.update(TESTING=True, SECRET_KEY='test-secret-for-community-only', SESSION_COOKIE_SECURE=False)
        self.client = app.test_client()
        self.other = app.test_client()
        self.admin = app.test_client()

    def tearDown(self):
        self.path.stop()
        self.env.stop()
        self.tmp.cleanup()

    def csrf(self, client, url=URL):
        client.get(url)
        with client.session_transaction() as sess:
            # Las páginas sin formulario ya no crean sesión; el token se genera al mostrar un formulario.
            return sess.setdefault('comunidad_csrf', 'token-de-prueba-' + uuid.uuid4().hex)

    def send(self, client=None, **data):
        client = client or self.client
        data['csrf_token'] = self.csrf(client)
        return client.post(URL+'participar', data=data)

    def post(self, kind='question', **extra):
        data = dict(action=kind, request_id=str(uuid.uuid4()), alias='Usuario',
            body='Mi consulta sobre el trabajo con esta herramienta.', consent='yes')
        if kind == 'question':
            data.update(title='¿Sirve para perforar metal todos los días?')
        if kind == 'review':
            data.update(usage='profesional', duration='mas_3', frequency='diario', task='Perforar metal',
                repurchase='depende')
        data.update(extra)
        return data

    def publish(self, post_id):
        db.moderate(post_id, 'published', 'Aporte pertinente al modelo')

    def scope(self):
        from comunidad.components import poll_scope
        from tallerlab_data.storage import get_tool_by_slug
        return poll_scope(get_tool_by_slug(SLUG))

    def test_public_routes_search_and_missing_model(self):
        for url in ['/comunidad/', '/comunidad/criterios/', '/comunidad/contacto/', URL]:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, url)
            # Portada y criterios son iguales para todos y se cachean en el CDN; el resto nunca.
            expected = 's-maxage=300' if url in ('/comunidad/', '/comunidad/criterios/') else 'no-store'
            self.assertIn(expected, res.headers['Cache-Control'], url)
        self.assertIn('no-store', self.client.get('/comunidad/?q=bosch').headers['Cache-Control'])
        self.assertIn('Bosch', self.client.get('/comunidad/?q=GSB+18V-50').text)
        self.assertEqual(self.client.get('/comunidad/modelos/no-existe/').status_code, 404)
        self.assertIn('noindex', self.client.get(URL).text)

    def test_pending_is_private_then_published_escaped_without_editorial_rewrites(self):
        data = self.post('review', body='<script>alert(1)</script> Mi experiencia con la herramienta durante tres años.')
        self.assertEqual(self.send(**data).status_code, 303)
        self.assertNotIn('alert(1)', self.other.get(URL).text)
        self.publish(data['request_id'])
        text = self.other.get(URL).text
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', text)
        self.assertNotIn('<script>alert(1)</script>', text)
        self.assertIn('Perforar metal', text)

    def test_idempotency_and_conflicting_replay(self):
        data = self.post()
        self.assertEqual(self.send(**data).status_code, 303)
        self.assertEqual(self.send(**data).status_code, 303)
        self.assertEqual(len(db.queue()), 1)
        data['body'] = 'Otro texto diferente que no debe reemplazar el primero.'
        self.assertEqual(self.send(**data).status_code, 400)

    def test_csrf_consent_honeypot_and_validation(self):
        self.assertEqual(self.client.post(URL+'participar', data=self.post()).status_code, 403)
        for extra in [dict(consent=''), dict(website='spam'), dict(body='corto'), dict(request_id='bad')]:
            self.assertEqual(self.send(**self.post(**extra)).status_code, 400)
        self.assertEqual(db.queue(), [])

    def test_helpful_ownership_and_deduplication(self):
        data = self.post()
        self.send(**data)
        self.publish(data['request_id'])
        action = dict(action='helpful', post_id=data['request_id'])
        self.assertEqual(self.send(**action).status_code, 400)
        self.assertEqual(self.send(self.other, **action).status_code, 303)
        self.assertEqual(self.send(self.other, **action).status_code, 303)
        self.assertEqual(db.visible_posts(SLUG)[0]['helpful'], 1)
        self.assertEqual(self.send(self.other, action='withdraw', post_id=data['request_id']).status_code, 400)

    def test_answer_acceptance_and_withdrawal_hides_children(self):
        q = self.post()
        self.send(**q)
        a = self.post('answer', parent_id=q['request_id'])
        self.assertEqual(self.send(self.other, **a).status_code, 400)
        self.publish(q['request_id'])
        self.assertEqual(self.send(self.other, **a).status_code, 303)
        self.publish(a['request_id'])
        choice = dict(action='accept', post_id=q['request_id'], answer_id=a['request_id'])
        self.assertEqual(self.send(self.other, **choice).status_code, 400)
        self.assertEqual(self.send(**choice).status_code, 303)
        self.assertTrue(any(p['accepted'] for p in db.visible_posts(SLUG)))
        with patch.dict(os.environ, {'COMUNIDAD_HABILITADA': '0'}):
            self.assertEqual(self.send(action='withdraw', post_id=q['request_id']).status_code, 303)
        self.assertEqual(db.visible_posts(SLUG), [])
        with self.assertRaises(ValueError):
            self.publish(q['request_id'])

    def test_poll_replaces_choice_and_counts_distinct_browsers(self):
        for option in ['precio', 'repuestos']:
            self.assertEqual(self.send(action='poll', option=option, poll_consent='yes').status_code, 303)
        self.send(self.other, action='poll', option='precio', poll_consent='yes')
        counts, _ = db.poll_results(self.scope())
        self.assertEqual(counts, {'precio': 1, 'repuestos': 1})
        self.assertEqual(self.send(action='poll', option='invalid', poll_consent='yes').status_code, 400)

    def login(self):
        token = self.csrf(self.admin, '/comunidad/admin/')
        res = self.admin.post('/comunidad/admin/', data={'action': 'login', 'key': 'test-admin-key', 'csrf_token': token})
        self.assertEqual(res.status_code, 303)

    def test_admin_auth_moderation_and_expiry(self):
        data = self.post()
        self.send(**data)
        fields = dict(action='moderate', post_id=data['request_id'], state='published', reason='Aporte pertinente')
        fields['csrf_token'] = self.csrf(self.other)
        self.assertEqual(self.other.post('/comunidad/admin/', data=fields).status_code, 403)
        self.login()
        fields['csrf_token'] = self.csrf(self.admin, '/comunidad/admin/')
        self.assertEqual(self.admin.post('/comunidad/admin/', data=fields).status_code, 303)
        self.assertEqual(len(db.visible_posts(SLUG)), 1)
        with self.admin.session_transaction() as sess:
            sess['comunidad_expires'] = 0
        self.assertEqual(self.admin.post('/comunidad/admin/', data=fields).status_code, 403)

    def test_private_contact_never_public_and_resolution_erases_data(self):
        rid = str(uuid.uuid4())
        token = self.csrf(self.client, '/comunidad/contacto/')
        fields = dict(csrf_token=token, request_id=rid, email='private@example.com',
            body='Quiero retirar un aporte que hice desde otro navegador.', contact_consent='yes')
        self.assertEqual(self.client.post('/comunidad/contacto/', data=fields).status_code, 303)
        self.assertNotIn('private@example.com', self.other.get('/comunidad/admin/').text)
        self.assertNotIn('private@example.com', self.other.get(URL).text)
        self.login()
        self.assertIn('private@example.com', self.admin.get('/comunidad/admin/').text)
        token = self.csrf(self.admin, '/comunidad/admin/')
        res = self.admin.post('/comunidad/admin/', data=dict(csrf_token=token, action='resolve_request', request_id=rid))
        self.assertEqual(res.status_code, 303)
        self.assertEqual(db.private_requests(), [])
        with db.connection() as conn:
            row = conn.execute('SELECT email,body FROM comunidad_requests WHERE id=?', (rid,)).fetchone()
        self.assertEqual(tuple(row), ('', ''))

    def test_atomic_rate_limit_under_concurrency(self):
        with db.connection():
            pass
        with ThreadPoolExecutor(max_workers=6) as pool:
            values = list(pool.map(lambda _: db.rate_allowed('test-concurrent', 10), range(25)))
        self.assertEqual(sum(values), 10)

    def test_production_requires_persistent_storage_and_secrets(self):
        with patch.dict(os.environ, {'APP_ENV': 'production', 'COMUNIDAD_SESSION_SECRET': '', 'RELEVAMIENTO_SESSION_SECRET': ''}):
            self.assertFalse(db.readable())
            self.assertFalse(db.enabled())
            res = self.client.get(URL)
            self.assertEqual(res.status_code, 503)
            self.assertEqual(res.headers['Retry-After'], '600')
            self.assertEqual(self.send(**self.post()).status_code, 503)
            with self.assertRaises(RuntimeError):
                with db.connection():
                    pass

    def test_forms_have_distinct_idempotency_keys(self):
        from bs4 import BeautifulSoup
        html = BeautifulSoup(self.client.get(URL).text, 'html.parser')
        keys = [i['value'] for i in html.select('form[data-draft] input[name=request_id]')]
        self.assertEqual(len(keys), 2)
        self.assertEqual(len(set(keys)), len(keys))

    def test_other_model_cannot_modify_post(self):
        from tallerlab_data.storage import get_all_tools
        other_slug = next(t.slug for t in get_all_tools() if t.slug != SLUG)
        data = self.post()
        self.send(**data)
        token = self.csrf(self.client)
        res = self.client.post('/comunidad/modelos/'+other_slug+'/participar',
            data=dict(csrf_token=token, action='withdraw', post_id=data['request_id']))
        self.assertEqual(res.status_code, 400)
        self.assertEqual(db.queue()[0]['state'], 'pending')

    def test_catalogue_links_and_sitemap(self):
        res = self.client.get('/herramientas/'+SLUG+'/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(URL+'#contar', res.text)
        sitemap = self.client.get('/sitemap.xml').text
        self.assertIn('/comunidad/criterios/', sitemap)
        self.assertNotIn('/comunidad/admin/', sitemap)

    def test_simplified_form_does_not_request_age_or_brand_relationship(self):
        from bs4 import BeautifulSoup
        html = BeautifulSoup(self.client.get(URL).text, 'html.parser')
        self.assertEqual(html.select('[name=adult], [name=relationship]'), [])
        self.assertNotIn('Soy mayor de edad', html.get_text())
        data = self.post('review')
        self.assertNotIn('adult', data)
        self.assertNotIn('relationship', data)
        self.assertEqual(self.send(**data).status_code, 303)
        self.assertNotIn('relationship', db.queue()[0]['context'])

    def test_model_links_back_to_its_editorial_guides(self):
        from bs4 import BeautifulSoup
        html = BeautifulSoup(self.client.get(URL).text, 'html.parser')
        self.assertIsNotNone(html.select_one('.co-related-guides a[href="/taladros/bosch-inalambrico/"]'))
        self.assertIn('opiniones y experiencias', html.h1.get_text())

    def test_guide_does_not_link_unrelated_or_partial_model_codes(self):
        from comunidad.components import guide_community_tools
        from servidor_local import ALL_ARTICLES
        article = next(a for a in ALL_ARTICLES if a['url'] == '/taladros/bosch-inalambrico/')
        self.assertEqual([t.slug for t in guide_community_tools(article)], [SLUG])
        fake = dict(article, h1='Bosch', body='Bosch GSB 18V-500: otro modelo diferente.')
        self.assertEqual(guide_community_tools(fake), [])

    def test_all_guides_have_visible_community_entry_and_valid_destinations(self):
        import contextlib
        import io
        from urllib.parse import urlsplit, parse_qs
        from bs4 import BeautifulSoup
        from servidor_local import ALL_ARTICLES
        from comunidad.components import guide_community_tools
        from tallerlab_data.storage import get_tool_by_slug, get_tools_by_category
        checked = set()
        for article in ALL_ARTICLES:
            with contextlib.redirect_stdout(io.StringIO()):
                response = self.client.get(article['url'])
            self.assertEqual(response.status_code, 200, article['url'])
            html = BeautifulSoup(response.text, 'html.parser')
            self.assertEqual(len(html.select('h1')), 1, article['url'])
            # Sin aportes publicados la guía no muestra el acceso superior: conserva su foco.
            self.assertIsNone(html.select_one('.co-guide-entry a'), article['url'])
            block = html.select_one('#comunidad-guia')
            self.assertIsNotNone(block, article['url'])
            self.assertEqual(len(html.select('#comunidad-guia')), 1)
            for tool in guide_community_tools(article):
                for anchor in ['contar','experiencias','preguntar']:
                    self.assertIsNotNone(block.select_one('a[href="/comunidad/modelos/'+tool.slug+'/#'+anchor+'"]'), article['url'])
            for link in block.select('a[href]'):
                target = link['href']
                parts = urlsplit(target)
                query = parse_qs(parts.query)
                if 'categoria' in query:
                    self.assertTrue(get_tools_by_category(query['categoria'][0]), target)
                if target in checked:
                    continue
                checked.add(target)
                res = self.client.get(parts.path + ('?' + parts.query if parts.query else ''))
                self.assertEqual(res.status_code, 200, target)
                if parts.fragment:
                    dest = BeautifulSoup(res.text, 'html.parser')
                    self.assertIsNotNone(dest.find(id=parts.fragment), target)


    # --- SEO y autoridad -------------------------------------------------------------
    def review(self, n, rating='4'):
        data = self.post('review', rating=rating, alias=f'Usuario {n}',
            body=f'Experiencia número {n}: la uso para perforar perfiles de hierro y madera dura en el taller. '
                 'La batería rinde una jornada completa y el mandril no perdió precisión con el uso diario. '
                 'Lo único que noté es que calienta en trabajos largos con mechas grandes.')
        data['advantages'] = 'Liviana, buen torque y la batería dura bastante en trabajos de herrería.'
        self.assertEqual(self.send(self.other if n % 2 else self.client, **data).status_code, 303)
        self.publish(data['request_id'])
        return data

    def test_unavailable_storage_returns_503_never_200_noindex(self):
        with patch.object(db, 'snapshot', side_effect=RuntimeError('caída')):
            res = self.client.get(URL)
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.headers['Retry-After'], '600')

    def test_reading_pages_does_not_create_session_cookie(self):
        for url in ['/comunidad/', '/comunidad/criterios/', '/herramientas/' + SLUG + '/']:
            self.assertNotIn('session', self.client.get(url).headers.get('Set-Cookie', ''), url)

    def test_question_page_qapage_editor_answer_and_canonical_redirect(self):
        from bs4 import BeautifulSoup
        import json as _json
        from comunidad.components import question_path
        q = self.post()
        self.send(**q)
        self.publish(q['request_id'])
        question = next(p for p in db.visible_posts(SLUG) if p['id'] == q['request_id'])
        path = question_path(SLUG, question)
        self.assertIn('/preguntas/sirve-para-perforar-metal-todos-los-dias-', path)
        res = self.other.get(path)
        self.assertEqual(res.status_code, 200)
        self.assertIn('noindex', res.text)
        wrong = path.replace('sirve-para', 'otro-texto')
        self.assertEqual(self.other.get(wrong).status_code, 301)
        self.assertEqual(self.other.get(URL + 'preguntas/nada-00000000/').status_code, 404)
        self.login()
        token = self.csrf(self.admin, '/comunidad/admin/')
        res = self.admin.post('/comunidad/admin/', data=dict(csrf_token=token, action='editor_answer', question_id=q['request_id'],
            body='Según el manual del fabricante, admite mechas de metal de hasta 13 mm con la batería de 4 Ah.'))
        self.assertEqual(res.status_code, 303)
        html = BeautifulSoup(self.other.get(path).text, 'html.parser')
        self.assertIsNone(html.select_one('meta[name=robots]'))
        self.assertEqual(html.h1.get_text(), '¿Sirve para perforar metal todos los días?')
        self.assertIn('Respuesta del editor de TallerLab', html.get_text())
        data = [_json.loads(t.string) for t in html.select('script[type="application/ld+json"]')]
        qa = next(d for d in data if d.get('@type') == 'QAPage')
        self.assertEqual(qa['mainEntity']['answerCount'], 1)
        self.assertIn('/autor/joaquin-vallasciani/', qa['mainEntity']['suggestedAnswer'][0]['author']['url'])
        self.assertIn(path, self.client.get('/sitemap.xml').text)
        # Una respuesta enviada desde la página de la pregunta vuelve a ella.
        a = self.post('answer', parent_id=q['request_id'], volver='pregunta', pregunta=q['request_id'])
        res = self.send(self.other, **a)
        self.assertEqual(res.status_code, 303)
        self.assertIn('/preguntas/', res.headers['Location'])

    def test_model_indexing_threshold_summary_sitemap_and_product_reviews(self):
        from bs4 import BeautifulSoup
        import json as _json
        self.review(1)
        self.review(2)
        self.assertIn('noindex', self.other.get(URL).text)
        self.assertNotIn(URL, self.client.get('/sitemap.xml').text)
        self.review(3, rating='5')
        html = BeautifulSoup(self.other.get(URL).text, 'html.parser')
        self.assertIsNone(html.select_one('meta[name=robots]'))
        self.assertIn('3 de 3', html.select_one('.co-summary').get_text())
        self.assertIn(URL, self.client.get('/sitemap.xml').text)
        ficha = BeautifulSoup(self.other.get('/herramientas/' + SLUG + '/').text, 'html.parser')
        self.assertIn('Experiencia número 3', ficha.select_one('#comunidad-modelo').get_text())
        product = next(d for d in (_json.loads(t.string) for t in ficha.select('script[type="application/ld+json"]')) if d.get('@type') == 'Product')
        self.assertEqual(product['aggregateRating']['ratingCount'], 3)
        self.assertEqual(product['aggregateRating']['ratingValue'], 4.3)
        self.assertEqual(len(product['review']), 3)

    def test_guide_entry_appears_only_with_published_content(self):
        from bs4 import BeautifulSoup
        self.review(1)
        html = BeautifulSoup(self.client.get('/taladros/bosch-inalambrico/').text, 'html.parser')
        entry = html.select_one('.co-guide-entry a')
        self.assertIsNotNone(entry)
        self.assertEqual(entry['href'], '#comunidad-guia')
        self.assertIn('1 experiencia', html.select_one('#comunidad-guia').get_text())

    def test_invalid_rating_and_missing_question_title_are_rejected_in_spanish(self):
        self.assertEqual(self.send(**self.post('review', rating='9')).status_code, 400)
        res = self.send(**self.post(title=''))
        self.assertEqual(res.status_code, 400)
        self.assertIn('pregunta en una línea', res.text)
        self.assertEqual(db.queue(), [])

    def test_poll_results_hidden_until_minimum_base(self):
        self.send(action='poll', option='precio', poll_consent='yes')
        text = self.client.get(URL).text
        self.assertIn('al menos 30 respuestas', text)
        self.assertNotIn('Resultados · base', text)


    # --- Operación: sesión, avisos, resumen diario y analítica ---------------------------
    def test_session_cookie_is_lax_and_persistent(self):
        cookie = self.client.get(URL).headers.get('Set-Cookie', '')
        self.assertIn('SameSite=Lax', cookie)
        self.assertIn('Expires=', cookie)

    def mail_env(self):
        return patch.dict(os.environ, {'RESEND_API_KEY': 're_test', 'COMUNIDAD_AVISOS_REMITENTE': 'TallerLab <avisos@example.com>',
                                       'COMUNIDAD_TELEGRAM_BOT_TOKEN': '1:abc', 'COMUNIDAD_TELEGRAM_CHAT_ID': '42'})

    def test_asker_gets_single_email_when_answer_is_published(self):
        from unittest.mock import MagicMock
        sent = MagicMock(return_value=MagicMock(ok=True))
        with self.mail_env(), patch('requests.post', sent):
            self.assertIn('aviso_email', self.client.get(URL).text)
            self.assertEqual(self.send(**self.post(aviso_email='persona@example.com')).status_code, 400)  # falta consentimiento
            q = self.post(aviso_email='persona@example.com', aviso_consent='yes')
            self.assertEqual(self.send(**q).status_code, 303)
            self.assertTrue(any('api.telegram.org' in c.args[0] for c in sent.call_args_list))
            self.assertNotIn('persona@example.com', str([c for c in sent.call_args_list if 'telegram' in c.args[0]]))
            self.publish(q['request_id'])
            a = self.post('answer', parent_id=q['request_id'])
            self.send(self.other, **a)
            self.login()
            token = self.csrf(self.admin, '/comunidad/admin/')
            sent.reset_mock()
            res = self.admin.post('/comunidad/admin/', data=dict(csrf_token=token, action='moderate', post_id=a['request_id'],
                                                                 state='published', reason='Respuesta pertinente'))
            self.assertEqual(res.status_code, 303)
            mails = [c for c in sent.call_args_list if 'resend' in c.args[0]]
            self.assertEqual(len(mails), 1)
            self.assertEqual(mails[0].kwargs['json']['to'], ['persona@example.com'])
            self.assertIn('/preguntas/', mails[0].kwargs['json']['text'])
            self.assertEqual(db.notifications_for(q['request_id']), [])
        self.assertNotIn('persona@example.com', self.other.get(URL).text)

    def test_email_field_hidden_without_mail_configuration(self):
        self.assertNotIn('aviso_email', self.client.get(URL).text)

    def test_daily_digest_requires_cron_secret_and_reports(self):
        from unittest.mock import MagicMock
        self.assertEqual(self.client.get('/api/comunidad/resumen').status_code, 401)
        q = self.post()
        self.send(**q)
        sent = MagicMock(return_value=MagicMock(ok=True))
        with self.mail_env(), patch.dict(os.environ, {'CRON_SECRET': 'cron-test', 'COMUNIDAD_AVISO_EDITOR_EMAIL': 'editor@example.com'}), \
                patch('requests.post', sent):
            self.assertEqual(self.client.get('/api/comunidad/resumen', headers={'Authorization': 'Bearer otro'}).status_code, 401)
            res = self.client.get('/api/comunidad/resumen', headers={'Authorization': 'Bearer cron-test'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['pending'], 1)
        self.assertEqual(sorted(res.json['sent']), ['email', 'telegram'])

    def test_admin_dashboard_lists_unanswered_questions(self):
        q = self.post()
        self.send(**q)
        self.publish(q['request_id'])
        self.login()
        text = self.admin.get('/comunidad/admin/').text
        self.assertIn('preguntas sin respuesta', text)
        self.assertIn('¿Sirve para perforar metal todos los días?', text)

    def test_vercel_web_analytics_only_when_enabled(self):
        self.assertNotIn('_vercel/insights', self.client.get('/comunidad/').text)
        with patch.dict(os.environ, {'VERCEL_WEB_ANALYTICS': '1'}):
            self.assertIn('/_vercel/insights/script.js', self.client.get('/comunidad/').text)
            self.assertNotIn('_vercel/insights', self.client.get('/comunidad/admin/').text)


    def test_hub_noindex_until_enough_model_pages_and_503_without_data(self):
        from comunidad import components as cc
        res = self.client.get('/comunidad/')
        self.assertIn('noindex', res.text)
        self.assertNotIn('experiencias reales', res.text)
        full = {'reviews': 3, 'answered_questions': [], 'words': 200}
        self.assertFalse(cc.hub_indexable({'a': full, 'b': full}))
        self.assertTrue(cc.hub_indexable({'a': full, 'b': full, 'c': full}))
        self.assertNotIn('/comunidad/</loc>', self.client.get('/sitemap.xml').text)
        with patch.object(cc, 'hub_indexable', return_value=True):
            self.assertNotIn('noindex', self.client.get('/comunidad/').text)
            self.assertIn('/comunidad/</loc>', self.client.get('/sitemap.xml').text)
        db.clear_cache()
        with patch.object(db, 'overview', side_effect=RuntimeError('caída')):
            res = self.client.get('/comunidad/')
        self.assertEqual(res.status_code, 503)
        self.assertNotIn('s-maxage', res.headers['Cache-Control'])

    def test_stale_overview_survives_storage_failure(self):
        db.clear_cache()
        fresh = db.overview()
        with patch.object(db, 'overview', side_effect=RuntimeError('caída')):
            self.assertEqual(db.safe_overview(), fresh)
            self.assertEqual(db.overview_or_none(), fresh)
        db.clear_cache()
        with patch.object(db, 'overview', side_effect=RuntimeError('caída')):
            self.assertEqual(db.safe_overview(), {})
            self.assertIsNone(db.overview_or_none())

    def test_postgres_uses_one_connection_per_request(self):
        import sqlite3

        class FakePostgres:
            opened = closed = 0

            def __init__(self, path):
                FakePostgres.opened += 1
                self.raw = sqlite3.connect(str(path), timeout=15)
                self.raw.row_factory = sqlite3.Row

            def execute(self, sql, params=()):
                return self.raw.execute(sql, params)

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                self.raw.rollback() if exc_type else self.raw.commit()

            def close(self):
                FakePostgres.closed += 1
                self.raw.close()

        path = Path(self.tmp.name)/'fake-pg.db'
        with patch.dict(os.environ, {'COMUNIDAD_DATABASE_URL': 'postgresql://prueba'}), \
                patch.object(db, '_open_postgres', lambda dsn: FakePostgres(path)):
            db._READY.discard('postgresql://prueba')
            with app.test_request_context('/comunidad/'):
                self.assertTrue(db.rate_allowed('prueba', 5))
                self.assertTrue(db.rate_allowed('prueba', 5))
                with self.assertRaises(ValueError):
                    db.save_post(str(uuid.uuid4()), 'actor', SLUG, 'answer', 'Ana', 'x' * 30, {}, str(uuid.uuid4()))
                # Después de un error, la misma conexión sigue sirviendo.
                db.save_post(str(uuid.uuid4()), 'actor', SLUG, 'review', 'Ana', 'x' * 30, {})
                self.assertEqual(FakePostgres.opened, 1)
            self.assertEqual(FakePostgres.closed, 1)
            db._READY.discard('postgresql://prueba')

if __name__ == '__main__':
    unittest.main()
