# Sorting Algorithm Analysis

DATA 5010 - Project 2

Bubble sort, selection sort and merge sort, implemented from scratch and compared on the California Housing dataset: runtime, comparisons and element writes across input sizes, input orders and columns with different amounts of duplication.

Repository: [sorting-algorithms-analysis](https://github.com/ZeyadHosny/sorting-algorithms-analysis)

## Environment setup

Use Python 3.11 or newer. The analysis uses the standard library only; `matplotlib` is optional and only draws the figures:

```bash
python -m pip install matplotlib
```

Tested with Python 3.11, 3.12 and 3.14; the official results were produced on Windows 11 with Python 3.14.6. No environment variables are needed. Open a terminal in the repository folder, the one containing `main.py`; all commands and paths below are relative to it.

## Dataset and preparation

`housing.csv` (California Housing Prices: 20,640 rows, 10 columns) is included in the repository folder. If it is missing, download it from <https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv> and save it there as `housing.csv`.

| Column | Used in |
|---|---|
| `median_income` | scaling, input order, repeated values |
| `housing_median_age` | repeated values |
| `median_house_value` | repeated values |

The file is read with the `csv` module, and the selected columns are converted to `float`. Rows with a missing, non-numeric or non-finite value in any selected column are excluded and reported; the included file has none. The other columns, including `total_bedrooms` and its blanks, are not analyzed, and the file is never modified.

## Run the code

```bash
python main.py
```

This is the official run, the same as `python main.py all`. It inspects the dataset, runs the three experiments, computes the growth factors and the bubble sort estimate, draws the figures and writes everything to `results/`. It first deletes the nine generated figures, `metadata.json` and any leftover `metadata.json.tmp`, then overwrites the CSV files; other files in `results/` are kept. It takes about 45 seconds on the tested machine; runtime varies.

The other commands are for development. `check` only prints; the others write to `results/dev/`, which Git ignores:

| Command | Action |
|---|---|
| `python main.py check` | Dataset inspection only |
| `python main.py scaling`, `order` or `dupes` | One experiment only |
| `python main.py analyze` | Growth factors and estimate from the `cases.csv` in the output folder |
| `python main.py plot` | Figures from the `cases.csv` in the output folder (needs matplotlib) |

Exit codes: `0` success (figures are missing without matplotlib), `1` computation or verification failure, `2` input or usage error, `130` interrupted.

## Parameter setup

### Command-line options

| Option | Default | Meaning |
|---|---|---|
| command | `all` | `all`, `check`, `scaling`, `order`, `dupes`, `analyze` or `plot` |
| `--csv PATH` | `housing.csv` | Dataset file |
| `--out DIR` | `results/` for `all`, `results/dev/` otherwise | Output folder |

### Experiment settings

The experiment parameters are constants in `sorting_analysis/config.py`; there are no command-line options for them. To change one, edit its constant there. The official results use the values below, and `results/metadata.json` records the values of every official run.

| Constant | Value | Meaning |
|---|---|---|
| `DEFAULT_SELECTED_COLUMNS` | `median_income`, `housing_median_age`, `median_house_value` | Columns inspected and compared in the repeated-values experiment |
| `DEFAULT_SCALING_COLUMN`, `DEFAULT_ORDER_COLUMN` | `median_income` | Column of the scaling and input-order experiments |
| `DEFAULT_SCALING_SIZES` | 5, 10, 20, 250, 500, 1000, 2000, 4000 | Input sizes of the scaling experiment |
| `DEFAULT_ORDER_SAMPLE_SIZE` | 2000 | Sample size of the input-order and repeated-values experiments |
| `DEFAULT_SAMPLE_SEED` | 42 | Seed of the sampled rows |
| `DEFAULT_SHUFFLE_SEED` | 43 | Seed of the random input order |
| `DEFAULT_NEARLY_SORTED_SEED` | 44 | Seed of the swaps in the nearly sorted input |
| `DEFAULT_TIMED_BATCHES` | 5 | Timed batches per case; their median is reported |
| `DEFAULT_SMALL_INPUT_LIMIT` | 20 | Largest input size timed as a very small input |
| `DEFAULT_SMALL_INPUT_REPETITIONS` | 1000 | Sorts per batch for very small inputs |
| `DEFAULT_NORMAL_INPUT_REPETITIONS` | 1 | Sorts per batch for all other inputs |
| `DEFAULT_EXTRAPOLATION_BASE_SIZES` | 250, 500, 1000, 2000, 4000 | Measured sizes the quadratic is fitted to |
| `DEFAULT_EXTRAPOLATION_TARGET_SIZE` | 20640 | Input size of the bubble sort estimate |
| `DEFAULT_CSV_PATH`, `DEFAULT_RESULTS_FOLDER` | `housing.csv`, `results` | Default dataset file and official output folder |

### Using a different dataset

```bash
python main.py --csv data/other.csv --out results/other
```

The file must contain the selected columns and enough usable rows for the largest scaling size and the order sample (4,000 by default); otherwise the run stops with exit code `2`. The extrapolation base sizes must be at least three distinct scaling sizes. The estimate stays at n = 20,640 unless `DEFAULT_EXTRAPOLATION_TARGET_SIZE` is changed, and it must exceed the largest base size. Use `--out` to keep the official `results/` unchanged.

## Method

- Samples are row indices drawn without replacement (seed 42). All three algorithms sort the same input in every comparison, and no sorting function modifies its input.
- The random input order is a shuffle of the 2,000-value sample (seed 43). The repeated-values experiment sorts the same rows, in the same order, for all three columns.
- The other orders are sorted (by the project's merge sort), reversed, and nearly sorted: floor(0.01 × n) = 20 swaps of two distinct random positions (seed 44).
- Bubble sort makes full passes and stops after a pass with no swaps; selection sort swaps only when the minimum is not already in place; merge sort takes the left value on ties (`<=`).
- A comparison is between two data values. A swap is 2 writes, and each value placed into a merged list is 1 write; copies made by slicing are not counted.
- Each algorithm has a plain version, timed with `time.perf_counter()`, and a counted version with the same loops, which supplies the counts. Loading and input preparation are not timed, and every output is verified against `sorted()` outside the clock.
- The bubble sort estimate is a least-squares fit of T(n) = a₀ + a₁n + a₂n² to the measured median times, evaluated at n = 20,640.

## Read the outputs

| File | Contents |
|---|---|
| `inspection.csv` | Rows, missing values and distinct values per column |
| `cases.csv` | One row per algorithm and input (45 rows): comparisons, writes, swaps, sorts per batch, and the median, minimum and maximum time |
| `timing_runs.csv` | Every timed batch behind each median |
| `dupes_stats.csv` | Distinct values, the most frequent value and its count, and repeated values per column |
| `growth.csv` | Observed runtime growth when n doubles, beside the theoretical factor |
| `extrapolation.csv` | The coefficients a₀, a₁, a₂ and the bubble sort estimate |
| `scaling_summary.png`, `input_order_summary.png`, `repeated_values_summary.png` | Runtime, comparisons and writes per experiment |
| `scaling_table.png`, `input_order_table.png`, `repeated_values_table.png` | The results of each experiment as a table |
| `scaling_tiny_runtime.png` | Runtime of the very small inputs (n = 5, 10, 20) |
| `growth_factors.png`, `bubble_extrapolation.png` | Growth factors, and the fitted curve with the estimate |
| `metadata.json` | Parameters, Python version, platform, dataset SHA-256 and the generated files |

- Times are seconds per sort, measured on the plain sorts: each batch's elapsed time divided by its number of sorts. `median_s` is the median of the 5 batches, and `min_s` and `max_s` their range. Counts are exact and come from the counted sorts.
- `swaps` is `n/a` for merge sort, which places values without swapping.
- The theoretical growth factor is 4 for bubble and selection sort, and 2·log(2n)/log(n) for merge sort.
- In `dupes_stats.csv`, `repeated_distinct` counts the distinct values that occur more than once, and `repeated_observations` the sample values that belong to them.
- `metadata.json` is written last, only when the run succeeds; `plots_status` is `missing` when matplotlib is not installed.

## Reproduce and check results

Run `python main.py` and compare `results/` with the examples below. Counts must match exactly on any machine; times and the estimate vary with the machine and Python version.

| Required result | Where to find it |
|---|---|
| Dataset inspection | `inspection.csv` |
| Scaling: runtime, comparisons and writes versus n | `cases.csv` (`experiment` = `scaling`), `scaling_summary.png`, `scaling_table.png`, `scaling_tiny_runtime.png` |
| Growth factors and the bubble sort estimate | `growth.csv`, `extrapolation.csv`, `growth_factors.png`, `bubble_extrapolation.png` |
| Input order | `cases.csv` (`experiment` = `order`), `input_order_summary.png`, `input_order_table.png` |
| Repeated values | `dupes_stats.csv`, `cases.csv` (`experiment` = `dupes`), `repeated_values_summary.png`, `repeated_values_table.png` |

These files are the evidence for the decision guide and the answers in the report; the program does not write the guide itself.

### Example 1: Official run

```bash
python main.py
```

The official run printed:

```text
Rows: 20640 loaded, 0 excluded (missing values), 20640 usable
  median_income: rows 20640, missing 0, distinct 12928
  housing_median_age: rows 20640, missing 0, distinct 52
  median_house_value: rows 20640, missing 0, distinct 3842
Scaling experiment
Input-order experiment
Repeated-values experiment
45 cases done
  Bubble sort estimate for n = 20640: 33.3 s (T(n) = 0.00278 + -1.12e-05 n + 7.87e-08 n^2)
    n = 250: measured 0.004049 s, fitted 0.004892 s
    n = 500: measured 0.01773 s, fitted 0.01685 s
    n = 1000: measured 0.07058 s, fitted 0.07027 s
    n = 2000: measured 0.2948 s, fitted 0.2952 s
    n = 4000: measured 1.217 s, fitted 1.217 s
```

The 45 cases are 24 scaling (8 sizes × 3 algorithms), 12 input-order (4 orders × 3) and 9 repeated-values (3 columns × 3). The estimate line gives the fitted curve; the lines below it compare each measured median time with the curve. A successful run ends with `metadata.json` in `results/`.

### Example 2: Dataset inspection

```bash
python main.py check
```

```text
Rows: 20640 loaded, 0 excluded (missing values), 20640 usable
  median_income: rows 20640, missing 0, distinct 12928
  housing_median_age: rows 20640, missing 0, distinct 52
  median_house_value: rows 20640, missing 0, distinct 3842
```

The same values are in `results/inspection.csv`. `median_income` has the most distinct values and `housing_median_age` the fewest. These counts describe the full dataset; `dupes_stats.csv` describes the 2,000-row sample.

### Example 3: Input-order experiment

```bash
python main.py order
```

```text
Rows: 20640 loaded, 0 excluded (missing values), 20640 usable
Input-order experiment
12 cases done
```

This writes `cases.csv` and `timing_runs.csv` to `results/dev/`, with the same counts as the official run (n = 2,000):

| Input order | Bubble comparisons (passes) | Bubble writes | Selection comparisons | Merge comparisons |
|---|---:|---:|---:|---:|
| Random | 3,884,057 (1,943) | 1,973,226 | 1,999,000 | 19,381 |
| Sorted | 1,999 (1) | 0 | 1,999,000 | 10,864 |
| Reversed | 3,998,000 (2,000) | 3,997,314 | 1,999,000 | 11,202 |
| Nearly sorted | 3,054,472 (1,528) | 42,518 | 1,999,000 | 14,649 |

Every bubble sort pass compares all n − 1 = 1,999 neighbouring pairs, so passes = comparisons ÷ 1,999. Sorted input needs one pass and no writes; reversed input needs 2,000 passes. Selection sort always makes n(n − 1)/2 = 1,999,000 comparisons, whatever the order. Merge sort writes 21,952 values for every input of 2,000 values.

## Tests

```bash
python -m unittest discover
```

Expected result: `Ran 263 tests ... OK`. Without matplotlib, 25 chart tests are skipped.

## Project structure

`main.py` is the command-line entry point. `sorting_analysis/` contains `data/` (loading, inspection, sampling, input orders), `sorts/` (plain and counted versions of each algorithm), `timing/`, `experiments/`, `analysis/` (growth factors, estimate) and `plots/`, with the parameters in `config.py`. Each feature keeps its code in `implementation/` and its unit tests in `testing/`; `tests/` contains the end-to-end tests. `results/` holds the official outputs.
