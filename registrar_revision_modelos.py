"""Deja una decisión trazable por artículo, además de las selecciones ampliadas."""
import json
from pathlib import Path
from comparaciones_por_guia import PLANS, EXISTING

ROOT=Path(__file__).parent
EXCEPTIONS={
 '/compresores/manguera/':'Conservar criterios de diámetro interior, longitud y caudal. La conexión roscada no identifica una manguera compatible para todos los equipos.',
 '/compresores/acoples-rapidos/':'Conservar comparación de perfiles, roscas y medidas; no añadir conectores sin identificar el perfil de ambas mitades.',
 '/compresores/aceite/':'Conservar los ejemplos por código y manual; no presentar aceites como sustitutos universales.',
 '/compresores/filtros/':'Conservar la separación entre admisión y línea; la compra depende del código, micronaje y drenaje.',
 '/compresores/gamma-50-litros/':'Ya contrasta G2802AR y G2802KAR en el documento. Los referidos siguen pendientes; no convertir el compresor en un kit sin acreditar contenido.',
 '/compresores/para-aerografo/':'Mantener los cinco modelos documentados y sus requisitos; los referidos Fengda pendientes no acreditan un kit comprable.',
 '/compresores/kits-aerografo/':'La elección combina aerógrafo, compresor y conexiones por tarea; conservar ejemplos documentados sin inventar un kit completo.',
 '/soldadoras/lusqtoff/':'Conservar alternativas MMA, MIG/MAG y Flux separadas por proceso. La selección MMA ya permite contrastar kits; no comparar fuentes distintas solo por amperios.',
 '/soldadoras/esab/':'Conservar las secciones MMA, MIG/MAG y TIG y las referencias de gama. Un enlace de compra por proceso no equivale a una comparación entre procesos intercambiables.',
 '/soldadoras/alambre-para-soldadura-mig/':'La guía compara clasificación, diámetro, gas y sistema de arrastre. Conservar la referencia ER70S-6 de 0,8 mm sin presentar diámetros o aleaciones distintos como reemplazos directos.',
 '/soldadoras/electrodo-para-fundicion/':'La tabla ya contrasta OK Ni-CI y OK NiFe-CI. La oferta de OK 92.18 exige cotejar clasificación y no acredita stock de NiFe; conservar esa distinción.',
 '/soldadoras/soldadora-dogo-180/':'Ya compara Dogo 160, 180 y 200 en la sección contextual. Conservar la oferta individual de 180 y las alternativas, sin duplicarlas en el mismo bloque.',
 '/soldadoras/lusqtoff-iron-250/':'Ya ofrece Iron 250, Dogo 180 y HandyArc 162i con diferencias y límites. La tarjeta individual del kit se conserva dentro de ese recorrido.',
 '/soldadoras/lusqtoff-iron-100/':'Ya contrasta Iron 100, Iron 250 y HandyArc 162i, distinguiendo generaciones y kits. Mantener esas alternativas.',
 '/soldadoras/esab-handyarc-162i/':'Ya contrasta HandyArc 162i, Dogo 160 y Dogo 180. Mantener límites de corriente por ciclo y accesorios.',
 '/soldadoras/soldadora-inverter-160-amp/':'Ya compara MMA HandyArc 162i y Dogo 160. La MIG 160i se conserva como alternativa de otro proceso, separada de la comparación MMA.',
 '/soldadoras/lusqtoff-sml130-7/':'El modelo principal está discontinuado; conservar la explicación y las alternativas SML120/SML150 sin simular stock del SML130.',
 '/generadores/gamma-6500/':'Conservar comparación histórica y actuales 6000V/7500V. No convertir referencias discontinuadas en ofertas actuales.',
 '/generadores/gamma-950/':'Conservar la ficha específica y la discrepancia de potencia. No sustituir una unidad 2T por un generador de otra escala sin calcular cargas.',
 '/taladros/combo-taladro-amoladora/':'Conservar los kits regionales explícitos; no presentar herramientas sueltas como combo ni trasladar disponibilidad de kits europeos a Argentina.',
 '/taladros/mecha-forstner-35-mm/':'La decisión se basa en el herraje y sus cotas: conservar diámetro, profundidad y borde sin añadir otra medida como sustituto.',
 '/soldadura-electronica/gadnic-878d/':'Conservar la discrepancia entre potencias y la distinción respecto de YiHUA. El nombre 878D no acredita equivalencia entre fabricantes.',
 '/soldadura-electronica/yihua-898d/':'Ya distingue 898D, 898D+ y 878D por funciones y variante. Mantener las referencias de fabricante sin mezclar sus kits.',
}

def main():
    rows=json.loads((ROOT/'auditoria-modelos-por-guia.json').read_text(encoding='utf-8'))
    ledger=json.loads((ROOT/'revision-editorial-por-tandas.json').read_text(encoding='utf-8'))
    count=sum(len(plan['models']) for plan in PLANS.values())
    commercial=sum(key in EXISTING for plan in PLANS.values() for key in plan['models'])
    lines=['# Revisión de modelos por artículo — 01/10/2026','',
           f'El inventario contiene las {len(rows)} guías; inventariar tablas y enlaces no equivale a leer y evaluar cada artículo. Se amplían {len(PLANS)} selecciones explícitas con {count} tarjetas: {commercial} enlaces comerciales ya suministrados y {count-commercial} referencias documentadas de fabricante. La lectura editorial por URL se registra aparte y continúa en curso. La disponibilidad local de las fichas extranjeras queda pendiente.', '',
           '## Selecciones ampliadas','']
    results=[]
    for row in rows:
        path=row['path']
        if path in PLANS:
            decision='Ampliar';reason=PLANS[path]['reason']
        elif path in EXCEPTIONS:
            decision='Criterio propuesto';reason=EXCEPTIONS[path]
        else:
            decision='Pendiente';reason='Evaluar las alternativas del artículo según su alcance: '+row['description']
        if path in ledger and path not in PLANS:
            decision='Lectura registrada';reason=ledger[path]['notes']
        results.append(dict(path=path,title=row['title'],decision=decision,reason=reason,tables=row['tables'],cards_before=row['cards']))
        if decision=='Ampliar':
            lines.append('- ['+row['title']+'](https://www.tallerlab.com.ar'+path+'): '+reason)
    lines+=['','## Evaluación y pendientes de las demás guías','']
    for row in results:
        if row['decision']!='Ampliar':
            lines.append('- ['+row['title']+'](https://www.tallerlab.com.ar'+row['path']+'): **'+row['decision']+'**. '+row['reason'])
    (ROOT/'revision-modelos-por-articulo-2026-10-01.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (ROOT/'decisiones-modelos-por-articulo.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print('179 guías inventariadas; 18 selecciones ampliadas. Las evaluaciones pendientes se mantienen explícitas.')

if __name__=='__main__':main()
