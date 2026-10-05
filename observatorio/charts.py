"""SVG accesible; los segmentos se interrumpen en días sin captura."""
from collections import defaultdict
from datetime import date
from html import escape

def render_history_chart(series, label):
    if not series:
        return '<p class="obs-empty">Todavía no hay capturas reales publicables para este modelo.</p>'
    prices=[r['price'] for r in series if r['price'] is not None]
    if not prices: return '<p>Sin precios publicables.</p>'
    dates=sorted(date.fromisoformat(r['day']) for r in series)
    first,last=dates[0],dates[-1]; span=max(1,(last-first).days)
    low,high=min(prices),max(prices); padding=max((high-low)*.1,high*.03,1)
    low,high=max(0,low-padding),high+padding
    x=lambda d:75+(date.fromisoformat(d)-first).days/span*585
    y=lambda p:205-(p-low)/(high-low)*170
    groups=defaultdict(list)
    for r in series: groups[r['offer_id']].append(r)
    marks=[]; legend=[]; table=[]
    for n,rows in enumerate(groups.values()):
        color=('#38bdf8','#fb923c','#a3e635','#e879f9')[n%4]; segment=[]
        seller=escape(rows[0]['seller'])
        legend.append(f'<span><i style="background:{color}"></i>{seller}</span>')
        for r in rows:
            if r['price'] is None:
                if len(segment)>1: marks.append(f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
                segment=[]; continue
            px,py=x(r['day']),y(r['price']); segment.append(f'{px:.1f},{py:.1f}')
            title=escape(f"{r['day']} · {r['seller']} · $ {r['price']:,.2f}")
            marks.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{color}"><title>{title}</title></circle>')
            table.append(f'<tr><td>{r["day"]}</td><td>{seller}</td><td>$ {r["price"]:,.2f}</td></tr>')
        if len(segment)>1: marks.append(f'<polyline points="{" ".join(segment)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
    ticks=''.join(f'<text x="67" y="{y(low+(high-low)*n/2):.1f}" text-anchor="end" fill="#94a3b8" font-size="12">{low+(high-low)*n/2:,.0f}</text>' for n in range(3))
    return f'''<figure class="obs-chart"><svg viewBox="0 0 700 250" role="img" aria-label="{escape(label,quote=True)}: precios en pesos argentinos por vendedor">
    <desc>Capturas reales. Los días sin datos interrumpen las líneas.</desc><path d="M75 25 V210 H670" fill="none" stroke="#475569"/>{ticks}{''.join(marks)}
    <text x="75" y="238" fill="#94a3b8" font-size="12">{first}</text><text x="660" y="238" text-anchor="end" fill="#94a3b8" font-size="12">{last}</text></svg>
    <figcaption><div class="obs-legend">{''.join(legend)}</div><p>ARS · una captura por día y vendedor · últimos 365 días · sin interpolación.</p></figcaption>
    <details><summary>Ver valores del gráfico</summary><div class="table-scroll"><table><thead><tr><th>Fecha ART</th><th>Vendedor</th><th>Precio ARS</th></tr></thead><tbody>{''.join(table)}</tbody></table></div></details></figure>'''
