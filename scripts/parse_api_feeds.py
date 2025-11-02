import pandas as pd
from datetime import datetime

data_path = r"C:\\Users\\seeds\\Documents\\Containrttransshipment\\data"

try:
    nz = pd.read_csv(f"{data_path}\\portconnect_departures.csv")
    sg = pd.read_csv(f"{data_path}\\singapore_arrivals.csv")
    jp = pd.read_csv(f"{data_path}\\japan_arrivals.csv")
except FileNotFoundError as e:
    print(f"⚠️ Missing data file: {e}")
    exit()

# --- Identify delayed vs on-time from NZ ---
if "Departure_Delay_Hours" in nz.columns:
    nz["DepartureType"] = nz["Departure_Delay_Hours"].apply(lambda x: "Delayed" if x > 2 else "On-time")
else:
    nz["DepartureType"] = "Unknown"

# --- Merge datasets ---
merged = pd.merge(nz, sg, on="Vessel_IMO", how="inner", suffixes=("_NZ", "_SG"))
merged = pd.merge(merged, jp, on="Vessel_IMO", how="inner", suffixes=("", "_JP"))

merged["NZ_to_SG_days"] = (pd.to_datetime(merged["ActualArrival_SG"]) - pd.to_datetime(merged["Departure_NZ"])).dt.days
merged["SG_to_JP_days"] = (pd.to_datetime(merged["ActualArrival_JP"]) - pd.to_datetime(merged["ActualArrival_SG"])).dt.days
merged["Total_Transit_Days"] = merged["NZ_to_SG_days"] + merged["SG_to_JP_days"]

# --- Group by delay type ---
summary = merged.groupby("DepartureType")[["NZ_to_SG_days","SG_to_JP_days","Total_Transit_Days"]].mean().round(1)
summary["Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")

summary.to_csv(f"{data_path}\\eta_summary_comparison.csv")
merged.to_csv(f"{data_path}\\eta_multileg_final.csv", index=False)
print("✅ Parsed and merged ETA data successfully.")
