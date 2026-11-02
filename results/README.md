# results

Official outputs, written only by `python main.py all`. Never edit these files by hand. Development runs write to `results/dev/`, which is not committed.

| File | One row per | Columns |
|---|---|---|
| `inspection.csv` | selected column | column, rows, missing, distinct, excluded_rows |
| `cases.csv` | algorithm × input (45) | experiment, algorithm, column, order, input_size, comparisons, writes, swaps, sorts_per_batch, median_s, min_s, max_s |
| `timing_runs.csv` | timed batch | experiment, algorithm, column, order, input_size, batch, seconds_per_sort |
| `dupes_stats.csv` | column of the repeated-values experiment | column, sample_size, distinct, modal_value, modal_count, repeated_distinct, repeated_observations |
| `growth.csv` | algorithm × doubling of n | algorithm, size_from, size_to, time_from_s, time_to_s, observed_factor, theoretical_factor |
| `extrapolation.csv` | method × base size | method, half_size, base_size, base_time_s, constant_c, exponent_b, estimate_s |
| `metadata.json` | run | seeds, sizes, timing tiers, Python version, dataset SHA-256, timestamp, plots_status, generated_files |
| `*.png` | chart | runtime, comparisons and writes per experiment |

Times are seconds per sort. `swaps` is `n/a` for merge sort. `metadata.json` is written last and only when the run succeeds; `plots_status` is `missing` if the charts could not be drawn.
