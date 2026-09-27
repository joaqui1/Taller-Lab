from pathlib import Path
import json, re

ROOT = Path(__file__).parent
PAGES_DIR = ROOT / 'paginas' / 'compresores'
DATA_FILE = ROOT / 'analisis-compresores' / 'datos.json'

data = json.loads(DATA_FILE.read_text(encoding='utf-8'))
specs = data['pages']

filenames = {
    1: "01-compresor-de-aire-para-auto.md",
    2: "02-compresor-de-50-litros.md",
    3: "03-manguera-para-compresor-de-aire.md",
    4: "04-aerografo-con-compresor.md",
    5: "05-pistola-para-pintar-con-compresor.md",
    6: "06-acople-rapido-para-compresor.md",
    7: "07-compresor-para-aerografo.md",
    8: "08-aceite-para-compresor-de-aire.md",
    9: "09-compresor-lusqtoff-50-litros.md",
    10: "10-filtro-de-aire-para-compresor.md",
    11: "11-compresor-de-100-litros.md",
    12: "12-compresor-gamma-50-litros.md",
    13: "13-kit-para-compresor-de-aire.md",
    14: "14-compresor-lusqtoff-100-litros.md",
    15: "15-compresor-sin-aceite.md",
    16: "16-compresor-de-200-litros.md",
    17: "17-compresor-bta-25-litros.md",
    18: "18-compresor-de-24-litros.md",
    19: "19-compresor-inalambrico.md",
    20: "20-compresor-stanley.md",
    21: "21-compresor-para-pintar.md",
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
        errors.append(f"{filename}: Title no coincide exactamente con el spec")
        
    if f'h1: "{spec["h1"]}"' not in fm_text:
        errors.append(f"{filename}: H1 en frontmatter no coincide exactamente")
        
    if f'# {spec["h1"]}' not in content:
        errors.append(f"{filename}: H1 en cuerpo de markdown no encontrado")
        
    # Check all H2s
    for h2 in spec['h2']:
        if f"## {h2}" not in content:
            errors.append(f"{filename}: Falta sección H2: '## {h2}'")
            
    # Check Mercado Libre link
    ml_link = re.search(
        r'\]\(https://(?:meli\.la/[^)]+|listado\.mercadolibre\.com\.ar/[^)]+)\)'
        r'\{[^}]*rel="[^"]*\bsponsored\b[^"]*"[^}]*\}',
        content,
    )
    if not ml_link:
        errors.append(f"{filename}: Falta enlace a Mercado Libre con rel=\"sponsored\"")
        
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
    print(f"\nTODAS LAS {len(specs)} PÁGINAS CUMPLEN EL 100% DE LAS ESPECIFICACIONES TÉCNICAS Y EDITORIALES.")
