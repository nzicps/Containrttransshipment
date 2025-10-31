import pandas as pd, datetime, requests, matplotlib.pyplot as plt, numpy as np
from pathlib import Path

# --- Setup ---
base = Path("C:/Users/seeds/Documents/Containrttransshipment")
data_dir, docs_dir = base / "data", base / "docs"
data_dir.mkdir(exist_ok=True); docs_dir.mkdir(exist_ok=True)

today = datetime.date.today()
print("📡 Fetching NZ→Singapore transshipment data...")

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
        print(f"⚠️ Using simulated data for {port}.")
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

# --- Baseline transshipment costs ---
handling_nzd, thc_nzd, storage_per_day_sg_nzd, admin_nzd, avg_stay_sg_days = 180, 160, 30, 40, 7
per_container_cost_nzd = handling_nzd + thc_nzd + admin_nzd + storage_per_day_sg_nzd * avg_stay_sg_days
nzd_to_usd, nzd_to_sgd = 0.60, 0.80

df["Transshipment_Cost_NZD"] = per_container_cost_nzd
df["Total_Transshipment_Cost_NZD"] = df["Transshipment_Cost_NZD"] * df["Containers"]

# --- Deferred departure model ---
NZ_storage_per_day_nzd = 15
SG_storage_per_day_nzd = 30
delay_to_sg_ratio = 0.8
SG_handling_nzd = handling_nzd + thc_nzd + admin_nzd
total_containers = df["Containers"].sum()

scenarios = []
for delay_days in range(0, 8):
    reduced_sg_days = max(1, avg_stay_sg_days - delay_days * delay_to_sg_ratio)
    cost_now = SG_handling_nzd + SG_storage_per_day_nzd * avg_stay_sg_days
    cost_defer = SG_handling_nzd + SG_storage_per_day_nzd * reduced_sg_days + NZ_storage_per_day_nzd * delay_days
    savings_per_teu = cost_now - cost_defer
    fleet_savings = savings_per_teu * total_containers
    scenarios.append((delay_days, reduced_sg_days, cost_now, cost_defer, savings_per_teu, fleet_savings))
df_scen = pd.DataFrame(scenarios, columns=[
    "Delay_Days","Reduced_SG_Days","Current_SG_Cost","Deferred_Total_Cost",
    "Savings_Per_TEU_NZD","Fleet_Savings_NZD"])
df_scen.to_csv(data_dir / "delay_scenarios.csv", index=False)

# --- Sensitivity analysis ---
print("📈 Running sensitivity analysis...")
yard_rates = range(10, 26, 3)
sens_rows = []
for rate in yard_rates:
    for delay_days in range(0, 8):
        reduced_sg_days = max(1, avg_stay_sg_days - delay_days * delay_to_sg_ratio)
        cost_defer = SG_handling_nzd + SG_storage_per_day_nzd * reduced_sg_days + rate * delay_days
        savings = (SG_handling_nzd + SG_storage_per_day_nzd * avg_stay_sg_days) - cost_defer
        sens_rows.append((rate, delay_days, savings))
df_sens = pd.DataFrame(sens_rows, columns=["NZ_Yard_Rate","Delay_Days","Savings_Per_TEU"])
pivot = df_sens.pivot(index="NZ_Yard_Rate", columns="Delay_Days", values="Savings_Per_TEU")

plt.figure(figsize=(8,6))
plt.imshow(pivot, cmap="RdYlGn", origin="lower", aspect="auto")
plt.colorbar(label="Savings per TEU (NZD)")
plt.xticks(range(0,8), range(0,8))
plt.yticks(range(len(pivot.index)), pivot.index)
plt.xlabel("Delay in NZ (days)")
plt.ylabel("NZ Yard Cost (NZD/day)")
plt.title("Sensitivity of Savings per TEU to Yard Cost and Delay")
plt.tight_layout()
plt.savefig(docs_dir / "yard_sensitivity_chart.png")
plt.close()

# --- Summary ---
opt_delay = df_scen.loc[df_scen["Deferred_Total_Cost"].idxmin(), "Delay_Days"]
opt_saving_teu = df_scen["Savings_Per_TEU_NZD"].max()
opt_fleet_saving = df_scen["Fleet_Savings_NZD"].max()
avg_cost_per_teu = df["Total_Transshipment_Cost_NZD"].sum() / total_containers

# --- Dashboard HTML ---
html_base = df.to_html(index=False)
html_scen = df_scen.to_html(index=False)

html = f"""
<html>
<head><title>NZ ➜ Singapore Transshipment Optimization Dashboard</title></head>
<body style='font-family:Arial;text-align:center;background-color:#f9fafc;'>
<h1>🚢 NZ ➜ Singapore Transshipment Optimization</h1>
<p>Last updated: {today}</p>
<div style='display:flex;justify-content:center;gap:15px;flex-wrap:wrap;'>
    <img src='cost_chart.png' width='380'>
    <img src='defer_chart.png' width='380'>
    <img src='fleet_savings_chart.png' width='380'>
    <img src='yard_sensitivity_chart.png' width='380'>
</div>
<h3>📊 Baseline Transshipment Costs</h3>
{html_base}
<hr style='margin:30px 0;'>
<h3>⏳ Deferred Departure Scenarios</h3>
{html_scen}
<hr style='margin:30px 0;'>
<div style='display:inline-block;padding:20px;background-color:#fff3cd;border-radius:10px;box-shadow:0 0 5px rgba(0,0,0,0.1);'>
<h3>📦 Summary</h3>
<p><b>Total Containers:</b> {total_containers}</p>
<p><b>Baseline Avg Cost per TEU:</b> NZD {avg_cost_per_teu:,.2f}</p>
<p><b>Optimal NZ Delay:</b> {opt_delay} days</p>
<p><b>Per-TEU Saving:</b> NZD {opt_saving_teu:,.2f}</p>
<p><b>Total Fleet Saving:</b> NZD {opt_fleet_saving:,.0f}</p>
</div>
<p style='margin-top:20px;color:gray;font-size:14px;'>
*Assumes: SG handling+THC+admin = {SG_handling_nzd} NZD, SG storage = {SG_storage_per_day_nzd} NZD/day.<br>
NZ yard = 10–25 NZD/day tested. Each 1 day NZ delay ≈ 0.8 day less dwell in Singapore.*
</p>
</body></html>
"""

html_path = docs_dir / "index.html"
with open(html_path, "w", encoding="utf-8") as f: f.write(html)
print(f"🌍 Dashboard updated with sensitivity analysis: {html_path}")

