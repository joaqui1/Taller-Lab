# Pasos en Vercel para que la base de compatibilidad funcione sola

Fecha límite: **3 de noviembre de 2026**. Ese día vencen las fuentes comprobadas el 4 de octubre y, sin mantenimiento, los 40 "Sí" desaparecen.

## 0. Plan
Vercel → tu equipo → Settings → Billing. Si dice **Hobby**, pasá a **Pro** (Hobby prohíbe uso comercial y el sitio tiene enlaces de afiliado).

## 1. Base de datos (PostgreSQL)
Si el proyecto ya tiene `ALERTAS_DATABASE_DATABASE_URL` de Neon, compatibilidad usa esa conexión con tablas propias (`compatibility_versions` y `compatibility_current`). No hace falta crear otra base ni copiar la contraseña. Una `COMPATIBILITY_DATABASE_URL` explícita tiene prioridad si se quiere separar el almacenamiento.

Solo si no existe ninguna conexión PostgreSQL:
1. Proyecto **taller-lab** → pestaña **Storage** → **Create Database** → **Neon (Serverless Postgres)** → plan Free.
2. Región: la misma que tus funciones (Settings → Functions → Function Region; por defecto Washington, D.C. = us-east-1).
3. Conectala al proyecto taller-lab en **Production y Preview**.
4. En la base creada → **.env.local** / Quickstart → copiá la cadena **pooled** (`postgresql://...-pooler...?sslmode=require`).

## 2. Variables de entorno
Proyecto → Settings → **Environment Variables** → Add (marcar Production y Preview):

| Nombre | Valor |
|---|---|
| `COMPATIBILITY_DATABASE_URL` | opcional con la integración de alertas existente; de lo contrario, la cadena pooled del paso 1.4 |
| `CRON_SECRET` | un texto aleatorio largo (ver abajo) |

Generar el secreto en PowerShell:
```powershell
-join ((48..57)+(65..90)+(97..122) | Get-Random -Count 48 | ForEach-Object {[char]$_})
```
Si ya existe `DATABASE_URL` no la toques (la usa el observatorio).

## 3. Publicar (desde tu PC, en la carpeta Taller Lab)
Asegurate de que ninguna otra sesión esté editando el proyecto. Luego:
```powershell
pip install -r requirements.txt
python preparar_compatibilidad.py
npx vercel login
npx vercel --prod
```

## 4. Primer mantenimiento
Vercel → proyecto → Settings → **Cron Jobs** → en `/api/compatibilidad/ejecutar` tocá **Run**.
O desde PowerShell:
```powershell
Invoke-RestMethod -Method Post -Uri https://www.tallerlab.com.ar/api/compatibilidad/ejecutar -Headers @{Authorization="Bearer TU_CRON_SECRET"} -ContentType "application/json" -Body "{}"
```

## 5. Comprobar
Abrí https://www.tallerlab.com.ar/api/compatibilidad/estado. Tiene que decir `"status": "ok"`, `verified_products: 18`, `documented_relations: 40`, `source_failures: 0`.
Si dice `degradado`: mirá Deployments → la última → **Logs** (función `/api/compatibilidad/ejecutar`).
Al día siguiente (07:30 Argentina) confirmá en Cron Jobs que corrió solo.

## 6. Plan B si no llegás
Antes del 3/11, en tu PC: `python -m compatibilidad.cli sync` y después `npx vercel --prod`. Eso renueva 30 días más.

## 7. Search Console
search.google.com/search-console → Agregar propiedad → **Dominio** `tallerlab.com.ar` → copiar el TXT → Vercel → Domains → tallerlab.com.ar → DNS Records → Add → Type TXT, Name `@`, Value el TXT (si el DNS no está en Vercel, cargalo donde esté).
Después: Sitemaps → `https://www.tallerlab.com.ar/sitemap.xml`.

## 8. Respaldo en GitHub
Quedó la rama local `respaldo-2026-10-05` con todo el proyecto. Subila:
```powershell
git push origin respaldo-2026-10-05
```
Si el repositorio es público, revisá antes que no haya nada privado. Para activar el monitor diario de GitHub (`.github/workflows/compatibilidad-operacion.yml`) hay que llevar esa rama a `main`.
