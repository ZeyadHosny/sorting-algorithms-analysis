"""End-to-end tests of main.py.

TestMockRun runs now: the pipeline works while some steps are still mocks.
TestEndToEnd is drafted and runs once no mock is left in main.py.
Spec: ARCHITECTURE.md F-E2E-1, F-E2E-2.
"""
import contextlib
import io
import os
import random
import tempfile
import unittest

import main
from sorting_analysis.config import Settings

NOT_WRITTEN = "test not implemented yet"
SMALL = Settings(scaling_sizes=(5, 10), order_sample_size=10, extrapolation_base_sizes=(5, 10), small_input_repetitions=2)


def write_fixture_csv(path, rows=30):
    """A small CSV with the three selected columns and valid, seeded values (some capped house values)."""
    rng = random.Random(1)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("median_income,housing_median_age,median_house_value\n")
        for _ in range(rows):
            value = 500001.0 if rng.random() < 0.2 else rng.uniform(15000, 500000)
            handle.write(f"{rng.uniform(0.5, 15):.4f},{rng.randint(1, 52)}.0,{value:.1f}\n")


def run_quietly(argv, settings=SMALL):
    """Run main.main(argv, settings) without printing; returns the exit code."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return main.main(argv, settings=settings)


class TestMockRun(unittest.TestCase):
    """While any step is mocked: every command runs, and metadata.json is never written.

    Uses a 30-row fixture and small settings, so it keeps passing as steps become real.
    """

    def setUp(self):
        if not main.mocked_steps():
            self.skipTest("no mocks left")
        self.tmp = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.tmp.name, "housing.csv")
        write_fixture_csv(self.csv)
        self.out = os.path.join(self.tmp.name, "out")

    def tearDown(self):
        self.tmp.cleanup()

    def test_commands_succeed_without_metadata(self):
        """check, scaling, order, dupes, all -> exit code 0 and no metadata.json."""
        for command in ("check", "scaling", "order", "dupes", "all"):
            with self.subTest(command=command):
                self.assertEqual(run_quietly([command, "--csv", self.csv, "--out", self.out]), main.EXIT_OK)
                self.assertFalse(os.path.exists(os.path.join(self.out, "metadata.json")))

    def test_mock_run_defaults_to_dev_folder(self):
        """`all` with mocks and no --out writes to results/dev/, never results/."""
        self.assertEqual(main.choose_output_folder("all", None, SMALL), os.path.join("results", "dev"))

    def test_mock_run_refuses_official_folder(self):
        """--out pointing at the results folder, or at a folder with a metadata.json -> exit code 2."""
        official = os.path.join(self.tmp.name, "results")
        settings = Settings(results_folder=official, scaling_sizes=(5, 10), order_sample_size=10)
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", official], settings), main.EXIT_INPUT)
        os.makedirs(self.out)
        open(os.path.join(self.out, "metadata.json"), "w").close()
        self.assertEqual(run_quietly(["scaling", "--csv", self.csv, "--out", self.out]), main.EXIT_INPUT)

    @unittest.skipUnless(os.name == "nt", "case-insensitive paths on Windows only")
    def test_mock_run_refuses_official_folder_in_other_case(self):
        """On Windows, --out RESULTS (upper case) is the same folder as results -> exit code 2."""
        official = os.path.join(self.tmp.name, "results")
        settings = Settings(results_folder=official, scaling_sizes=(5, 10), order_sample_size=10)
        upper = os.path.join(self.tmp.name, "RESULTS")
        self.assertEqual(run_quietly(["all", "--csv", self.csv, "--out", upper], settings), main.EXIT_INPUT)

    def test_missing_dataset_is_an_input_error(self):
        """A CSV path that does not exist -> exit code 2."""
        missing = os.path.join(self.tmp.name, "missing.csv")
        self.assertEqual(run_quietly(["check", "--csv", missing]), main.EXIT_INPUT)

    def test_plot_without_matplotlib_is_an_input_error(self):
        """plot while matplotlib is unavailable -> exit code 2."""
        if main.matplotlib_available():
            self.skipTest("matplotlib is available")
        self.assertEqual(run_quietly(["plot", "--out", self.out]), main.EXIT_INPUT)

    def test_check_accepts_header_only_dataset(self):
        """check on a CSV with only the header -> exit code 0 (reports 0 rows)."""
        if "load_csv" in main.mocked_steps():
            self.skipTest("needs the real load_csv")
        with open(self.csv, "w", encoding="utf-8") as handle:
            handle.write("median_income,housing_median_age,median_house_value\n")
        self.assertEqual(run_quietly(["check", "--csv", self.csv]), main.EXIT_OK)


class TestEndToEnd(unittest.TestCase):
    """main(['all']) on the 30-row fixture with small settings; outputs in a temporary folder."""

    def setUp(self):
        if main.mocked_steps():
            self.skipTest("steps still mocked: " + ", ".join(main.mocked_steps()))

    def test_all_writes_every_output(self):
        """Exit code 0; every CSV in main.CSV_OUTPUTS and metadata.json exist."""
        self.skipTest(NOT_WRITTEN)

    def test_pngs_only_when_matplotlib_available(self):
        """PNG files exist if matplotlib_available(); plots_status is complete or missing accordingly."""
        self.skipTest(NOT_WRITTEN)

    def test_old_metadata_and_pngs_removed_first(self):
        """A stale metadata.json and PNG in the output folder are removed before the run."""
        self.skipTest(NOT_WRITTEN)

    def test_failure_writes_no_metadata(self):
        """A sort that fails verification -> exit code 1 and no metadata.json."""
        self.skipTest(NOT_WRITTEN)

    def test_never_writes_into_committed_results(self):
        """The repository's results/ folder is unchanged by the test run."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
