from pathlib import Path
import re

descriptions = {
'paginas/hidrolavadoras/01-hidrolavadoras.md': 'Compará cuatro fichas Gamma con las eléctricas Lüsqtoff HL100-7 y Logus HL-105. Separá presión nominal y máxima; evaluá Logus a nafta por su alimentación.',
'paginas/hidrolavadoras/03-hidrolavadoras-lusqtoff.md': 'Compará HL-120, HL100-8, HL110-9 y HL130-9 con la ficha propia de HL100-7. Diferenciá códigos, presión y condición de caudal antes de consultar su oferta.',
'paginas/taladros/01-taladro-inalambrico.md': 'Compará Bosch, Einhell y Black+Decker con el kit percutor Ingco anunciado. Revisá voltaje, mandril, baterías y qué datos del sufijo -4 faltan confirmar.',
'paginas/taladros/03-taladro-percutor.md': 'Elegí entre percusión y SDS por material, encastre y capacidades documentadas. Evaluá el kit Ingco sin atribuirle los datos de los ejemplos Bosch.',
'paginas/taladros/04-taladro-de-banco.md': 'Compará las fichas Lüsqtoff TB-16 y TBL710-9D con la oferta Omaha AB550161K: mandril, recorrido, velocidades y régimen publicado o pendiente.',
'paginas/10-amoladoras-bosch.md': 'Compará GWS 700, GWS 9-125 S, GWS 180-LI y la referencia GWS 770 por código, alimentación y disco. Confirmá variante y garantía de la oferta local.',
'paginas/compresores/01-compresor-de-aire-para-auto.md': 'Compará Lüsqtoff, Gadnic, Nictom IE01 y JD Extreme 107 por alimentación, conexión y controles. Distinguí batería, 12 V y construcción de doble pistón.',
'paginas/sierras/04-sierra-caladora.md': 'Compará BES603-B2, TC-JS 85 y TE-JS 100 por material y capacidad publicada. Confirmá el sufijo BES603; metal sin especificar no equivale a acero.',
'paginas/generadores/01-grupos-electrogenos.md': 'Compará nominal y máxima en fichas Honda/Gamma y evaluá ofertas Pektra/Philco por escala de carga. Conservá W, kVA y respaldo comercial separados.',
'paginas/generadores/02-precios-de-grupos-electrogenos.md': 'Revisá PVP Lüsqtoff capturados el 27/09/2026 y consultá ofertas Pektra/Philco sin precios recotizados. Calculá envío y extras con importes confirmados.',
}
for relative, description in descriptions.items():
    path=Path(relative)
    text=path.read_text(encoding='utf-8')
    text,count=re.subn(r'^description: "[^"]*"$', 'description: "'+description+'"',text,count=1,flags=re.M)
    assert count==1,relative
    path.write_text(text,encoding='utf-8')
print('Actualizadas las descripciones de las diez guías.')
