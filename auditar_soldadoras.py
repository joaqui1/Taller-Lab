from pathlib import Path
import json, re

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'soldadoras'
DATA_FILE = ROOT / 'analisis-soldadoras' / 'datos.json'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
specs = data['pages']

filenames = {
    1: "01-electrodo-7018.md",
    2: "02-soldadora-lusqtoff.md",
    3: "03-soldadora-de-punto.md",
    4: "04-soldadora-mig-con-gas.md",
    5: "05-guantes-para-soldar.md",
    6: "06-soldadora-tig.md",
    7: "07-soldadora-mig-sin-gas.md",
    8: "08-alambre-para-soldadura-mig.md",
    9: "09-mascara-de-soldar-fotosensible.md",
    10: "10-electrodo-6013.md",
    11: "11-soldadora-inverter-200-amp.md",
    12: "12-electrodo-para-fundicion.md",
    13: "13-alambre-flux.md",
    14: "14-soldadora-dogo-180.md",
    15: "15-soldadora-esab.md",
    16: "16-electrodo-para-acero-inoxidable.md",
    17: "17-soldadora-para-aluminio.md",
    18: "18-soldadora-lusqtoff-iron-250.md",
    19: "19-soldadora-tig-ac-dc.md",
    20: "20-soldadora-inverter-160-amp.md",
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
        errors.append(f"{filename}: Title no coincide exactamente con el spec. Esperado: {spec['title']}")
        
    if f'h1: "{spec["h1"]}"' not in fm_text:
        errors.append(f"{filename}: H1 en frontmatter no coincide exactamente. Esperado: {spec['h1']}")
        
    if f'# {spec["h1"]}' not in content:
        errors.append(f"{filename}: H1 en cuerpo de markdown no encontrado. Esperado: # {spec['h1']}")
        
    # Check all H2s
    for h2 in spec['h2']:
        if f"## {h2}" not in content:
            errors.append(f"{filename}: Falta sección H2: '## {h2}'")
            
    # Accept either a Mercado Libre category link or an affiliate short link.
    sponsored_link = re.search(
        r'\]\(https://(?:listado\.mercadolibre\.com\.ar|meli\.la)/[^)]+\)\{[^}]*rel="sponsored"',
        content,
    )
    if not sponsored_link:
        errors.append(f"{filename}: Falta enlace patrocinado de Mercado Libre o meli.la")
        
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
