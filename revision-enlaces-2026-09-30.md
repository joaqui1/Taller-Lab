# Revisión previa a publicación — 30/09/2026

Se corrigieron 100 destinos internos en 27 de las 29 páginas de soldadoras,
agregando `/soldadoras/` según las rutas reales del frontmatter. Se conservaron
H1, títulos, textos, tablas y ofertas. La integración comercial normaliza ahora
las rutas en todas las guías de soldadoras.

En las guías publicadas de amoladoras y sierras había otras 30 referencias a
borradores excluidos del sitio. Se conservaron sus textos sin enlace en el
Markdown, haciendo explícito el resultado que antes producía el renderer. No se
cambió el estado editorial de esos borradores.

`validacion_enlaces.py` analiza anclas HTML generadas desde Markdown, incluidas
referencias, HTML directo y rutas relativas. Compara la ruta del destino con
`INDEXABLE_PATH_SET`, admitiendo query y fragmento en páginas válidas. Los enlaces
externos no se consideran rutas internas. La carga del servidor y de Flask falla
con un diagnóstico por archivo si una guía publicada tiene un destino inválido.
El renderer también rechaza estos enlaces; se retiró el borrado silencioso.

## Dominio canónico

`vercel.json` fija `SITE_URL=https://www.tallerlab.com.ar` para las funciones.
`.env.example` documenta el mismo valor. El servidor reconoce producción por
`VERCEL_ENV=production` o `APP_ENV=production`, exige `SITE_URL` y rechaza HTTP,
localhost y subdominios `vercel.app`. No usa `VERCEL_PROJECT_PRODUCTION_URL` ni
`VERCEL_URL` como alternativa. Sin configuración, el servidor local usa localhost.

La propiedad `env` está documentada por
[Vercel](https://vercel.com/docs/project-configuration/vercel-json#env);
Vercel recomienda administrar variables desde Project Settings. El valor público
queda aquí versionado para que el próximo despliegue lo incluya explícitamente.
Para otro proveedor, configurar `APP_ENV=production` y el mismo `SITE_URL`.

No se desplegó el sitio ni se verificaron DNS o la asociación del dominio en Vercel.
El archivo de ejemplo no se carga automáticamente: fuera de Vercel se debe pasar
la variable al proceso.

## Verificación reproducible

Con las dependencias de `requirements.txt` instaladas:

```powershell
python verificar_enlaces_publicados.py
python verificar_soldadoras_comerciales.py
```

El primer control comprueba las 157 guías, las 167 rutas indexables por HTTP,
los enlaces del HTML final, la conservación de enlaces de soldadoras, canonical,
sitemap, robots, datos estructurados y el rechazo de enlaces inválidos y de
configuraciones de producción incorrectas. El segundo verifica ofertas,
atributos de afiliación, integridad editorial e idempotencia de la integración.

Resultados finales: ambos controles pasaron. Se comprobaron 5.737 enlaces del
HTML final y 167 respuestas HTTP 200. El catálogo actual tiene 31 productos,
66 CTA en 27 guías y 29 rutas de soldadoras verificadas por el servidor local.
La comparación con Git confirmó que las 157 guías conservan sus textos y
metadatos, salvo las sustituciones de enlaces descritas arriba.
