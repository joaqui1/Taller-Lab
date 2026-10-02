"""Verifica la selección, la procedencia y la explicación de cada artículo ampliado."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
import servidor_local as site
from comparaciones_por_guia import PLANS, MODELS, EXISTING
from fotos_productos import PHOTOS

def main():
    articles={a['url']:a for a in site.ALL_ARTICLES}
    rows=[]
    for path,plan in PLANS.items():
        article=articles[path]
        selected=site.guide_comparison_selection(path,article['section'],site.PRODUCT_FACTS)
        expected=[item[2] for _,item in selected]
        assert len(expected)>=2 and len(expected)==len(set(expected)),path
        soup=BeautifulSoup(site.render_article_page(article),'html.parser')
        blocks=soup.select('[data-guide-comparison]')
        assert len(blocks)==1,path
        cards=blocks[0].select('.offer-card')
        assert [card['data-product'] for card in cards]==expected,path
        assert plan['reason'] in blocks[0].get_text(),path
        for card,url in zip(cards,expected):
            image=card.select_one('.offer-photo img')
            assert image and image['src'].startswith('/assets/productos/'),(path,url)
            assert image['src'] in {p['image'] for p in PHOTOS.values()},(path,url)
            assert card.select_one('.compare-checkbox'),(path,url)
            assert len(json.loads(card['data-compare-details']))==3,(path,url)
            action=card.select_one('.offer-button')
            assert action['href']==url,(path,url)
            if url not in site.AFFILIATE_URLS:
                assert site.PRODUCT_FACTS[url]['cta'] in action.get_text(),(path,url)
                assert not action.get('data-affiliate-placement') and 'sponsored' not in action.get('rel',[]),(path,url)
                assert 'MODELO DOCUMENTADO' in card.get_text(),(path,url)
        if path.startswith('/compresores/'):
            original=[offer['url'] for offer in site.COMPRESORES_OFFERS[path]['offers']]
        elif path.startswith('/hidrolavadoras/'):
            original=[offer['url'] for offer in site.HIDROLAVADORAS_OFFERS[path]['offers']]
        else:
            original=[offer['url'] for offer in (site.TALADROS_OFFERS if path.startswith('/taladros/') else site.SOLDADORAS_OFFERS)[path]['offers']]
        assert set(original)<=set(expected),(path,'Oferta anterior retirada')
        rows.append(dict(path=path,models=[card.select_one('h3').get_text(' ',strip=True) for card in cards],original_offers=len(original),count=len(cards),reason=plan['reason'],documented=sum(u not in site.AFFILIATE_URLS for u in expected)))
    report=dict(articles_reviewed=len(articles),expanded=len(rows),cards=sum(r['count'] for r in rows),documented_cards=sum(r['documented'] for r in rows),failures=[],rows=rows)
    Path('qa-comparaciones-por-guia.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False))

if __name__=='__main__':main()
