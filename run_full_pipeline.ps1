Write-Host "`n🌊 Running NZ ➜ Singapore Transshipment Full Analysis..."

$projectPath = "C:\Users\seeds\Documents\Containrttransshipment"
$scriptsPath = "$projectPath\scripts"
$docsPath    = "$projectPath\docs"
$dataPath    = "$projectPath\data"
$python      = "python"

# Fetch live MarineTraffic ETA data
Write-Host "
🌐 Fetching live MarineTraffic ETA data..."
& powershell -ExecutionPolicy Bypass -File "C:\Users\seeds\Documents\Containrttransshipment\scripts\\fetch_marinetraffic_data.ps1" -apiKey "YOUR_API_KEY_HERE"

# Run all analyses
Write-Host "`n⚙️ Running analysis scripts..."
& $python "$scriptsPath\analyze_transit.py"
& $python "$scriptsPath\infer_dwell_real.py"
& $python "$scriptsPath\local_storage_analysis.py"
& $python "$scriptsPath\breakeven_analysis.py"

# Calculate summary CSV
Write-Host "`n🧮 Generating summary CSV..."
$breakevenFile = "$dataPath\local_breakeven_summary.csv"
$summaryFile   = "$dataPath\local_storage_summary.csv"
if (Test-Path $breakevenFile) {
    $data = Import-Csv $breakevenFile
    $out = @()
    foreach ($r in $data) {
        $savings = [int]$r.SG_Transshipment_Total - [int]$r.NZ_Cost_at_BE
        $out += [pscustomobject]@{
            Port=$r.Port; Containers=$r.Containers
            Deferred_Days=$r.Breakeven_Day
            NZ_Storage_Cost=$r.NZ_Cost_at_BE
            Transshipment_Total=$r.SG_Transshipment_Total
            Savings_vs_Transshipment=$savings
        }
    }
    $out | Export-Csv -Path $summaryFile -NoTypeInformation
}

# Compute metrics
Write-Host "`n📊 Computing metrics..."
$avgBE="N/A"; $avgSave="N/A"
if (Test-Path $breakevenFile) {
    $d=Import-Csv $breakevenFile
    $avgBE=[math]::Round(($d|Measure-Object -Property Breakeven_Day -Average).Average,1)
}
if (Test-Path $summaryFile) {
    $s=Import-Csv $summaryFile
    if ($s -and $s.Savings_vs_Transshipment) {
        $avgSave=[math]::Round(($s|Measure-Object -Property Savings_vs_Transshipment -Average).Average,0)
    }
}
$updateDate=Get-Date -Format 'yyyy-MM-dd HH:mm'
$metrics=@{"updated"=$updateDate;"average_breakeven_days"=$avgBE;"average_savings_nzd"=$avgSave}
$metrics|ConvertTo-Json|Set-Content "$dataPath\summary_metrics.json" -Encoding UTF8
Write-Host "✅ Saved summary_metrics.json"

# Build dashboard
Write-Host "`n🧱 Updating dashboard..."
$summaryBanner=@"
<section style='background:#e8f3ff;border-left:6px solid #0078d7;margin:0;padding:20px 40px;border-radius:0 0 12px 12px;box-shadow:0 3px 6px rgba(0,0,0,0.08);'>
<h2 style='color:#004a9f;text-align:center;'>📘 NZ ➜ Singapore Transshipment Summary</h2>
<p style='text-align:center;color:#555;'>Updated: $updateDate</p>
<p style='font-size:16px;line-height:1.6;width:85%;margin:auto;text-align:justify;'>
This analysis compares container movements from New Zealand to Singapore, integrating PortConnect departures, Singapore port data, and modeled local logistics costs.
It evaluates transshipment dwell times and domestic deferred storage trade-offs across major NZ ports.
The <b>average breakeven point is approximately $avgBE day(s)</b>, where total NZ holding costs (yard, trucking, and wharf) equal Singapore transshipment expenses.
On average, NZ deferred storage yields <b>estimated savings of NZD $avgSave per batch</b> before breakeven.
These insights help optimize export flows, vessel scheduling, and congestion management using real-time cost intelligence.
</p></section>
"@

$indexHTML = Get-Content "$docsPath\index.html" -Raw
$dwellHTML = Get-Content "$docsPath\index.html" -Raw
$localHTML = Get-Content "$docsPath\local_storage.html" -Raw
$breakHTML = Get-Content "$docsPath\breakeven.html" -Raw

$combinedHTML=@"
<html><head><title>NZ ➜ Singapore Transshipment Dashboard</title>
<style>body{font-family:Arial;background:#f9fafc;margin:0;}
section{margin:40px auto;width:90%;background:white;padding:30px;border-radius:12px;
box-shadow:0 0 8px rgba(0,0,0,0.1);}h1,h2{text-align:center;}
hr{margin:40px 0;border:0;border-top:2px solid #eee;}
a{color:#0078d7;text-decoration:none;}a:hover{text-decoration:underline;}
footer{text-align:center;margin:30px;color:gray;font-size:14px;}
</style></head><body>
$summaryBanner
<h1>🚢 NZ ➜ Singapore Transshipment Intelligence Dashboard</h1>
<p style='text-align:center;'>Updated: $updateDate</p>
<section><h2>1️⃣ Cost, Delay & Sensitivity Analysis</h2>$indexHTML</section><hr>
<section><h2>2️⃣ Real Vessel Dwell Time</h2>$dwellHTML</section><hr>
<section><h2>3️⃣ Local NZ Deferred Departure</h2>$localHTML</section><hr>
<section><h2>4️⃣ Breakeven Curve</h2>$breakHTML</section>
<footer>Built automatically using PortConnect (NZ), OpenFreightData & Singapore Port Data • $(Get-Date -Format 'yyyy')
<br><a href='summary.html'>📘 Read Full Summary</a></footer></body></html>
"@
Set-Content -Path "$docsPath\index.html" -Value $combinedHTML -Encoding UTF8

# Push to GitHub
Write-Host "`n📤 Pushing to GitHub..."
Set-Location $projectPath
git add .
git commit -m "Automated daily update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
git push origin main
Write-Host "`n✅ Dashboard updated and published!"
Write-Host "🌐 View: https://nzicps.github.io/Containrttransshipment/"



# Apply cache-busters to all CSV links (prevent stale GitHub Pages)
Write-Host "
🔁 Updating cache-busters for dashboard..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File "C:\Users\seeds\Documents\Containrttransshipment\scripts\\add_cachebuster.ps1"


# =====================================================
# 🇯🇵 Generate Japan Arrival Analysis Page
# =====================================================
Write-Host "
🗾 Generating Japan Arrival Analysis Page..." -ForegroundColor Cyan
& powershell -ExecutionPolicy Bypass -File "C:\Users\seeds\Documents\Containrttransshipment\scripts\\generate_japan_page.ps1"
