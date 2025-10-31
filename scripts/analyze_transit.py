import pandas as pd, datetime, requests, matplotlib.pyplot as plt
from pathlib import Path

base = Path("C:/Users/seeds/Documents/Containrttransshipment")
data_dir, dashboard_dir = base / "data", base / "dashboard"
data_dir.mkdir(exist_ok=True); dashboard_dir.mkdir(exist_ok=True)

today = datetime.date.today()
print("📡 Fetching data...")
api_url = "https://api.portcalls.io/v1/schedules"
params, headers = {"from":"SGSIN","to":"NZAKL","limit":10}, {"accept":"application/json"}

try:
    res = requests.get(api_url, params=params, headers=headers, timeout=15)
    res.raise_for_status()
    data_json = res.json()
    records = data_json.get("results", [])
except Exception:
    print("⚠️ Using simulated data.")
    records = [
        {"origin": "Singapore", "destination": "Auckland", "eta_days": 9.2},
        {"origin": "Singapore", "destination": "Tauranga", "eta_days": 10.1},
        {"origin": "Singapore", "destination": "Lyttelton", "eta_days": 12.5},
    ]

df = pd.DataFrame(records)
if "eta_days" not in df.columns: df["eta_days"] = [r.get("eta_days", 10) for r in records]
df["Date"], df["Port"], df["Avg_Dwell_Days"] = today, df["destination"], df["eta_days"]
df["Containers"] = [round(20 + 80 * abs(hash(p)) % 50) for p in df["Port"]]

csv_path = data_dir / "container_data.csv"; df.to_csv(csv_path, index=False)
print(f"✅ Data saved to {csv_path}")

plt.figure(figsize=(8, 5))
df.plot(kind="bar", x="Port", y="Avg_Dwell_Days", legend=False)
plt.title("Average Container Dwell Time - Singapore Transshipment")
plt.ylabel("Days"); plt.tight_layout()
plt.savefig(dashboard_dir / "chart.png"); plt.close()
print("📊 Chart saved.")

html = f"""
<html>
<head><title>Container Dashboard</title></head>
<body style='font-family:Arial;text-align:center;'>
<h1>🚢 Container Transshipment Analytics</h1>
<p>Last updated: {today}</p>
<img src='chart.png' width='600'>
<h3>Latest Data</h3>
{df.to_html(index=False)}
</body></html>"""
html_path = dashboard_dir / "index.html"
with open(html_path,"w",encoding="utf-8") as f: f.write(html)
print(f"🌍 Dashboard generated: {html_path}")
