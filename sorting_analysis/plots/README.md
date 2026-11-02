# plots

Draws the charts from `cases.csv` and saves them as PNG files. This is the only package that uses matplotlib, which is optional and imported inside the functions.

| Feature | Purpose |
|---|---|
| `charts/` | Scaling, input-order and repeated-values charts |

Without matplotlib, `python main.py all` completes and prints `INCOMPLETE: plots missing`. Build the same charts in Excel or Google Sheets from `results/cases.csv` and save them in `results/`.

## Interfaces

| Function | Input | Output |
|---|---|---|
| `matplotlib_available()` | — | `True` if matplotlib can be imported |
| `plot_scaling(cases, output_folder)` | typed case rows, folder | paths of runtime, comparisons and writes vs n charts |
| `plot_input_order(cases, output_folder)` | same | paths of the per-order charts |
| `plot_repeated_values(cases, output_folder)` | same | paths of the per-column charts |
