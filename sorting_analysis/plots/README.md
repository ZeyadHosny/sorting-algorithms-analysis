# plots

Draws static charts from typed experiment and analysis results. Matplotlib is optional and
is imported only inside the chart functions. Data preparation uses the standard library and
the project's own Merge Sort for ordering size metadata; it never uses `sort()` or `sorted()`.

## The six figures

| File | Contents | Function |
|---|---|---|
| `scaling_summary.png` | Runtime, comparisons and writes versus n; three vertically stacked panels | `plot_scaling` |
| `scaling_tiny_runtime.png` | Tiny-input runtime on linear axes, in microseconds per sort | `plot_scaling` |
| `input_order_summary.png` | Runtime, comparisons and writes for the four input orders | `plot_input_order` |
| `repeated_values_summary.png` | Runtime, comparisons and writes across dataset columns | `plot_repeated_values` |
| `growth_factors.png` | Observed versus theoretical runtime multipliers for each doubling pair | `plot_growth` |
| `bubble_extrapolation.png` | Measured-range model fit and full-range extrapolation, in two panels | `plot_bubble_extrapolation` |

The three original summary functions keep their existing signatures. The last two figures
are team-selected additions; the PDF requires the associated analyses, not these exact image layouts.
`plot_scaling` returns two paths when tiny inputs exist and one otherwise. Other plotting
functions return one path when their inputs exist. Empty inputs or missing matplotlib return `[]`.

## Interfaces

Import public functions from the area: `from sorting_analysis.plots import ...`.

| Function | Input | Return |
|---|---|---|
| `matplotlib_available()` | None | Boolean |
| `plot_scaling(cases, output_folder)` | Typed `case_row` or `read_cases` rows | List of written PNG paths |
| `plot_input_order(cases, output_folder)` | Same | List of written PNG paths |
| `plot_repeated_values(cases, output_folder)` | Same | List of written PNG paths |
| `plot_growth(growth_rows, output_folder)` | Typed rows returned by `growth_factors` | List of written PNG paths |
| `plot_bubble_extrapolation(cases, estimate_row, fitted_rows, output_folder)` | Cases and both outputs of `extrapolate_bubble` | List of written PNG paths |

No function reruns the sorting experiments or fits a new model. The extrapolation chart only
evaluates the supplied coefficients to draw that existing model. It checks that the estimate,
fitted values and measured medians agree with the supplied inputs. Predictions are never
added to the measured markers. Non-positive model predictions are shown with a warning,
rather than silently changed into physically plausible values.

## Visual conventions

- Bubble: blue `#0072B2`, circles, solid lines.
- Selection: orange `#E69F00`, squares, dashed lines.
- Merge: green `#009E73`, triangles, dash-dot lines.
- Algorithm order is always Bubble, Selection, Merge. Input orders are random, sorted,
  reversed, nearly. Required columns appear in the configured default column order.
- Scaling uses lines with markers; categorical comparisons use grouped dots without connecting lines.
- Scaling size axes are logarithmic. Positive scaling runtime/comparison axes are logarithmic.
  Categorical runtime/comparison axes become logarithmic only when max/min is at least 100.
  This threshold is a documented display choice, not a statistical rule. Writes always use a
  linear axis starting at zero; other panels with zeros also stay linear. Axis labels identify logs.
- All runtime summaries use seconds per sort. Only the tiny-input detail converts to microseconds
  for display (`seconds * 1,000,000`), without dividing by batch repetitions again.
- Runtime whiskers are the observed min-to-max range, not a confidence interval. Counts have no whiskers.
- Missing cases stay gaps, with a missing-case count in the summary caption. Zeros stay zero.
- Text uses Arial when installed, with DejaVu Sans as a portable fallback.
- Summary PNGs are 6.5 by 8 inches at 300 dpi. Tiny detail is 6.5 by 4.6; growth is 6.5 by 8.4; extrapolation is 6.5 by 7.3.
  Keep figures legible at their final placed size; a slide may show one panel at a time.
- Duplicate case keys, inconsistent experiment context, negative counts and invalid measured timing
  ranges raise `ValueError` instead of silently combining incomparable measurements.
- Plots alone do not establish a duplication effect or memory usage. Use the sample duplication
  table and explain implementation and input-order limitations in the report.

## Integration handoff

The supplied `main.py` snapshot still contains mocks. This feature does not edit that shared file.
During the separate integration step, replace the original plot mocks with the real functions,
then explicitly call the two new functions using already computed analysis results:

```python
plot_files += plot_growth(growth_rows, output_folder)
plot_files += plot_bubble_extrapolation(case_rows, estimate_row, fitted_rows, output_folder)
```

Here `growth_rows` is the result of `growth_factors(case_rows)` and `(estimate_row, fitted_rows)`
is the result of `extrapolate_bubble(...)`. Wire these values into the actual pipeline when its
analysis functions are integrated; the names above are not existing globals. Include all six
returned paths in the run's generated-file metadata. The first three existing plot calls produce
four files because scaling includes the tiny-input detail.

Without matplotlib, `python main.py all` must continue to print `INCOMPLETE: plots missing`.
Build equivalent charts from the real CSV outputs in Excel/Sheets if needed. Module unit tests
skip rendering when matplotlib is absent; availability/fallback tests still run.

Run chart tests from the repository root:

```text
python -m sorting_analysis.plots.charts.testing.test_charts
python -m unittest discover
```

Test fixture numbers are invented solely to verify plotting. They are not experimental evidence.
No official charts or runtime conclusions are included in this code-only feature.
