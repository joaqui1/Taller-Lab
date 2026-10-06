param([switch]$Actualizar, [int]$Puerto = 8921)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $observatorioPython = $bundledPython }
else { $observatorioPython = (Get-Command python -ErrorAction Stop).Source }
$originalPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = "$PSScriptRoot;$PSScriptRoot\.observatorio-deps;$PSScriptRoot\tmp\auditoria-observatorio-deps"
    & $observatorioPython -c 'import requests, bs4'
    if ($LASTEXITCODE -ne 0) {
        & $observatorioPython -m pip install -r observatorio/requirements-gratuito.txt --target .observatorio-deps
        if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
    }
    if ($Actualizar) { & $observatorioPython -m observatorio.gratuito }
    else { & $observatorioPython -m observatorio.gratuito --skip-collection }
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo generar el observatorio.' }
    Write-Host "Observatorio: http://127.0.0.1:$Puerto/datos/precios-herramientas-argentina/"
    Write-Host 'Ctrl+C para cerrar. La automatizacion diaria se ejecuta en GitHub, no en esta PC.'
    & $observatorioPython -m http.server $Puerto --bind 127.0.0.1 --directory public
} finally { $env:PYTHONPATH = $originalPythonPath }
