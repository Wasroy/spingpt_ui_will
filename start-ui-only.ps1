# Script de lancement pour le mode UI-Only
# Ce mode désactive le backend (Supabase + IA) pour travailler uniquement sur l'apparence

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SpinGPT Web v2 - Mode UI-Only" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mode UI-Only activé:" -ForegroundColor Green
Write-Host "  - Backend désactivé (Supabase + IA)" -ForegroundColor Yellow
Write-Host "  - Vous pouvez modifier uniquement l'apparence" -ForegroundColor Yellow
Write-Host "  - Aucune authentification requise" -ForegroundColor Yellow
Write-Host ""

# Activer le mode UI-only
$env:UI_ONLY_MODE = "true"

# Vérifier que l'environnement virtuel existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "ERREUR: L'environnement virtuel n'existe pas!" -ForegroundColor Red
    Write-Host "Exécutez d'abord: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Lancer Streamlit
Write-Host "Lancement de Streamlit en mode UI-Only..." -ForegroundColor Green
Write-Host ""

.\venv\Scripts\python.exe -m streamlit run app.py

