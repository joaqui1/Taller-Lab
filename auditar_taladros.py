from pathlib import Path
import json, re

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'taladros'
DATA_FILE = ROOT / 'analisis-taladros' / 'datos.json'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
specs = data['pages']

filenames = {
    1: "01-taladro-inalambrico.md",
    2: "02-rotomartillo.md",
    3: "03-taladro-percutor.md",
    4: "04-taladro-de-banco.md",
    5: "05-atornillador-de-impacto.md",
    6: "06-rotomartillo-bosch.md",
    7: "07-taladro-percutor-inalambrico.md",
    8: "08-atornillador-para-durlock.md",
    9: "09-taladro-black-decker.md",
    10: "10-rotomartillo-einhell.md",
    11: "11-rotomartillo-dewalt.md",
    12: "12-taladro-inalambrico-einhell.md",
    13: "13-taladro-inalambrico-dewalt.md",
    14: "14-mecha-para-porcelanato.md",
    15: "15-taladro-milwaukee.md",
    16: "16-taladro-inalambrico-lusqtoff.md",
    17: "17-brocas-para-ceramica.md",
    18: "18-taladro-stanley.md",
    19: "19-atornillador-de-impacto-dewalt.md",
    20: "20-taladro-inalambrico-bosch.md",
}

errors = []
success_count = 0

for spec in specs:
    pid = spec['id']
    filename = filenames[pid]
    filepath = PAGES_DIR / filename
    
    if not filepath.exists():
        errors.append(f"Archivo no encontrado: {filename}")
        continue
        
    content = filepath.read_text(encoding='utf-8')
    
    # Check frontmatter
    if not content.startswith('---\n'):
        errors.append(f"{filename}: Falta apertura de frontmatter")
        continue
    
    fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not fm_match:
        errors.append(f"{filename}: Frontmatter mal formado")
        continue
        
    fm_text = fm_match.group(1)
    
    for req_key in ['title:', 'h1:', 'url:', 'description:', 'author:', 'category:', 'keywords:']:
        if req_key not in fm_text:
            errors.append(f"{filename}: Falta clave en frontmatter: {req_key}")
            
    # Check Title and H1 match
    if f'title: "{spec["title"]}"' not in fm_text:
        errors.append(f"{filename}: Title no coincide exactamente con el spec (Esperado: '{spec['title']}')")
        
    if f'h1: "{spec["h1"]}"' not in fm_text:
        errors.append(f"{filename}: H1 en frontmatter no coincide exactamente (Esperado: '{spec['h1']}')")
        
    if f'# {spec["h1"]}' not in content:
        errors.append(f"{filename}: H1 en cuerpo de markdown no encontrado (Esperado: '# {spec['h1']}')")
        
    # Check all H2s
    for h2 in spec['h2']:
        if f"## {h2}" not in content:
            errors.append(f"{filename}: Falta sección H2: '## {h2}'")
            
    # Check Mercado Libre link
    if 'listado.mercadolibre.com.ar' not in content or 'rel="sponsored"' not in content:
        errors.append(f"{filename}: Falta enlace de afiliación a Mercado Libre con rel=\"sponsored\"")
        
    # Check substantial body content (> 400 words)
    words = len(content.split())
    if words < 400:
        errors.append(f"{filename}: Contenido demasiado corto ({words} palabras)")
        
    success_count += 1

print(f"Total especificaciones: {len(specs)}")
print(f"Páginas verificadas con éxito: {success_count}")

if errors:
    print(f"\nERRORES ENCONTRADOS ({len(errors)}):")
    for err in errors:
        print(f" - {err}")
    exit(1)
else:
    print("\nTODAS LAS 20 PÁGINAS CUMPLEN EL 100% DE LAS ESPECIFICACIONES TÉCNICAS Y EDITORIALES.")
