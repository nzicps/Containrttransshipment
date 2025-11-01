import pandas as pd, numpy as np, matplotlib.pyplot as plt, os, datetime

print("📈 Running breakeven cost comparison...")

base = r"C:\Users\seeds\Documents\Containrttransshipment"
data_dir = os.path.join(base, "data")
docs_dir = os.path.join(base, "docs")

os.makedirs(data_dir, exist_ok=True)
os.makedirs(docs_dir, exist_ok=True)

ports = ["Auckland", "Tauranga", "Lyttelton"]
containers = [60, 70, 65]
nz_cost_per_day = 45
transship_cost = [108000, 115500, 113750]

rows = []
for port, cont, t_cost in zip(ports, containers, transship_cost):
    days = np.arange(0, 15)
    nz_costs = cont * (nz_cost_per_day * days + 320 + 180)
    diff = t_cost - nz_costs
    breakeven_day = int(days[np.argmin(np.abs(diff))])
    rows.append((port, breakeven_day))

    plt.figure(figsize=(6,4))
    plt.plot(days, nz_costs, label="NZ Deferred Storage")
    plt.axhline(y=t_cost, color="gray", linestyle="--", label="Singapore Transshipment")
    plt.title(f"{port} Breakeven Analysis")
    plt.xlabel("Deferred Days in NZ")
    plt.ylabel("Total Cost (NZD)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(docs_dir, f"breakeven_{port}.png"))
    plt.close()

df = pd.DataFrame(rows, columns=["Port", "Breakeven_Day"])
df.to_csv(os.path.join(data_dir, "breakeven_summary.csv"), index=False)
print(df)
print(f"✅ Saved breakeven charts to {docs_dir}")

html = f"""
<html><head><title>NZ Storage vs Singapore Breakeven</title>
<style>
body {{font-family: Arial; background: #f9fafc; margin: 40px;}}
h1,h2 {{text-align: center;}}
table {{border-collapse: collapse; margin: 0 auto; width: 80%;}}
th,td {{border:1px solid #ccc; padding:8px; text-align:center;}}
img {{display:block; margin:20px auto; max-width:80%; border-radius:8px;}}
</style></head>
<body>
<h1>⚖️ NZ Storage vs Singapore Transshipment Breakeven</h1>
<p style='text-align:center;'>Updated {datetime.date.today()}</p>
<table>
<tr><th>Port</th><th>Breakeven Day (Days)</th></tr>
{''.join([f"<tr><td>{p}</td><td>{d}</td></tr>" for p,d in rows])}
</table>
<hr>
<h2>Cost Curves by Port</h2>
""" + "\\n".join(
    [f"<img src='breakeven_{p}.png' alt='{p} breakeven plot'>" for p in ports]
) + """
<footer style='text-align:center;color:gray;margin-top:40px;'>
Data: PortConnect (NZ), OpenFreightData, Simulated Cost Curves
</footer>
</body></html>
"""

with open(os.path.join(docs_dir, "breakeven.html"), "w", encoding="utf-8") as f:
    f.write(html)

print(f"🌍 Breakeven dashboard ready: {docs_dir}\\breakeven.html")
