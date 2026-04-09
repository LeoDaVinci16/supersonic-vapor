import os
import re
from collections import defaultdict
import plotly.graph_objects as go
import pandas as pd
from points_dict import main

# Configuration
csv_folder = "data/raw"
qmd_file = "report_generated_pdf.qmd"
variables_to_plot = ["A Flow velocity [m/s]"]  # add more if needed
cache_folder = "_quarto_cache_pdf"
output_folder = "outputs"
plots_folder = os.path.join(output_folder, "plots")

# Ensure output folders exist
os.makedirs(output_folder, exist_ok=True)
os.makedirs(cache_folder, exist_ok=True)
os.makedirs(plots_folder, exist_ok=True)

# 1️⃣ Scan CSV files and group by measurement point
files_by_point = defaultdict(list)
for f in os.listdir(csv_folder):
    if f.lower().endswith(".csv"):
        point = f.rsplit("_", 1)[-1].replace(".csv", "")
        files_by_point[point].append(f)

# 1.1 Sort measurement points like STE-1, STE-2, ..., non-STE alphabetically
def point_sort_key(point_name):
    m = re.match(r"STE-(\d+)(?:_(.*))?$", point_name)
    if m:
        number = int(m.group(1))
        suffix = m.group(2) or ""
        return (0, number, suffix)
    else:
        return (1, point_name)

sorted_points = sorted(files_by_point.keys(), key=point_sort_key)

# 2️⃣ Helper functions

def load_csv(path):
    df = pd.read_csv(path, sep='\t')
    df.columns = df.columns.str.strip()  # remove leading/trailing spaces
    print("doing plot number n")
    return df

def sanitize_filename(name):
    # Replace spaces, slashes, brackets, percent signs, etc.
    name = name.replace(' ', '_')
    name = name.replace('/', '-')
    name = name.replace('[', '')
    name = name.replace(']', '')
    name = name.replace('%', '')
    name = name.replace('(', '')
    name = name.replace(')', '')
    return name


def create_plot(df, variable, output_path):
    fig = go.Figure()
    if variable in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[variable], mode='lines+markers', name=variable))
        fig.update_layout(title=variable, xaxis_title='Index', yaxis_title=variable)
        fig.write_image(output_path, scale=2)  # high-res for PDF
        print(f"Saved plot: {output_path}")
    else:
        print(f"Variable {variable} not found in {csv_path}")

# 3️⃣ Step 1: Generate all plots first
plot_paths = defaultdict(dict)  # {point: {csv_file: {variable: path}}}
for point, files in sorted(files_by_point.items()):
    for csv_file in files:
        csv_path = os.path.join(csv_folder, csv_file)
        df = load_csv(csv_path)
        plot_paths[point][csv_file] = {}
        for var in variables_to_plot:
            sanitized_var = sanitize_filename(var)
            sanitized_csv = sanitize_filename(csv_file)
            plot_file = os.path.join(plots_folder, f"{sanitized_csv}_{sanitized_var}.png")
            create_plot(df, var, plot_file)
            plot_paths[point][csv_file][var] = plot_file

# 4️⃣ Step 2: Write QMD file referencing existing plots
with open(qmd_file, "w", encoding="utf-8") as f:
    f.write(f"""---
title: "Informe dels cabals (PDF)"
author: Arnau Coronado Nadal
execute:
  cache: true
  cache-dir: {cache_folder}
format:
  pdf:
    toc: true
---\n\n""")

    for point in sorted_points:
        f.write(f"## Punt de mesura {point}\n\n")
        f.write(f"Gràfiques de les mesures fetes en el punt {point}:\n\n")
        for csv_file in sorted(files_by_point[point]):
            date_str = csv_file.split("_")[0]
            date_formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"  # YYYY-MM-DD
            f.write(f"### {csv_file} ({date_formatted})\n\n")
            for var in variables_to_plot:
                plot_file = plot_paths[point][csv_file][var]
                # Use raw string with forward slashes to prevent LaTeX errors
                plot_file = plot_file.replace('\\', '/')
                f.write(f"![]({plot_file}){{ width=80% }}\n\n")

print(f"✅ Generated {qmd_file} with sanitized static plots for PDF")
