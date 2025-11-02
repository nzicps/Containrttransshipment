$projectPath = "C:\\Users\\seeds\\Documents\\Containrttransshipment"
$docsPath = "$projectPath\\docs"
$dataPath = "$projectPath\\data"
$today = (Get-Date -Format "yyyy-MM-dd HH:mm")

Write-Host "`n🌸 Rebuilding Japan Arrival Analysis with table view..." -ForegroundColor Cyan

# --- Read CSV data ---
$csvFile = "$dataPath\\japan_arrivals.csv"
if (!(Test-Path $csvFile)) {
    Write-Host "⚠️ Missing $csvFile — cannot generate page." -ForegroundColor Red
    exit
}

$data = Import-Csv $csvFile
if ($data.Count -eq 0) {
    Write-Host "⚠️ CSV has no rows." -ForegroundColor Yellow
}

# --- Build HTML Table ---
$tableRows = ""
foreach ($row in $data) {
    $cells = ""
    foreach ($col in $row.PSObject.Properties.Name) {
        $cells += "<td>$($row.$col)</td>"
    }
    $tableRows += "<tr>$cells</tr>`n"
}
$headers = ($data[0].PSObject.Properties.Name | ForEach-Object { "<th>$_</th>" }) -join ""

$html = @"
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>Japan Arrival Analysis - MNGO Limited</title>
  <link rel='stylesheet' href='assets/style.css'>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f6fbff; color: #003366; margin: 40px; }
    table { border-collapse: collapse; width: 100%; margin-top: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
    th { background-color: #0077b6; color: white; }
    tr:nth-child(even) { background-color: #e8f4fc; }
    header { font-size: 22px; margin-bottom: 20px; }
    h1 { color: #005b96; }
    a { color: #005b96; text-decoration: none; font-weight: 500; }
  </style>
</head>
<body>
  <header>
    <img src='assets/logo.svg' alt='MNGO Logo' style='height:40px;vertical-align:middle;margin-right:10px;'>
    <span class='logo'>MNGO Limited</span>
  </header>

  <section>
    <h1>🇯🇵 Japan Arrival Performance Analysis</h1>
    <p>This section shows the latest recorded vessel arrival times for the Japan leg of the NZ ➜ SG ➜ JP route.</p>

    <h2>📊 Arrival Data</h2>
    <table>
      <thead><tr>$headers</tr></thead>
      <tbody>
        $tableRows
      </tbody>
    </table>

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
git commit -m "Fix: Display Japan arrivals data as inline HTML table ($today)"
git push origin main

Write-Host "`n✅ Japan Arrival page updated to inline display!"
Write-Host "👉 https://nzicps.github.io/Containrttransshipment/japan_arrivals.html"
