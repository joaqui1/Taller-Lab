from pathlib import Path
import json, re

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'sierras'
DATA_FILE = ROOT / 'analisis-sierras' / 'datos.json'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
specs = data['pages']

filenames = {
    1: "01-sierra-circular.md",
    2: "02-sensitiva.md",
    3: "03-sierra-sable.md",
    4: "04-sierra-caladora.md",
    5: "05-sierra-sin-fin-para-madera.md",
    6: "06-sierra-de-banco.md",
    7: "07-sierra-sin-fin-para-metal.md",
    8: "08-ingletadora-einhell.md",
    9: "09-sierra-de-banco-einhell.md",
    10: "10-caladora-skil.md",
    11: "11-guia-para-sierra-circular.md",
    12: "12-sensitiva-dewalt.md",
    13: "13-ingletadora-dewalt.md",
    14: "14-ingletadora-total.md",
    15: "15-disco-para-sierra-circular.md",
    16: "16-sierra-circular-bosch-gks-150.md",
    17: "17-sierra-circular-black-and-decker.md",
    18: "18-caladora-einhell.md",
    19: "19-sierra-sable-inalambrica.md",
    20: "20-sierra-circular-lusqtoff.md",
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
        errors.append(f"{filename}: Title no coincide exactamente con el spec. Esperado: '{spec['title']}'")
        
    if f'h1: "{spec["h1"]}"' not in fm_text:
        errors.append(f"{filename}: H1 en frontmatter no coincide exactamente. Esperado: '{spec['h1']}'")
        
    if f'# {spec["h1"]}' not in content:
        errors.append(f"{filename}: H1 en cuerpo de markdown no encontrado: '# {spec['h1']}'")
        
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
    print("\nTODAS LAS 20 PÁGINAS DE SIERRAS CUMPLEN EL 100% DE LAS ESPECIFICACIONES TÉCNICAS Y EDITORIALES.")
