plots
Draws static charts and result tables from typed experiment and analysis results.
Matplotlib is optional and is imported inside the chart functions. Data preparation
uses the standard library and the project's own Merge Sort to order size metadata;
it never uses `sort()` or `sorted()`.
Output files
With the default experiments and Matplotlib available, the plotting stage generates
six charts and three result-table images:
File	Contents	Function
`scaling_summary.png`	Runtime, comparisons and writes versus n; three vertically stacked panels	`plot_scaling`
`scaling_tiny_runtime.png`	Tiny-input runtime on linear axes, in microseconds per sort	`plot_scaling`
`input_order_summary.png`	Runtime, comparisons and writes for the four input orders	`plot_input_order`
`repeated_values_summary.png`	Runtime, comparisons and writes across the three selected columns	`plot_repeated_values`
`growth_factors.png`	Observed versus theoretical runtime multipliers for each doubling pair	`plot_growth`
`bubble_extrapolation.png`	Measured-range model fit and full-range extrapolation, in two panels	`plot_bubble_extrapolation`
`scaling_table.png`	Operation counts, swaps and median runtime for each scaling case	`plot_result_tables`
`input_order_table.png`	Operation counts, swaps and median runtime for each input-order case	`plot_result_tables`
`repeated_values_table.png`	Operation counts, swaps and median runtime for each repeated-value case	`plot_result_tables`
The assignment requires the associated measurements and analyses, not these exact
image layouts. `plot_scaling` returns two paths when tiny inputs exist and one
otherwise. The other individual chart functions return one path when their inputs
exist. `plot_result_tables` returns up to three paths, one per available experiment.
Empty inputs or missing Matplotlib return `[]` from the plotting functions.
Interfaces
Import public functions from the area: `from sorting_analysis.plots import ...`.
Function	Input	Return
`matplotlib_available()`	None	Boolean
`plot_scaling(cases, output_folder)`	Typed `case_row` or `read_cases` rows	List of written PNG paths
`plot_input_order(cases, output_folder)`	Same	List of written PNG paths
`plot_repeated_values(cases, output_folder)`	Same	List of written PNG paths
`plot_growth(growth_rows, output_folder)`	Typed rows returned by `growth_factors`	List of written PNG paths
`plot_bubble_extrapolation(cases, estimate_row, fitted_rows, output_folder)`	Cases and both outputs of `extrapolate_bubble`	List of written PNG paths
`plot_result_tables(cases, output_folder)`	Typed `case_row` or `read_cases` rows	List of written table-image PNG paths
The plotting functions do not rerun sorting experiments or fit a new model.
The extrapolation chart evaluates the supplied coefficients and checks that the
estimate, fitted values and measured medians agree with its inputs, and that the
target size lies beyond the largest fitted size. Predictions are never added to
the measured markers. Non-positive model predictions are shown
with a warning rather than silently changed.
Visual conventions
Bubble: blue `#0072B2`, circles, solid lines where lines are used.
Selection: orange `#E69F00`, squares, dashed lines where lines are used.
Merge: green `#009E73`, triangles, dash-dot lines where lines are used.
Algorithm order is Bubble, Selection, Merge. Input orders are random, sorted,
reversed, nearly. The three required columns follow the default selected-column order.
Scaling uses lines with markers. Categorical comparisons use grouped dots
without connecting lines.
Summary runtime axes are logarithmic. Scaling size axes are also logarithmic.
The separate tiny-input runtime chart uses linear axes starting at zero on y.
Comparison axes are logarithmic when all counts are positive and either the
experiment is scaling or the largest count is at least 100 times the smallest.
Otherwise, comparison axes are linear and start at zero.
Summary write axes use a symmetric logarithmic (`symlog`) scale with a linear
region from 0 to 1 and logarithmic spacing above it. This keeps zero writes
visible while allowing large counts to be compared. Axis labels identify the scale.
Runtime markers show the median of batch averages. Each batch average is elapsed
time divided by sorts per batch. The current charts do not draw minimum-to-maximum
whiskers or confidence intervals. Minimum and maximum values remain in `cases.csv`;
individual batch averages remain in `timing_runs.csv`.
Summary runtime axes use seconds per sort. The tiny-input chart converts to
microseconds (`seconds * 1,000,000`) without dividing by repetitions again.
Result tables select microseconds, milliseconds or seconds and label each value.
Operation counts are deterministic counts, not timing estimates. Merge Sort's
swap count is shown as `n/a` in the result tables.
Missing summary-chart cases remain gaps, with a missing-case count in the caption.
Missing result-table cases are omitted and counted in the table note. Zeros stay zero.
Text uses Arial when installed, with DejaVu Sans as a portable fallback.
PNGs are exported at 300 dpi. Summary charts are 6.5 by 8 inches; the tiny-input
chart is 6.5 by 4.6; growth is 6.5 by 8.4; extrapolation is 6.5 by 7.3.
Result-table height depends on the number of rows. Keep figures legible at their
final report or slide size.
Duplicate case keys, inconsistent experiment contexts, negative counts and invalid
measured timing ranges raise `ValueError` rather than mixing incompatible results.
Growth charts distinguish observed multipliers from theoretical references.
Extrapolation charts distinguish measurements, the fitted curve and the prediction.
Plots alone do not establish a causal duplication effect or measure memory use.
Interpret them alongside duplication statistics, input order and implementation details.
Pipeline integration and usage
Plotting is integrated into `main.py`. Its `run_plots()` function calls all six
plotting functions: `plot_scaling`, `plot_input_order`, `plot_repeated_values`,
`plot_growth`, `plot_bubble_extrapolation` and `plot_result_tables`.
During an official `python main.py all` run, the program prepares the cases and
analysis results, draws the nine PNGs when Matplotlib is available, and records
their returned paths in `metadata.json` under `generated_files`.
To regenerate the plots from the existing official `results/cases.csv`, run this
command from the repository root:
```text
python main.py plot --out results
```
This command recomputes the growth and extrapolation inputs from the saved case
rows and generates the PNGs without rerunning the sorting measurements. Use
`--out` to select the folder containing the intended `cases.csv`; without it,
the development `plot` command defaults to `results/dev/`.
The `plot` command requires Matplotlib. Without Matplotlib, `python main.py all`
still completes the computations, prints `INCOMPLETE: plots missing`, and records
`plots_status` as `missing`. Equivalent charts can be made from the real CSV outputs
in Excel or Google Sheets.
Tests
Run from the repository root:
```text
python -m sorting_analysis.plots.charts.testing.test_charts
python -m unittest discover
```
Rendering tests skip when Matplotlib is unavailable; availability and fallback
checks still run. Test-fixture numbers are invented solely to verify plotting.
Use the actual experiment outputs in `results/` as evidence in the report.