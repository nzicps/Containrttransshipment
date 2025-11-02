$projectPath = "C:\\Users\\seeds\\Documents\\Containrttransshipment"
$docsPath    = "$projectPath\\docs"
$today       = (Get-Date -Format "yyyyMMdd")

Write-Host "`n💠 Adding cache-buster to all CSV links..." -ForegroundColor Cyan

Get-ChildItem -Path $docsPath -Filter "*.html" -Recurse | ForEach-Object {
    $html = Get-Content $_.FullName -Raw
    $updated = $html -replace "(data\\/[^\"'>]+\\.csv)(?!\\?v=)", "`$1?v=$today"
    if ($updated -ne $html) {
        Set-Content $_.FullName -Value $updated -Encoding UTF8
        Write-Host "✅ Updated cache-busters in $($_.Name)"
    }
}

Set-Location $projectPath
git add docs/
git commit -m "Auto cache-buster update ($today)"
git push origin main

Write-Host "`n🌐 Cache-busters applied and pushed!" -ForegroundColor Green
Write-Host "👉 https://nzicps.github.io/Containrttransshipment/"
