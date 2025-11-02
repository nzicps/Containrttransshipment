# =====================================================================
# 🧭 MNGO Limited: Full ETA Pipeline Validator + Runner
# NZ ➜ Singapore ➜ Japan Multi-leg Impact Dashboard
# =====================================================================

Write-Host "`n🌊 Checking environment and running pipeline..."

$projectPath = "C:\Users\seeds\Documents\Containrttransshipment"
$dataPath    = "$projectPath\data"
$scriptsPath = "$projectPath\scripts"
$docsPath    = "$projectPath\docs"
$python      = "python"

# --- Check Folder Structure ---
$folders = @($projectPath, $dataPath, $scriptsPath, $docsPath)
$missingFolders = @()
foreach ($f in $folders) {
    if (!(Test-Path $f)) {
        $missingFolders += $f
    }
}
if ($missingFolders.Count -gt 0) {
    Write-Host "`n❌ Missing folders:" -ForegroundColor Red
    $missingFolders | ForEach-Object { Write-Host "   - $_" }
    Write-Host "`nPlease create them before running again."
    exit
} else {
    Write-Host "✅ Folder structure OK."
}

# --- Check Required CSV Files ---
$requiredFiles = @(
    "$dataPath\portconnect_departures.csv",
    "$dataPath\singapore_arrivals.csv",
    "$dataPath\japan_arrivals.csv"
)
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "`n⚠️ Missing required CSV files:"
    $missingFiles | ForEach-Object { Write-Host "   - $_" }
    Write-Host "`nPlease make sure these exist in your /data/ folder before continuing."
    exit
} else {
    Write-Host "✅ All required data files found."
}

# --- Check Key Scripts ---
$mainPipeline = "$projectPath\run_full_pipeline.ps1"
if (!(Test-Path $mainPipeline)) {
    Write-Host "`n❌ Missing $mainPipeline. Please re-create it first."
    exit
} else {
    Write-Host "✅ Main pipeline found."
}

# --- Check GitHub Link in Dashboard ---
$indexPath = "$docsPath\index.html"
if (Test-Path $indexPath) {
    $html = Get-Content $indexPath -Raw
    if ($html -match "nzicps.github.io/Containrttransshipment") {
        Write-Host "✅ Dashboard correctly linked to GitHub Pages."
    } else {
        Write-Host "⚠️ Dashboard does not contain live GitHub link. Adding it..."
        $footerText = "`n<footer>🌐 View Live Dashboard: <a href='https://nzicps.github.io/Containrttransshipment/' target='_blank'>Containrttransshipment</a></footer>"
        Add-Content -Path $indexPath -Value $footerText
        Write-Host "✅ Link inserted."
    }
}

# --- Run the Full Pipeline ---
Write-Host "`n⚙️ Running full pipeline..."
powershell -ExecutionPolicy Bypass -File $mainPipeline

# --- Verify Git Push Status ---
Write-Host "`n🔍 Checking latest Git commit..."
Set-Location $projectPath
$latestCommit = git log -1 --pretty=format:"%h - %s (%cr)"
Write-Host "✅ Latest Commit:" $latestCommit

# --- Show Live Dashboard Link ---
Write-Host "`n🌐 View Dashboard:"
Write-Host "   https://nzicps.github.io/Containrttransshipment/"
Write-Host "`n✅ All checks and updates completed successfully!"
