"""
Description:
- Command-line entry point of the sorting analysis:
      python main.py {check,scaling,order,dupes,analyze,plot,all} [--csv PATH] [--out FOLDER]
- Steps that are not implemented yet use the mock functions below. To switch a step to the
  real code, replace its line under "Pipeline steps" with the import in its comment, then
  delete its mock.
- While any mock is in use, outputs go to results/dev/, writing into results/ (or any folder
  holding a metadata.json) is refused, and metadata.json is not written.
- Exit codes: 0 success (plots may be missing) | 1 computation failure (wrong sort output,
  invalid timing, step not implemented, unexpected error) | 2 input or usage error (dataset,
  columns, sample size, cases.csv, matplotlib for `plot`) | 130 interrupted.
- Spec: ARCHITECTURE.md F-MAIN-1 - F-MAIN-6.
"""

import argparse
import os
import sys
import traceback

from sorting_analysis.analysis import EXTRAPOLATION_FIELDS, GROWTH_FIELDS
from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.data import DUPES_FIELDS, INSPECTION_FIELDS
from sorting_analysis.experiments import ALGORITHMS, CaseResult
from sorting_analysis.sorts import SortStats
from sorting_analysis.timing import TimingResult, VerificationError

# Exit codes returned by main.
EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_INPUT = 2
EXIT_INTERRUPTED = 130
# Commands accepted on the command line; `all` is the official run.
COMMANDS = ("check", "scaling", "order", "dupes", "analyze", "plot", "all")
# The four input orders of the input-order experiment.
ORDERS = ("random", "sorted", "reversed", "nearly")
# CSV files written by an official run (recorded in metadata.json).
CSV_OUTPUTS = ("inspection.csv", "cases.csv", "timing_runs.csv", "dupes_stats.csv", "growth.csv",
               "extrapolation.csv")
# Number of rows the mock dataset pretends to have.
MOCK_ROW_COUNT = 20640
# Seconds the mock timings charge per comparison.
MOCK_SECONDS_PER_COMPARISON = 1e-8


class InputError(Exception):
    """
    Description:
    - Raised for a problem with the dataset, the arguments, the output folder or cases.csv.
    - main turns it into exit code 2.
    """


# -----------------------------------------------------------------------------
# Mocks: fake versions of the steps that are not implemented yet. They return
# fixed fake values and never write files.
# -----------------------------------------------------------------------------

