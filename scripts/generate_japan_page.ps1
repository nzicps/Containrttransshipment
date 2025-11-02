$projectPath = "C:\\Users\\seeds\\Documents\\Containrttransshipment"
$docsPath = "$projectPath\\docs"
$dataPath = "$projectPath\\data"
$today = (Get-Date -Format "yyyy-MM-dd HH:mm")

Write-Host "`n🌸 Rebuilding Japan Arrival Analysis page..." -ForegroundColor Cyan

$html = @"
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Japan Arrival Analysis - MNGO Limited</title>
  <link rel='stylesheet' href='assets/style.css'>
</head>
<body>
  <header>
    <img src='assets/logo.svg' alt='MNGO Logo' style='height:40px;vertical-align:middle;margin-right:10px;'>
    <span class='logo'>MNGO Limited</span>
  </header>

  <section>
    <h1>🇯🇵 Japan Arrival Performance Analysis</h1>
    <p>This page presents vessel arrival times and comparative performance for the Japan leg of the NZ ➜ SG ➜ JP route.</p>

    <h2>📊 Latest Arrival Data</h2>
    <iframe src='data/japan_arrivals.csv?v=$((Get-Date -Format "yyyyMMdd"))' width='100%' height='400px' style='border:none;'></iframe>

    <p style='text-align:center;color:gray;'>Last updated: $today</p>
  </section>

  <section>
    <h2>🔗 Navigation</h2>
    <p style='text-align:center;'>
      <a href='index.html'>← Back to Main Dashboard</a> |
      <a href='data/japan_arrivals.csv' target='_blank'>📥 Download Raw CSV</a>
    </p>
  </section>

  <footer>
    © $(Get-Date -Format 'yyyy') MNGO Limited | Maritime Analytics
    <br><small>🔁 Auto-updated: $today</small>
  </footer>
</body>
</html>
"@

Set-Content "$docsPath\\japan_arrivals.html" -Value $html -Encoding UTF8

Set-Location $projectPath
git add docs/japan_arrivals.html
git commit -m "Auto-update Japan Arrival Analysis page ($today)"
git push origin main

Write-Host "✅ Japan arrival page refreshed and published!"
Write-Host "👉 https://nzicps.github.io/Containrttransshipment/japan_arrivals.html"
