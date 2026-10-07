"""Contratos de captura y publicación. Sin red, secretos ni base productiva."""
import csv
import io
import json
import tempfile
import shutil
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch, Mock

from bs4 import BeautifulSoup
from observatorio.gratuito import collect, extract_public_product, atomic_json, MANIFEST, DEFAULT_HISTORY
from observatorio.estatico import build_site, snapshot, current_state, HUB, METHOD, CATEGORIES


def fixture(source='megastore', price='123456.20', visible='$ 123.456,20', stock='InStock', currency='ARS'):
    model = {'id':'test-model','brand':'Marca','model':'X1','variant':'Solo','source':source,'category':'taladros',
             'url':'https://store.example/producto/', 'schema_sku':'X1', 'schema_mpn':None,'schema_name':'Taladro X1 Solo','schema_brand':'Marca', 'variant_properties':{'Incluye batería':'No'}}
    product = {'@type':'Product','@id':model['url'],'sku':'X1','name':model['schema_name'],'brand':{'name':'Marca'},'additionalProperty':[{'name':'Incluye batería','value':'No'}],
               'offers':{'@type':'Offer','url':model['url'],'price':price,'priceCurrency':currency,'availability':'https://schema.org/'+stock}}
    selector = 'price_display' if source=='megastore' else 'precio-mostrado'
    html = '<script type="application/ld+json">'+json.dumps(product)+'</script><span id="'+selector+'">'+visible+'</span>'
    return html, model, product


