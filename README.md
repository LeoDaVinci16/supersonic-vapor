# supersonic-vapor

## Automated Steam Measurement Report

This repository contains a fully automated system to generate measurement reports for Euromed’s steam pipes. The workflow uses Python to process CSV data, Plotly for interactive plotting, and Quarto for report generation. The system supports both interactive HTML reports for analysis and static PDF-ready reports for printing.

## 📂 Repository Structure

```Bash
vapor/
│
├─ data/raw/                # Raw CSV files from measurement campaigns
├─ src/                     # Python scripts
│  ├─ create_plots.py       # Functions to load CSVs and generate interactive/static plots
│  └─ create_report.py      # Script to generate Quarto files dynamically from CSVs
├─ outputs/                 # Optional output folder for PNGs or exported figures
├─ report_vapor.qmd         # Main Quarto report (HTML + optional PDF)
├─ report_generated.qmd     # Dynamically generated QMD from Python script
└─ README.md                # This file
```

## ⚡ Features

1. Automated CSV Processing
    - Detects CSV files in data/raw/
    - Groups files by measurement points (STE-1, STE-2, …, E800, PEC)
    - Automatically extracts the measurement date from filenames

2. Interactive Plot Generation
    - Uses Plotly for interactive HTML plots
    - Figures are embedded in the Quarto report for immediate analysis
    - Plot size can be adjusted dynamically

3. Dynamic Report Creation
    - Python create_report.py generates Quarto markdown (.qmd)
    - Titles, dates, and sections are automatically added based on CSV filenames
    - Code chunks can be hidden for a clean report

4. PDF/Printable Reports
    - Optional workflow to export static PNG figures
    - Generate a PDF-ready report using Quarto from the PNG-based QMD
    - Automatic page breaks and pagination for printing

5. File Sorting & Naming Automation
    - CSVs with STE-1, STE-2 … STE-10 are sorted numerically
    - Optional zero-padding (e.g., STE-01) to maintain correct order

## 🛠️ Usage
1. Install dependencies
```bash
pip install pandas plotly kaleido quarto
```

`kaleido` is required for exporting Plotly figures to PNG.

`quarto` must be installed for rendering QMD files.

2. Generate the interactive HTML report
```bash
python src/create_report.py
quarto render report_generated.qmd
```
    - Opens `report_generated.html` with interactive plots.
    - Useful for exploring the data during analysis.

3. Generate a static, printable report
    1. Modify create_plots.py to export figures as PNG:

    ```bash
    fig.write_image(f"outputs/{csv_file_name}.png", width=800, height=400)
    ```

    2. Modify `create_report_png.py` (or reuse the main script) to embed PNG images instead of interactive plots:

    ```bash
    ![](outputs/STE-01_20251204.png){ width=80% }
    ```

    3. Render PDF from the PNG-based Quarto file:

    ```bash
    quarto render report_png.qmd --to pdf
    ```
    
        - Ensures figures are fixed-size, paginated, and ready to print.

## 🧩 Customization
- Variables to plot: Edit the variables_to_plot list in create_report.py
- Figure size: Adjust in create_plotly_plot() or write_image()
- Measurement point detection: Modify the regex in point_sort_key() for custom naming schemes

## ⚙️ Notes
- Keep interactive HTML for analysis; use PNG exports for final PDF/printing.
- CSV filenames must include the measurement point (e.g., STE-2) and date (YYYYMMDD).
- Zero-padded STE numbers (e.g., STE-01) ensure correct numeric sorting.

## 👤 Author
**Arnau Coronado Nadal**
Estudi de cabals Euromed