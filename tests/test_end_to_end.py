"""End-to-end tests of main.py on a 30-row fixture with small settings; outputs go to temporary folders.

Spec: ARCHITECTURE.md F-E2E-1, F-E2E-2.
"""
import contextlib
import csv
import hashlib
import io
import json
import os
import random
import tempfile
import unittest
from unittest.mock import patch

import main
from sorting_analysis.config import Settings
from sorting_analysis.experiments import ALGORITHMS, read_cases
from sorting_analysis.sorts import counted_bubble_sort

# Five scaling sizes, all fitted, so the quadratic regression has enough points (it needs at least 3).
SMALL = Settings(scaling_sizes=(5, 10, 15, 20, 25), order_sample_size=10, extrapolation_base_sizes=(5, 10, 15, 20, 25),
                 small_input_repetitions=2)
# The repository's committed results folder, which no test may change.
COMMITTED_RESULTS = os.path.join(os.path.dirname(os.path.abspath(main.__file__)), "results")


# Function to write the small dataset used by every test
def write_fixture_csv(path, rows=30):
    """
    Description:
    - Write a CSV with the three selected columns and valid, seeded values (some capped house values).

    Input arguments:
       path (str): Destination path.
       rows (int): Number of data rows.

    Return:
        None
    """
    rng = random.Random(1)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("median_income,housing_median_age,median_house_value\n")
        for i in range(rows):
            value = 500001.0 if rng.random() < 0.2 else rng.uniform(15000, 500000)
            handle.write(f"{rng.uniform(0.5, 15):.4f},{rng.randint(1, 52)}.0,{value:.1f}\n")


# Function to run main without printing
def run_quietly(argv, settings=SMALL):
    """
    Description:
    - Run main.main(argv, settings) with stdout and stderr captured.

    Input arguments:
       argv (list[str]): Command-line arguments without the program name.
       settings (Settings): Run settings.

    Return:
        int: the exit code.
    """
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main.main(argv, settings=settings)


# Function to describe every file under a folder
def folder_snapshot(folder):
    """
    Description:
    - Map each file's relative path to its size and modification time.

    Input arguments:
       folder (str): Folder to describe; a missing folder gives an empty map.

    Return:
        dict: relative path -> (size in bytes, modification time in ns).
    """
    snapshot = {}
    for root, folders, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            status = os.stat(path)
            snapshot[os.path.relpath(path, folder)] = (status.st_size, status.st_mtime_ns)
    return snapshot


# Function to return a sort that leaves its input unsorted
def broken_sort(values):
    """
    Description:
    - Stand-in for bubble_sort that returns a copy of the input unchanged, so verification fails.

    Input arguments:
       values (list): Values to "sort".

    Return:
        list: the values in their original order.
    """
    return values[:]


