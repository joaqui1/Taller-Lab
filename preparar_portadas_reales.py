"""Fotos de fabricantes para guías sin referencia en el catálogo comercial."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from preparar_fotos_modelos import page, candidates, optimize
import sys
import ssl
from urllib.request import urlopen, Request
from types import SimpleNamespace
import preparar_fotos_modelos as image_tools

_get=image_tools.get
def get_image(url):
 if url.startswith('https://ref.prokits.com.tw/'):
  # Python 3.14 activa X509_STRICT; conservar validación de cadena y host
  # con las reglas compatibles usadas por los navegadores para este CDN.
  context=ssl.create_default_context()
  context.verify_flags &= ~ssl.VERIFY_X509_STRICT
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),context=context,timeout=20) as response:
   return SimpleNamespace(content=response.read())
 return _get(url)
image_tools.get=get_image

SOURCES = {
 '/compresores/manguera/': ('Rolair Hybrid Air Hose','https://www.rolair.com/accessories/accessories/hybrid-air-hose'),
 '/compresores/kits-aerografo/': ('Paasche H-100D','https://paascheairbrush.com/products/h-100d'),
 '/compresores/acoples-rapidos/': ('Airex Universal','https://www.airex.it/en/catalog/attacchi-rapidi/universal-series-quick-couplings-and-fittings/'),
 '/compresores/para-aerografo/': ('Sparmax TC-501N','https://www.sparmaxair.com/compressor-master-1/tc-501n'),
 '/generadores/diesel/': ('Lüsqtoff LGD8000-8','https://lusqtoff.com.ar/ver-producto/LGD8000-8'),
 '/hidrolavadoras/gamma-150/': ('Gamma G2514AR','https://www.gammaherramientas.com.ar/producto/hidrolavadora-150-elite/'),
 '/hidrolavadoras/hyundai/': ('Hyundai HYEW65','https://hyundaiherramientas.com.ar/producto/hidrolavadora-1600-w-hyew65/'),
 '/hidrolavadoras/200-bar/': ('Comet KM Extra 8.16','https://www.gammaherramientas.com.ar/producto/hidrolavadora-comet-km-extra-8-16-16-200-t/'),
 '/sierras/sable/': ('Bosch S 644 D','https://www.bosch-professional.com/es/es/hoja-de-sierra-sable-wood-clean-s644d-8485969-ocs-ac/'),
 '/soldadoras/soldadora-de-punto/': ('Malectrics Spot Welder V4','https://malectrics.eu/product/diy-arduino-battery-spot-welder-prebuilt-kit-v3/'),
 '/soldadoras/carro-para-soldadora-mig/': ('Telwin Federal 803091','https://www.telwin.com/intl/en/products/trolleys/803091-trolley-federal'),
 '/soldadura-electronica/kit-soldador-de-estano/': ('Pro’sKit PK-916G','https://www.proskit.com/Product/PK-916G?hl=en-US'),
 '/soldadura-electronica/estacion-de-soldadura/': ('Yihua 878D','https://www.yihua-soldering.com/product-1-2-1-hot-air-rework-station-en/147657/'),
 '/soldadura-electronica/gadnic-878d/': ('Gadnic 878D SOLD0002','https://www.gadnic.com.ar/soldadoras/estacion-de-soldado-smd-750w'),
 '/soldadura-electronica/yihua-898d/': ('Yihua 898D','https://yihua-soldering.com/product-1-2-3-hot-air-rework-station-en/147659/'),
 '/soldadura-electronica/soporte-para-soldar-con-lupa/': ('Pro’sKit 608-391E','https://www.proskit.com/Product/608-391E?hl=en-US'),
 '/taladros/mecha-forstner-35-mm/': ('Bosch Expert Forstner Wood','https://www.bosch-professional.com/es/es/broca-forstner-expert-wood-7427439-ocs-ac/'),
}

def discover(item):
 path,(subject,source)=item
 try:
  html=page(source);soup=BeautifulSoup(html,'html.parser')
  urls=candidates(subject.split(' ',1)[-1],source)
  gallery=[urljoin(source,i.get('data-src') or i.get('src') or '') for i in soup.select('.woocommerce-product-gallery img, .product-image img, .product-detail img')]
  og=soup.select_one('meta[property="og:image"]')
  return path,dict(subject=subject,source=source,title=soup.title.get_text() if soup.title else '',candidates=list(dict.fromkeys(gallery+urls+([urljoin(source,og['content'])] if og else [])))[:8],all_images=[dict(alt=i.get('alt'),image=urljoin(source,i.get('data-src') or i.get('src') or '')) for i in soup.find_all('img')][:60])
 except Exception as e:return path,dict(subject=subject,source=source,error=str(e))

def prepare():
 data=json.loads(Path('fuentes-portadas-reales.json').read_text(encoding='utf-8'))
 choices={path:record['candidates'][0] for path,record in data.items() if record.get('candidates')}
 choices['/compresores/manguera/']=next(i['image'] for i in data['/compresores/manguera/']['all_images'] if 'Noodle' in i['image'])
 choices['/soldadoras/carro-para-soldadora-mig/']=next(i['image'] for i in data['/soldadoras/carro-para-soldadora-mig/']['all_images'] if '803091_FEDERAL' in i['image'])
 choices['/compresores/kits-aerografo/']=data['/compresores/kits-aerografo/']['candidates'][1]
 choices['/compresores/para-aerografo/']=data['/compresores/para-aerografo/']['candidates'][0].split('/v1/')[0]
 choices['/taladros/mecha-forstner-35-mm/']='https://www.bosch-professional.com/binary/ocsmedia/optimized/full/o481059v82_2608901837_bo_pro_u_f_1.png'
 # Esta guía general usa la foto documentada de una sierra, no de su hoja.
 choices.pop('/sierras/sable/')
 def download(item):
  path,url=item;record=data[path]
  photo=optimize(url,'portada-real-'+path.strip('/').replace('/','-'))
  photo.update(source=record['source'],alt=record['subject'],kind='product',label='Foto del fabricante')
  if path=='/soldadura-electronica/estacion-de-soldadura/':photo['alt']='Yihua serie 878, estación de cautín y aire caliente'
  if path=='/taladros/mecha-forstner-35-mm/':photo['alt']='Bosch Expert Forstner Wood 35 mm, 2608901837'
  return path,photo
 with ThreadPoolExecutor(max_workers=6) as pool:photos=dict(pool.map(download,choices.items()))
 Path('fotos-portadas-reales.json').write_text(json.dumps(photos,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Fotos reales preparadas:',len(photos))

if __name__=='__main__' and '--prepare' in sys.argv:
 prepare()
elif __name__=='__main__':
 with ThreadPoolExecutor(max_workers=6) as pool:results=dict(pool.map(discover,SOURCES.items()))
 Path('fuentes-portadas-reales.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
 for path,r in results.items():print(path,r.get('title'),r.get('candidates'),r.get('error'),r.get('all_images') if not r.get('candidates') else '')
