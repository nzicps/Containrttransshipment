import pandas as pd, numpy as np, matplotlib.pyplot as plt, os, datetime

print("📈 Rebuilding breakeven comparison with clearer visuals...")

base = r"C:\Users\seeds\Documents\Containrttransshipment"
data_dir = os.path.join(base, "data")
docs_dir = os.path.join(base, "docs")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

ports = ["Auckland", "Tauranga", "Lyttelton"]
containers = [60, 70, 65]
nz_cost_per_day = 45
transship_total = {"Auckland":108000, "Tauranga":115500, "Lyttelton":113750}

rows = []
days = np.arange(0, 15)

for port, c, t_cost in zip(ports, containers, [transship_total[p] for p in ports]):
    nz_costs = c * (nz_cost_per_day * days + 320 + 180)
    diff = t_cost - nz_costs
    be_day = int(days[np.argmin(np.abs(diff))])
    rows.append((port, be_day))

    plt.figure(figsize=(7.5,5.2), dpi=140)
    plt.plot(days, nz_costs, linewidth=3, label="NZ Deferred Storage (total)")
    plt.axhline(y=t_cost, linestyle="--", linewidth=2, label="SG Transshipment (total)")

    cheaper_mask = nz_costs < t_cost
    if cheaper_mask.any():
        plt.fill_between(days, nz_costs, t_cost, where=cheaper_mask, alpha=0.18)

    plt.axvline(be_day, linestyle=":", linewidth=2)
    y_val = c * (nz_cost_per_day * be_day + 320 + 180)
    plt.scatter([be_day], [y_val], s=60)
    plt.annotate(f"Breakeven ≈ {be_day} day(s)",
                 xy=(be_day, y_val),
                 xytext=(be_day+0.5, y_val*1.03),
                 arrowprops=dict(arrowstyle="->", lw=1))

    plt.title(f"{port}: NZ vs SG — Breakeven", fontsize=13, pad=12)
    plt.xlabel("Deferred days in NZ yard", fontsize=11)
    plt.ylabel("Total cost (NZD)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend(loc="best", frameon=False)
    plt.tight_layout()
    plt.savefig(os.path.join(docs_dir, f"breakeven_{port}.png"))
    plt.close()

df = pd.DataFrame(rows, columns=["Port", "Breakeven_Day"])
df.to_csv(os.path.join(data_dir, "breakeven_summary.csv"), index=False)

html = f"""
<html><head><title>⚖️ NZ Storage vs Singapore Transshipment — Breakeven</title>
<style>
body {{font-family: Arial; background: #f9fafc; margin: 30px;}}
h1,h2 {{text-align: center;}}
table {{border-collapse: collapse; margin: 0 auto; width: 85%;}}
th,td {{border:1px solid #ddd; padding:8px; text-align:center;}}
th {{background:#f0f3f8;}}
img {{display:block; margin:18px auto; max-width:95%; border-radius:8px;}}
</style></head>
<body>
<h1>⚖️ NZ Storage vs Singapore Transshipment — Breakeven</h1>
<p style='text-align:center;'>Updated {datetime.date.today()}</p>
<table>
<tr><th>Port</th><th>Breakeven Day (days)</th></tr>
{''.join([f"<tr><td>{p}</td><td>{d}</td></tr>" for p,d in df.values])}
</table>
<hr>
<h2>Cost Curves by Port</h2>
""" + "\\n".join([f"<img src='breakeven_{p}.png' alt='{p} breakeven'>" for p in ports]) + """
<footer style='text-align:center;color:gray;margin-top:24px;'>
Assumptions: NZ yard 45 NZD/day/TEU, Truck 320 NZD/ctn, Wharf 180 NZD/ctn.
</footer>
</body></html>
"""

with open(os.path.join(docs_dir, "breakeven.html"), "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Breakeven visuals refreshed → {docs_dir}\\breakeven.html")
