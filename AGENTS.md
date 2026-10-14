# Guía para agentes de TallerLab

## El sitio y las reglas editoriales

TallerLab publica en español rioplatense guías de compra de herramientas para Argentina. Las guías se basan en documentación oficial de fabricantes; no se hacen pruebas físicas.

- No inventes datos, credenciales, revisores ni pruebas. Separá los datos documentados de las conclusiones editoriales y enlazá las fuentes consultadas.
- No publiques ni cambies contenido editorial que el dueño no haya cargado o autorizado. En `paginas/`, `published: "true"` y los campos documentales completos habilitan la publicación; no los agregues para hacer visible un borrador.
- Los enlaces afiliados de Mercado Libre (`meli.la` y dominios de Mercado Libre) deben llevar `rel="sponsored"` (normalmente también `nofollow noopener noreferrer`). Conservá la identificación y el aviso de afiliación.
- Usá las fechas `dd/mm/aaaa` del frontmatter `reviewed`; no atribuyas revisión o autoría a terceros sin respaldo.

## Mapa del código

- `app.py`: entrada Flask para Vercel; `app = Flask(...)` cerca de la línea 56. Tiene rutas de APIs, assets y descargas. La ruta general `page()` (líneas 352–354) despacha páginas y redirecciones. Las redirecciones están aquí, no en `vercel.json`.
- `servidor_local.py`: render compartido con Vercel y servidor local. `PORT` es 8080 (línea 150); `extract_frontmatter()` (171), `load_all_articles()` (899), filtro de guías publicables (973) e `INDEXABLE_PATHS` (995).
- `servidor_local.py`: `organization_schema()` (1030), `canonical_tag()` (1138), `render_sitemap()` (1415), `HTML_SHELL` (1569; menú, estructura general y pie), `render_editorial_page()` (2320), `render_home_page()` (2427), `render_article_page()` (2594), `author_schema()` (2909), `article_schema_tag()` (2936). Las líneas son aproximadas y pueden cambiar.
- `paginas/`: guías Markdown con frontmatter. Las de amoladoras están directamente en esta carpeta; las demás, en subcarpetas por categoría. El cargador lee `title`, `h1`, `url`, `description`, `author`, `reviewed`, `published`, `research_type`, `physical_test`, `specifications_contrasted`, `buyer_opinions`, `primary_sources`, `information_asset`, `asset_status`, `category` y `keywords`.
- `perfil_autor.json`: datos del autor. `paginas_institucionales.py`: contenido institucional que renderiza `render_editorial_page()` (metodología, autor, contacto y privacidad).
- `tallerlab_data/`: fichas de `/herramientas/`, comparador, fuentes y enlaces a guías; `guide_links.py` define enlaces entre fichas y guías; `quality.py` contiene `tool_is_indexable()` y reglas de respaldo documental.
- `tallerlab_data/model_equivalences.py` y `model_equivalences.json`: equivalencias seguras entre slugs de fichas, precios, alertas y compatibilidad. La tabla se regenera con `python -c "from tallerlab_data.model_equivalences import generate_files; generate_files()"`; solo enlaza coincidencias únicas de marca y código/modelo normalizado. Los candidatos dudosos van en `model_equivalences_review.json` y no se publican como enlaces hasta revisarlos.
- `tallerlab_data/afiliados_por_modelo.json` es la tabla única de modelo exacto a URL afiliada `meli.la`, ficha técnica y página de precio; se regenera con `python -m tallerlab_data.affiliates_by_model`. Las coincidencias dudosas se anotan en `tallerlab_data/afiliados_por_modelo_review.json` y no se enlazan automáticamente.
- `observatorio/`: datos y publicación de precios. Los informes de prensa se calculan con `python -m observatorio.cli informe-mensual --mes AAAA-MM`; `observatorio/informes/AAAA-MM.json` controla la nota editorial y su publicación (`publicado: true`), mientras `observatorio/ipc_indec.json` contiene solo IPC mensual verificado manualmente. Las páginas mensuales se generan desde el historial publicado por `observatorio/estatico.py`. En producción de Vercel, el observatorio heredado requiere PostgreSQL mediante `DATABASE_URL` (`observatorio/db.py`, alrededor de la línea 26). No intervengas en el trabajo en curso de este módulo fuera del alcance autorizado para la tarea.
- `compatibilidad/`: reglas, datos, búsqueda, presentación y pipeline de compatibilidad.
- `comunidad/`: páginas, componentes y almacenamiento de la comunidad. `relevamiento_piloto.py`: flujo de relevamiento.
- `alertas_*.py`: alertas editoriales y sus rutas. `recursos_editoriales.py`: recursos asociados a guías. `assets/decision-tools.js`: calculadoras y herramientas interactivas embebidas en guías.
- `servidor_local.py`: páginas de calculadoras y embeds reutilizan `render_resource()` y `assets/decision-tools.js`. Rutas indexables: `/calculadoras/`, `/calculadoras/generador-para-casa/`, `/calculadoras/caudal-compresor/`, `/calculadoras/costo-final-oferta/` y `/calculadoras/consumo-agua-hidrolavadora/`. Rutas de inserción noindex: `/embed/calculadoras/{generador-para-casa,caudal-compresor,costo-final-oferta,consumo-agua-hidrolavadora}/`.
- El frontmatter de las guías admite `veredictos` como lista YAML de objetos con los campos `uso`, `recomendacion` y `condicion`. Solo se muestran entradas con los tres campos completos; no completar veredictos sin autorización editorial. Los campos opcionales `revisor`, `revision_tecnica` y `alcance_revision` vinculan una guía con un perfil marcado como publicado en `revisores.json`; `respuestas_usuarios` puede indicar `{ cantidad: N }`.
- `publicaciones_autoridad.py` lee los JSON raíz `quienes_somos.json`, `consultas_fabricantes.json` y `prensa.json`. Publica condicionalmente `/quienes-somos/` (cinco apartados y `publicado: true`), `/fabricantes/respuestas/` (cinco consultas válidas; CSV en `/fabricantes/respuestas/descargar.csv`) y `/en-los-medios/` (una mención válida). Los enlaces del pie y el sitemap siguen esos mismos estados. Las guías pueden insertar una respuesta literal asociada con `{{respuesta_fabricante:id}}`; solo se muestra si el registro está respondido y enumera la ruta de esa guía en `guias`.
- `vercel.json`: build `python preparar_assets_publicos.py` y cron jobs de alertas, compatibilidad y comunidad; actualmente no programa el endpoint `/api/observatorio/ejecutar`. `requirements.txt` fija Flask 3.1.3; el workflow de CI usa Python 3.12.

