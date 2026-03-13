# create_report.py

import os
import re
from collections import defaultdict
from IPython.display import Image, display
import plotly.io as pio

# Configuration
csv_folder = "data/raw"
qmd_file = "report_generated.qmd"
variables_to_plot = ["A Flow velocity [m/s]"]  # you can add more
cache_folder = "_quarto_cache"
output_folder = "outputs"

os.makedirs(output_folder, exist_ok=True)
os.makedirs(cache_folder, exist_ok=True)

# 1️⃣ Scan CSV files and group by measurement point
files_by_point = defaultdict(list)

for f in os.listdir(csv_folder):
    if f.lower().endswith(".csv"):
        point = f.rsplit("_", 1)[-1].replace(".csv", "")
        files_by_point[point].append(f)

# 1.1 Sort the points
def point_sort_key(point_name):
    m = re.match(r"STE-(\d+)(?:_(.*))?$", point_name)
    if m:
        number = int(m.group(1))
        suffix = m.group(2) or ""
        return (0, number, suffix)
    else:
        return (1, point_name)

sorted_points = sorted(files_by_point.keys(), key=point_sort_key)

# 2️⃣ Write QMD
with open(qmd_file, "w", encoding="utf-8") as f:
    f.write(f"""---
title: "Automated Measurement Report"
author: Arnau Coronado Nadal
execute:
  cache: true
  cache-dir: {cache_folder}
format:
  html:
    toc: true
    code-fold: true
  pdf:
    css: print.css
    toc: true
---\n\n""")

    for point, files in sorted(files_by_point.items()):
        f.write(f"## {point}\n\n")
        f.write(f"Plots for measurement point {point}:\n\n")
        
        for csv_file in files:
            csv_path = os.path.join(csv_folder, csv_file)
            date_str = csv_file.split("_")[0]
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # YYYY-MM-DD
            f.write(f"### {csv_file} ({date_formatted})\n\n")
            
            for var in variables_to_plot:
                chunk = f"""```{{python}}
#| echo: false
#| fig-align: center

import sys, os
sys.path.append(os.path.abspath("src"))
from create_plots import load_csv, create_plotly_plot
from IPython.display import Image, display
import plotly.io as pio

csv_path = r"{csv_path}"
variable = "{var}"

df = load_csv(csv_path)
fig = create_plotly_plot(df, variable, csv_path)

# Detect Quarto output format
quarto_format = os.environ.get("QUARTO_FORMAT", "").lower()
is_pdf = quarto_format in ["pdf", "latex"]

if is_pdf:
    os.makedirs(r"{output_folder}", exist_ok=True)
    png_path = os.path.join(r"{output_folder}", os.path.basename(csv_path).replace(".csv", ".png"))
    try:
        fig.write_image(png_path, width=900, height=450, scale=2)
        display(Image(filename=png_path))
    except Exception as e:
        print("Could not export figure. Make sure 'kaleido' is installed.")
        print(e)
else:
    # Interactive HTML plot
    pio.renderers.default = "notebook_connected"
    fig.show()
```\n\n"""
                f.write(chunk)

print(f"✅ Generated {qmd_file}")