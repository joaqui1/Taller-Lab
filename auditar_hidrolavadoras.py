from pathlib import Path
import json, re

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'hidrolavadoras'
DATA_FILE = ROOT / 'analisis-hidrolavadoras' / 'datos.json'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
specs = data['pages']

filenames = {
    1: "01-hidrolavadoras.md",
    2: "02-hidrolavadora-inalambrica.md",
    3: "03-hidrolavadoras-lusqtoff.md",
    4: "04-hidrolavadoras-gamma.md",
    5: "05-hidrolavadoras-stihl.md",
    6: "06-hidrolavadoras-bosch.md",
    7: "07-hidrolavadoras-black-decker.md",
    8: "08-hidrolavadora-karcher-k2.md",
    9: "09-hidrolavadora-karcher-k5.md",
    10: "10-hidrolavadora-gamma-150.md",
    11: "11-hidrolavadora-profesional.md",
    12: "12-hidrolavadora-karcher-k3.md",
    13: "13-hidrolavadoras-einhell.md",
    14: "14-hidrolavadora-gamma-130.md",
    15: "15-hidrolavadoras-hyundai.md",
    16: "16-hidrolavadora-lusqtoff-hl-120.md",
    17: "17-hidrolavadora-karcher-k4.md",
    18: "18-hidrolavadora-150-bar.md",
    19: "19-hidrolavadora-200-bar.md",
    20: "20-hidrolavadoras-niwa.md",
    21: "21-hidrolavadoras-karcher.md",
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
    lines = content.splitlines()
    
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
        errors.append(f"{filename}: Title no coincide exactamente con el spec. Esperado: {spec['title']}")
        
    if f'h1: "{spec["h1"]}"' not in fm_text:
        errors.append(f"{filename}: H1 en frontmatter no coincide exactamente. Esperado: {spec['h1']}")
        
    if f'# {spec["h1"]}' not in content:
        errors.append(f"{filename}: H1 en cuerpo de markdown no encontrado. Esperado: # {spec['h1']}")
        
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
for spec in specs:
    pid = spec['id']
    fn = filenames[pid]
    fp = PAGES_DIR / fn
    w = len(fp.read_text(encoding='utf-8').split())
    print(f" - {fn}: {w} palabras")

if errors:
    print(f"\nERRORES ENCONTRADOS ({len(errors)}):")
    for err in errors:
        print(f" - {err}")
    exit(1)
else:
    print("\nTODAS LAS 20 PÁGINAS CUMPLEN EL 100% DE LAS ESPECIFICACIONES TÉCNICAS Y EDITORIALES.")
