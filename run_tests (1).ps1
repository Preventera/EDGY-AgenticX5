# Script PowerShell pour exécuter les tests EDGY-AgenticX5
# Usage: .\run_tests.ps1 [options]

param(
    [string]$Mode = "all",  # all, unit, integration, cartography, neo4j, coverage
    [switch]$Verbose,
    [switch]$Html
)

Write-Host "🧪 Tests EDGY-AgenticX5" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$TestPath = "tests/"
$PytestArgs = @()

# Mode verbeux
if ($Verbose) {
    $PytestArgs += "-vv"
} else {
    $PytestArgs += "-v"
}

# Sélection des tests selon le mode
switch ($Mode) {
    "all" {
        Write-Host "📋 Exécution de TOUS les tests..." -ForegroundColor Green
        $PytestArgs += $TestPath
    }
    "unit" {
        Write-Host "⚡ Exécution des tests unitaires..." -ForegroundColor Green
        $PytestArgs += "-m", "unit", $TestPath
    }
    "integration" {
        Write-Host "🔗 Exécution des tests d'intégration..." -ForegroundColor Green
        $PytestArgs += "-m", "integration", $TestPath
    }
    "cartography" {
        Write-Host "🗺️ Exécution des tests cartographie..." -ForegroundColor Green
        $PytestArgs += "-m", "cartography", $TestPath
    }
    "neo4j" {
        Write-Host "🔗 Exécution des tests Neo4j..." -ForegroundColor Green
        $PytestArgs += "-m", "neo4j", $TestPath
    }
    "coverage" {
        Write-Host "📊 Exécution avec couverture de code..." -ForegroundColor Green
        $PytestArgs += "--cov=src", "--cov-report=term-missing", $TestPath
        if ($Html) {
            $PytestArgs += "--cov-report=html"
        }
    }
    default {
        Write-Host "❌ Mode inconnu: $Mode" -ForegroundColor Red
        Write-Host "Modes disponibles: all, unit, integration, cartography, neo4j, coverage" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""

# Vérifier que pytest est installé
try {
    $null = python -m pytest --version 2>&1
} catch {
    Write-Host "❌ pytest n'est pas installé!" -ForegroundColor Red
    Write-Host "Installation: pip install pytest pytest-cov pytest-mock --break-system-packages" -ForegroundColor Yellow
    exit 1
}

# Exécuter les tests
Write-Host "🚀 Commande: python -m pytest $($PytestArgs -join ' ')" -ForegroundColor Gray
Write-Host ""

$StartTime = Get-Date
python -m pytest @PytestArgs
$ExitCode = $LASTEXITCODE
$Duration = (Get-Date) - $StartTime

Write-Host ""
Write-Host "========================" -ForegroundColor Cyan
if ($ExitCode -eq 0) {
    Write-Host "✅ TOUS LES TESTS ONT RÉUSSI!" -ForegroundColor Green
} else {
    Write-Host "❌ CERTAINS TESTS ONT ÉCHOUÉ" -ForegroundColor Red
}
Write-Host "⏱️ Durée: $($Duration.TotalSeconds.ToString('0.00'))s" -ForegroundColor Cyan
Write-Host ""

# Ouvrir le rapport HTML si généré
if ($Html -and $ExitCode -eq 0 -and (Test-Path "htmlcov/index.html")) {
    Write-Host "📊 Ouverture du rapport de couverture..." -ForegroundColor Cyan
    Start-Process "htmlcov/index.html"
}

exit $ExitCode
