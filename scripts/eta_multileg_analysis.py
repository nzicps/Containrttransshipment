import pandas as pd
from datetime import datetime

data_path = r"C:\\Users\\seeds\\Documents\\Containrttransshipment\\data"

# Load required CSVs
try:
    nz = pd.read_csv(f"{data_path}\\portconnect_departures.csv")
    sg = pd.read_csv(f"{data_path}\\singapore_arrivals.csv")
    jp = pd.read_csv(f"{data_path}\\japan_arrivals.csv")
except FileNotFoundError as e:
    print("⚠️ Missing required CSV files:", e)
    exit()

# --- Merge and compute ETA metrics ---
leg1 = pd.merge(nz, sg, on="Vessel_IMO", how="inner", suffixes=("_NZ", "_SG"))
leg2 = pd.merge(sg, jp, on="Vessel_IMO", how="inner", suffixes=("_SG", "_JP"))

leg1["NZ_to_SG_days"] = (pd.to_datetime(leg1["ActualArrival_SG"]) - pd.to_datetime(leg1["Departure_NZ"])).dt.days
leg2["SG_to_JP_days"] = (pd.to_datetime(leg2["ActualArrival_JP"]) - pd.to_datetime(leg2["Departure_SG"])).dt.days

combined = pd.merge(leg1, leg2, on="Vessel_IMO", how="inner")
combined["Total_Transit_Days"] = combined["NZ_to_SG_days"] + combined["SG_to_JP_days"]

avg_leg1 = combined["NZ_to_SG_days"].mean()
avg_leg2 = combined["SG_to_JP_days"].mean()
avg_total = combined["Total_Transit_Days"].mean()

summary = {
    "updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "avg_NZ_to_SG_days": round(avg_leg1, 2),
    "avg_SG_to_JP_days": round(avg_leg2, 2),
    "avg_total_days": round(avg_total, 2)
}

pd.DataFrame([summary]).to_json(f"{data_path}\\eta_multileg_summary.json", orient="records")
combined.to_csv(f"{data_path}\\eta_multileg_comparison.csv", index=False)

print("✅ Multi-leg ETA analysis complete.")
print(f"Average NZ→SG: {avg_leg1:.1f} days | SG→JP: {avg_leg2:.1f} days | Total: {avg_total:.1f} days")
