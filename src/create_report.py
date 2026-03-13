# create report

import os
from collections import defaultdict


# Configuration
csv_folder = "data/raw"
qmd_file = "report_generated.qmd"
variables_to_plot = ["A Flow velocity [m/s]"]  # you can add more

# 1️⃣ Scan CSV files and group by measurement point
files_by_point = defaultdict(list)

for f in os.listdir(csv_folder):
    if f.lower().endswith(".csv"):
        # Extract measurement point: everything after last underscore before .csv
        # e.g., 20251007_100341_STE-4.csv -> STE-4
        point = f.rsplit("_", 1)[-1].replace(".csv", "")
        files_by_point[point].append(f)

# 1.1 Sort the points and files
import re
def point_sort_key(point_name):
    """
    Sort measurement points like:
    STE-1, STE-2, STE-3, ..., STE-10, STE-11, ..., then non-STE points alphabetically.
    """
    m = re.match(r"STE-(\d+)(?:_(.*))?$", point_name)
    if m:
        number = int(m.group(1))        # numeric part
        suffix = m.group(2) or ""       # anything after _
        return (0, number, suffix)      # 0 ensures STE points come first
    else:
        return (1, point_name)          # non-STE points come later, sorted alphabetically

# Now sort the points
sorted_points = sorted(files_by_point.keys(), key=point_sort_key)

# 2️⃣ Start writing the QMD file
with open(qmd_file, "w") as f:
    f.write("""---
title: "Automated Measurement Report"
format: html
---\n\n""")

    # Iterate over each measurement point
    for point, files in sorted(files_by_point.items()):
        f.write(f"## {point}\n\n")
        f.write(f"Next I will show the plots done on the measurement point {point}.\n\n")
        
        # Add each CSV file as a subsection
        for csv_file in files:
            csv_path = os.path.join(csv_folder, csv_file)
            # Optional: extract date from filename (first part YYYYMMDD)
            date_str = csv_file.split("_")[0]
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # YYYY-MM-DD
            
            f.write(f"### {csv_file} ({date_formatted})\n\n")
            
            # Add Python chunk to create plot
            for var in variables_to_plot:
                chunk = f"""```{{python}}
#| echo: false
#| fig-align: center

import sys, os
sys.path.append(os.path.abspath("src"))
from create_plots import load_csv, create_plotly_plot

csv_path = r"{csv_path}"
variable = "A Flow velocity [m/s]"

df = load_csv(csv_path)
fig = create_plotly_plot(df, variable, csv_path)
fig 
```\n\n"""
                f.write(chunk)

print(f"✅ Generated {qmd_file}")



