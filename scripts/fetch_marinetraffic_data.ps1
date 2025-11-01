param (
    [string]$apiKey
)
$data_path = "C:\\Users\\seeds\\Documents\\Containrttransshipment\\data"

Write-Host "🌐 Fetching latest vessel ETA data from MarineTraffic..."

$ports = @{
    "nz" = "port:nz"
    "sg" = "port:sg"
    "jp" = "port:jp"
}

foreach ($key in $ports.Keys) {
    $url = "https://services.marinetraffic.com/api/exportvessel/v:8/$apiKey/timespan:48/$($ports[$key])"
    $out = "$data_path\\${key}_arrivals.csv"
    try {
        Invoke-RestMethod -Uri $url -OutFile $out -ErrorAction Stop
        Write-Host "✅ Downloaded data for $key → $out"
    } catch {
        Write-Host "⚠️ Could not download for $key. Using existing file if present."
    }
}

Write-Host "🌍 All available data fetched."
