"""Selecciones revisadas para fichas que devuelven banners, piezas o despieces."""
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json
import re
from preparar_fotos_modelos import ROOT, REPORT, page, optimize, candidates

# La selección explícita evita confundir el modelo con repuestos de igual prefijo.
SELECTIONS = {
 'https://meli.la/2SvkJCm': ('https://www.kaercher.com/ar/home-garden/hidrolavadora/k4-93982940.html', 'mainproduct'),
 'https://meli.la/2oUJyrQ': ('https://ar.blackanddecker.global/producto/cs1004-ar/sierra-circular-1400-w', '/CS1004_1.jpg'),
 'https://meli.la/1hh4SkK': ('https://www.dewalt.com/en-us/node/32266', 'DCF887'),
 'https://meli.la/1ruBvJN': ('https://www.todoferreteria.com/products/view/2472.html', '9004'),
 'https://meli.la/1uvMFdz': ('https://ferreterasanluis.com/p/hidrolavadora-de-alta-presion-2100w-60lts-lusqhl110-9', '/43561/1_original.webp'),
 'https://meli.la/2uoDsq6': ('https://www.arcomaquinarias.com/index.php/producto/50005410-mascara-fotosensible-lusqtoff-st-1x-compacta', 'BrizGxe640.jpg'),
 'https://meli.la/2XU7X44': ('https://www.bosch-professional.com/es/es/broca-expert-hex-9-hard-ceramic-2867225-ocs-ac/', '2608902308_bo_pro_u_f_1'),
 'https://meli.la/2wKN4UX': ('https://www.bosch-professional.com/es/es/broca-cyl-9-soft-ceramic-7724656-ocs-ac/', '2608707346_bo_pro_u_f_1'),
 'https://meli.la/1khPuL9': ('https://www.bosch-professional.com/ar/es/disco-de-corte-con-diamantes-pro-ceramic-para-amoladoras-angulares-pequenas-orificio-de-22-23-mm-3088608-ocs-ac/', '2608602478.png'),
 'https://meli.la/1tL91SZ': ('https://www.bosch-professional.com/ar/es/disco-de-desbaste-pro-metal-para-amoladoras-angulares-pequenas-22-23-mm-2869103-ocs-ac/', '2608600218'),
 'https://meli.la/127ZaQu': ('https://ferreterasanluis.com/p/compresor-aire-bicilindrico-100-lts-4hp-lusqtoff-lc40100', 'product'),
 'https://meli.la/2W1Y9Zs': ('https://btatools.com.ar/producto/kit-de-aire-multiuso-5-piezas-alimentacion-por-gravedad', '279010'),
 'https://meli.la/2KQQEjE': ('https://www.dogoherramientas.com.ar/tienda/soldadura/inverter/soldadora-inverter-dogostar-180-moderna-mma', '500_500-SOLDADORAINVERTER-DOGOSTAR-180.jpg'),
 'https://meli.la/1b2mqhW': ('https://pe.stanleytools.global/producto/sdh700/taladro-de-martillo-de-700-w-13-mm', 'SDH700'),
 'https://meli.la/1zzNj8Z': ('https://ar.blackanddecker.global/producto/bepw1300-ar/hidrolavadora-1300-psi-1200w', '/BEPW1300_1.'),
 'https://meli.la/1x65DAe': ('https://tradermotorstore.com.ar/producto/amoladora-angular-dowen-pagio-vel-variable-115-y-125mm-1250w/', 'gallery'),
 'https://meli.la/2zYHZrk': ('https://www.kregtool.com/support/faqs-product-info/discontinued-products/rip-cut/KMA2685.html', 'KMA2685'),
}

def main():
 d=json.loads(REPORT.read_text(encoding='utf-8'))
 def work(entry):
  key,(source,match)=entry
  current=d['products'][key]
  # Las selecciones posteriores ya verificadas no se reemplazan por una
  # búsqueda histórica que puede haber dejado de devolver la ficha correcta.
  if current.get('image') and current.get('status') in ('verified', 'verified-offer'):
   return key,current
  model=current.get('model','')
  try:
   soup=BeautifulSoup(page(source),'html.parser')
   values=[]
   for node in soup.find_all('img'):
    for field in ['src','data-src','data-large_image']:
     value=node.get(field,'')
     if value and (match.lower() in value.lower() or match.lower() in node.get('alt','').lower()):values.append(urljoin(source,value))
   values+= [urljoin(source,v) for v in re.findall(r'["\']([^"\']+\.(?:png|jpg|webp)(?:\?[^"\']*)?)["\']',str(soup)) if match.lower() in v.lower()]
   values=list(dict.fromkeys(values))
   if not values:
    values=[v for v in candidates(model,source) if match.lower() in v.lower()]
   values=[v for v in values if not any(x in v.lower() for x in ['icon-image','logo','fallback','banner','127x','137x','100x100'])]
   if match=='product':
    values=[]
    m=soup.select_one('meta[property="og:image"]')
    if m: values=[urljoin(source,m.get('content',''))]
   if match=='gallery':
    values=[urljoin(source,i.get('data-large_image') or i.get('src','')) for i in soup.select('.woocommerce-product-gallery__image img')]
   if not values:raise ValueError('No se localizó foto de producto')
   image=optimize(values[0],'revision-'+key.split('/')[-1])
   return key,dict(status='review',brand=current.get('brand',''),model=model,source=source,checked='2026-10-01',**image)
  except Exception as e:
   if current.get('image'):
    return key,current
   return key,dict(status='pending',brand=current.get('brand',''),model=model,reason='Foto anterior descartada en revisión visual',source=source,error=type(e).__name__)
 with ThreadPoolExecutor(max_workers=6) as pool:
  for key,result in pool.map(work,SELECTIONS.items()):
   d['products'][key]=result
   print(key,result['status'],result.get('original_image',''),flush=True)
 d['products']['https://meli.la/11Nc9wu']=dict(d['products']['https://meli.la/1QUvfns'],model='Pagio 9993220.7 / AA115H4',brand='Dowen')
 REPORT.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
