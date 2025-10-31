import pandas as pd, datetime, requests, matplotlib.pyplot as plt
from pathlib import Path

# --- Setup ---
base = Path("C:/Users/seeds/Documents/Containrttransshipment")
data_dir, docs_dir = base / "data", base / "docs"
data_dir.mkdir(exist_ok=True); docs_dir.mkdir(exist_ok=True)

today = datetime.date.today()
print(" Fetching NZSingapore transshipment data...")

api_url = "https://api.portcalls.io/v1/schedules"
nz_ports = ["NZAKL", "NZTRG", "NZLYT"]
records = []

for port in nz_ports:
    try:
        params = {"from": port, "to": "SGSIN", "limit": 10}
        headers = {"accept": "application/json"}
        res = requests.get(api_url, params=params, headers=headers, timeout=15)
        res.raise_for_status()
        data_json = res.json()
        records += data_json.get("results", [])
    except Exception:
        print(f" Using simulated data for {port}.")
        fallback = {
            "NZAKL": {"origin": "Auckland", "destination": "Singapore", "eta_days": 12.3},
            "NZTRG": {"origin": "Tauranga", "destination": "Singapore", "eta_days": 11.8},
            "NZLYT": {"origin": "Lyttelton", "destination": "Singapore", "eta_days": 13.5},
        }
        records.append(fallback[port])

df = pd.DataFrame(records)
if "eta_days" not in df.columns:
    df["eta_days"] = [r.get("eta_days", 12) for r in records]

df["Date"], df["Port"], df["Avg_Transit_Days"] = today, df["origin"], df["eta_days"]
df["Containers"] = [round(50 + 50 * abs(hash(p)) % 30) for p in df["Port"]]

# --- Transshipment cost estimation ---
handling_nzd, thc_nzd, storage_per_day_nzd, admin_nzd, avg_stay_days = 180, 160, 30, 40, 7
per_container_cost_nzd = handling_nzd + thc_nzd + admin_nzd + storage_per_day_nzd * avg_stay_days

# --- Exchange rates ---
nzd_to_usd, nzd_to_sgd = 0.60, 0.80

# --- Cost calculations ---
df["Transshipment_Cost_NZD"] = per_container_cost_nzd
df["Total_Transshipment_Cost_NZD"] = df["Transshipment_Cost_NZD"] * df["Containers"]
df["Total_Transshipment_Cost_USD"] = df["Total_Transshipment_Cost_NZD"] * nzd_to_usd
df["Total_Transshipment_Cost_SGD"] = df["Total_Transshipment_Cost_NZD"] * nzd_to_sgd

# --- Add Cost Share column ---
total_cost = df["Total_Transshipment_Cost_NZD"].sum()
df["Cost_Share_Percent"] = (df["Total_Transshipment_Cost_NZD"] / total_cost * 100).round(2)

# --- Add TOTAL row ---
total_row = {
    "Port": "TOTAL",
    "Containers": df["Containers"].sum(),
    "Transshipment_Cost_NZD": "",
    "Total_Transshipment_Cost_NZD": total_cost,
    "Total_Transshipment_Cost_USD": total_cost * nzd_to_usd,
    "Total_Transshipment_Cost_SGD": total_cost * nzd_to_sgd,
    "Cost_Share_Percent": 100.00
}
df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

# --- Save data ---
csv_path = data_dir / "nz_to_sg_data.csv"
df_total.to_csv(csv_path, index=False)
print(f" Data saved to {csv_path}")

# --- Chart ---
plt.figure(figsize=(8, 5))
df.plot(kind="bar", x="Port", y="Total_Transshipment_Cost_NZD", legend=False, color="orange")
plt.title("Total Transshipment Cost by Port (NZ  Singapore)")
plt.ylabel("NZD")
plt.tight_layout()
plt.savefig(docs_dir / "cost_chart.png")
plt.close()
print(" Chart saved.")

# --- Color-coded summary logic ---
color = "#d4edda" if total_cost < 100000 else "#fff3cd" if total_cost <= 150000 else "#f8d7da"
color_label = " Low" if total_cost < 100000 else " Moderate" if total_cost <= 150000 else " High"

# --- Dashboard HTML ---
html_table = df_total.to_html(index=False)
html_table = html_table.replace("<td>TOTAL</td>", "<td style='font-weight:bold;background-color:#fff3cd;'>TOTAL</td>")

total_containers = int(df["Containers"].sum())
avg_cost_per_teu = total_cost / total_containers

html = f"""
<html>
<head><title>NZ  Singapore Transshipment Dashboard</title></head>
<body style='font-family:Arial;text-align:center;background-color:#f9fafc;'>
<h1> NZ  Singapore Transshipment Analytics</h1>
<p>Last updated: {today}</p>

<img src='cost_chart.png' width='500'>

<h3>Latest Data (with Totals)</h3>
{html_table}

<hr style='margin:30px 0;'>
<div style='display:inline-block;padding:20px;background-color:{color};border-radius:10px;box-shadow:0 0 5px rgba(0,0,0,0.1);'>
<h3> Summary</h3>
<p><b>Total Containers:</b> {total_containers}</p>
<p><b>Total Cost:</b> NZD {total_cost:,.0f} | USD {total_cost*nzd_to_usd:,.0f} | SGD {total_cost*nzd_to_sgd:,.0f}</p>
<p><b>Average Cost per TEU:</b> NZD {avg_cost_per_teu:,.2f}</p>
<p><b>Cost Level:</b> {color_label}</p>
</div>

<p style='margin-top:20px;color:gray;font-size:14px;'>
*Assumes 7-day stay at Singapore PSA  handling + THC + storage + admin  NZD {per_container_cost_nzd:.0f} per container.*<br>
*Exchange rates: 1 NZD = {nzd_to_usd} USD = {nzd_to_sgd} SGD.*
</p>
</body></html>"""

html_path = docs_dir / "index.html"
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f" Dashboard updated: {html_path}")
