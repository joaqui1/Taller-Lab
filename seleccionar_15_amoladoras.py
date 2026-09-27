import csv, json
from pathlib import Path

out=Path(__file__).parent/'analisis-amoladoras'
data=json.loads((out/'plan-estructurado.json').read_text(encoding='utf-8'))
with Path(r'C:\Users\joaqu\Desktop\keywords\keywords_amoladora.csv').open(encoding='utf-8-sig',newline='') as f:
    ads={r['Keyword']:r['Avg. monthly searches'] for r in csv.DictReader(f)}
measured={r['keyword']:r for r in data['measured']}
selected=[(3,'disco flap'),(5,'disco de corte para amoladora'),(7,'amoladora dewalt'),(4,'disco de desbaste'),(6,'amoladora recta'),(2,'amoladora de banco'),(8,'amoladora makita'),(15,'amoladora inalambrica'),(17,'disco para cortar ceramica'),(14,'amoladora bosch'),(21,'amoladora lusqtoff'),(11,'amoladora 9 pulgadas'),(16,'amoladora skil 830w'),(26,'disco diamantado segmentado'),(9,'amoladora stanley')]
text=['# Las 15 páginas de amoladoras seleccionadas por volumen Ads y KD\n\nActualización: 23/09/2026. Esta selección sustituye la propuesta de 30 páginas como alcance inicial.\n\nSe prioriza primero la banda de 5.000 de Google Ads con KD hasta 18. Después se seleccionan tres consultas de 500 y KD 5, y Stanley (500/KD 8) frente a otras empatadas por su mayor volumen Semrush. No se divide volumen por KD: KD no es una escala lineal de esfuerzo ni una probabilidad de posicionar. El orden de la tabla sigue banda Ads, KD y, en los empates, volumen Semrush.\n\nLos valores Ads son exactamente los del CSV y están muy agrupados (50, 500, 5.000 y 50.000): no representan precisión suficiente para proyectar visitas. El volumen Semrush se incluye para contrastar. Cada KD pertenece a la consulta exacta indicada, no al conjunto de variantes ni a todos los H2. Mercado asumido: Argentina; falta confirmar país de la exportación Semrush.\n\n| Nº | Keyword exacta | Volumen Ads | Volumen Semrush | KD |\n|---:|---|---:|---:|---:|\n']
briefs=[]
for i,(pid,k) in enumerate(selected,1):
    p=dict(data['pages'][pid-1]); s=measured[k]; a=int(float(ads[k]))
    text.append(f'| {i} | {k} | {a:,}'.replace(',','.')+f" | {int(s['volume']):,}".replace(',','.')+f" | {s['kd']} |\n")
    if pid==16:
        p.update(title='Amoladora Skil de 830 W: qué revisar antes de comprar',h1='Amoladora Skil de 830 W: prestaciones y diferencias frente a 700 W',h2=['Cómo identificar el modelo Skil de 830 W','Diámetro, potencia y equipamiento según la ficha oficial','Qué cambia frente a las opciones Skil de 700 W','Para qué trabajos está indicada y cuáles son sus límites','Qué incluye la publicación y dónde consultar precio'])
    if pid==26:
        p.update(title='Disco diamantado segmentado: usos y cómo elegir',h1='Disco diamantado segmentado: para qué sirve y cuándo elegirlo',h2=['Qué caracteriza a un disco diamantado segmentado','Qué materiales admite cada referencia','Diferencias frente a los discos turbo y continuos','Diámetro, eje, RPM y corte seco o húmedo','Qué revisar antes de comprar un disco compatible'])
    briefs.append(f"\n## {i}. {k}\n\n**Volumen Ads:** {a:,} · **KD:** {s['kd']} · **Volumen Semrush:** {s['volume']}\n\n**URL propuesta:** `{p['url']}`\n\n**Title:** {p['title']}\n\n**H1:** {p['h1']}\n\n**H2:**\n\n".replace(f'{a:,}',f'{a:,}'.replace(',','.'))+'\n'.join('- '+h for h in p['h2'])+'\n')
text.extend(briefs)
text.append('''
## Publicación y agrupación

Para arrancar producción priorizaría disco flap, banco, discos para amoladora, desbaste y recta; después las comparativas de marcas y el resto de esta selección. KD bajo por sí solo no asegura espacio para guías en búsquedas dominadas por tiendas: el muestreo previo fue orientativo y falta validar cada SERP local antes de producir.

Conservar una URL por tema: batería e inalámbrica van juntas; recta y neumática se diferencian dentro de una guía; las variantes ortográficas de DeWalt o los granos de flap no justifican páginas separadas. Los modelos de cada marca empiezan como secciones. La guía Skil compara 830 y 700 W sin asumir que son el mismo modelo. No asignar el KD 5 de segmentado a todo el tema diamantados.

Estas son 15 páginas objetivo de captación. Si el sitio necesita un índice de navegación para amoladoras, puede integrarse en la estructura existente; no se agrega aquí una guía genérica de volumen bajo para completar el número.

La salida a Mercado Libre debe corresponder al modelo, kit o disco explicado, con botón “Ver precio en Mercado Libre”. No publicar importes sin actualización, opiniones inventadas ni afirmar pruebas no realizadas. Si el enlace genera comisión, informar la afiliación y usar rel="sponsored". No se seleccionaron publicaciones ni se verificó stock.

## Fuentes

- [Google Ads: keywords_amoladora.csv](C:/Users/joaqu/Desktop/keywords/keywords_amoladora.csv)
- [Semrush: amoladoras](C:/Users/joaqu/Desktop/keywords/semrush/semrush_amoladoras.csv)
- [Semrush: consultas adicionales](C:/Users/joaqu/Desktop/keywords/semrush/semrush_consulta_adicional.csv)

Las fuentes se conservaron sin cambios. La selección contiene 15 keywords distintas, 15 URLs distintas y KD exactos entre 5 y 18.
''')
assert len(selected)==15 and len({x[0] for x in selected})==15
assert all(k in ads and k in measured for _,k in selected)
report=''.join(text)
assert report.count('**Title:**')==15 and report.count('**H1:**')==15
(out/'15-paginas-prioritarias-amoladoras.md').write_text(report,encoding='utf-8')
print('Verificado: 15 páginas con volumen Ads y KD exactos; 15 titles, H1 y esquemas H2.')
