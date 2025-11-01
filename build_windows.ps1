# Build script for Windows (PowerShell)
# Usage: Open PowerShell as Administrator (if needed) and run: .\build_windows.ps1

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $projectRoot

Write-Host "[pix_app] Iniciando build..." -ForegroundColor Cyan

# Create virtual env? optional
if (-not (Test-Path ".venv")) {
    Write-Host "Criando virtualenv .venv..."
    python -m venv .venv
}

$env:Path = (Join-Path $projectRoot ".venv\Scripts") + ";" + $env:Path

Write-Host "Instalando dependências..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Build with PyInstaller (one-folder to keep dependencies separate; change to --onefile if preferred)
$exeName = "PixApp"
$iconFile = "pixapp.ico"
Write-Host "Executando PyInstaller..." -ForegroundColor Green
# Gera ícone a partir do Logo Oficial.png se não existir
if (-not (Test-Path $iconFile)) {
    Write-Host "convert_icon.py não encontrado no workspace? Tentando gerar ícone..." -ForegroundColor Yellow
    if (Test-Path "convert_icon.py") {
        python convert_icon.py
    } else {
        Write-Host "Aviso: convert_icon.py não encontrado. Continuando sem ícone." -ForegroundColor Yellow
    }
}
pyinstaller --noconfirm --windowed --name $exeName --icon "$iconFile" --add-data "perfis.json;." --add-data "pix_utils.py;." --add-data "Logo Oficial.png;." --add-data "$iconFile;." main.py

Write-Host "Build concluído. Verifique a pasta dist\$exeName\" -ForegroundColor Cyan

# Optional: create installer with Inno Setup if ISCC.exe is available
$innoPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (Test-Path $innoPath) {
    Write-Host "ISCC encontrado. Criando instalador..." -ForegroundColor Green
    & "$innoPath" "installer\pix_app.iss"
    Write-Host "Instalador criado (se não houver erros)." -ForegroundColor Cyan
} else {
    Write-Host "ISCC (Inno Setup) não encontrado. Skipando criação do instalador." -ForegroundColor Yellow
}

Write-Host "Feito." -ForegroundColor Green
