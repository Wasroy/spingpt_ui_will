# Script de lancement pour SpinGPT Web v2
# Usage: .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SpinGPT Web v2 - Lancement" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que l'environnement virtuel existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERREUR: L'environnement virtuel n'existe pas!" -ForegroundColor Red
    Write-Host "Exécutez d'abord: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Vérifier les variables d'environnement
Write-Host "Vérification des variables d'environnement..." -ForegroundColor Yellow
$missing = @()

if (-not $env:SUPABASE_URL) {
    $missing += "SUPABASE_URL"
}
if (-not $env:SUPABASE_ANON_KEY) {
    $missing += "SUPABASE_ANON_KEY"
}
if (-not $env:HF_TOKEN) {
    $missing += "HF_TOKEN (optionnel)"
}

if ($missing -and $missing.Count -gt 0 -and $missing -notcontains "HF_TOKEN (optionnel)") {
    Write-Host ""
    Write-Host "ATTENTION: Variables d'environnement manquantes:" -ForegroundColor Yellow
    foreach ($var in $missing) {
        Write-Host "  - $var" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Vous pouvez:" -ForegroundColor Yellow
    Write-Host "  1. Créer un fichier .env (voir SETUP.md)" -ForegroundColor Yellow
    Write-Host "  2. Ou les définir dans ce terminal avant de lancer" -ForegroundColor Yellow
    Write-Host ""
}

# Lancer Streamlit
Write-Host "Lancement de Streamlit..." -ForegroundColor Green
Write-Host ""

.\venv\Scripts\python.exe -m streamlit run app.py