def mock_load_csv(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    fake_row = {"median_income": "3.5", "housing_median_age": "20.0", "median_house_value": "150000.0"}
    return [fake_row] * MOCK_ROW_COUNT


def mock_complete_cases(rows, columns):
    return list(range(len(rows)))


def mock_inspect_data(rows, columns):
    return [{"column": column, "rows": len(rows), "missing": 0, "distinct": 0, "excluded_rows": 0}
            for column in columns]


def mock_case(experiment, algorithm, column, order, input_size):
    """Fake case: n(n-1)/2 comparisons (n log n for merge sort), a fixed time per comparison."""
    if algorithm == "merge":
        comparisons = input_size * input_size.bit_length()
        swaps = None
    else:
        comparisons = input_size * (input_size - 1) // 2
        swaps = comparisons // 2
    seconds = MOCK_SECONDS_PER_COMPARISON * comparisons
    sort_stats = SortStats(comparisons, comparisons, swaps)
    timing = TimingResult((seconds,) * 5, 1, seconds, seconds, seconds)
    return CaseResult(experiment, algorithm, column, order, input_size, sort_stats, timing)


def mock_run_scaling(rows, usable_indices, settings):
    return [mock_case("scaling", algorithm, settings.scaling_column, "random", size)
            for size in settings.scaling_sizes for algorithm in ALGORITHMS]


def mock_run_input_order(rows, usable_indices, settings):
    return [mock_case("order", algorithm, settings.scaling_column, order, settings.order_sample_size)
            for order in ORDERS for algorithm in ALGORITHMS]


def mock_run_repeated_values(rows, usable_indices, settings):
    size = settings.order_sample_size
    cases = [mock_case("dupes", algorithm, column, "random", size)
             for column in settings.selected_columns for algorithm in ALGORITHMS]
    duplicate_rows = [{"column": column, "sample_size": size, "distinct": 0, "modal_value": 0, "modal_count": 0,
                       "repeated_distinct": 0, "repeated_observations": 0}
                      for column in settings.selected_columns]
    return cases, duplicate_rows


def mock_case_row(case):
    sort_stats, timing = case.get_sort_stats(), case.get_timing()
    return {"experiment": case.get_experiment(), "algorithm": case.get_algorithm(), "column": case.get_column(),
            "order": case.get_order(), "input_size": case.get_input_size(),
            "comparisons": sort_stats.get_comparisons(), "writes": sort_stats.get_writes(),
            "swaps": sort_stats.get_swaps(), "sorts_per_batch": timing.get_sorts_per_batch(),
            "median_s": timing.get_median_seconds(), "min_s": timing.get_min_seconds(),
            "max_s": timing.get_max_seconds()}


def mock_write_rows(rows, path, fieldnames):
    print(f"  [mock] {path}: {len(rows)} rows (not written)")


def mock_write_cases(cases, path):
    print(f"  [mock] {path}: {len(cases)} rows (not written)")


def mock_write_runs(cases, path):
    print(f"  [mock] {path}: {len(cases)} cases (not written)")


def mock_read_cases(path):
    return []


def mock_growth_factors(cases):
    return []


def mock_extrapolate_bubble(cases, target_size, base_sizes):
    return []


def mock_extrapolate_bubble_growth(cases, target_size, base_sizes):
    return []


def mock_estimate_range(estimate_rows):
    estimates = [row["estimate_s"] for row in estimate_rows]
    return min(estimates), max(estimates)


def mock_matplotlib_available():
    return False


def mock_plot_scaling(cases, output_folder):
    return []


def mock_plot_input_order(cases, output_folder):
    return []


def mock_plot_repeated_values(cases, output_folder):
    return []


# -----------------------------------------------------------------------------
# Pipeline steps: one line per step. Replace the mock with the import in the
# comment when the step is implemented, then delete the mock.
# -----------------------------------------------------------------------------

load_csv = mock_load_csv                          # from sorting_analysis.data import load_csv
complete_cases = mock_complete_cases              # from sorting_analysis.data import complete_cases
inspect_data = mock_inspect_data                  # from sorting_analysis.data import inspect_data
run_scaling = mock_run_scaling                    # from sorting_analysis.experiments import run_scaling
run_input_order = mock_run_input_order            # from sorting_analysis.experiments import run_input_order
run_repeated_values = mock_run_repeated_values    # from sorting_analysis.experiments import run_repeated_values
case_row = mock_case_row                          # from sorting_analysis.experiments import case_row
write_rows = mock_write_rows                      # from sorting_analysis.experiments import write_rows
write_cases = mock_write_cases                    # from sorting_analysis.experiments import write_cases
write_runs = mock_write_runs                      # from sorting_analysis.experiments import write_runs
read_cases = mock_read_cases                      # from sorting_analysis.experiments import read_cases
growth_factors = mock_growth_factors              # from sorting_analysis.analysis import growth_factors
extrapolate_bubble = mock_extrapolate_bubble      # from sorting_analysis.analysis import extrapolate_bubble
extrapolate_bubble_growth = mock_extrapolate_bubble_growth  # from sorting_analysis.analysis import extrapolate_bubble_growth
estimate_range = mock_estimate_range              # from sorting_analysis.analysis import estimate_range
matplotlib_available = mock_matplotlib_available  # from sorting_analysis.plots import matplotlib_available
plot_scaling = mock_plot_scaling                  # from sorting_analysis.plots import plot_scaling
plot_input_order = mock_plot_input_order          # from sorting_analysis.plots import plot_input_order
plot_repeated_values = mock_plot_repeated_values  # from sorting_analysis.plots import plot_repeated_values

# Every pipeline step by name, used to report which steps are still mocks.
PIPELINE_STEPS = {
    "load_csv": load_csv, "complete_cases": complete_cases, "inspect_data": inspect_data,
    "run_scaling": run_scaling, "run_input_order": run_input_order, "run_repeated_values": run_repeated_values,
    "case_row": case_row, "write_rows": write_rows, "write_cases": write_cases, "write_runs": write_runs,
    "read_cases": read_cases, "growth_factors": growth_factors, "extrapolate_bubble": extrapolate_bubble,
    "extrapolate_bubble_growth": extrapolate_bubble_growth, "estimate_range": estimate_range,
    "matplotlib_available": matplotlib_available, "plot_scaling": plot_scaling,
    "plot_input_order": plot_input_order, "plot_repeated_values": plot_repeated_values,
}


# -----------------------------------------------------------------------------
# Pipeline
# -----------------------------------------------------------------------------

# Function to list the steps that are still mocks
def mocked_steps():
    """
    Description:
    - Return the names of the pipeline steps still bound to a mock function.

    Input arguments:
       None

    Return:
        list[str]: e.g. ['load_csv', 'run_scaling']; empty when everything is real.
    """
    return [name for name, step in PIPELINE_STEPS.items() if step.__name__.startswith("mock_")]


# Function to read the command line
def parse_arguments(argument_list):
    """
    Description:
    - Read the command and the --csv and --out options.

    Input arguments:
       argument_list (list[str]): Arguments without the program name; None reads sys.argv.

    Return:
        argparse.Namespace: command, csv, out.
    """
    parser = argparse.ArgumentParser(description="Sorting algorithm analysis on housing.csv.")
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument("--csv", help="dataset path (default: housing.csv)")
    parser.add_argument("--out", help="output folder (default: results/ for `all`, results/dev/ otherwise)")
    return parser.parse_args(argument_list)


# Function to choose the output folder of a command
def choose_output_folder(command, requested_folder, settings):
    """
    Description:
    - Use --out if given; otherwise results/ for an official `all` run and results/dev/ for
      development commands and for any run that still uses mocks.

    Input arguments:
       command (str): Command name, e.g. 'all'.
       requested_folder (str): Value of --out, or None.
       settings (Settings): Run settings.

    Return:
        str: e.g. 'results' or 'results/dev'.
    """
    if requested_folder:
        return requested_folder
    if command == "all" and not mocked_steps():
        return settings.results_folder
    return os.path.join(settings.results_folder, "dev")


# Function to compare two folder paths
def same_folder(first_path, second_path):
    """
    Description:
    - Whether two paths name the same folder (case-insensitive on Windows).

    Input arguments:
       first_path (str): A folder path.
       second_path (str): Another folder path.

    Return:
        bool: True if both point to the same folder.
    """
    return os.path.normcase(os.path.realpath(first_path)) == os.path.normcase(os.path.realpath(second_path))


# Function to protect the official results while mocks are in use
def check_output_folder(output_folder, settings):
    """
    Description:
    - While any step is mocked, refuse to write into the official results folder or into a
      folder that already holds a metadata.json.

    Input arguments:
       output_folder (str): Folder the command will write to.
       settings (Settings): Run settings.

    Return:
        None (raises InputError if the folder is protected)
    """
    if not mocked_steps():
        return
    is_official = same_folder(output_folder, settings.results_folder)
    if is_official or os.path.exists(os.path.join(output_folder, "metadata.json")):
        raise InputError(f"steps are still mocked - refusing to write into {output_folder}; use results/dev/")


# Function to load the dataset and find the usable rows
def load_dataset(csv_path, settings, need_usable_rows=True):
    """
    Description:
    - Load the CSV, check that the selected columns exist, and find the rows where every
      selected column holds a valid value. Prints how many rows were excluded.

    Input arguments:
       csv_path (str): Dataset path (--csv, or settings.csv_path).
       settings (Settings): Run settings (selected_columns).
       need_usable_rows (bool): Fail if no row is usable (False for `check`).

    Return:
        tuple: (raw rows, usable row indices) (raises InputError if the file or a column is
         missing, or no row is usable)
    """
    try:
        rows = load_csv(csv_path)
    except FileNotFoundError:
        raise InputError(f"dataset not found: {csv_path} (see README for the source)") from None
    columns = settings.selected_columns
    missing_columns = [column for column in columns if rows and column not in rows[0]]
    if missing_columns:
        raise InputError(f"dataset lacks column(s): {', '.join(missing_columns)}")
    usable_indices = complete_cases(rows, columns)
    excluded = len(rows) - len(usable_indices)
    print(f"Rows: {len(rows)} loaded, {excluded} excluded (missing values), {len(usable_indices)} usable")
    if need_usable_rows and not usable_indices:
        raise InputError("no row has a valid value in every selected column")
    return rows, usable_indices


# Function to check that a sample fits in the usable rows
def check_sample_size(sample_size, usable_indices):
    """
    Description:
    - Fail early if a sample of this size cannot be drawn from the usable rows.

    Input arguments:
       sample_size (int): Requested sample size, e.g. 4000.
       usable_indices (list[int]): Usable row indices.

    Return:
        None (raises InputError if the sample is too large)
    """
    if sample_size > len(usable_indices):
        raise InputError(f"sample size {sample_size} exceeds the {len(usable_indices)} usable rows")


# Function to inspect and print the selected columns
def run_inspection(rows, settings):
    """
    Description:
    - Inspect the selected columns and print rows, missing and distinct values per column.

    Input arguments:
       rows (list[dict]): Raw rows.
       settings (Settings): Run settings (selected_columns).

    Return:
        list[dict]: one row per column with the INSPECTION_FIELDS keys.
    """
    inspection_rows = inspect_data(rows, settings.selected_columns)
    for row in inspection_rows:
        print(f"  {row['column']}: rows {row['rows']}, missing {row['missing']}, distinct {row['distinct']}")
    return inspection_rows


# Function to run the requested experiments
def run_experiments(experiment_names, rows, usable_indices, settings, output_folder):
    """
    Description:
    - Run the named experiments and write cases.csv, timing_runs.csv and dupes_stats.csv.

    Input arguments:
       experiment_names (tuple[str]): Any of 'scaling', 'order', 'dupes'.
       rows (list[dict]): Raw rows.
       usable_indices (list[int]): Usable row indices.
       settings (Settings): Run settings.
       output_folder (str): Folder for the CSV files.

    Return:
        list[CaseResult]: every measured case (raises InputError if a sample is too large,
         VerificationError if a sort output is wrong)
    """
    if "scaling" in experiment_names:
        check_sample_size(max(settings.scaling_sizes), usable_indices)
    if "order" in experiment_names or "dupes" in experiment_names:
        check_sample_size(settings.order_sample_size, usable_indices)

    cases = []
    if "scaling" in experiment_names:
        print("Scaling experiment")
        cases += run_scaling(rows, usable_indices, settings)
    if "order" in experiment_names:
        print("Input-order experiment")
        cases += run_input_order(rows, usable_indices, settings)
    if "dupes" in experiment_names:
        print("Repeated-values experiment")
        duplicate_cases, duplicate_rows = run_repeated_values(rows, usable_indices, settings)
        cases += duplicate_cases
        write_rows(duplicate_rows, os.path.join(output_folder, "dupes_stats.csv"), DUPES_FIELDS)
    write_cases(cases, os.path.join(output_folder, "cases.csv"))
    write_runs(cases, os.path.join(output_folder, "timing_runs.csv"))
    print(f"{len(cases)} cases done")
    return cases


# Function to compute growth factors and the bubble sort estimates
def run_analysis(case_rows, settings, output_folder):
    """
    Description:
    - Compute the growth factors and both bubble sort estimates, print each method's range,
      and write growth.csv and extrapolation.csv.

    Input arguments:
       case_rows (list[dict]): Case rows from case_row or read_cases.
       settings (Settings): Run settings (extrapolation target and base sizes).
       output_folder (str): Folder for the CSV files.

    Return:
        None (raises ValueError on a zero or negative timing)
    """
    write_rows(growth_factors(case_rows), os.path.join(output_folder, "growth.csv"), GROWTH_FIELDS)
    target_size = settings.extrapolation_target_size
    base_sizes = settings.extrapolation_base_sizes
    all_estimates = []
    for method, extrapolate in (("c", extrapolate_bubble), ("growth", extrapolate_bubble_growth)):
        estimate_rows = extrapolate(case_rows, target_size, base_sizes)
        if estimate_rows:
            lowest, highest = estimate_range(estimate_rows)
            print(f"  Bubble sort estimate for n = {target_size} (method {method}): {lowest:.1f} - {highest:.1f} s")
        else:
            print(f"  Bubble sort estimate for n = {target_size} (method {method}): no estimate available")
        all_estimates += estimate_rows
    write_rows(all_estimates, os.path.join(output_folder, "extrapolation.csv"), EXTRAPOLATION_FIELDS)


# Function to draw every chart
def run_plots(case_rows, output_folder):
    """
    Description:
    - Draw the scaling, input-order and repeated-values charts.

    Input arguments:
       case_rows (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the PNG files written.
    """
    plot_files = []
    for plot in (plot_scaling, plot_input_order, plot_repeated_values):
        plot_files += plot(case_rows, output_folder)
    return plot_files


# Function to read cases.csv for `analyze` and `plot`
def read_case_rows(output_folder):
    """
    Description:
    - Read output_folder/cases.csv written by an earlier run.

    Input arguments:
       output_folder (str): Folder holding cases.csv.

    Return:
        list[dict]: typed case rows (raises InputError if the file is missing or malformed)
    """
    path = os.path.join(output_folder, "cases.csv")
    try:
        return read_cases(path)
    except FileNotFoundError:
        raise InputError(f"{path} not found - run the experiments first") from None
    except ValueError as error:
        raise InputError(f"{path} is malformed: {error}") from None


# Function to run the official pipeline
def run_all(csv_path, settings, output_folder):
    """
    Description:
    - Official run: inspection, all experiments, analysis, plots, then metadata.json last.
    - With mocks in use, old outputs are kept and metadata.json is not written.

    Input arguments:
       csv_path (str): Dataset path.
       settings (Settings): Run settings.
       output_folder (str): Folder for every output.

    Return:
        None
    """
    is_official = not mocked_steps()
    if is_official:
        remove_previous_outputs(output_folder)
    rows, usable_indices = load_dataset(csv_path, settings)
    inspection_rows = run_inspection(rows, settings)
    write_rows(inspection_rows, os.path.join(output_folder, "inspection.csv"), INSPECTION_FIELDS)
    cases = run_experiments(("scaling", "order", "dupes"), rows, usable_indices, settings, output_folder)
    case_rows = [case_row(case) for case in cases]
    run_analysis(case_rows, settings, output_folder)

    if matplotlib_available():
        plot_files = run_plots(case_rows, output_folder)
        plots_status = "complete"
    else:
        print("INCOMPLETE: plots missing (matplotlib not installed) - build the charts from the CSV files")
        plot_files = []
        plots_status = "missing"

    if is_official:
        generated_files = [os.path.join(output_folder, name) for name in CSV_OUTPUTS] + plot_files
        write_metadata(os.path.join(output_folder, "metadata.json"), csv_path, settings, plots_status,
                       generated_files)
    else:
        print("Mock run: metadata.json not written")


# Function to delete the outputs of an earlier official run
def remove_previous_outputs(output_folder):
    """
    Description:
    - Delete metadata.json and old PNG files before an official run, so a failed run never
      leaves an old success marker or stale charts.

    Input arguments:
       output_folder (str): Folder of the official run.

    Return:
        None
    """
    raise NotImplementedError("remove_previous_outputs: not implemented yet")


# Function to write the success marker of an official run
def write_metadata(path, csv_path, settings, plots_status, generated_files):
    """
    Description:
    - Write metadata.json: dataset path and SHA-256, seeds, sizes, timing tiers, Python
      version, a timestamp, plots_status and generated_files.
    - Write a temporary file first, then rename it with os.replace, so an interrupted run
      never leaves a partial file.

    Input arguments:
       path (str): Destination, normally results/metadata.json.
       csv_path (str): Dataset path, used for its SHA-256.
       settings (Settings): Run settings.
       plots_status (str): 'complete' or 'missing'.
       generated_files (list[str]): Paths written by this run.

    Return:
        None
    """
    raise NotImplementedError("write_metadata: not implemented yet")


# Function to run one command
def run_command(command, csv_path, settings, output_folder):
    """
    Description:
    - Run one command: check, scaling, order, dupes, analyze, plot or all.

    Input arguments:
       command (str): Command name.
       csv_path (str): Dataset path.
       settings (Settings): Run settings.
       output_folder (str): Folder for the outputs.

    Return:
        None (InputError, VerificationError, ValueError and NotImplementedError are handled by main)
    """
    if command != "check":
        check_output_folder(output_folder, settings)
        os.makedirs(output_folder, exist_ok=True)
    if command == "check":
        rows, _ = load_dataset(csv_path, settings, need_usable_rows=False)
        run_inspection(rows, settings)
    elif command in ("scaling", "order", "dupes"):
        rows, usable_indices = load_dataset(csv_path, settings)
        run_experiments((command,), rows, usable_indices, settings, output_folder)
    elif command == "analyze":
        run_analysis(read_case_rows(output_folder), settings, output_folder)
    elif command == "plot":
        if not matplotlib_available():
            raise InputError("the plot command needs matplotlib")
        run_plots(read_case_rows(output_folder), output_folder)
    else:
        run_all(csv_path, settings, output_folder)


# Function to run the program
def main(argument_list=None, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Run the command given on the command line and turn failures into exit codes.
    - metadata.json is never written after a failure.

    Input arguments:
       argument_list (list[str]): Arguments without the program name; None reads sys.argv.
       settings (Settings): Run settings; tests pass a small one.

    Return:
        int: the exit code (0, 1, 2 or 130).
    """
    arguments = parse_arguments(argument_list)
    csv_path = arguments.csv or settings.csv_path
    output_folder = choose_output_folder(arguments.command, arguments.out, settings)
    if mocked_steps():
        print(f"Mocked steps: {', '.join(mocked_steps())}")
    try:
        run_command(arguments.command, csv_path, settings, output_folder)
    except InputError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_INPUT
    except VerificationError as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
        return EXIT_FAILURE
    except NotImplementedError as error:
        print(f"NOT IMPLEMENTED: {error}", file=sys.stderr)
        return EXIT_FAILURE
    except KeyboardInterrupt:
        print("Interrupted - metadata.json not written", file=sys.stderr)
        return EXIT_INTERRUPTED
    except Exception:
        traceback.print_exc()
        return EXIT_FAILURE
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
