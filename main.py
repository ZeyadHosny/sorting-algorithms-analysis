"""
Description:
- Command-line entry point of the sorting analysis:
      python main.py {check,scaling,order,dupes,analyze,plot,all} [--csv PATH] [--out FOLDER]
- `all` is the official run and writes to results/; the other commands are for development and
  write to results/dev/ unless --out is given.
- Exit codes: 0 success (plots may be missing) | 1 computation failure (wrong sort output,
  invalid timing, unexpected error) | 2 input or usage error (dataset, columns, sample size,
  cases.csv, matplotlib for `plot`) | 130 interrupted.
- Spec: ARCHITECTURE.md F-MAIN-1 - F-MAIN-6.
"""

import argparse
import datetime
import hashlib
import json
import os
import platform
import sys
import traceback

from sorting_analysis.analysis import EXTRAPOLATION_FIELDS, GROWTH_FIELDS, extrapolate_bubble, growth_factors
from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.data import DUPES_FIELDS, INSPECTION_FIELDS, complete_cases, inspect_data, load_csv
from sorting_analysis.experiments import (case_row, read_cases, run_input_order, run_repeated_values, run_scaling,
                                          write_cases, write_rows, write_runs)
from sorting_analysis.plots import (matplotlib_available, plot_bubble_extrapolation, plot_growth, plot_input_order,
                                    plot_repeated_values, plot_scaling)
from sorting_analysis.timing import VerificationError

# Exit codes returned by main.
EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_INPUT = 2
EXIT_INTERRUPTED = 130
# Commands accepted on the command line; `all` is the official run.
COMMANDS = ("check", "scaling", "order", "dupes", "analyze", "plot", "all")
# CSV files written by an official run (recorded in metadata.json).
CSV_OUTPUTS = ("inspection.csv", "cases.csv", "timing_runs.csv", "dupes_stats.csv", "growth.csv",
               "extrapolation.csv")
# PNG files the charts can write; an official run deletes old copies of these only.
PLOT_OUTPUTS = ("scaling_summary.png", "scaling_tiny_runtime.png", "input_order_summary.png",
                "repeated_values_summary.png", "growth_factors.png", "bubble_extrapolation.png")
# Name of the success marker of an official run.
METADATA_NAME = "metadata.json"