### Agregar una ruta

1. Para producción, declarala en `app.py` con Flask o agregá su despacho a `page()` (desde la línea 352), según el tipo de respuesta.
2. Para que funcione en local, agregá el despacho equivalente en `TallerLabHandler.do_GET()` de `servidor_local.py` (desde la línea 3070); reutilizá las funciones de render compartidas cuando corresponda.
3. Si la URL debe indexarse, añadila a `INDEXABLE_PATHS` en `servidor_local.py` (línea aproximada 995) y verificá que sitemap y canonical la incluyan. Para páginas de datos, respetá además sus reglas específicas de indexación.
4. Si es una página editorial, el dueño debe cargar o autorizar el contenido antes de publicarla.

## Desarrollo y verificaciones

- Requiere Python 3.12; instalá dependencias con `python -m pip install -r requirements.txt`.
- Iniciá el sitio local con `python servidor_local.py` y abrí `http://localhost:8080`.
- Corré las verificaciones del proyecto:
  - `python -m unittest discover -s tests -p 'test_*.py'`
  - `python verificar_tallerlab_data.py`
  - `python preparar_assets_publicos.py`
- `.github/workflows/verificacion-produccion.yml` también ejecuta `verificar_alertas` y `verificar_relevamiento_seguro` en CI.
- `tests/test_public_authority_pages.py` cubre publicación condicionada, JSON-LD Dataset, CSV y el marcador de respuestas de fabricantes.

## Flujo de trabajo

- Trabajá en la rama local `mejoras-autoridad`, creada desde `main` actualizado. No hagas push ni abras pull requests hasta que el dueño lo decida.
- Hacé un commit por tarea y limitá cada commit a los archivos de esa tarea.
- No toques el trabajo en curso del Observatorio.
- No modifiques ni muevas los archivos sueltos de la raíz que sean informes, JSON de QA o patches. Dejalos donde están.

## Cambios recientes

- El email público de contacto vive en `perfil_autor.json`, campo `email_publico`; `paginas_institucionales.contact_email()` lo carga y `PublicTemplate` lo agrega al pie.
- Los perfiles de revisión técnica se cargan en `revisores.json`, con `_instrucciones` y entradas que usan `slug`, `nombre`, `oficio`, `anios_oficio` (opcional), `localidad` (opcional), `foto`, `bio_corta`, `perfiles`, `categorias`, `activo` y `consentimiento_publicacion`. Solo se muestran quienes tienen `activo: true` y `consentimiento_publicacion: true`. `servidor_local.py` comparte el render de `/revisores/` y `/revisores/{slug}/` con Flask en `app.py`; las guías los vinculan con los campos de frontmatter `revisor`, `revision_tecnica` y `alcance_revision`.
- `perfil_autor.json` admite además `foto` (ruta dentro de `assets/`), `que_hace` y `que_no_hace` (listas). La página institucional del autor calcula sus métricas a partir de los datos del sitio.
