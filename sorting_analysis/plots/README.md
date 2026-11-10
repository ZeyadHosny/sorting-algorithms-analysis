# plots

Draws the charts and result tables from the experiment and analysis results. Matplotlib is optional and imported only inside the functions; without it, every plotting function returns `[]`. Sizes are ordered with merge sort, never `sort()` or `sorted()`.

## Figures

| File | Contents | Function |
|---|---|---|
| `scaling_summary.png` | Runtime, comparisons and writes versus n | `plot_scaling` |
| `scaling_tiny_runtime.png` | Runtime of the very small inputs, in microseconds | `plot_scaling` |
| `input_order_summary.png` | Runtime, comparisons and writes for the four input orders | `plot_input_order` |
| `repeated_values_summary.png` | Runtime, comparisons and writes for the three columns | `plot_repeated_values` |
| `growth_factors.png` | Observed versus theoretical growth for each doubling of n | `plot_growth` |
| `bubble_extrapolation.png` | Measured medians, the fitted curve and the estimate at the target size | `plot_bubble_extrapolation` |
| `scaling_table.png`, `input_order_table.png`, `repeated_values_table.png` | Comparisons, writes, swaps and median runtime of every case | `plot_result_tables` |

Each function returns the paths it wrote: `plot_scaling` up to two, `plot_result_tables` up to three, the others one.

## Interfaces

Import from the area: `from sorting_analysis.plots import ...`.

| Function | Input |
|---|---|
| `matplotlib_available()` | None; returns `True` if the charts can be drawn |
| `plot_scaling`, `plot_input_order`, `plot_repeated_values`, `plot_result_tables` `(cases, output_folder)` | Case rows from `case_row` or `read_cases` |
| `plot_growth(growth_rows, output_folder)` | Rows from `growth_factors` |
| `plot_bubble_extrapolation(cases, estimate_row, fitted_rows, output_folder)` | Case rows and both outputs of `extrapolate_bubble` |

The extrapolation chart draws the given model without refitting it, after checking that the estimate, fitted values and measured medians agree and that the target lies beyond the fitted sizes. Non-positive model values are shown with a warning, never changed.

## Conventions

- Bubble: blue, circles, solid lines. Selection: orange, squares, dashed. Merge: green, triangles, dash-dot. Algorithms always appear in this order; input orders as random, sorted, reversed, nearly.
- Summary charts: runtime and scaling sizes use logarithmic axes. Comparisons use a logarithmic axis when every count is positive and either the experiment is scaling or the largest count is at least 100 times the smallest. Writes use a symmetric logarithmic axis, linear from 0 to 1, so zero stays visible.
- Runtime points are medians, without whiskers; the CSV files keep the minimum and maximum. Footers explain the runtime and report missing cases, which stay gaps.
- Text uses Arial when installed, otherwise DejaVu Sans. PNGs are 6.5 inches wide at 300 dpi.
- Duplicate cases, mixed experiment contexts, negative counts and invalid times raise `ValueError`.

## Tests

`python -m sorting_analysis.plots.charts.testing.test_charts` runs the chart tests; the rendering tests are skipped without matplotlib. Fixture numbers are invented for the tests.