class InputError(Exception):
    """
    Description:
    - Raised for a problem with the dataset, the arguments, the output folder or cases.csv.
    - main turns it into exit code 2.
    """


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
    - Use --out if given; otherwise results/ for the official `all` run and results/dev/ for the
      development commands.

    Input arguments:
       command (str): Command name, e.g. 'all'.
       requested_folder (str): Value of --out, or None.
       settings (Settings): Run settings.

    Return:
        str: e.g. 'results' or 'results/dev'.
    """
    if requested_folder:
        return requested_folder
    if command == "all":
        return settings.results_folder
    return os.path.join(settings.results_folder, "dev")


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


# Function to compute growth factors and the bubble sort estimate
def compute_analysis(case_rows, settings):
    """
    Description:
    - Growth factors of every doubling pair and the bubble sort estimate (quadratic regression on
      the base sizes), from the scaling rows of case_rows.

    Input arguments:
       case_rows (list[dict]): Case rows from case_row or read_cases.
       settings (Settings): Run settings (extrapolation target and base sizes).

    Return:
        tuple: (growth rows, estimate row, measured-versus-fitted rows) (raises ValueError on a
         missing base size, an invalid timing or a singular fit)
    """
    growth_rows = growth_factors(case_rows)
    estimate_row, fitted_rows = extrapolate_bubble(case_rows, settings.extrapolation_target_size,
                                                   settings.extrapolation_base_sizes)
    return growth_rows, estimate_row, fitted_rows


# Function to write and print the analysis
def write_analysis(growth_rows, estimate_row, fitted_rows, output_folder):
    """
    Description:
    - Write growth.csv and extrapolation.csv, and print the estimate and the measured-versus-fitted times.

    Input arguments:
       growth_rows (list[dict]): Rows from growth_factors.
       estimate_row (dict): Estimate row from extrapolate_bubble.
       fitted_rows (list[dict]): Measured-versus-fitted rows from extrapolate_bubble.
       output_folder (str): Folder for the CSV files.

    Return:
        None
    """
    write_rows(growth_rows, os.path.join(output_folder, "growth.csv"), GROWTH_FIELDS)
    print(f"  Bubble sort estimate for n = {estimate_row['target_size']}: {estimate_row['estimate_s']:.1f} s "
          f"(T(n) = {estimate_row['a0']:.3g} + {estimate_row['a1']:.3g} n + {estimate_row['a2']:.3g} n^2)")
    for fitted in fitted_rows:
        print(f"    n = {fitted['input_size']}: measured {fitted['measured_s']:.4g} s, "
              f"fitted {fitted['fitted_s']:.4g} s")
    write_rows([estimate_row], os.path.join(output_folder, "extrapolation.csv"), EXTRAPOLATION_FIELDS)


# Function to draw every chart
def run_plots(case_rows, growth_rows, estimate_row, fitted_rows, output_folder):
    """
    Description:
    - Draw the scaling, input-order, repeated-values, growth and bubble extrapolation charts.

    Input arguments:
       case_rows (list[dict]): Case rows from case_row or read_cases.
       growth_rows (list[dict]): Rows from growth_factors.
       estimate_row (dict): Estimate row from extrapolate_bubble.
       fitted_rows (list[dict]): Measured-versus-fitted rows from extrapolate_bubble.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the PNG files written.
    """
    plot_files = []
    for plot in (plot_scaling, plot_input_order, plot_repeated_values):
        plot_files += plot(case_rows, output_folder)
    plot_files += plot_growth(growth_rows, output_folder)
    plot_files += plot_bubble_extrapolation(case_rows, estimate_row, fitted_rows, output_folder)
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


# Function to analyze the cases.csv of an earlier run
def analyze_saved_cases(output_folder, settings):
    """
    Description:
    - Read cases.csv and compute the analysis; a file without the needed scaling rows is an input
      error, not a computation failure.

    Input arguments:
       output_folder (str): Folder holding cases.csv.
       settings (Settings): Run settings.

    Return:
        tuple: (case rows, growth rows, estimate row, measured-versus-fitted rows) (raises InputError)
    """
    case_rows = read_case_rows(output_folder)
    try:
        return (case_rows,) + compute_analysis(case_rows, settings)
    except ValueError as error:
        raise InputError(f"{os.path.join(output_folder, 'cases.csv')} cannot be analyzed: {error}") from None


# Function to run the official pipeline
def run_all(csv_path, settings, output_folder):
    """
    Description:
    - Official run: remove old outputs, then inspection, all experiments, analysis, plots, and
      metadata.json last.

    Input arguments:
       csv_path (str): Dataset path.
       settings (Settings): Run settings.
       output_folder (str): Folder for every output.

    Return:
        None
    """
    remove_previous_outputs(output_folder)
    rows, usable_indices = load_dataset(csv_path, settings)
    inspection_rows = run_inspection(rows, settings)
    write_rows(inspection_rows, os.path.join(output_folder, "inspection.csv"), INSPECTION_FIELDS)
    cases = run_experiments(("scaling", "order", "dupes"), rows, usable_indices, settings, output_folder)
    case_rows = [case_row(case) for case in cases]
    growth_rows, estimate_row, fitted_rows = compute_analysis(case_rows, settings)
    write_analysis(growth_rows, estimate_row, fitted_rows, output_folder)

    if matplotlib_available():
        plot_files = run_plots(case_rows, growth_rows, estimate_row, fitted_rows, output_folder)
        plots_status = "complete"
    else:
        print("INCOMPLETE: plots missing (matplotlib not installed) - build the charts from the CSV files")
        plot_files = []
        plots_status = "missing"

    generated_files = [os.path.join(output_folder, name) for name in CSV_OUTPUTS] + plot_files
    write_metadata(os.path.join(output_folder, METADATA_NAME), csv_path, settings, plots_status, generated_files)


# Function to delete the outputs of an earlier official run
def remove_previous_outputs(output_folder):
    """
    Description:
    - Delete metadata.json, a leftover temporary metadata file and the chart PNGs (PLOT_OUTPUTS)
      before an official run, so a failed run never leaves an old success marker or stale charts.
    - Other files, e.g. charts made by hand in Excel, are kept.

    Input arguments:
       output_folder (str): Folder of the official run.

    Return:
        None
    """
    for name in (METADATA_NAME, METADATA_NAME + ".tmp") + PLOT_OUTPUTS:
        path = os.path.join(output_folder, name)
        if os.path.isfile(path):
            os.remove(path)


# Function to write the success marker of an official run
def write_metadata(path, csv_path, settings, plots_status, generated_files):
    """
    Description:
    - Write metadata.json: dataset path and SHA-256, seeds, columns, sizes, timing tiers, Python
      version, platform, a UTC timestamp, plots_status and generated_files.
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
    with open(csv_path, "rb") as dataset_file:
        dataset_sha256 = hashlib.sha256(dataset_file.read()).hexdigest()
    metadata = {
        "dataset": {"path": csv_path.replace(os.sep, "/"), "sha256": dataset_sha256},
        "seeds": {"sample": settings.sample_seed, "shuffle": settings.shuffle_seed,
                  "nearly_sorted": settings.nearly_sorted_seed},
        "columns": {"selected": list(settings.selected_columns), "scaling": settings.scaling_column,
                    "order": settings.order_column},
        "sizes": {"scaling": list(settings.scaling_sizes), "order_sample": settings.order_sample_size,
                  "extrapolation_base": list(settings.extrapolation_base_sizes),
                  "extrapolation_target": settings.extrapolation_target_size},
        "timing": {"timed_batches": settings.timed_batches, "small_input_limit": settings.small_input_limit,
                   "small_input_repetitions": settings.small_input_repetitions,
                   "normal_input_repetitions": settings.normal_input_repetitions},
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "plots_status": plots_status,
        "generated_files": [file_path.replace(os.sep, "/") for file_path in generated_files],
    }
    temporary_path = path + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2)
        metadata_file.write("\n")
    os.replace(temporary_path, path)


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
        None (InputError, VerificationError and other errors are handled by main)
    """
    if command != "check":
        os.makedirs(output_folder, exist_ok=True)
    if command == "check":
        rows, usable_indices = load_dataset(csv_path, settings, need_usable_rows=False)
        run_inspection(rows, settings)
    elif command in ("scaling", "order", "dupes"):
        rows, usable_indices = load_dataset(csv_path, settings)
        run_experiments((command,), rows, usable_indices, settings, output_folder)
    elif command == "analyze":
        case_rows, growth_rows, estimate_row, fitted_rows = analyze_saved_cases(output_folder, settings)
        write_analysis(growth_rows, estimate_row, fitted_rows, output_folder)
    elif command == "plot":
        if not matplotlib_available():
            raise InputError("the plot command needs matplotlib")
        run_plots(*analyze_saved_cases(output_folder, settings), output_folder)
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
    try:
        run_command(arguments.command, csv_path, settings, output_folder)
    except InputError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return EXIT_INPUT
    except VerificationError as error:
        print(f"VERIFICATION FAILED: {error}", file=sys.stderr)
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
