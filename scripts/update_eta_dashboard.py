import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

data_path = r"C:\\Users\\seeds\\Documents\\Containrttransshipment\\data"
docs_path = r"C:\\Users\\seeds\\Documents\\Containrttransshipment\\docs"

try:
    df = pd.read_csv(f"{data_path}\\eta_multileg_final.csv")
except FileNotFoundError:
    print("⚠️ Missing merged data file.")
    exit()

# Compute averages by delay type
if "DepartureType" in df.columns:
    avg = df.groupby("DepartureType")[["NZ_to_SG_days","SG_to_JP_days","Total_Transit_Days"]].mean().reset_index()
else:
    avg = pd.DataFrame(columns=["DepartureType","NZ_to_SG_days","SG_to_JP_days","Total_Transit_Days"])

# Create stacked bar chart
fig = go.Figure()
for _, row in avg.iterrows():
    fig.add_trace(go.Bar(
        name=row["DepartureType"],
        x=["NZ→SG", "SG→JP"],
        y=[row["NZ_to_SG_days"], row["SG_to_JP_days"]],
        text=[f"{row['NZ_to_SG_days']} d", f"{row['SG_to_JP_days']} d"],
        textposition="auto"
    ))

fig.update_layout(
    barmode='group',
    title="⛴️ NZ → SG → JP Transit Comparison (Delayed vs On-Time)",
    yaxis_title="Days",
    xaxis_title="Leg Segment",
    template="plotly_white",
    legend_title_text="Departure Type"
)

chart_html = f"{docs_path}\\eta_multileg_chart.html"
fig.write_html(chart_html, include_plotlyjs="cdn", full_html=False)

# Update dashboard HTML
index_path = f"{docs_path}\\index.html"
with open(index_path, "r", encoding="utf-8") as f:
    html = f.read()

section_html = f"""
<section>
<h2>🧭 ETA Delay Impact (NZ ➜ SG ➜ JP)</h2>
<p>Visual analysis of delay propagation from NZ departures to Japan arrivals.</p>
<iframe src="eta_multileg_chart.html" width="100%" height="480" style="border:none;"></iframe>
<p style='text-align:center;color:gray;'>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</section>
"""

import re
if re.search("🧭 ETA Delay Impact", html):
    html = re.sub(r"<section>.*?🧭 ETA Delay Impact.*?</section>", section_html, html, flags=re.S)
else:
    html = html.replace("</footer>", section_html + "\n</footer>")

with open(index_path, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard updated with delay impact chart.")