class FreeObservatoryTests(unittest.TestCase):
    def test_exact_product_ignores_recommended(self):
        html, m, product = fixture()
        recommendation = deepcopy(product); recommendation['@id']='https://store.example/otro/'; recommendation['offers']['price']='9999'
        result = extract_public_product('<script type="application/ld+json">'+json.dumps(recommendation)+'</script>'+html, m)
        self.assertEqual(result['price_ars'],'123456.20')
        self.assertEqual(result['availability'],'disponible')

    def test_wrong_identity_variant_currency_and_offer_refused(self):
        _, m, product = fixture()
        cases = [('sku','otro'),('name','Taladro X1 con batería'),('mpn','otra'),('brand',{'name':'otra'}),('additionalProperty',[{'name':'Incluye batería','value':'Sí'}])]
        for key,value in cases:
            p=deepcopy(product);p[key]=value
            html='<script type="application/ld+json">'+json.dumps(p)+'</script><span id="price_display">$ 123.456,20</span>'
            with self.subTest(key=key),self.assertRaises(ValueError):extract_public_product(html,m)
        for key,value in [('priceCurrency','USD'),('url','https://store.example/otro/'),('itemCondition','https://schema.org/UsedCondition')]:
            p=deepcopy(product);p['offers'][key]=value
            html='<script type="application/ld+json">'+json.dumps(p)+'</script><span id="price_display">$ 123.456,20</span>'
            with self.subTest(key=key),self.assertRaises(ValueError):extract_public_product(html,m)

    def test_installment_and_mismatched_main_price_refused(self):
        html,m,_=fixture(visible='$ 12.345,62')
        with self.assertRaises(ValueError):extract_public_product(html,m)
        html,m,_=fixture();html += '<span id="price_display">$ 1000</span>'
        with self.assertRaises(ValueError):extract_public_product(html,m)

    def test_dgm_rounding_is_exact_and_not_generic_tolerance(self):
        html,m,_=fixture('dgm','123456.78','$ 123.457')
        self.assertEqual(extract_public_product(html,m)['price_ars'],'123456.78')
        for visible in ('$ 123.456', '$ 123.456,40'):
            html,m,_=fixture('dgm','123456.78',visible)
            with self.assertRaises(ValueError):extract_public_product(html,m)

    def test_stock_zero_and_unpriced_are_not_free_offers(self):
        html,m,_=fixture(price='0',visible='',stock='OutOfStock')
        result=extract_public_product(html,m)
        self.assertIsNone(result['price_ars']);self.assertEqual(result['availability'],'agotado')
        html,m,_=fixture(price='0',visible='$ 0',stock='InStock')
        with self.assertRaises(ValueError):extract_public_product(html,m)

    def test_expiry_later_failure_and_future_time_hide_prices(self):
        now=datetime.now(timezone.utc)
        observation={'observed_at':(now-timedelta(hours=1)).isoformat(),'availability':'disponible'}
        self.assertEqual(current_state(observation,{},now),'disponible')
        self.assertEqual(current_state(observation,{'status':'error','observed_at':now.isoformat()},now),'error')
        observation['observed_at']=(now-timedelta(hours=49)).isoformat()
        self.assertEqual(current_state(observation,{},now),'vencido')
        observation['observed_at']=(now+timedelta(hours=1)).isoformat()
        self.assertEqual(current_state(observation,{},now),'vencido')

    def test_catalog_and_initial_data_are_real_and_complete(self):
        manifest=json.loads(MANIFEST.read_text(encoding='utf-8'));history=json.loads(DEFAULT_HISTORY.read_text(encoding='utf-8'))
        self.assertTrue(40<=len(manifest['models'])<=50)
        self.assertEqual(len({m['id'] for m in manifest['models']}),len(manifest['models']))
        self.assertEqual(set(CATEGORIES),{m['category'] for m in manifest['models']})
        self.assertEqual(set(history['latest_attempts']),{m['id'] for m in manifest['models']})
        self.assertTrue(all(len(o['evidence_sha256'])==64 for o in history['observations']))
        self.assertTrue(all(o['extractor_version']=='gratuito-1.0' for o in history['observations']))
        self.assertNotIn('feed_importer',json.dumps(history))

    def test_daily_idempotency_and_failure_preserves_history(self):
        html,m,_=fixture()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.json';manifest=Path(tmp)/'manifest.json'
            atomic_json(manifest,{'models':[m],'sources':{'megastore':{'domain':'store.example'}}})
            robots=Mock();robots.can_fetch.return_value=True;robots.crawl_delay.return_value=0
            with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page',return_value=html) as fetch,patch('observatorio.gratuito.time.sleep'):
                run=collect(path,manifest);self.assertEqual(run['captured'],1)
                run=collect(path,manifest);self.assertEqual(run['already_captured'],1);self.assertEqual(run['captured'],0);self.assertEqual(fetch.call_count,1)
            data=json.loads(path.read_text());data['observations'][0]['day_art']='2000-01-01';atomic_json(path,data)
            with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page',side_effect=ValueError('HTTP 403')) as fetch,patch('observatorio.gratuito.time.sleep'):
                run=collect(path,manifest);self.assertEqual(run['failed'],1);self.assertEqual(run['status'],'degraded')
            data=json.loads(path.read_text());self.assertEqual(len(data['observations']),1);self.assertEqual(data['latest_attempts'][m['id']]['status'],'error')

    def test_robots_denial_and_http_block_never_bypassed(self):
        html,m,_=fixture();m2=dict(m,id='model2',url='https://store.example/otro/')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.json';manifest=Path(tmp)/'manifest.json';atomic_json(manifest,{'models':[m,m2],'sources':{'megastore':{'domain':'store.example'}}})
            robots=Mock();robots.can_fetch.return_value=False;robots.crawl_delay.return_value=0
            with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page') as fetch:
                self.assertEqual(collect(path,manifest)['failed'],2);fetch.assert_not_called()
            robots.can_fetch.return_value=True
            with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page',side_effect=ValueError('HTTP 429')) as fetch,patch('observatorio.gratuito.time.sleep'):
                self.assertEqual(collect(path,manifest)['failed'],2);self.assertEqual(fetch.call_count,1)

    def test_corroborated_price_jumps_are_automatic_and_reset_baseline(self):
        now=datetime.now(timezone.utc).isoformat()
        for price, visible in [('173452.00', '$ 173.452,00'), ('60000.00', '$ 60.000,00')]:
            with self.subTest(price=price), tempfile.TemporaryDirectory() as tmp:
                html,m,_=fixture(price=price,visible=visible)
                path=Path(tmp)/'history.json';manifest=Path(tmp)/'manifest.json'
                atomic_json(manifest,{'models':[m],'sources':{'megastore':{'domain':'store.example'}}})
                atomic_json(path,{'version':1,'observations':[{'model_id':m['id'],'day_art':'2000-01-01','observed_at':now,'availability':'disponible','price_ars':'112744.00'}],'latest_attempts':{},'run':{}})
                robots=Mock();robots.can_fetch.return_value=True;robots.crawl_delay.return_value=0
                with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page',return_value=html),patch('observatorio.gratuito.time.sleep'):
                    run=collect(path,manifest)
                    self.assertEqual(run['captured'],1);self.assertEqual(run['failed'],0)
                    data=json.loads(path.read_text())
                    self.assertEqual(data['observations'][-1]['price_ars'],price)
                    self.assertTrue(data['observations'][-1]['jump_verified'])
                    self.assertNotIn('jump_reviewed',data['observations'][-1])
                    data['observations'][-1]['day_art']='2000-01-02';atomic_json(path,data)
                    self.assertEqual(collect(path,manifest)['captured'],1)
                    data=json.loads(path.read_text())
                    self.assertNotIn('jump_verified',data['observations'][-1])

    def test_large_jump_with_contradictory_visible_price_stays_hidden(self):
        html,m,_=fixture(price='173452.00',visible='$ 112.744,00')
        now=datetime.now(timezone.utc).isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'history.json';manifest=Path(tmp)/'manifest.json'
            atomic_json(manifest,{'models':[m],'sources':{'megastore':{'domain':'store.example'}}})
            old={'model_id':m['id'],'day_art':'2000-01-01','observed_at':now,'availability':'disponible','price_ars':'112744.00'}
            atomic_json(path,{'version':1,'observations':[old],'latest_attempts':{},'run':{}})
            robots=Mock();robots.can_fetch.return_value=True;robots.crawl_delay.return_value=0
            with patch('observatorio.gratuito.get_allowed_robots',return_value=robots),patch('observatorio.gratuito.fetch_page',return_value=html),patch('observatorio.gratuito.time.sleep'):
                self.assertEqual(collect(path,manifest)['failed'],1)
            data=json.loads(path.read_text())
            self.assertEqual(data['observations'],[old])
            self.assertEqual(current_state(old,data['latest_attempts'][m['id']],datetime.now(timezone.utc)),'error')

    def test_pages_prefix_downloads_and_main_home_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);summary=build_site(DEFAULT_HISTORY,output,'/Taller-Lab','https://joaqui1.github.io',canonical_url='https://www.tallerlab.com.ar')
            self.assertEqual(summary['monitored'],44)
            html=(output/HUB.strip('/')/'index.html').read_text(encoding='utf-8')
            soup=BeautifulSoup(html,'html.parser');self.assertEqual(len(soup.select('.product')),44)
            self.assertTrue(all(a['href'].startswith('/Taller-Lab/') for a in soup.select('.categories a')))
            for asset in soup.select('link[rel=stylesheet],script[src]'):
                value=(asset.get('href') or asset['src']).split('?')[0];self.assertTrue((output/value.removeprefix('/Taller-Lab/')).is_file())
            self.assertEqual(soup.select_one('link[rel=canonical]')['href'],'https://www.tallerlab.com.ar'+HUB)
            self.assertEqual(soup.select_one('meta[name=robots]')['content'],'noindex, follow')
            self.assertFalse((output/'sitemap.xml').exists())
            self.assertEqual(len(summary['routes']),9+44)
            links=[a['href'] for a in soup.select('.product h3 a')];self.assertEqual(len(links),44)
            for link in links:self.assertTrue((output/link.removeprefix('/Taller-Lab/')/'index.html').is_file())
            for category in CATEGORIES:
                self.assertTrue((output/'datos/precios'/category/'index.html').is_file())
                with (output/'datos/precios'/category/'historial.csv').open(encoding='utf-8-sig',newline='') as f:
                    rows=list(csv.DictReader(f));self.assertTrue(rows);self.assertTrue(all(r['categoria']==category for r in rows))
            (output/'index.html').write_text('HOME');(output/'robots.txt').write_text('ROBOTS')
            build_site(DEFAULT_HISTORY,output,standalone=False)
            self.assertEqual((output/'index.html').read_text(),'HOME');self.assertEqual((output/'robots.txt').read_text(),'ROBOTS')

    def test_main_domain_model_pages_are_indexable_and_linked(self):
        from observatorio.estatico import model_path, price_stats, verdict, chart_svg
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp);summary=build_site(DEFAULT_HISTORY,output)
            self.assertIn('/datos/precios/compresores/lusqtoff-lc2550b-8/',summary['routes'])
            soup=BeautifulSoup((output/'datos/precios/compresores/lusqtoff-lc2550b-8/index.html').read_text(encoding='utf-8'),'html.parser')
            self.assertEqual(soup.select_one('link[rel=canonical]')['href'],'https://www.tallerlab.com.ar/datos/precios/compresores/lusqtoff-lc2550b-8/')
            self.assertTrue(soup.select_one('meta[name=robots]')['content'].startswith('index'))
            self.assertIn('LC2550B-8',soup.h1.text)
            types=[json.loads(s.string)['@type'] for s in soup.select('script[type="application/ld+json"]')]
            self.assertEqual(types,['Dataset','BreadcrumbList'])
            self.assertTrue(soup.select('.model-context a[href^="https://www.tallerlab.com.ar/compresores/"]'))
            sitemap=(output/'sitemap.xml').read_text(encoding='utf-8');self.assertEqual(sitemap.count('<loc>'),53)
            descriptions={BeautifulSoup((output/p.strip('/')/'index.html').read_text(encoding='utf-8'),'html.parser').select_one('meta[name=description]')['content'] for p in summary['routes']}
            self.assertEqual(len(descriptions),len(summary['routes']))
        series=[{'observed_at':f'2026-10-{d:02d}T12:00:00+00:00','availability':'disponible','price_ars':f'{100000+d*1000}.00'} for d in range(1,21)]
        row={'model':{'brand':'X','model':'Y'},'state':'disponible','observation':series[-1],'series':series}
        stats=price_stats(series);self.assertEqual(stats['n'],20);self.assertEqual(verdict(row,stats)[0],'above')
        self.assertEqual(verdict(dict(row,series=series[:5]),price_stats(series[:5]))[0],'collecting')
        self.assertIn('<polyline',chart_svg(series,'x'))

    def test_build_requires_all_pages_and_downloads(self):
        from observatorio.estatico import verify_publication
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            summary = build_site(DEFAULT_HISTORY, output, standalone=False)
            verify_publication(output, summary)
            (output / 'datos/precios/compresores/historial.csv').unlink()
            with self.assertRaisesRegex(RuntimeError, 'historial.csv'):
                verify_publication(output, summary)

    def test_sitemap_requires_generated_artifacts_not_only_history(self):
        from observatorio.estatico import published_observatory_paths, expected_observatory_paths
        with tempfile.TemporaryDirectory() as tmp:
            publication = Path(tmp) / 'publication.json'
            with patch('observatorio.estatico.static_observatory_file', return_value=None), patch('observatorio.estatico.PUBLICATION_MANIFEST', publication):
                self.assertEqual(published_observatory_paths(), [])
                atomic_json(publication, {'schema_version': 1, 'routes': expected_observatory_paths()[:-1]})
                self.assertEqual(published_observatory_paths(), [])
                atomic_json(publication, {'schema_version': 1, 'routes': expected_observatory_paths()})
                self.assertEqual(published_observatory_paths(), [])

    def test_promotion_changes_are_not_list_price_increases(self):
        from observatorio.estatico import classify_change, hub_body
        previous = {'price_ars': '112744.00', 'reference_ars': '173452.00'}
        current = {'price_ars': '173452.00', 'reference_ars': None}
        self.assertEqual(classify_change(previous, current), 'offer_ended')
        self.assertEqual(classify_change(current, previous), 'offer_started')
        self.assertEqual(classify_change(previous, dict(current, price_ars='180000.00')), 'offer_changed')
        self.assertEqual(classify_change(current, dict(current, price_ars='180000.00')), 'price_changed')
        self.assertEqual(classify_change(previous, previous), 'unchanged')
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
        model = manifest['models'][0]
        now = datetime.now(timezone.utc)
        series = [dict(previous, model_id=model['id'], observed_at=(now-timedelta(days=1)).isoformat(), availability='disponible'),
                  dict(current, model_id=model['id'], observed_at=now.isoformat(), availability='disponible')]
        rows = snapshot({'observations':series,'latest_attempts':{}}, {'models':[model]}, now)
        html = hub_body(None, rows, rows, manifest, lambda p:p, now.isoformat(), 'https://www.tallerlab.com.ar'+HUB)
        soup = BeautifulSoup(html, 'html.parser')
        self.assertIn('Fin de oferta', soup.select_one('.moves').text)
        self.assertIn('+53.8%', soup.select_one('.moves').text)
        self.assertEqual(soup.select_one('.product-change small').text, 'Fin de oferta')
        self.assertIn('2 días con capturas', soup.select_one('.coverage-note').text)

    @unittest.skipUnless(__import__('importlib.util').util.find_spec('flask'), 'Flask no instalado')
    def test_all_routes_work_with_only_serverless_copy_and_missing_page_is_not_indexed(self):
        import app as module
        from observatorio.estatico import published_observatory_paths
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            summary = build_site(DEFAULT_HISTORY, root/'public', standalone=False)
            # Simula la función de Vercel: public/ ausente y copia generada disponible.
            shutil.move(str(root/'public'), str(root/'observatorio_publicado'))
            with patch('observatorio.estatico.ROOT', root):
                client = module.app.test_client()
                for path in summary['routes']:
                    with self.subTest(path=path), client.get(path) as response:
                        self.assertEqual(response.status_code, 200)
                        soup = BeautifulSoup(response.get_data(as_text=True), 'html.parser')
                        self.assertEqual(soup.select_one('link[rel=canonical]')['href'], 'https://www.tallerlab.com.ar'+path)
                missing = summary['routes'][-1]
                (root/'observatorio_publicado'/missing.strip('/')/'index.html').unlink()
                self.assertNotIn(missing, published_observatory_paths())

    def test_failed_generation_fails_the_deployment(self):
        import preparar_assets_publicos as build
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'assets').mkdir()
            with patch.object(build, 'latest_history', return_value=DEFAULT_HISTORY), patch('observatorio.estatico.build_site', side_effect=RuntimeError('captura inválida')):
                with self.assertRaisesRegex(RuntimeError, 'captura inválida'):
                    build.main(root)
                self.assertFalse((root / 'assets/datos/observatorio-publicacion.json').exists())

    def test_build_bypasses_mutable_remote_history_cache(self):
        import preparar_assets_publicos as build
        from urllib.parse import urlsplit, parse_qs
        remote = json.loads(DEFAULT_HISTORY.read_text(encoding='utf-8'))
        remote['run']['finished_at'] = (datetime.fromisoformat(remote['run']['finished_at']) + timedelta(minutes=1)).isoformat()
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(remote).encode())) as fetch:
            target = build.latest_history(DEFAULT_HISTORY)
            request = fetch.call_args.args[0]
            self.assertIn('publication', parse_qs(urlsplit(request.full_url).query))
            self.assertEqual(request.get_header('Cache-control'), 'no-cache')
            self.assertEqual(json.loads(target.read_text())['run'], remote['run'])

    # El workflow de captura instala solo requests y bs4; la suite completa sí incluye Flask.
    @unittest.skipUnless(__import__('importlib.util').util.find_spec('flask'), 'Flask no instalado en el workflow de captura')
    def test_http_downloads_and_generated_json_do_not_need_legacy_database(self):
        import app as module
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_site(DEFAULT_HISTORY, root / 'public', standalone=False)
            with patch('observatorio.estatico.ROOT', root), patch.object(module, 'ASSETS_DIR', root / 'assets'), patch.object(module, 'export_observations_to_csv', side_effect=RuntimeError('La base anterior no está disponible')):
                client = module.app.test_client()
                for category in CATEGORIES:
                    for name in ('descargar-csv', 'historial.csv'):
                        with client.get('/datos/precios/' + category + '/' + name) as response:
                            self.assertEqual(response.status_code, 200)
                            self.assertEqual(response.mimetype, 'text/csv')
                            self.assertTrue(list(csv.DictReader(io.StringIO(response.get_data(as_text=True).lstrip('\ufeff')))))
                with client.get('/assets/datos/precios-observatorio-publico.json') as dataset:
                    self.assertEqual(dataset.status_code, 200)
                    self.assertIsInstance(dataset.get_json(), dict)

    def test_expired_build_keeps_history_and_removes_current_prices(self):
        manifest=json.loads(MANIFEST.read_text(encoding='utf-8'));history=json.loads(DEFAULT_HISTORY.read_text(encoding='utf-8'))
        now=max(datetime.fromisoformat(o['observed_at']) for o in history['observations'])+timedelta(hours=49)
        self.assertTrue(all(r['state']=='vencido' for r in snapshot(history,manifest,now)))
        with tempfile.TemporaryDirectory() as tmp:
            summary=build_site(DEFAULT_HISTORY,tmp,now=now)
            self.assertEqual(summary['available'],0)
            soup=BeautifulSoup((Path(tmp)/HUB.strip('/')/'index.html').read_text(encoding='utf-8'),'html.parser')
            self.assertTrue(all(p.text=='—' for p in soup.select('.current-price')))
            self.assertEqual(len(soup.select('tbody tr')),len(history['observations']))


if __name__ == '__main__':unittest.main()
