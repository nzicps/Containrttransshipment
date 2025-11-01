import os, datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

base = r"C:\Users\seeds\Documents\Containrttransshipment"
docs = os.path.join(base, "docs")
data = os.path.join(base, "data")
os.makedirs(docs, exist_ok=True); os.makedirs(data, exist_ok=True)

print("📦 Rebuilding Local-Storage (NZ) scenario with clearer breakeven charts...")

# --- Inputs (fallbacks kept simple & explicit) ---
ports         = ["Auckland", "Tauranga", "Lyttelton"]
containers    = [60, 70, 65]                 # per-port fleet
yard_nz_day   = 45.0                         # NZ yard/day/TEU
truck_per_ctn = 320.0                        # one-off per container
wharf_per_ctn = 180.0                        # one-off per container
# Reference Singapore transshipment totals from your prior page (constant lines)
trans_total   = {"Auckland":108000, "Tauranga":115500, "Lyttelton":113750}

days = np.arange(0, 15)                      # show up to 14 deferred days

rows = []
for port, ctn in zip(ports, containers):
    # NZ deferred total = per-container yard*days + truck + wharf, times number of containers
    nz_costs = ctn * (yard_nz_day * days + truck_per_ctn + wharf_per_ctn)
    sg_line  = np.full_like(days, trans_total[port])

    # Breakeven = day with minimal abs difference
    diff = sg_line - nz_costs
    be_day = int(days[np.argmin(np.abs(diff))])
    cheaper_mask = nz_costs < sg_line

    # --- Pretty chart ---
    plt.figure(figsize=(7.5, 5.2), dpi=140)
    plt.plot(days, nz_costs, linewidth=3, label="NZ Deferred Storage (total)")
    plt.plot(days, sg_line, linewidth=2, linestyle="--", label="SG Transshipment (total)")

    # Shade region where NZ is cheaper
    if cheaper_mask.any():
        plt.fill_between(days, nz_costs, sg_line, where=cheaper_mask, alpha=0.18)

    # Breakeven marker & label
    plt.axvline(be_day, linestyle=":", linewidth=2)
    y_val = ctn * (yard_nz_day * be_day + truck_per_ctn + wharf_per_ctn)
    plt.scatter([be_day], [y_val], s=60)
    plt.annotate(f"Breakeven ≈ {be_day} day(s)",
                 xy=(be_day, y_val),
                 xytext=(be_day+0.5, y_val*1.03),
                 arrowprops=dict(arrowstyle="->", lw=1))

    # Formatting for readability
    plt.title(f"{port}: Local NZ vs SG Transshipment — Breakeven", fontsize=13, pad=12)
    plt.xlabel("Deferred days in NZ yard", fontsize=11)
    plt.ylabel("Total cost (NZD)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend(loc="best", frameon=False)
    plt.tight_layout()
    out_png = os.path.join(docs, f"local_breakeven_{port}.png")
    plt.savefig(out_png)
    plt.close()

    rows.append((port, ctn, be_day, int(y_val), int(trans_total[port])))

# Summary table & small overview bar chart
df = pd.DataFrame(rows, columns=["Port","Containers","Breakeven_Day","NZ_Cost_at_BE","SG_Transshipment_Total"])
df.to_csv(os.path.join(data, "local_breakeven_summary.csv"), index=False)

# Overview bar chart of Breakeven Day per port
plt.figure(figsize=(7.5, 4.5), dpi=140)
plt.bar(df["Port"], df["Breakeven_Day"])
for i,(p,be) in enumerate(zip(df["Port"], df["Breakeven_Day"])):
    plt.text(i, be+0.15, f"{be}d", ha="center", va="bottom")
plt.title("Breakeven Day by Port (NZ defer vs SG transshipment)", fontsize=13, pad=10)
plt.ylabel("Days", fontsize=11)
plt.grid(axis="y", linestyle="--", alpha=0.35)
plt.tight_layout()
plt.savefig(os.path.join(docs, "local_breakeven_overview.png"))
plt.close()

# Rebuild local_storage.html to include the clearer charts
html = f"""
<html><head><title>📦 Local NZ Deferred Departure — Breakeven</title>
<style>
body {{ font-family:Arial; background:#f9fafc; margin:30px; }}
h1, h2 {{ text-align:center; }}
.card {{ background:white; padding:20px; border-radius:12px; box-shadow:0 0 8px rgba(0,0,0,0.08); margin:20px auto; width:92%; }}
img {{ display:block; margin:12px auto; max-width:95%; border-radius:8px; }}
table {{ border-collapse:collapse; width:95%; margin:10px auto; }}
th,td {{ border:1px solid #ddd; padding:8px; text-align:center; }}
th {{ background:#f0f3f8; }}
.note {{ color:gray; font-size:13px; text-align:center; margin-top:14px; }}
</style></head>
<body>
<div class="card">
  <h1>📦 Local NZ Deferred Departure — Breakeven View</h1>
  <p style="text-align:center;">Updated {datetime.date.today()}</p>
  <img src="local_breakeven_overview.png" alt="Breakeven day overview">
</div>

<div class="card">
  <h2>Per-Port Cost Curves</h2>
  {''.join([f"<img src='local_breakeven_{p}.png' alt='{p} breakeven chart'>" for p in df['Port']])}
</div>

<div class="card">
  <h2>Summary</h2>
  {df.to_html(index=False)}
  <p class="note">Assumptions: NZ yard {yard_nz_day:.0f} NZD/day/TEU, Truck {truck_per_ctn:.0f} NZD/ctn, Wharf {wharf_per_ctn:.0f} NZD/ctn.<br>
  SG transshipment totals from prior analysis are used as constant comparison lines.</p>
</div>
</body></html>
"""
with open(os.path.join(docs, "local_storage.html"), "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Local-storage breakeven visuals refreshed → {docs}\\local_storage.html")
