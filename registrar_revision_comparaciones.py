"""Registra evaluación de selecciones; no representa lectura integral ni ensayo."""
import hashlib,json
from pathlib import Path
import servidor_local as site
from auditar_modelos_por_guia import inventory

ROOT=Path(__file__).parent
rows=inventory();p=ROOT/'revision-editorial-por-tandas.json';ledger=json.loads(p.read_text(encoding='utf-8'))
specific={
 '/taladros/taladro-de-banco/':'TB-16 y TBL710-9D por recorrido, rpm, mesa y régimen S2; la oferta TBL16-7 requiere su código propio, no se equipara sin placa.',
 '/taladros/rotomartillo-bosch/':'GBH220/2-26/18V26/8-45 por energía y encastre. GBH180-LI es otra alternativa a batería; no recibe los 2,5 J del GBH18V26.',
 '/taladros/dewalt-inalambrico/':'DCD794B, DCD796D2-AR y DCD805D2 por percusión, kit y región. Oferta DCD805B es cuerpo, no kit D2.',
 '/taladros/milwaukee/':'M12 3403/3404 y M18 3601/2904 por percusión, plataforma y peso. 2904-259A es bundle del 2904-20; no atribuirle otro cuerpo.',
 '/taladros/mechas-escalonadas/':'Bosch 2608597524 y Högert HT6D323; afiliado Bosch 2608597519 conserva SKU diferente, sin asignarle los nueve pasos del 7524.',
 '/sierras/ingletadoras-einhell/':'Dos modelos fija/deslizante; se agregó TC-SM2131/2 Dual 4300390 al bloque con enlace oficial. Espacio de afiliado preparado.',
 '/sierras/ingletadoras-total/':'Dos códigos distintos TS42142107/TS42182553; segundo modelo agregado con catálogo. No sustituir por TS42182552. Espacio de afiliado preparado.',
 '/sierras/circulares-black-decker/':'CS1004-AR/CS1350P-AR; segundo modelo agregado con manual regional. No confundir con variantes BR de127V. Espacio de afiliado preparado.',
 '/sierras/bosch-gks-150/':'Tres modelos del cuadro ahora tienen oferta: GKS150/DWE560/SC16. Diámetro y eje específicos; no intercambiables.',
 '/sierras/sierra-circular-dewalt-dwe560/':'Tres modelos del cuadro ahora tienen oferta: DWE560/GKS150/SC16; capacidades desconocidas del DWE no se completan desde otra variante.',
 '/sierras/stanley-sc16/':'Tres modelos del cuadro ahora tienen oferta: SC16/GKS150/DWE560; discrepancia180/190mm permanece atribuida a documentos, sin montar un disco por inferencia.',
 '/sierras/sensitivas-lusqtoff/':'Añadida alternativa TOTAL de355mm para comparar geometría y consumible. CM14K-9 discontinuada no recibe kit/peso CM-14K.',
 '/sierras/sensitivas-total/':'Añadida alternativa CM-14K de355mm; código base TS223558 no se equipara al sufijo-4 sin placa. Ambas ofertas y fotos ya registradas.',
 '/soldadoras/electrodo-para-fundicion/':'Comparación Ni-CI/NiFe-CI por grado, aplicación, composición y diámetro. Dos fichas primarias en tabla; falta afiliado OKNiFe-CI exacto. Imagen genérica VacPac consultada y descartada para no atribuir un empaque sin identificación de referencia.',
 '/soldadoras/alambre-para-soldadura-mig/':'Bremen ER70S-6 frente a ejemplos Weld70S6/308LSi/4043. No añadir alambre inoxidable/aluminio como reemplazo barato de acero al carbono; presentaciones industriales no garantizan entrada en bobina compacta.',
 '/soldadoras/lusqtoff-sml150-8/':'SML150-8/8D por proceso, ciclo y discontinuación; compra 8D y alternativa120DK sin atribuirle la generación8.',
 '/soldadoras/tig/':'Comparación DC/ACDC y red220/380. ST200 discontinuado conserva referencia documental; SmartTIG alternativaACDC. No inferir AC desde palabraTIG.',
}
assessment=[]
for row in rows:
 article=next(a for a in site.ALL_ARTICLES if a['url']==row['path'])
 tables=row['tables'];notes=specific.get(row['path'],'Evaluadas las selecciones y tablas: '+ '; '.join(t['heading'] or 'cuadro inicial' for t in tables)+'. Opciones de compra: '+('; '.join(row['cards']) if row['cards'] else 'enlaces en tablas o fichas por modelo; no se fuerza un bloque de tarjetas')+'. La elección conserva clases, variantes y aplicaciones documentadas por separado.')
 if row['path'] not in ledger:
  ledger[row['path']]=dict(checked='2026-10-02',batch=row['section']+'-comparaciones-02',body_sha256=hashlib.sha256(article['body'].encode()).hexdigest(),scope='evaluación individual de tablas, modelos, selección y opciones; no lectura integral de todos los párrafos',notes=notes,full_claim_verification='contrastes selectivos; no ensayo ni certificación de stock')
 elif 'evaluación individual de tablas' in ledger[row['path']]['scope'] or row['section']=='sierras' and row['path'] in specific:
  ledger[row['path']].update(body_sha256=hashlib.sha256(article['body'].encode()).hexdigest(),notes=notes)
 elif row['section']=='sierras' and ledger[row['path']]['body_sha256']!=hashlib.sha256(article['body'].encode()).hexdigest():
  ledger[row['path']].update(body_sha256=hashlib.sha256(article['body'].encode()).hexdigest(),commercial_followup='2026-10-02: bloque comercial regenerado; tablas y encabezados técnicos preservados, enlaces y plural de comparación verificados.')
 assessment.append(dict(path=row['path'],section=row['section'],models_in_cards=row['cards'],comparison_tables=tables,decision=notes,scope='selección y comparación de modelos; fotos, enlaces e interacciones verificados por pruebas separadas'))
p.write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'revision-comparaciones-179-2026-10-02.json').write_text(json.dumps(assessment,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ROOT/'afiliados-por-completar.json';slots=json.loads(p.read_text(encoding='utf-8'));slots['BLACK+DECKER CS1350P-AR']=dict(affiliate_url='',guides=['/sierras/circulares-black-decker/'],configuration='Variante AR de220V; manual enlazado. No sustituir por BR127V');slots['ESAB OK NiFe-CI 3,2 mm']=dict(affiliate_url='',guides=['/soldadoras/electrodo-para-fundicion/'],configuration='ENiFe-CI, código92603230L0 según ficha europea; confirmar presentación local y código');p.write_text(json.dumps(slots,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(len(assessment),'selecciones individuales;',len(slots),'espacios de afiliado')
