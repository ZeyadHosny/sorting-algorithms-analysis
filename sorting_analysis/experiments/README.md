# experiments

The three experiments. Each measures all three algorithms with `benchmark` and returns one `CaseResult` per algorithm and input.

| Feature | Purpose | Cases |
|---|---|---|
| `common/` | `CaseResult`, the algorithm table, and CSV writing/reading | — |
| `scaling/` | Increasing sample sizes of `median_income` | 3 algorithms × 8 sizes = 24 |
| `input_order/` | Random, sorted, reversed, nearly sorted (`median_income`, n = 2000) | 3 × 4 = 12 |
| `repeated_values/` | The three columns, same rows in the same order as the input-order experiment | 3 × 3 = 9 |

## Interfaces

### common

| Name | Input | Output |
|---|---|---|
| `ALGORITHMS` | — | `{"bubble", "selection", "merge"}` → sort function |
| `CaseResult(experiment, algorithm, column, order, input_size, sort_stats, timing)` | labels, `SortStats`, `TimingResult` | read-only record of one case, with a getter per value |
| `case_row(case)` | one case | dict with the `CASE_FIELDS` keys (used by `write_cases` and `main.py`) |
| `write_cases(cases, path)` | cases, path | `cases.csv` with `CASE_FIELDS`; merge sort swaps written as `n/a` |
| `write_runs(cases, path)` | cases, path | `timing_runs.csv` with `RUN_FIELDS`, one row per batch |
| `write_rows(rows, path, fieldnames)` | dicts, path, header | CSV; empty rows give a header-only file |
| `read_cases(path)` | path | typed rows; `ValueError` on a malformed number |

### experiments

| Function | Input | Output |
|---|---|---|
| `run_scaling(rows, usable_indices, settings)` | raw rows, usable indices, settings | `list[CaseResult]` |
| `run_input_order(rows, usable_indices, settings)` | same | `list[CaseResult]` |
| `run_repeated_values(rows, usable_indices, settings)` | same | `(list[CaseResult], duplicate stats per column)` |

All three raise `ValueError` if a sample size exceeds the usable rows; `VerificationError` from `benchmark` is passed on.
