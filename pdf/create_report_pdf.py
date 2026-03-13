# create_report_pdf.py

import os
import re
from collections import defaultdict
from IPython.display import Image, display
import plotly.io as pio

# ----------------------
# Script folder & paths
# ----------------------
script_dir = os.path.dirname(os.path.abspath(__file__))

# CSV folder (repo root/data/raw)
csv_folder = os.path.join(script_dir, "..", "data", "raw")

# Output and cache inside this PDF folder
output_folder = os.path.join(script_dir, "outputs")
cache_folder = os.path.join(script_dir, "_quarto_cache")

# QMD file and CSS
qmd_file = os.path.join(script_dir, "report_generated_pdf.qmd")
css_file = "print.css"  # CSS file should be in the same folder

# Variables to plot
variables_to_plot = ["A Flow velocity [m/s]"]  # add more if needed

# Ensure folders exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(cache_folder, exist_ok=True)

# ----------------------
# 1️⃣ Scan CSV files
# ----------------------
files_by_point = defaultdict(list)
for f in os.listdir(csv_folder):
    if f.lower().endswith(".csv"):
        point = f.rsplit("_", 1)[-1].replace(".csv", "")
        files_by_point[point].append(f)

# Sort points nicely
def point_sort_key(point_name):
    m = re.match(r"STE-(\d+)(?:_(.*))?$", point_name)
    if m:
        number = int(m.group(1))
        suffix = m.group(2) or ""
        return (0, number, suffix)
    else:
        return (1, point_name)

sorted_points = sorted(files_by_point.keys(), key=point_sort_key)

# ----------------------
# 2️⃣ Write QMD
# ----------------------
with open(qmd_file, "w", encoding="utf-8") as f:
    f.write(f"""---
title: "Automated Measurement Report (PDF)"
author: Arnau Coronado Nadal
execute:
  cache: true
  cache-dir: {cache_folder}
format:
  pdf:
    css: {css_file}
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
                # Python chunk with code hidden in PDF
                f.write(f"""```{{python}}
#| echo: false
from create_plots import load_csv, create_plotly_plot
from IPython.display import Image, display
import plotly.io as pio
import os

csv_path = r"{csv_path}"
variable = "{var}"
output_folder = r"{output_folder}"

df = load_csv(csv_path)
fig = create_plotly_plot(df, variable, csv_path)

# Export static PNG for PDF (updated API)
os.makedirs(output_folder, exist_ok=True)
png_path = os.path.join(output_folder, os.path.basename(csv_path).replace(".csv", ".png"))
try:
    pio.defaults.default_format = "png"
    fig.write_image(png_path, width=900, height=450, scale=2)
    display(Image(filename=png_path))
except Exception as e:
    print("Could not export figure. Make sure 'kaleido' is installed.")
    print(e)
```\n\n""")

print(f"✅ Generated {qmd_file}")