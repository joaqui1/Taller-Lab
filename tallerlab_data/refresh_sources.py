"""Read public sources and retain documentary evidence; never mark specifications as tested."""
import sys, json, sqlite3, hashlib, re, io
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tmp/auditoria-observatorio-deps'))
sys.path.insert(0,str(ROOT/'.qa-deps'))
import requests
from bs4 import BeautifulSoup
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader=None
dest=ROOT/'tallerlab_data/data/documentos'
dest.mkdir(exist_ok=True)
def retired_redirect(requested, final):
    """A product URL answering 200 after redirecting to a listing is a soft 404."""
    from urllib.parse import urlparse
    a, b = urlparse(requested), urlparse(final or requested)
    if a.netloc.replace('www.', '') != b.netloc.replace('www.', ''):
        return False
    pa, pb = a.path.rstrip('/'), b.path.rstrip('/')
    return pa != pb and (pb in {'', '/categorias', '/productos', '/catalogo'} or pb.count('/') < pa.count('/'))


def fetch(url):
    record={'url':url,'checked_at':datetime.now(timezone.utc).isoformat()}
    publisher_path = ROOT/'tallerlab_data/data/source_publishers.json'
    publishers = json.loads(publisher_path.read_text(encoding='utf-8')) if publisher_path.exists() else {}
    if url in publishers:
        record['publisher_url'] = publishers[url]
    try:
        r=requests.get(url,timeout=22,headers={'User-Agent':'TallerLab/1.0 documentary research; https://www.tallerlab.com.ar/contacto/'})
        record.update(http_status=r.status_code,final_url=r.url)
        if r.status_code!=200:
            return {**record,'status':'no_recuperado','reason':f'HTTP {r.status_code}'}
        content=r.content
        pdf=content.startswith(b'%PDF')
        if pdf and PdfReader:
            reader=PdfReader(io.BytesIO(content))
            pages=[page.extract_text() or '' for page in reader.pages]
            text='\n'.join(f'\n[PÁGINA {i+1}]\n{p}' for i,p in enumerate(pages))
            record['pages']=len(pages)
        elif pdf:
            text=''
        else:
            soup=BeautifulSoup(content,'html.parser')
            record['title']=soup.title.get_text(' ',strip=True) if soup.title else ''
            for tag in soup(['script','style','nav','footer','header']): tag.decompose()
            text=soup.get_text(' ',strip=True)
        challenge=any(x in text.lower() for x in ['verify you are human','access denied','just a moment...','captcha'])
        if retired_redirect(url, r.url):
            return {**record,'status':'no_recuperado','reason':'Redirige a un listado general: página del producto retirada'}
        if pdf and len(text.strip())<500:
            return {**record,'status':'no_recuperado','reason':'PDF sin texto extraíble (escaneado); requiere transcripción u OCR'}
        if len(text)<100 or challenge or any(x in record.get('title', '').lower() for x in ['la gama de productos einhell', 'mercado libre']):
            return {**record,'status':'no_recuperado','reason':'Respuesta sin documento legible o con control de acceso'}
        key=hashlib.sha256(url.encode()).hexdigest()[:20]
        (dest/f'{key}.txt').write_text(text,encoding='utf-8')
        record.update(status='recuperado',text_file=f'documentos/{key}.txt',sha256=hashlib.sha256(content).hexdigest(),text_sha256=hashlib.sha256(text.encode()).hexdigest(),characters=len(text),format='pdf' if pdf else 'html')
        return record
    except Exception as exc:
        return {**record,'status':'no_recuperado','reason':type(exc).__name__+': '+str(exc)[:180]}
def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--additional-only', action='store_true', help='Recuperar solo fuentes nuevas conservando el inventario anterior')
    args = parser.parse_args()
    output=ROOT/'tallerlab_data/data/documentary_sources.json'
    records=json.loads(output.read_text(encoding='utf-8'))['sources'] if output.exists() else []
    extra_path=ROOT/'tallerlab_data/data/additional_sources.json'
    urls=set(json.loads(extra_path.read_text(encoding='utf-8'))) if extra_path.exists() else set()
    if not args.additional_only:
        from tallerlab_data import storage
        db=storage.get_connection()
        urls.update(r[0] for r in db.execute('select distinct source_url from tool_specs') if r[0])
        for (raw,) in db.execute('select primary_sources_json from tools'):
            urls.update(s['url'] for s in json.loads(raw) if isinstance(s,dict) and s.get('url'))
        db.close()
    else:
        urls.difference_update(r['url'] for r in records)
    with ThreadPoolExecutor(max_workers=8) as pool:
        fresh=list(pool.map(fetch,sorted(urls)))
    merged={r['url']:r for r in records}
    merged.update({r['url']:r for r in fresh})
    records=[merged[k] for k in sorted(merged)]
    output.write_text(json.dumps({'scope':'Recuperación documental; no acredita ensayo ni validación automática de cada cifra','sources':records},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sources':len(records),'retrieved':sum(r['status']=='recuperado' for r in records),'new_sources':[{k:v for k,v in r.items() if k in {'url','status','reason','pages'}} for r in fresh]},ensure_ascii=True))


if __name__ == '__main__':
    main()
