# Sorting Algorithm Analysis — Architecture & Requirements

Project 2, Fall 2026 · Reference: `Project-2.pdf` (all `§` numbers refer to it) · Python 3, standard library only (matplotlib optional for plots)

**Contents**
1. [Architecture and flow](#1-architecture-and-flow)
2. [Interfaces](#2-interfaces)
3. [Project requirements](#3-project-requirements) — [3.1 Clear and clarified](#31-clear-requirements) · [3.2 ⚠️ Open](#32-open-requirements-waiting-for-the-instructor) · [3.3 Design decisions](#33-design-decisions-not-from-the-pdf) · [3.4 Known limitations](#34-known-limitations)
4. [Requirements per file](#4-requirements-per-file)
5. [Coverage check](#5-coverage-check)

---

## 1. Architecture and flow

### 1.1 Repository layout

```
Project_2/
├── README.md                       general README: overview, obtain housing.csv, run, interpret outputs
├── main.py                         command-line entry point
├── .gitignore                      __pycache__/, results/dev/, .venv/, .vscode/
├── housing.csv                     dataset, committed (U-02)
│
├── sorting_analysis/
│   ├── README.md · __init__.py · config.py                     testing/test_config.py
│   ├── data/            README.md
│   │   ├── loader/          implementation/loader.py           testing/test_loader.py
│   │   ├── inspection/      implementation/inspection.py       testing/test_inspection.py
│   │   ├── sampling/        implementation/sampling.py         testing/test_sampling.py
│   │   └── orders/          implementation/orders.py           testing/test_orders.py
│   ├── sorts/           README.md
│   │   ├── common/          sort_stats.py                      testing/logged_value.py (test helper)
│   │   ├── bubble_sort/     implementation/bubble_sort.py, counted_bubble_sort.py        testing/test_bubble_sort.py
│   │   ├── selection_sort/  implementation/selection_sort.py, counted_selection_sort.py  testing/test_selection_sort.py
│   │   └── merge_sort/      implementation/merge_sort.py, counted_merge_sort.py          testing/test_merge_sort.py
│   ├── timing/          README.md
│   │   └── benchmark/       implementation/benchmark.py        testing/test_benchmark.py
│   ├── experiments/     README.md
│   │   ├── common/          records.py                         testing/test_records.py
│   │   ├── scaling/         implementation/scaling.py          testing/test_scaling.py
│   │   ├── input_order/     implementation/input_order.py      testing/test_input_order.py
│   │   └── repeated_values/ implementation/repeated_values.py  testing/test_repeated_values.py
│   ├── analysis/        README.md
│   │   ├── common/          filters.py                         testing/test_filters.py
│   │   ├── growth/          implementation/growth.py           testing/test_growth.py
│   │   └── extrapolation/   implementation/extrapolation.py    testing/test_extrapolation.py
│   └── plots/           README.md
│       └── charts/          implementation/charts.py           testing/test_charts.py
│
├── tests/               README.md · test_end_to_end.py
└── results/             README.md · generated outputs (committed)
```

Every area and feature folder, `common/` and `testing/` contains an `__init__.py`; `implementation/` folders have none (the feature's `__init__.py` imports from them directly). `testing/` folders keep theirs because `python -m unittest discover` only searches folders that have one. `config.py` and the `common/` modules with logic (`records.py`, `filters.py`) have their own `testing/` folder; `sort_stats.py` is a plain record, covered by the sort tests. Each sort has two files with the same loops: the plain version (timed) and the counted version (operation counts), see U-11. Each feature's `__init__.py` re-exports its public names (`from .implementation.bubble_sort import bubble_sort`), and each area's `__init__.py` re-exports its features, so every import has the form `from sorting_analysis.sorts import bubble_sort`. This holds inside an area too; each area's `__init__.py` imports its `common/` first, because the features import its names back through the area. Everything runs from the repository root (the folder with `main.py`): `python main.py ...`, `python -m unittest discover`, or one test file as a module, e.g. `python -m sorting_analysis.sorts.selection_sort.testing.test_selection_sort`. All paths are relative to the root.

### 1.2 Allowed dependencies

| Module | May import |
|---|---|
| `config.py` | standard library only |
| `sorts/common` | nothing from the project |
| `sorts/<algorithm>` | `sorts/common` |
| `data/loader`, `data/sampling` | `config` |
| `data/inspection` | `config`, `data/loader` (shared `parse_value`, U-01) |
| `data/orders` | `config`, `sorts/merge_sort` (plain version, to build "already sorted", U-08) |
| `timing/benchmark` | `config`, `sorts/merge_sort` (plain version, for the median, U-16); the plain and counted sorts are passed in |
| `experiments/common` | `config`, `sorts`, `timing` |
| `experiments/<experiment>` | `config`, `data`, `sorts`, `timing`, `experiments/common` |
| `analysis/common` | `experiments/common` |
| `analysis/<feature>` | `config`, `experiments/common` (CSV read/write), `analysis/common` |
| `plots/charts` | `config`, `experiments/common`, matplotlib (optional) |
| `main.py` | everything |

Rules: `sorts` never imports data preparation. `common/` holds what an area's features share (record types, CSV schema I/O, filters) and never imports the features that use it. Only `plots/` may import matplotlib. The graph has no cycles.

### 1.3 Data flow

```
housing.csv
   │  data.loader.load_csv
   ▼
raw rows ──► data.inspection.inspect_data ──(main: write_rows)──────────► results/inspection.csv
   │  data.loader.complete_cases
   ▼
valid row indices
   │  data.sampling.sample_indices   (seeded, without replacement)
   ▼
   │  data.sampling.shuffle_indices   (4.3 and 4.4: same seed → same order)
   ▼
samples: list[float] ──► data.orders.make_orders   (4.3 only)
   │
   ▼
experiments.{scaling, input_order, repeated_values}
   │   for each input × algorithm:  timing.benchmark(sort_function, counted_sort_function, values, settings)
   │        → per batch: counted sort once, untimed (counts) + timed loop of the plain sort
   │        → verify every output vs sorted() after the clock → TimingResult + SortStats
   ▼
CaseResult list ──(write_cases / write_runs / write_rows)───────────────► results/cases.csv, timing_runs.csv, dupes_stats.csv
   │
   ▼
analysis.{growth, extrapolation (quadratic fit)} ──(main: write_rows)──► results/growth.csv, extrapolation.csv
   │
   ▼
plots.charts (matplotlib) ──────────────────────────────────────────────► results/*.png
   │      (if matplotlib is missing: run reports "plots missing"; make them in Excel/Sheets — D-09)
   ▼
main.write_metadata ────────────────────────────────────────────────────► results/metadata.json  (written last, only on success)
```

At the start of `all`, any existing `metadata.json` and previously generated PNGs are deleted, so a failed run can never leave an old success marker or stale charts beside partly overwritten files (D-03). `metadata.json` records `plots_status` (`"complete"` / `"missing"`) and the list of files this run generated. The exit code is 0 when all computations succeed, even with plots missing; submission completeness is read from `plots_status`.

### 1.4 Timing rule

| Input tier | Sizes | Sorts per timed batch (`reps`) | Batches | Reported |
|---|---|---|---|---|
| Very small | n ≤ 20 (5, 10, 20) | 1,000 | 5 | median of (batch time ÷ 1,000) |
| Normal | n > 20 (250 … 4000) | 1 | 5 | median of the 5 single-sort times |

Only the **plain** sort (no counters) is timed (U-11). The timed region (`time.perf_counter()`) contains its calls **plus** storing each output for later verification (U-15, D-08). The **counted** sort runs once per batch outside the clock and supplies the counts. Loading, sampling, building input orders, counting and verification all happen outside the timed region.

**Workload with the default settings:** 45,180 timed sort calls (45,000 of them in the very-small tier) plus 225 untimed counted calls (45 cases × 5 batches), dominated in wall-clock time by the bubble and selection sorts at n = 2000–4000. Do a pilot run before relying on any runtime estimate.

### 1.5 Command line

| Command | Does |
|---|---|
| `python main.py check` | Load and inspect the dataset; print rows, missing values and distinct values. |
| `python main.py scaling` / `order` / `dupes` | Run one experiment (development; see D-03). |
| `python main.py analyze` | Compute growth factors and the bubble sort estimate (quadratic regression) from `results/cases.csv`; print measured vs fitted times. |
| `python main.py plot` | Draw charts (needs matplotlib). |
| `python main.py all` | Official run: check → 3 experiments → analyze → plot (skipped with a message if matplotlib is missing) → metadata. |
| Options `--csv PATH`, `--out DIR` | Override the dataset path and output folder. |
| `python -m unittest discover` | Run every unit test and the end-to-end test. |

Exit codes (team convention, not a PDF requirement): `0` all computations succeeded (plots may be missing, see `plots_status`) · `1` computation failure (verification failed, invalid timings, unimplemented step, unexpected error) · `2` input or usage error (dataset missing, required column missing, no complete rows, sample size larger than the usable rows, `cases.csv` missing or malformed) · `130` interrupted. `analyze` and `plot` read `<out>/cases.csv`. While any pipeline step in `main.py` is still a mock, outputs default to `results/dev/`, writing into `results/` (or any folder holding a `metadata.json`) is refused with exit code 2, old outputs are not deleted, and `metadata.json` is not written, so fake numbers never reach `results/`. In `all`, the analysis uses the run's cases directly (`case_row`); `analyze` and `plot` read them back with `read_cases`.

### 1.6 Result files

| File | Written by | One row per | Columns |
|---|---|---|---|
| `inspection.csv` | `main` via `write_rows` | selected column | column, rows, missing, distinct, excluded_rows |
| `cases.csv` | `experiments/common.write_cases` | algorithm × input (45 rows) | experiment, algorithm, column, order, input_size, comparisons, writes, swaps, sorts_per_batch, median_s, min_s, max_s |
| `timing_runs.csv` | `experiments/common.write_runs` | timed batch | experiment, algorithm, column, order, input_size, batch, seconds_per_sort |
| `dupes_stats.csv` | `main` via `write_rows` | column in 4.4 | column, sample_size, distinct, modal_value, modal_count, repeated_distinct, repeated_observations |
| `growth.csv` | `main` via `write_rows` | algorithm × doubling | algorithm, size_from, size_to, time_from_s, time_to_s, observed_factor, theoretical_factor |
| `extrapolation.csv` | `main` via `write_rows` | the estimate (1 row) | method (`quadratic_fit`), sizes_used, a0, a1, a2, target_size, estimate_s |
| `metadata.json` | `main.write_metadata` | run | seeds, sizes, timing tiers, Python version, dataset SHA-256, timestamp, plots_status, generated_files |
| `*.png` | `plots/charts` | chart | runtime/comparisons/writes vs n; per input order; per column |

---

## 2. Interfaces

Signatures are binding between team members. Code style: no type hints; `Settings` is values only (public attributes, no methods); the result records are plain classes with private attributes, set once by the constructor and read with `get_<attribute>()`; every docstring has **Description / Input arguments / Return** (types are given there). Comments below show the types.

### 2.1 `sorting_analysis/config.py`

```python
class Settings:
    def __init__(self, csv_path="housing.csv", results_folder="results",
                 selected_columns=("median_income", "housing_median_age", "median_house_value"),
                 scaling_column="median_income", order_column="median_income",
                 sample_seed=42, shuffle_seed=43, nearly_sorted_seed=44,
                 scaling_sizes=(5, 10, 20, 250, 500, 1000, 2000, 4000), order_sample_size=2000,
                 timed_batches=5, small_input_limit=20, small_input_repetitions=1000,
                 normal_input_repetitions=1, extrapolation_target_size=20640,
                 extrapolation_base_sizes=(250, 500, 1000, 2000, 4000)): ...
    # Stores each argument as a public attribute (settings.order_sample_size, ...). No methods:
    # the code that uses a value lives in its feature module.

DEFAULT_SETTINGS = Settings()
```

Defaults are module constants with a comment each (`DEFAULT_SAMPLE_SEED = 42`, …). Tests pass a small `Settings(...)`, e.g. `Settings(scaling_sizes=(5, 10, 15, 20, 25), order_sample_size=10, extrapolation_base_sizes=(5, 10, 15, 20, 25))` (D-04); the quadratic fit needs at least 3 sizes.

### 2.2 `data/`

```python
# data/loader/implementation/loader.py
def load_csv(path): ...                          # -> list[dict]: every row via csv.DictReader, values as strings; FileNotFoundError
def parse_value(raw_value): ...                  # -> float | None: None if blank, unparsable or not finite
def complete_cases(rows, columns): ...           # -> list[int]: indices of rows where every selected column parses
def column_values(rows, column, row_indices): ...  # -> list[float]: parsed values in the order of row_indices

# data/inspection/implementation/inspection.py
INSPECTION_FIELDS = ("column", "rows", "missing", "distinct", "excluded_rows")
DUPES_FIELDS = ("column", "sample_size", "distinct", "modal_value", "modal_count", "repeated_distinct",
                "repeated_observations")
def inspect_data(rows, columns): ...             # -> list[dict]: one INSPECTION_FIELDS row per column, from raw rows;
                                                 #    missing = parse_value is None; excluded_rows = rows dropped by complete_cases
def duplicate_stats(values): ...                 # -> dict with the DUPES_FIELDS keys except column

# data/sampling/implementation/sampling.py
def sample_indices(usable_indices, sample_size, seed): ...  # -> list[int]: without replacement, random.Random(seed); ValueError if too large
def shuffle_indices(row_indices, seed): ...      # -> list[int]: new list in random.Random(seed).shuffle order (used once by 4.3 and 4.4)

# data/orders/implementation/orders.py
def ascending(values): ...                       # -> list[float]: new ascending list by our plain merge_sort (never sorted())
def descending(values): ...                      # -> list[float]: reverse of ascending(values)
def nearly_sorted(values, seed): ...             # -> list[float]: ascending, then floor(0.01 * len(values)) swaps of two distinct random positions
def make_orders(shuffled_values, nearly_sorted_seed): ...  # -> dict: 'random' (shuffled_values unchanged), 'sorted', 'reversed', 'nearly'
```

### 2.3 `sorts/`

```python
# sorts/common/sort_stats.py
class SortStats:
    def __init__(self, comparisons, writes, swaps): ...   # ints; swaps is None for merge sort (U-18)
    # get_comparisons(), get_writes(), get_swaps()

# Plain versions: timed, no counters, return the new ascending list.
# sorts/bubble_sort/implementation/bubble_sort.py
def bubble_sort(values): ...                     # -> list[float]; lecture code: full passes, stop after a pass with no swaps
# sorts/selection_sort/implementation/selection_sort.py
def selection_sort(values): ...                  # -> list[float]; at most one swap per position (PDF)
# sorts/merge_sort/implementation/merge_sort.py
def merge_sort(values): ...                      # -> list[float]
def _merge_sort_recursive(sublist): ...          # -> list[float]
def _merge(left_half, right_half): ...           # -> list[float]; ties take from left_half (<=)

# Counted versions: same loops plus local counters, never timed, return (new ascending list, SortStats).
# sorts/bubble_sort/implementation/counted_bubble_sort.py
def counted_bubble_sort(values): ...             # [3,1,2] -> 4 comparisons, 4 writes, 2 swaps
# sorts/selection_sort/implementation/counted_selection_sort.py
def counted_selection_sort(values): ...          # [3,1,2] -> 3 comparisons, 4 writes, 2 swaps
# sorts/merge_sort/implementation/counted_merge_sort.py
def counted_merge_sort(values): ...              # [2,1] -> 1 comparison, 2 writes, swaps None
def _merge_sort_recursive(sublist): ...          # -> tuple: (sorted list, comparisons, writes) for this subtree
def _merge(left_half, right_half): ...           # -> tuple: (merged list, comparisons, writes)

# sorts/common/testing/logged_value.py (test helper; re-exported: from sorting_analysis.sorts import logged_values)
class LoggedValue: ...                           # a number that logs every <, <=, >, >= into a shared list
def logged_values(numbers, log): ...             # -> list[LoggedValue]
```

All six sorts return a **new** list and never modify the input. Bubble and selection sort copy it first by slicing (`a = values[:]`); merge sort never writes into its input, because splitting by slicing creates new lists. Copies made by splitting or slicing, including the initial copy, are **not** counted (§4.1, U-10, R-16); every value placed into a merged output list, including leftover tails, **is** counted. The plain and counted versions of an algorithm have the same loops; each sort test checks on `logged_values` inputs that both make the same comparison sequence (D-10).

### 2.4 `timing/`

```python
# timing/benchmark/implementation/benchmark.py
class TimingResult:
    def __init__(self, batch_seconds, sorts_per_batch, median_seconds, min_seconds, max_seconds): ...
    # batch_seconds: tuple of seconds per sort, one per batch; the median (via median_of), min and max
    # are computed once by benchmark. Getters: get_batch_seconds() ... get_max_seconds()

class VerificationError(Exception): ...           # output differs from sorted(), counts differ between runs, or input changed

def benchmark(sort_function, counted_sort_function, values, settings=DEFAULT_SETTINGS): ...
    # -> tuple: (TimingResult, SortStats); settings.timed_batches batches. Per batch: counted_sort_function
    #    once outside the clock (output, unchanged input and identical counts checked), then
    #    repetitions_for(len(values), settings) timed calls of sort_function; every output verified afterwards

def repetitions_for(input_size, settings=DEFAULT_SETTINGS): ...
    # -> int: settings.small_input_repetitions if input_size <= settings.small_input_limit,
    #    else settings.normal_input_repetitions

def median_of(values): ...                        # -> float: median computed with our plain merge_sort
```

### 2.5 `experiments/`

```python
# experiments/common/records.py
ALGORITHMS = {"bubble": (bubble_sort, counted_bubble_sort),      # name -> (plain sort, counted sort)
              "selection": (selection_sort, counted_selection_sort),
              "merge": (merge_sort, counted_merge_sort)}
CASE_FIELDS = ("experiment", "algorithm", "column", "order", "input_size", "comparisons", "writes", "swaps",
               "sorts_per_batch", "median_s", "min_s", "max_s")
RUN_FIELDS = ("experiment", "algorithm", "column", "order", "input_size", "batch", "seconds_per_sort")
NOT_APPLICABLE = "n/a"                            # how merge sort's missing swap count is written

class CaseResult:
    def __init__(self, experiment, algorithm, column, order, input_size, sort_stats, timing): ...
    # experiment: 'scaling' | 'order' | 'dupes'; algorithm: 'bubble' | 'selection' | 'merge';
    # order: 'random' | 'sorted' | 'reversed' | 'nearly'. Getters: get_experiment() ... get_timing()

def case_row(case): ...                           # -> dict with the CASE_FIELDS keys (swaps stays None)
def write_cases(cases, path): ...                 # cases.csv; swaps None written as "n/a"
def write_runs(cases, path): ...                  # timing_runs.csv, one row per batch
def write_rows(rows, path, fieldnames): ...       # generic CSV with explicit header; [] -> header-only file
def read_cases(path): ...                         # -> list[dict]: typed (ints, floats, "n/a" -> None); ValueError if malformed

# experiments/scaling/implementation/scaling.py
def run_scaling(rows, usable_indices, settings=DEFAULT_SETTINGS): ...          # -> list[CaseResult]: 3 algorithms x scaling_sizes (24)

# experiments/input_order/implementation/input_order.py
def run_input_order(rows, usable_indices, settings=DEFAULT_SETTINGS): ...      # -> list[CaseResult]: one sample -> shuffle_indices -> make_orders -> 12

# experiments/repeated_values/implementation/repeated_values.py
def run_repeated_values(rows, usable_indices, settings=DEFAULT_SETTINGS): ...  # -> tuple: (9 CaseResults, duplicate_stats per column)
```

### 2.6 `analysis/`

```python
# analysis/common/filters.py
def scaling_cases(cases): ...                     # -> list[dict]: only rows with experiment == 'scaling'

# analysis/growth/implementation/growth.py
GROWTH_FIELDS = ("algorithm", "size_from", "size_to", "time_from_s", "time_to_s", "observed_factor",
                 "theoretical_factor")
def theoretical_factor(algorithm, smaller_size, larger_size): ...  # -> float: size ratio squared, or the n log n ratio for merge
def growth_factors(cases): ...                    # -> list[dict]: observed T(2n)/T(n) per doubling pair, beside the theoretical factor

# analysis/extrapolation/implementation/extrapolation.py
FIT_METHOD = "quadratic_fit"
EXTRAPOLATION_FIELDS = ("method", "sizes_used", "a0", "a1", "a2", "target_size", "estimate_s")
FITTED_FIELDS = ("input_size", "measured_s", "fitted_s")
def determinant_3x3(matrix): ...                  # -> float
def fit_quadratic(sizes, times): ...              # -> tuple: (a0, a1, a2), least squares via Cramer's rule;
                                                  #    ValueError if < 3 distinct sizes, lengths differ, or singular
def predict_time(coefficients, input_size): ...   # -> float: a0 + a1*n + a2*n**2
def bubble_times(cases, base_sizes): ...          # -> list[float]: bubble sort scaling median_s per base size;
                                                  #    ValueError if a size is missing/duplicated or a time is not > 0 and finite
def extrapolate_bubble(cases, target_size, base_sizes): ...
    # -> tuple: (estimate row with EXTRAPOLATION_FIELDS, measured-vs-fitted rows with FITTED_FIELDS)
```

### 2.7 `plots/`

```python
# plots/charts/implementation/charts.py
def matplotlib_available(): ...                   # -> bool
def plot_scaling(cases, output_folder): ...       # -> list[str]: scaling summary and tiny-runtime detail paths
def plot_input_order(cases, output_folder): ...
def plot_repeated_values(cases, output_folder): ...
def plot_growth(growth_rows, output_folder): ...  # -> list[str]: observed and theoretical growth figure
def plot_bubble_extrapolation(cases, estimate_row, fitted_rows, output_folder): ...
    # -> list[str]: measured points, fitted quadratic and explicitly labelled extrapolation
    # Inputs are existing analysis outputs; charts do not rerun experiments or fit a new model.
```

### 2.8 `main.py` and `tests/`

```python
# main.py
def main(argument_list=None, settings=DEFAULT_SETTINGS): ...   # -> int: exit code
def write_metadata(path, csv_path, settings, plots_status, generated_files): ...
    # seeds, sizes, timing tiers, Python version, dataset SHA-256, timestamp, plots_status
    # ("complete" / "missing"), generated_files; temporary file + os.replace
# Pipeline helpers: mocked_steps, parse_arguments, choose_output_folder, same_folder, check_output_folder,
# load_dataset, check_sample_size, run_inspection, run_experiments, run_analysis, run_plots,
# read_case_rows, run_all, remove_previous_outputs, run_command.

# tests/test_end_to_end.py
class TestMockRun(unittest.TestCase): ...         # pipeline while steps are mocked
class TestEndToEnd(unittest.TestCase): ...        # main(['all'], settings=<small Settings>) on a tiny CSV, temp folder
```

---

## 3. Project requirements

### 3.1 Clear requirements

R-rows are stated explicitly in the PDF; the U-rows under **Clarified requirements** were unclear and are now settled. `Qn` = numbered item in §4 (Q1–Q5 are the numbered items of §4.2).

| ID | Requirement | § | Example |
|---|---|---|---|
| **Scope & rules** | | | |
| R-01 | Implement bubble, selection and merge sort from scratch | §2 | Own loops, no library sort |
| R-02 | Standard library only for loading data and the algorithms; no pandas, NumPy, scikit-learn, heapq | §2 | `csv`, `time`, `random`, `math` |
| R-03 | Never use `sort()` or `sorted()` to load, sort or process data; `sorted()` is allowed **solely** to verify output | §2 | `assert out == sorted(values)` |
| R-04 | *Permission:* a command-line program or notebook is sufficient; a GUI is not required | §2 | `python main.py all` |
| R-05 | *Permission:* tables/plots may be made with Excel/Sheets; matplotlib is optional | §2 | `results/scaling_runtime.png` |
| **Data** | | | |
| R-06 | Use `housing.csv` from the given URL, placed in the same folder as the code | §3 (1) | `Project_2/housing.csv` |
| R-07 | Read with the `csv` module (e.g. `DictReader`); convert selected values to float | §3 (2) | `float(row["median_income"])` |
| R-08 | Code inspects the CSV and reports the number of rows, missing values in the selected columns, and distinct values per selected column | §3 | `median_income: 20640 rows, 0 missing, … distinct` |
| R-09 | 4.2 and 4.3 use `median_income`; 4.4 uses all three columns | §3 | — |
| R-10 | Sort the numeric values themselves. *Optional, not planned:* if full records are sorted, use the selected column as the key and explain | §3 (4) | `[8.3252, 7.2574, …]` |
| R-11 | *Optional, not planned:* if `total_bedrooms` is analysed, document missing-value handling | §3 (3) | — |
| **Fairness & counting** | | | |
| R-12 | Same input values for all three algorithms within a comparison | §4 | One sample → 3 sorts |
| R-13 | Preserve an unchanged copy of each input; sorting functions must not modify the original list | §4 | `values` unchanged after the call |
| R-14 | Comparison = each comparison of two data values; loop-counter and index checks not counted | §4.1 | `a[j] > a[j+1]` → +1 |
| R-15 | Write = each store of a data value into a list position; a swap = 2 writes (swaps may also be reported) | §4.1 | One swap → writes += 2 |
| R-16 | Merge: each value placed into the merged output = 1 write; splitting/slicing copies not counted, and the report says so | §4.1 | Merge of 4 values → 4 writes |
| R-17 | Bubble sort stops as soon as a full pass makes no swaps | §4.1 | Sorted input → 1 pass |
| R-18 | Selection sort swaps only when the minimum is not already in place | §4.1 | Sorted input → 0 swaps |
| R-19 | Merge sort takes from the left half on ties (`<=`) | §4.1 | `left[i] <= right[j]` |
| R-20 | Time with `time.perf_counter()`; exclude data loading | §4.1 | — |
| R-21 | Verify every output against `sorted()` | §4.1 | — |
| R-22 | State any additional implementation choices in the report | §4.1 | Clarified requirements (§3.1), §3.2 – §3.4 of this document |
| **4.2 Scaling** | | | |
| R-23 | Q1: random samples of increasing size with a recorded seed, including very small sizes; all three algorithms on the same sample at each size | §4.2 (1) | n = 5, 10, 20, 250 … 4000, seed 42 |
| R-24 | Q2: record runtime, comparisons and writes for each algorithm and size | §4.2 (2) | One row per case |
| R-25 | Q2: repeat each timing ≥ 5 times on the same input; report the median | §4.2 (2) | 5 batches → median |
| R-26 | Q2: operation counts identical across repeated runs on the same input | §4.2 (2) | 5 runs → same comparisons |
| R-27 | Q2: very small inputs — time a loop of many repetitions and divide by the count | §4.2 (2) | 1,000 sorts ÷ 1,000 |
| R-28 | Q3: when n doubles, compute the observed growth factor; compare with O(n²) and O(n log n); explain differences | §4.2 (3) | 1000→2000: quadratic 4.00, merge ≈ 2.20 |
| R-29 | Q4: estimate bubble sort on **20,640 random values** from measurements; show calculation and assumptions; use more than one sample size **if possible**; explain why approximate | §4.2 (4) | Quadratic regression on n = 250 … 4000 (U-19) |
| R-30 | *Optional, not planned:* run bubble sort once on all 20,640 values, only after the estimate; if done, report the actual time and compare it with the estimate | §3, §4.2 (4) | — |
| R-31 | Q5: identify the sizes where merge sort's advantage becomes apparent; discuss why less visible for very small inputs | §4.2 (5) | — |
| **4.3 Input order** | | | |
| R-32 | Fixed sample size ≥ 1,000, large enough to show differences, small enough for all three to finish | §4.3 | n = 2000 |
| R-33 | Four versions of the same values: random (shuffle with recorded seed); already sorted (using **own** implementation); reverse sorted; nearly sorted (ascending, then floor(0.01·n) swaps, each of two distinct positions chosen **uniformly** at random, seed recorded) | §4.3 | n = 2000 → 20 swaps |
| R-34 | Run each algorithm on each version; record comparisons, writes, swaps (if counted), median runtime; identical versions across algorithms | §4.3 | 12 cases |
| R-35a | Q6: explain why bubble sort on sorted data makes ~n−1 comparisons and no swaps | §4.3 (6) | n = 2000 → 1,999 comparisons |
| R-35b | Q7: explain why selection sort makes ~n(n−1)/2 comparisons even on sorted input | §4.3 (7) | n = 2000 → 1,999,000 |
| R-35c | Q8: explain why merge sort's comparison count changes less with order than bubble sort's; note it depends on implementation | §4.3 (8) | — |
| R-35d | Q9: best algorithm for each input order, justified in 2–3 sentences | §4.3 (9) | — |
| R-35e | Q10: bubble sort's worst-case arrangement among the four, with explanation | §4.3 (10) | Reversed |
| R-35f | Q11: does early termination help much on nearly sorted input? Why can a few misplaced elements force many passes? | §4.3 (11) | — |
| **4.4 Repeated values** | | | |
| R-36 | For each of the three columns, a sample of the 4.3 size with the same random seed | §4.4 | n = 2000, seed 42 |
| R-37 | Record per sample: distinct values; count of the most frequent value; number of values that occur more than once | §4.4 | `[1,1,2,3,3,3]` → 3 distinct, mode ×3 |
| R-38 | Run all three algorithms on each sample | §4.4 | 9 cases |
| R-39 | Q12: compare comparisons, writes and median runtimes across the columns; separate effects of duplication from those of input order or implementation | §4.4 (12) | — |
| **4.5 Decision guide** | | | |
| R-40 | Table with best algorithm, evidence from results, and why — for: large random input; very small list (n < 20); already sorted; nearly sorted; reverse sorted; many repeated values. Not based on Big-O alone | §4.5 | "Already sorted → bubble: n−1 comparisons" |
| **4.6 Reflection** | | | |
| R-41a | Q13: why bubble and selection sort (both O(n²)) behave differently on sorted input | §4.6 (13) | — |
| R-41b | Q14: **one** realistic reason to still choose selection or bubble sort | §4.6 (14) | Few writes |
| R-41c | Q15: **at least two** reasons the doubling slowdown is not exactly 4× or 2× | §4.6 (15) | — |
| R-41d | Q16: how merge sort's extra memory affects the choice | §4.6 (16) | — |
| R-41e | Q17: why the same input and consistent measurement matter | §4.6 (17) | — |
| **Deliverables** | | | |
| R-42 | One PDF report per group on Canvas, Mon Nov 16, 2026, 11:59 p.m. EST; late work not accepted | §5 | — |
| R-43 | Report includes the GitHub repository link and the completed peer-assessment form | §5 | — |
| R-44 | Repo contains source code, result files (tables and plots), and a README with instructions for obtaining `housing.csv`, running the code, and interpreting outputs | §5 | `README.md`, `results/` |
| R-45 | Report ≤ 10 pages (excl. references, peer form, optional appendix); single column; Arial 11; detail may go in the appendix but key results and all answers stay in the main report | §5 | — |
| R-46 | Report contains: key questions + brief algorithm explanation; implementation details (language, tools, input preparation, counting conventions); results (runtime and counts vs size, each input order, each repeated-value column, bubble extrapolation); decision guide; answers to every numbered question; limitations; conclusions | §5 | — |
| R-47 | *Optional:* design-flow diagram or concise description of key subroutines, if useful | §5 | §1.3 of this document |
| R-48 | Peer assessment at the **end of the report**: every member, contribution description, percentages summing to 100 %, signed by all members | §5, p. 6 | 50 % / 50 % |
| R-49 | Presentation in class on Nov 16, 2026: 20-minute slot (~15 min + ~5 min Q&A); covers research questions, algorithms, experimental design, key findings, limitations; all members participate | §5 | — |
| **Evaluation** | | | |
| R-50 | Correct, ordered output that preserves the input values | §7 | Same multiset |
| R-51 | Reproducible: same input → same output and counts; seeds and data preparation documented | §7 | `metadata.json` |
| R-52 | Suitable sizes, repeated timing trials, clear tables and plots, consistent measurement methods | §7 | — |
| R-53 | Findings explained by algorithm behaviour as well as asymptotic complexity | §2, §7 | — |
| R-54 | Report and presentation quality: clear organisation, complete decision guide, sound conclusions, participation by all members | §7 | — |

#### Clarified requirements

Points the PDF left unclear, now settled. **Instructor** = confirmed by the instructor; **Group** = our choice, stated in the report (R-22). They keep their U-IDs, which the code, tests and task plan refer to. **Bold** module = the module that implements the requirement; if one changes, update it first, then review the others listed and their tests.

| ID | Point the PDF left unclear | § | Settled requirement | Affected modules | Example |
|---|---|---|---|---|---|
| U-01 | Missing, unparsable or non-finite values in the selected columns | §3 | **Instructor:** our choice (none expected). A value is missing if blank, unparsable or non-finite; rows with any missing selected value are dropped before sampling and the count is reported | **`data/loader`**, `data/inspection`, `main.py` | Expected 0 dropped |
| U-02 | Whether `housing.csv` is committed | §3, §5 | **Instructor:** may be committed. Committed at the repository root; README also gives the source URL; `metadata.json` records its SHA-256 | **`.gitignore`**, `README.md`, `main.py` | — |
| U-03 | "Same random seed" in 4.4 | §4.4 | **Group:** one seeded draw of row indices; the same indices **in the same order** (the 4.3 `shuffle_indices` order) are used for all three columns, so 4.4's `median_income` input equals 4.3's "random" input. The columns still differ in value distribution and inversion count, not only in duplication; Q12 must separate those effects | **`data/sampling`**, `experiments/repeated_values`, `experiments/input_order` | Row 17 → its income, age and value, at the same position |
| U-04 | Sampling with or without replacement | §4.2, §4.4 | **Group** (instructor: "a seed to take specific indices"): row indices drawn without replacement | **`data/sampling`**, `experiments/*` | `random.Random(42).sample(...)` |
| U-05 | Seed management | §4.2, §4.3, §7 | **Instructor:** several seeds are fine but must be reported. One `random.Random(seed)` per purpose: sample 42, shuffle 43, nearly sorted 44; reported in README, report and `metadata.json` | **`config.py`**, `data/sampling`, `data/orders`, `experiments/*` | — |
| U-06 | Exact sample sizes ("for example" in the PDF) | §4.2 (1), §4.3 | **Instructor:** scaling 5, 10, 20, 250, 500, 1000, 2000, 4000; 4.3/4.4 use n = 2000 | **`config.py`**, `experiments/*`, `analysis/*` | — |
| U-07 | Bubble sort pass structure | §4.1 | **Instructor:** early termination as in the lecture. Lecture code (Week 8, slide 20): every pass compares each neighbouring pair over the **whole** list; stop after a full pass with no swaps (no shrinking range). Selection and merge sort follow the PDF where the lecture differs (one swap per position; `<=` on ties) | **`sorts/bubble_sort`** | Reversed n = 5 → 5 passes × 4 = 20 comparisons, 10 swaps |
| U-08 | Which own sort produces "already sorted" | §4.3 | **Instructor:** our choice. Our plain merge sort, outside timing | **`data/orders`** | — |
| U-09 | Nearly sorted: may a position be picked in several swaps? | §4.3 | **Group:** two distinct positions per swap; reuse across swaps allowed | **`data/orders`** | — |
| U-10 | The defensive copy at the start of each sort | §4, §4.1 | **Instructor:** follow the stated write definition. **Group** reading: the copy is made by slicing (`values[:]`), so it falls under "copies made only by splitting or slicing" and is not counted; it stays inside the sort (the input is never modified) and therefore inside the timing; stated in the report | **`sorts/*`**, `timing/benchmark` | `a = values[:]` |
| U-11 | Counter overhead in timings | §4.1 | **Instructor:** counters must not be timed. Two files per algorithm with the same loops: the **plain** version is timed; the **counted** version runs once per batch outside the clock and supplies the counts. A comparison-trace test keeps both versions identical (D-10) | **`sorts/*`**, `timing/benchmark`, `experiments/common` | `benchmark(bubble_sort, counted_bubble_sort, values)` |
| U-13 | Number of repetitions ("for example, 1,000") | §4.2 (2) | **Instructor:** 5 timed batches, median reported. Very small inputs (n ≤ 20) are sorted 1,000 times per batch (the PDF requires a loop there); others once | **`config.py`**, `timing/benchmark` | §1.4 |
| U-14 | "Very small": §4.2 lists n = 20, the §4.5 row says n < 20 | §4.2, §4.5 | **Instructor:** 5, 10 and 20 are very small. The decision-guide row (PDF label "n < 20") uses all three; the report notes that 20 is included as confirmed by the instructor | **`config.py`**, report | — |
| U-15 | "Verify every output" combined with repeated timing | §4.1 | **Instructor:** verify against `sorted()`. Every timed output and every counted output is verified, outside the clock: the counted output before the timed run, the timed outputs after the clock stops (mechanics: D-08) | **`timing/benchmark`** | 5 × 1,000 outputs at n = 5 |
| U-16 | How to compute the median (`statistics.median` uses `sorted()`) | §2, §4.2 (2) | **Instructor:** `sorted()` is for verification only. The median is computed with our plain merge sort | **`timing/benchmark`** | `median_of([3,1,2]) == 2` |
| U-18 | Swaps are reported "if counted separately"; merge sort performs none | §4.1, §4.3 | **Instructor:** follow the stated definition. Swaps reported for bubble and selection; merge sort's value is "n/a" (`None`), not 0 | **`sorts/common`**, `sorts/merge_sort`, `experiments/common` | — |
| U-19 | Extrapolation method | §4.2 (4) | **Instructor:** fit a curve by regression to the measured times at n = 250, 500, 1000, 2000, 4000 and extrapolate to 20,640. Least-squares fit of T(n) = a₀ + a₁·n + a₂·n² to bubble sort's random-input medians, solved with Cramer's rule; estimate = T(20,640). The report shows the curve, the estimate, measured vs fitted times, and why it is approximate (5 points, ×5.16 beyond the largest size) | **`analysis/extrapolation`**, `config.py`, `main.py` | times 0.001 + 2·10⁻⁶n + 10⁻⁷n² → estimate 42.64324 s |

### 3.2 Open requirements (waiting for the instructor)

> ⚠️ **Open.** Points the PDF leaves unclear and the instructor has not answered yet. Each row records the **draft** used for now. Neither blocks the code: `duplicate_stats` already reports both readings of U-17, and U-22 only affects how the report reads `cases.csv`. When an answer arrives, move the row to §3.1 (Clarified requirements), then update the **bold** module and the others listed.
>
> Pure implementation mechanics with no basis in the PDF are in §3.3 (D-xx), and known limitations are in §3.4 (L-xx). IDs U-12, U-20 and U-21 were moved there (to D-07, L-01 and L-02) and are not reused.

| ID | ⚠️ Unclear point | § | Draft (for now) | Affected modules | Example |
|---|---|---|---|---|---|
| U-17 | "Number of values that occur more than once" | §4.4 | **Open** (asked to the instructor). For now report both: distinct values that repeat, and observations belonging to them | **`data/inspection`**, `experiments/repeated_values`, `experiments/common` | `[1,1,2,3,3,3]` → 2 and 5 |
| U-22 | How to choose the "best-performing algorithm" when three metrics are measured | §4.3 (9), §4.5 | **Open** (asked to the instructor). Draft rule: lowest median runtime decides; comparisons and writes justify it; if the fastest algorithm's max run ≥ the runner-up's min run, report "no clear winner". Report only; no code depends on it | report (`results/cases.csv` supplies median/min/max) | Sorted input: bubble wins on runtime and comparisons |

### 3.3 Design decisions (not from the PDF)

Implementation mechanics the PDF doesn't address, listed so per-file requirements can cite them.

| ID | Decision |
|---|---|
| D-01 | Counted sorts count with local integers and build `SortStats` once, on return; plain sorts have no counters |
| D-02 | Counted merge sort's recursive helper returns its counts; the parent adds them up (no shared counter object) |
| D-03 | `main.py all` is the only official run. It first deletes any old `metadata.json`, overwrites only the files it generates, and writes `metadata.json` last, only on success. Single-experiment commands are for development and write to `--out` (default `results/dev/`, git-ignored) |
| D-04 | All tunable values live in `Settings`, passed into functions, so tests can run with small sizes and temporary paths |
| D-05 | `metadata.json` records seeds, sizes, timing tiers, Python version and the dataset's SHA-256 |
| D-06 | One feature per folder (`implementation/` + `testing/`); shared definitions in `common/`; a README per main folder |
| D-07 | Garbage collection is disabled during timed batches and restored to its **previous** state afterwards (`was = gc.isenabled()` … `if was: gc.enable()`). The PDF doesn't mention GC; this reduces timing noise |
| D-08 | To verify every output (U-15), outputs are stored in a list allocated before the clock starts; storing them happens inside the timed region and is reported as harness overhead |
| D-10 | Plain and counted versions are kept identical by a comparison-trace test: both run on `logged_values` inputs (sorted, reversed, duplicates, random) and must log the same comparison sequence, whose length equals the counted comparisons |
| D-09 | Plots are **required submission outputs** (§5), even though matplotlib is optional (§2). The official plots are made with matplotlib. If it's missing, `all` still completes but prints "INCOMPLETE: plots missing", and the README explains how to build the same charts from the CSVs in Excel/Sheets and commit them to `results/` |

### 3.4 Known limitations

To be stated in the report's limitations section (R-46).

| ID | Limitation | Affects |
|---|---|---|
| L-01 | Repeated timings measure noise on **one** sample per case, not robustness across different samples | Q3–Q5, Q12, decision guide |
| L-02 | Fast single-sort cases in the normal tier (e.g. bubble sort on sorted input, n = 2000) are the noisiest timings | Q9, decision guide |
| L-03 | Timings exclude the counters but include harness overhead (the slicing copy of the input, storing each output for verification, function calls), so they are not "pure" algorithm times | All runtime results |

---

## 4. Requirements per file

`Satisfies` lists the IDs from §3. Examples use small inputs whose results can be checked by hand.

### 4.1 `config.py`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-CFG-1 | `Settings` holds every seed, size, column name, path and timing setting | R-09, R-23, R-51, U-05, U-06, D-04 | `DEFAULT_SETTINGS.sample_seed == 42` |

### 4.2 `data/loader`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-LOAD-1 | `load_csv` reads the file with `csv.DictReader`, standard library only | R-02, R-06, R-07 | 20,640 rows returned |
| F-LOAD-2 | `parse_value` returns a float, or `None` for blank, unparsable or non-finite text | R-07, U-01 | `"8.3"` → 8.3; `""`, `"abc"`, `"nan"` → `None` |
| F-LOAD-3 | `complete_cases` keeps rows whose selected columns all parse | U-01 | Row with `""` income excluded |
| F-LOAD-4 | `column_values` returns floats in index order | R-07, R-10 | `["8.3252"]` → `[8.3252]` |
| F-LOAD-5 | Loading always happens outside any timed region | R-20 | — |

### 4.3 `data/inspection`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-INS-1 | `inspect_data` reports rows, missing, distinct and excluded rows per selected column, from raw rows, using the same `parse_value` rule as the loader | R-08, U-01 | `{'column': 'median_income', 'rows': 20640, 'missing': 0, …}` |
| F-INS-2 | `duplicate_stats` returns distinct, modal value and count, repeated distinct values, repeated observations | R-37, U-17 | `[1,1,2,3,3,3]` → distinct 3, mode 3 (×3), 2, 5 |
| F-INS-3 | Counting uses a `dict`, no built-in sorting | R-03 | — |

### 4.4 `data/sampling`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-SMP-1 | `sample_indices` draws n indices uniformly without replacement using `random.Random(seed)` | R-23, R-36, U-04, U-05 | Same seed → same indices |
| F-SMP-2 | Never modifies the usable_indices list | R-51 | — |
| F-SMP-3 | `shuffle_indices` returns a new, seeded permutation; 4.3 and 4.4 call it with the same indices and seed | R-33, R-36, U-03, U-05 | Same seed → same order |

### 4.5 `data/orders`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-ORD-1 | `make_orders` keeps the supplied random sequence as `'random'` unchanged; it never shuffles again | R-33, U-03 | `make_orders([3,1,2], 44)['random'] == [3,1,2]` |
| F-ORD-2 | `ascending` uses our `merge_sort`, never `sorted()` | R-03, R-33, U-08 | `[3,1,2]` → `[1,2,3]` |
| F-ORD-3 | `descending` reverses the ascending sequence | R-33 | `[1,2,3]` → `[3,2,1]` |
| F-ORD-4 | `nearly_sorted` applies exactly floor(0.01·n) swaps; each picks two distinct positions uniformly at random, seeded | R-33, U-05, U-09 | n = 2000 → 20 swaps |
| F-ORD-5 | All four versions contain exactly the same values | R-12, R-33 | Same multiset |

### 4.6 `sorts/common/sort_stats.py`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-STA-1 | `SortStats` holds comparisons, writes, swaps (`None` for merge sort) | R-15, R-24, R-34, U-18 | `SortStats(4, 4, 2)` |
| F-SRT-1 | `common/testing/logged_value.py`: `LoggedValue` records every comparison; each sort's tests compare the plain and counted traces | U-11, D-10 | `bubble_sort` and `counted_bubble_sort` on `[3,1,2]` log the same 4 comparisons |

### 4.7 `sorts/bubble_sort`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-BUB-1 | Both versions copy the input by slicing and return a new ascending list; the input is unchanged; the copy is not counted | R-01, R-13, R-50, U-10 | `[3,1,2]` → `[1,2,3]` |
| F-BUB-2 | Counted version counts each `a[j-1] > a[j]` as one comparison | R-14 | `[3,1,2]` → 4 comparisons |
| F-BUB-3 | Each swap = 2 writes and 1 swap | R-15 | `[3,1,2]` → 2 swaps, 4 writes |
| F-BUB-4 | Stops after a full pass with no swaps | R-17, R-35a | `[1,2,3,4,5]` → 4 comparisons, 0 swaps |
| F-BUB-5 | Every pass covers the whole list, as in the lecture code | U-07 | Reversed n = 5 → 20 comparisons, 10 swaps |
| F-BUB-6 | Counted version: local integer counters; `SortStats` built once on return | D-01 | — |
| F-BUB-7 | Two files with the same loops: `bubble_sort` (plain, timed) and `counted_bubble_sort` (counts); same comparison trace | U-11, D-10 | — |

### 4.8 `sorts/selection_sort`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-SEL-1 | Both versions copy the input by slicing and return a new ascending list; the input is unchanged; the copy is not counted | R-01, R-13, R-50, U-10 | `[3,1,2]` → `[1,2,3]` |
| F-SEL-2 | Counted version counts every comparison made while searching for the minimum | R-14, R-35b | Any n = 5 → 10 comparisons |
| F-SEL-3 | Swaps only when the minimum is not in place (at most one swap per position, PDF rule, not the lecture's); swap = 2 writes | R-15, R-18 | `[1,2,3]` → 0 writes; `[3,1,2]` → 2 swaps, 4 writes |
| F-SEL-4 | Counted version: local integer counters; `SortStats` built once on return | D-01 | — |
| F-SEL-5 | Two files with the same loops: `selection_sort` (plain, timed) and `counted_selection_sort` (counts); same comparison trace | U-11, D-10 | — |

### 4.9 `sorts/merge_sort`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-MRG-1 | Both versions return a new ascending list; the input is unchanged (splitting by slicing never touches it) | R-01, R-13, R-50, U-10 | `[2,1]` → `[1,2]` |
| F-MRG-1b | Counted version counts each executed `left[i] <= right[j]` as one comparison; moving a leftover tail costs no comparisons | R-14 | `[2,1]` → 1 comparison |
| F-MRG-2 | Each value placed in the merged output = 1 write, including leftover tails | R-16 | `[1,2,3,4]` → 8 writes |
| F-MRG-3 | Slicing/splitting copies are not counted | R-16 | — |
| F-MRG-4 | Ties take the left element (`<=`, PDF rule; the lecture uses `<`) | R-19 | Equal keys keep left-before-right |
| F-MRG-5 | Counted version: counts returned per recursive call and summed by the parent; `SortStats` built once | D-01, D-02 | `[1,2,3,4]` → 4 comparisons |
| F-MRG-6 | `swaps` is `None` | U-18 | — |
| F-MRG-7 | Two files with the same structure: `merge_sort` (plain, timed) and `counted_merge_sort` (counts); same comparison trace | U-11, D-10 | — |

### 4.10 `timing/benchmark`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-BEN-1 | Uses `time.perf_counter()`; the timed region holds only the plain sort's calls and output storage | R-20, U-11, D-08 | — |
| F-BEN-2 | Runs `timed_batches` (5) batches of `repetitions_for(input_size)` plain sorts on the same input | R-25, R-27, U-13 | n = 5 → 5 × 1,000 sorts |
| F-BEN-3 | Records seconds per sort for each batch as a tuple, plus their median (via `median_of`), min and max, computed once | R-24, R-25 | batch 0.0021 s ÷ 1,000 = 2.1 µs |
| F-BEN-4 | Median computed with our plain merge sort | U-16 | `median_of([3,1,2]) == 2` |
| F-BEN-5 | Verifies every timed and counted output against `sorted()`, outside the clock: the counted output before the timed run, the timed outputs after the clock stops | R-03, R-21, U-15 | Wrong output → `VerificationError` |
| F-BEN-6 | Checks the counts are identical across the batches and the input is unchanged | R-13, R-26, R-51 | — |
| F-BEN-7 | Disables garbage collection while timing; restores the previous state | D-07 | — |
| F-BEN-8 | Timing includes the slicing copy and output storage, never the counters | U-10, U-11, L-03 | — |
| F-BEN-9 | `repetitions_for(input_size, settings)` returns 1,000 for input_size ≤ 20 and 1 otherwise | R-27, U-13, U-14 | `repetitions_for(20) == 1000`, `repetitions_for(250) == 1` |
| F-BEN-10 | Runs the counted sort once per batch, outside the clock; its `SortStats` is returned | R-24, R-26, U-11 | 5 batches → 5 counted calls |

### 4.11 `experiments/common/records.py`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-REC-1 | `CaseResult` holds labels, `SortStats` and `TimingResult` for one case; `case_row` flattens it to a `CASE_FIELDS` row | R-24, R-34 | — |
| F-REC-2 | `write_cases`, `write_runs` and `write_rows` write the schemas in §1.6 with explicit headers (`CASE_FIELDS`, etc.); an empty list writes a header-only file | R-44, R-52 | 45 rows in `cases.csv` |
| F-REC-5 | `read_cases` converts types (ints, floats, "n/a" → `None`) and rejects malformed numbers; a write → read round trip returns equal values (tested in `experiments/common/testing/test_records.py`) | R-51 | `"n/a"` → `None`; `"abc"` in `n` → `ValueError` |
| F-REC-3 | `ALGORITHMS` maps each name to its (plain sort, counted sort) pair | R-12, U-11 | `ALGORITHMS["merge"] == (merge_sort, counted_merge_sort)` |
| F-REC-4 | Merge sort's swaps are written as empty / "n/a" | U-18 | — |

### 4.12 `experiments/scaling`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-SCL-1 | One seeded sample of `scaling_column` (`median_income`) per size in `scaling_sizes` | R-09, R-23, U-04, U-06 | 8 samples |
| F-SCL-2 | The same sample goes to all three algorithms | R-12, R-23 | — |
| F-SCL-3 | Returns one `CaseResult` per algorithm × size (24 with the default sizes) with runtime, comparisons and writes | R-24 | — |
| F-SCL-4 | Results provide the evidence for Q3–Q5 | R-28, R-29, R-31 | — |

### 4.13 `experiments/input_order`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-IOR-1 | One `order_sample_size` sample of `order_column` (`median_income`), ordered by `shuffle_indices`, then turned into four orders by `make_orders` | R-09, R-32, R-33, U-03 | n = 2000 |
| F-IOR-2 | Every algorithm runs on every order: 12 cases with comparisons, writes, swaps, median runtime | R-12, R-34 | — |
| F-IOR-3 | Results provide the evidence for Q6–Q11 | R-35a – R-35f | Q10: reversed → bubble swaps = number of strict inversions (1,999,000 if all 2,000 values are distinct) |

### 4.14 `experiments/repeated_values`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-REP-1 | Uses the 4.3 row indices, in the same shuffled order, for all three columns | R-36, U-03 | `median_income` input identical to 4.3's "random" input |
| F-REP-2 | Records `duplicate_stats` per column | R-37, U-17 | `dupes_stats.csv` |
| F-REP-3 | Runs all three algorithms per column: 9 cases | R-38 | — |
| F-REP-4 | Results provide the evidence for Q12 | R-39 | — |

### 4.15 `analysis/growth`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-FLT-1 | `analysis/common/filters.scaling_cases` keeps only scaling rows (`median_income`, random order), never 4.3/4.4 rows of the same n; used by growth and extrapolation (tested in `analysis/common/testing/test_filters.py`) | R-09, R-28, R-29 | n = 2000 appears in 3 experiments → only the scaling row is kept |
| F-GRO-1 | Observed factor T(2n)/T(n) for doubling pairs only | R-28 | 20→250 skipped |
| F-GRO-2 | Theoretical factor beside each observed one | R-28 | 1000→2000: quadratic 4.00, merge ≈ 2.20 |

### 4.16 `analysis/extrapolation`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-EXT-1 | `bubble_times` takes bubble sort's scaling median times (`median_income`, random) at the base sizes 250, 500, 1000, 2000, 4000 only | R-29, U-19 | n = 2000 rows of 4.3/4.4 ignored |
| F-EXT-2 | `fit_quadratic` fits T(n) = a₀ + a₁·n + a₂·n² by least squares (normal equations from Σnᵖ and Σ T·nᵖ) solved with Cramer's rule (`determinant_3x3`), standard library only | R-02, R-29, U-19 | times 0.00775, 0.027, 0.103, 0.405, 1.609 → (0.001, 2·10⁻⁶, 10⁻⁷) |
| F-EXT-3 | `extrapolate_bubble` returns one `EXTRAPOLATION_FIELDS` row with estimate = `predict_time` at 20,640, and measured-vs-fitted rows (`FITTED_FIELDS`); `main analyze` writes the row to `extrapolation.csv` and prints both | R-29, U-19 | estimate 42.64324 s for the times above |
| F-EXT-4 | The report shows the fitted curve, the estimate, the measured-vs-fitted table, and why the estimate is approximate (5 points, ×5.16 beyond the largest size, timing noise) | R-29, U-19 | — |
| F-EXT-5 | Rejects a missing or duplicated base size, a non-positive or non-finite time, fewer than 3 distinct sizes, and a singular system | R-29 | T = 0 → `ValueError` |

### 4.17 `plots/charts`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-PLT-1 | Runtime, comparisons and writes vs n for each algorithm | R-05, R-44, R-52 | `scaling_runtime.png` |
| F-PLT-2 | Charts for input order and repeated values | R-44, R-52 | `order_comparisons.png` |
| F-PLT-3 | The only module importing matplotlib; its tests skip if it isn't installed | R-02, R-05 | — |
| F-PLT-4 | If matplotlib is missing, `all` prints "INCOMPLETE: plots missing" (the run still succeeds) | R-44, D-09 | — |

Chart design extension agreed with Bahareh: three summary PNGs, each with runtime, comparisons
and writes panels; a tiny-input runtime PNG; a growth-factor PNG; and a bubble extrapolation PNG.
These six files are team design choices, not six separately prescribed PDF requirements.
`plot_scaling` writes the first and the tiny-input detail. `plot_growth` receives typed `growth.csv`
rows; `plot_bubble_extrapolation` receives cases and the two outputs of `extrapolate_bubble`.
No existing public signature changes. New names are re-exported through `sorting_analysis.plots`.
Times remain seconds per sort except the labelled tiny-input detail, which displays microseconds.
Runtime whiskers are observed minimum-to-maximum ranges, never confidence intervals.
Missing cases are gaps and reported in captions. Summary runtimes use a log axis; writes use a symmetric log axis (linear from 0 to 1), so true zero writes stay exactly zero beside counts in the millions.
Charts validate duplicate cases and consistent experiment context instead of mixing different runs.
The two new plotting functions need explicit calls during the later `main.py` integration;
implementing them alone does not replace the existing mock pipeline or produce official results.

### 4.18 `main.py`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-MAIN-1 | Command-line interface with `check`, `scaling`, `order`, `dupes`, `analyze`, `plot`, `all`, plus `--csv` and `--out` | R-04, D-04 | `python main.py check` |
| F-MAIN-2 | `check` prints the dataset inspection; `all` writes `inspection.csv` | R-08 | — |
| F-MAIN-3 | `all` deletes any old `metadata.json` and generated PNGs first, overwrites only the files it generates, and writes `metadata.json` last, only on success; development commands write to `--out` (default `results/dev/`) | R-44, R-51, D-03 | — |
| F-MAIN-6 | `metadata.json` records `plots_status` and the generated file list; exit code 0 means all computations succeeded | R-44, D-03, D-09 | `"plots_status": "missing"` |
| F-MAIN-4 | `write_metadata` records seeds, sizes, timing tiers, Python version, dataset SHA-256 | R-51, U-02, D-05 | — |
| F-MAIN-5 | Writes `dupes_stats.csv`, `growth.csv` and `extrapolation.csv` via `write_rows` | R-37, R-28, R-29, R-44 | — |

### 4.19 `tests/test_end_to_end.py`

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-E2E-1 | Runs `main(['all'], settings=…)` on a tiny temporary CSV with small `Settings`; checks every CSV and `metadata.json` exist, and PNGs only if `matplotlib_available()` | R-44, R-51, D-04 | 30-row CSV, sizes (5, 10, 15, 20, 25), `order_sample_size` 10 |
| F-E2E-2 | Never writes into the committed `results/` | D-03 | Temporary directory |

### 4.20 READMEs

| ID | Requirement | Satisfies | Example |
|---|---|---|---|
| F-DOC-1 | Root README: overview, source of `housing.csv` (committed), running, interpreting outputs, seeds, counting conventions, and the Excel/Sheets fallback for plots | R-44, R-51, U-02, D-09 | — |
| F-DOC-2 | One README per main folder describing its features and interfaces | D-06 | `sorts/README.md` |
| F-DOC-3 | `results/README.md` explains each output file | R-44 | — |

### 4.21 Report and presentation (not code)

| ID | Requirement | Satisfies |
|---|---|---|
| F-RPT-1 | Answers Q1–Q17 with evidence from `results/`; Q9 in 2–3 sentences per order, winner chosen per U-22 (open); Q14 gives ≥ 1 reason, Q15 ≥ 2 reasons | R-23 – R-31, R-35a – R-35f, R-39, R-41a – R-41e, R-53, U-22 |
| F-RPT-2 | Decision guide with all six situations | R-40 |
| F-RPT-3 | Introduction with the key questions and a brief explanation of each algorithm; implementation section: language, tools, input preparation, counting conventions (incl. slicing not counted), the plain/counted split (counters not timed), the instructor's decisions and our own choices (U-xx) and design decisions (D-xx); results for every experiment incl. the bubble extrapolation | R-16, R-22, R-46 |
| F-RPT-4 | Limitations (L-01 – L-03) and sound conclusions; clear organisation | R-46, R-54, L-01 – L-03 |
| F-RPT-5 | Design-flow description (adapted from §1.3 of this document) | R-47 |
| F-RPT-6 | ≤ 10 pages, single column, Arial 11, GitHub link, signed peer form at the end of the report, submitted on Canvas by the deadline | R-42, R-43, R-45, R-48 |
| F-PRS-1 | In-class presentation on Nov 16: ~15 min + ~5 min Q&A covering research questions, algorithms, experimental design, key findings and limitations; all members speak | R-49 |

---

## 5. Coverage check

| Requirement IDs | Covered by |
|---|---|
| R-01 – R-03 | F-BUB-1, F-SEL-1, F-MRG-1, F-LOAD-1, F-ORD-2, F-INS-3, F-BEN-5 |
| R-04, R-05 | F-MAIN-1, F-PLT-1, F-PLT-3 |
| R-06 – R-09 | F-LOAD-1 – F-LOAD-4, F-INS-1, F-CFG-1, F-SCL-1, F-IOR-1 |
| R-10, R-11, R-30 | Optional: R-10's core part by F-LOAD-4; the optional parts are **not planned** |
| R-12 – R-21 | F-BUB-*, F-SEL-*, F-MRG-*, F-BEN-1 – F-BEN-6, F-ORD-5, F-SCL-2, F-IOR-2 |
| R-22 | F-RPT-3 |
| R-23 – R-29, R-31 | F-SCL-*, F-BEN-*, F-GRO-*, F-EXT-*, F-RPT-1 |
| R-32 – R-35f | F-ORD-*, F-IOR-*, F-BUB-4, F-SEL-2, F-RPT-1 |
| R-36 – R-39 | F-SMP-1, F-REP-*, F-INS-2, F-RPT-1 |
| R-40, R-41a – R-41e | F-RPT-1, F-RPT-2 |
| R-42 – R-49 | F-DOC-*, F-REC-2, F-MAIN-3, F-MAIN-5, F-RPT-3 – F-RPT-6, F-PRS-1 |
| R-50 – R-54 | F-BUB-1, F-SEL-1, F-MRG-1, F-BEN-6, F-MAIN-4, F-PLT-*, F-RPT-1, F-RPT-4, F-PRS-1 |
| U-01 – U-22 (excl. retired U-12, U-20, U-21) | Each listed in at least one F-row or in F-RPT-1/F-RPT-3 |
| D-01 – D-10, L-01 – L-03 | F-rows citing them; L-xx in F-RPT-4 |
