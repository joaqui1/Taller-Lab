"""Amplía fuentes específicas usando códigos de los catálogos oficiales."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin
import json
import re
from bs4 import BeautifulSoup
from preparar_fotos_modelos import inventory, norm, page, ROOT

PATH = ROOT / 'fuentes-fotos-adicionales.json'
extra = json.loads(PATH.read_text(encoding='utf-8')) if PATH.exists() else {}
products = inventory()
def add(brand, model, url):
    key = norm(brand + model)
    extra.setdefault(key, [])
    if url not in extra[key]:
        extra[key].append(url)

manual = [
    ('Makita','GA4534','https://makita.com.ar/producto/386-amoladora-makita-115mm-4-1-2-720-w/'),
    ('Makita','GA9020','https://www.makita.com.mx/producto/ga9020-esmeriladora-angular/'),
    ('DeWalt','DCF887B','https://asia.dewalt.global/product/dcf887b/20v-max-xtreme-cordless-brushless-14-3-speed-impact-driver-drill-kit'),
    ('Einhell','TC-RH 620 4F','https://www.einhell.com.ar/p/4257997-tc-rh-620-4f/'),
    ('Einhell','TC-HP 130','https://www.einhell.com.ar/p/4140750-tc-hp-130/'),
    ('Einhell','HYPRESSO 18/24-1 Li','https://www.einhell.com.ar/p/4140135-hypresso-18-24-1-li-solo/'),
    ('Gamma','GE3497AR','https://www.gammaherramientas.com.ar/producto/grupo-electrogeno-inverter-2kw/'),
]
for args in manual:
    add(*args)

def catalog(url):
    try:
        soup = BeautifulSoup(page(url), 'html.parser')
        for item in soup.select('li.product, .product.type-product'):
            text = norm(item.get_text(' ', strip=True))
            link = item.select_one('a.woocommerce-LoopProduct-link, a[href*="/producto/"]')
            if not link:
                continue
            for p in products.values():
                model = re.sub(r'^Professional\s+|\s+Black Series$', '', p['model'].split(' · ')[0])
                k = norm(model)
                if len(k) >= 5 and k in text:
                    add(p['brand'], model, urljoin(url, link['href']))
        return url, len(soup.select('li.product'))
    except Exception as e:
        return url, type(e).__name__

urls = ['https://www.gammaherramientas.com.ar/?post_type=product&type_aws=true']
urls += [f'https://makita.com.ar/productos/page/{i}/' for i in range(1, 9)]
with ThreadPoolExecutor(max_workers=5) as pool:
    for result in pool.map(catalog, urls):
        print(result, flush=True)
PATH.write_text(json.dumps(extra, ensure_ascii=False, indent=2), encoding='utf-8')
print('Fuentes específicas',len(extra), flush=True)
