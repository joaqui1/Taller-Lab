# Descarga una copia del sistema de alertas de TallerLab FUERA de Neon (en esta PC).
# Uso manual:   powershell -ExecutionPolicy Bypass -File descargar-respaldo-alertas.ps1
# La clave editorial se lee de la variable de usuario TALLERLAB_EDITOR_TOKEN.
# Para guardarla una sola vez:  [Environment]::SetEnvironmentVariable("TALLERLAB_EDITOR_TOKEN","<clave>","User")

$ErrorActionPreference = "Stop"
$token = [Environment]::GetEnvironmentVariable("TALLERLAB_EDITOR_TOKEN", "User")
if (-not $token) { $token = Read-Host "Clave editorial de TallerLab" }

$destino = Join-Path $env:USERPROFILE "Documents\TallerLab\respaldos-alertas"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$archivo = Join-Path $destino ("alertas-" + (Get-Date -Format "yyyy-MM-dd") + ".zip")

Invoke-WebRequest -Uri "https://www.tallerlab.com.ar/api/alertas/respaldo" `
  -Headers @{ Authorization = "Bearer $token" } -OutFile $archivo -UseBasicParsing

$tam = (Get-Item $archivo).Length
if ($tam -lt 1000) { Remove-Item $archivo; throw "La descarga salio vacia o con error (revisa la clave)." }
try { Add-Type -AssemblyName System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::OpenRead($archivo).Dispose() }
catch { throw "El archivo descargado no es un ZIP valido." }

# Conserva los ultimos 30 respaldos.
Get-ChildItem $destino -Filter "alertas-*.zip" | Sort-Object Name -Descending | Select-Object -Skip 30 | Remove-Item
Write-Host "OK: respaldo guardado en $archivo ($tam bytes)"
