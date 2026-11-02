# Sorting Algorithm Analysis

Implements bubble sort, selection sort and merge sort from scratch and compares them on the California Housing dataset: runtime, comparisons and writes across increasing input sizes, different input orders, and columns with different amounts of duplication.

## Requirements

- Python 3.10 or newer, standard library only.
- `matplotlib` (optional) for the charts. Without it, the run completes and reports that the plots are missing; the charts can then be built from the CSV files in Excel or Google Sheets.

## Dataset

`housing.csv` (California Housing Prices, 20,640 rows) is included in the repository root.
Source: <https://raw.githubusercontent.com/ageron/handson-ml2/master/datasets/housing/housing.csv>

| Column | Used in |
|---|---|
| `median_income` | scaling, input-order and repeated-values experiments |
| `housing_median_age` | repeated-values experiment |
| `median_house_value` | repeated-values experiment |

Rows with a missing or invalid value in any of these columns are excluded and reported.

## Usage

Run from the repository root.

| Command | Description |
|---|---|
| `python main.py check` | Inspect the dataset: rows, missing values and distinct values per column |
| `python main.py scaling` | Scaling experiment only (development) |
| `python main.py order` | Input-order experiment only (development) |
| `python main.py dupes` | Repeated-values experiment only (development) |
| `python main.py analyze` | Growth factors and bubble sort extrapolation from `cases.csv` |
| `python main.py plot` | Charts from `cases.csv` (requires matplotlib) |
| `python main.py all` | **Official run**: inspection, all experiments, analysis, charts, metadata |
| `python -m unittest discover` | Run all tests |

Options: `--csv PATH` (dataset path), `--out DIR` (output folder; default `results/` for `all`, `results/dev/` otherwise).

Exit codes: `0` success (charts may be missing) · `1` computation failure · `2` input or usage error · `130` interrupted.

## Outputs

`python main.py all` writes the CSV tables, charts and `metadata.json` to `results/`. See [results/README.md](results/README.md) for every file.

## Method

- **Sizes:** 5, 10, 20, 250, 500, 1000, 2000, 4000 (scaling); 2000 (input order and repeated values).
- **Seeds:** sample 42, shuffle 43, nearly sorted 44. All settings are in `sorting_analysis/config.py`.
- **Timing:** `time.perf_counter()`, median of 5 timed batches. Inputs with n ≤ 20 are sorted 1,000 times per batch; larger inputs once. Loading and input preparation are not timed. Every output is verified against `sorted()`.
- **Comparisons:** comparisons between two data values.
- **Writes:** a swap is 2 writes; each value placed into a merged list is 1 write, including leftover tails; the initial copy of the input and the lists created by slicing are not counted.

## Project structure

| Folder | Contents |
|---|---|
| `sorting_analysis/data/` | Dataset loading, inspection, sampling, input orders |
| `sorting_analysis/sorts/` | The three sorting algorithms |
| `sorting_analysis/timing/` | Verified, repeated timing |
| `sorting_analysis/experiments/` | The three experiments and their result records |
| `sorting_analysis/analysis/` | Growth factors and extrapolation |
| `sorting_analysis/plots/` | Charts |
| `tests/` | End-to-end tests |
| `results/` | Official outputs |

Each feature folder holds its code in `implementation/` and its unit tests in `testing/`. The full design is in [ARCHITECTURE.md](ARCHITECTURE.md); team rules are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Development status

The pipeline in `main.py` is complete. Steps not yet implemented use the mock functions at the top of the file; the **Pipeline steps** block lists every step with the real import in its comment. Replace one line at a time with that import and delete the mock. While any mock is in use, outputs go to `results/dev/` and `metadata.json` is not written. Drafted tests are skipped until they are written.