class TestDevelopmentCommands(unittest.TestCase):
    """check, the single experiments, analyze and plot."""

    # Method to prepare a temporary dataset and output folder
    def setUp(self):
        """
        Description:
        - Write the fixture CSV into a temporary folder that is removed after the test.

        Input arguments:
           None

        Return:
            None
        """
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.csv = os.path.join(temporary.name, "housing.csv")
        write_fixture_csv(self.csv)
        self.out = os.path.join(temporary.name, "out")

    def test_development_commands_write_no_metadata(self):
        """check, scaling, order, dupes -> exit code 0, cases.csv written, never metadata.json."""
        for command in ("check", "scaling", "order", "dupes"):
            with self.subTest(command=command):
                self.assertEqual(run_quietly([command, "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
                self.assertFalse(os.path.exists(os.path.join(self.out, main.METADATA_NAME)))
        self.assertEqual({row["experiment"] for row in read_cases(os.path.join(self.out, "cases.csv"))}, {"dupes"})

    def test_default_output_folders(self):
        """`all` without --out -> results/; development commands -> results/dev/; --out wins."""
        self.assertEqual(main.choose_output_folder("all", None, SMALL), "results")
        self.assertEqual(main.choose_output_folder("scaling", None, SMALL), os.path.join("results", "dev"))
        self.assertEqual(main.choose_output_folder("all", "elsewhere", SMALL), "elsewhere")

    def test_missing_dataset_is_an_input_error(self):
        """A CSV path that does not exist -> exit code 2."""
        missing = os.path.join(os.path.dirname(self.csv), "missing.csv")
        self.assertEqual(run_quietly(["check", "--csv", missing]), main.EXIT_INPUT)

    def test_check_accepts_header_only_dataset(self):
        """check on a CSV with only the header -> exit code 0 (reports 0 rows)."""
        with open(self.csv, "w", encoding="utf-8") as handle:
            handle.write("median_income,housing_median_age,median_house_value\n")
        self.assertEqual(run_quietly(["check", "--csv", self.csv]), main.EXIT_OK)

    def test_analyze_and_plot_after_scaling(self):
        """scaling, then analyze and plot -> growth.csv, extrapolation.csv and the scaling-based PNGs."""
        self.assertEqual(run_quietly(["scaling", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        self.assertEqual(run_quietly(["analyze", "--out", self.out]), main.EXIT_OK)
        with open(os.path.join(self.out, "extrapolation.csv"), newline="", encoding="utf-8") as handle:
            estimate_rows = list(csv.DictReader(handle))
        self.assertEqual(len(estimate_rows), 1)
        self.assertEqual(estimate_rows[0]["sizes_used"], "5;10;15;20;25")
        self.assertTrue(os.path.isfile(os.path.join(self.out, "growth.csv")))
        if main.matplotlib_available():
            self.assertEqual(run_quietly(["plot", "--out", self.out]), main.EXIT_OK)
            for name in ("scaling_summary.png", "scaling_tiny_runtime.png", "growth_factors.png",
                         "bubble_extrapolation.png"):
                self.assertTrue(os.path.isfile(os.path.join(self.out, name)), name)

    def test_analyze_without_cases_is_an_input_error(self):
        """analyze or plot with no cases.csv -> exit code 2."""
        for command in ("analyze", "plot"):
            with self.subTest(command=command):
                self.assertEqual(run_quietly([command, "--out", self.out]), main.EXIT_INPUT)

    def test_analyze_without_scaling_rows_is_an_input_error(self):
        """order only, then analyze -> exit code 2 (no bubble scaling rows to fit)."""
        self.assertEqual(run_quietly(["order", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        self.assertEqual(run_quietly(["analyze", "--out", self.out]), main.EXIT_INPUT)

    def test_plot_without_matplotlib_is_an_input_error(self):
        """plot with a valid cases.csv while matplotlib is unavailable -> exit code 2 and no PNG."""
        self.assertEqual(run_quietly(["scaling", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        with patch.object(main, "matplotlib_available", return_value=False):
            self.assertEqual(run_quietly(["plot", "--out", self.out]), main.EXIT_INPUT)
        self.assertEqual([name for name in os.listdir(self.out) if name.endswith(".png")], [])


class TestEndToEnd(unittest.TestCase):
    """main(['all']) on the 30-row fixture with small settings."""

    # Method to prepare a temporary dataset and output folder
    def setUp(self):
        """
        Description:
        - Write the fixture CSV into a temporary folder that is removed after the test.

        Input arguments:
           None

        Return:
            None
        """
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.csv = os.path.join(temporary.name, "housing.csv")
        write_fixture_csv(self.csv)
        self.out = os.path.join(temporary.name, "results")

    # Method to read the metadata of the run
    def read_metadata(self):
        """
        Description:
        - Load metadata.json from the output folder.

        Input arguments:
           None

        Return:
            dict: the metadata.
        """
        with open(os.path.join(self.out, main.METADATA_NAME), encoding="utf-8") as handle:
            return json.load(handle)

    def test_all_writes_every_output(self):
        """Exit code 0; every CSV in main.CSV_OUTPUTS and metadata.json exist, with the expected contents."""
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        for name in main.CSV_OUTPUTS:
            self.assertTrue(os.path.isfile(os.path.join(self.out, name)), name)
        self.assertEqual(len(read_cases(os.path.join(self.out, "cases.csv"))), 5 * 3 + 4 * 3 + 3 * 3)
        metadata = self.read_metadata()
        with open(self.csv, "rb") as handle:
            self.assertEqual(metadata["dataset"]["sha256"], hashlib.sha256(handle.read()).hexdigest())
        self.assertEqual(metadata["seeds"], {"sample": 42, "shuffle": 43, "nearly_sorted": 44})
        self.assertEqual(metadata["sizes"]["scaling"], [5, 10, 15, 20, 25])
        self.assertEqual(metadata["timing"]["small_input_repetitions"], 2)
        for path in metadata["generated_files"]:
            self.assertTrue(os.path.isfile(path), path)
        self.assertFalse(os.path.exists(os.path.join(self.out, main.METADATA_NAME + ".tmp")))

    def test_no_command_runs_all(self):
        """No command -> parsed as `all`, written to results/ by default, and a full run with metadata.json."""
        self.assertEqual(main.parse_arguments([]).command, "all")
        self.assertEqual(main.choose_output_folder(main.parse_arguments([]).command, None, SMALL), "results")
        self.assertEqual(run_quietly(["--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        for name in main.CSV_OUTPUTS + (main.METADATA_NAME,):
            self.assertTrue(os.path.isfile(os.path.join(self.out, name)), name)

    def test_pngs_only_when_matplotlib_available(self):
        """PNG files exist if matplotlib_available(); plots_status is complete or missing accordingly."""
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        metadata = self.read_metadata()
        pngs = sorted(name for name in os.listdir(self.out) if name.endswith(".png"))
        if main.matplotlib_available():
            self.assertEqual(metadata["plots_status"], "complete")
            self.assertEqual(pngs, sorted(main.PLOT_OUTPUTS))
            self.assertEqual(sorted(os.path.basename(path) for path in metadata["generated_files"]),
                             sorted(main.CSV_OUTPUTS + main.PLOT_OUTPUTS))
        else:
            self.assertEqual((metadata["plots_status"], pngs), ("missing", []))
        with patch.object(main, "matplotlib_available", return_value=False):
            self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        metadata = self.read_metadata()
        self.assertEqual(metadata["plots_status"], "missing")
        self.assertEqual([name for name in os.listdir(self.out) if name.endswith(".png")], [])
        self.assertEqual(sorted(os.path.basename(path) for path in metadata["generated_files"]),
                         sorted(main.CSV_OUTPUTS))

    def test_old_metadata_and_pngs_removed_first(self):
        """Stale metadata and chart PNGs are removed before anything else, even when the dataset is missing
        or a sort then fails; other files stay."""
        missing_csv = os.path.join(os.path.dirname(self.csv), "missing.csv")
        for csv_path, expected_code in ((missing_csv, main.EXIT_INPUT), (self.csv, main.EXIT_FAILURE)):
            with self.subTest(expected_code=expected_code):
                os.makedirs(self.out, exist_ok=True)
                for name in (main.METADATA_NAME, main.METADATA_NAME + ".tmp", "scaling_summary.png",
                             "excel_chart.png"):
                    with open(os.path.join(self.out, name), "w", encoding="utf-8") as handle:
                        handle.write("old")
                with patch.dict(ALGORITHMS, {"bubble": (broken_sort, counted_bubble_sort)}):
                    self.assertEqual(run_quietly(["all", "--csv", csv_path, "--out", self.out]), expected_code)
                remaining = os.listdir(self.out)
                for name in (main.METADATA_NAME, main.METADATA_NAME + ".tmp", "scaling_summary.png"):
                    self.assertNotIn(name, remaining)
                self.assertIn("excel_chart.png", remaining)

    def test_failure_writes_no_metadata(self):
        """A sort that fails verification -> exit code 1 and no metadata.json."""
        with patch.dict(ALGORITHMS, {"bubble": (broken_sort, counted_bubble_sort)}):
            self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_FAILURE)
        self.assertFalse(os.path.exists(os.path.join(self.out, main.METADATA_NAME)))
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        self.assertTrue(os.path.isfile(os.path.join(self.out, main.METADATA_NAME)))

    def test_failed_metadata_rename_leaves_no_metadata(self):
        """os.replace failing while publishing metadata.json -> exit code 1 and no metadata.json."""
        with patch.object(main.os, "replace", side_effect=OSError("disk full")):
            self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_FAILURE)
        self.assertFalse(os.path.exists(os.path.join(self.out, main.METADATA_NAME)))

    def test_never_writes_into_committed_results(self):
        """The repository's results/ folder is unchanged by an official run with --out."""
        before = folder_snapshot(COMMITTED_RESULTS)
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
        self.assertEqual(folder_snapshot(COMMITTED_RESULTS), before)


if __name__ == "__main__":
    unittest.main()
