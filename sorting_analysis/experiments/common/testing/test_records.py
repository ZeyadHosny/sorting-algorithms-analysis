"""Unit and integration tests for experiments.common.records."""
import csv
import os
import tempfile
import unittest

from sorting_analysis.config import Settings
from sorting_analysis.experiments import (ALGORITHMS, CASE_FIELDS, RUN_FIELDS, CaseResult, case_row,
                                          read_cases, write_cases, write_rows, write_runs)
from sorting_analysis.sorts import (SortStats, bubble_sort, counted_bubble_sort, counted_merge_sort,
                                    counted_selection_sort, merge_sort, selection_sort)
from sorting_analysis.timing import TimingResult, benchmark


class TestRecords(unittest.TestCase):
    """CSV writing and reading of results; fixture times are invented test data."""

    # Method to prepare a temporary folder and a measured-case fixture
    def setUp(self):
        """
        Description:
        - Prepare sample records and isolated temporary output paths for each test.

        Input arguments:
           None

        Return:
            None
        """
        temporary_folder = tempfile.TemporaryDirectory()
        self.addCleanup(temporary_folder.cleanup)
        self.case_path = os.path.join(temporary_folder.name, "cases.csv")
        self.run_path = os.path.join(temporary_folder.name, "timing_runs.csv")
        self.batch_times = (0.003, 0.001, 0.002, 0.004, 0.005)
        self.timing = TimingResult(self.batch_times, 1000, 0.003, 0.001, 0.005)
        self.case = CaseResult("scaling", "bubble", "median_income", "random", 5,
                               SortStats(12, 8, 4), self.timing)
        self.merge_case = CaseResult("order", "merge", "median_income", "sorted", 5,
                                     SortStats(7, 12, None), self.timing)
        self.expected_row = {
            "experiment": "scaling", "algorithm": "bubble", "column": "median_income", "order": "random",
            "input_size": 5, "comparisons": 12, "writes": 8, "swaps": 4, "sorts_per_batch": 1000,
            "median_s": 0.003, "min_s": 0.001, "max_s": 0.005,
        }

    def test_algorithms_map_to_the_three_sorts(self):
        """ALGORITHMS has keys bubble, selection, merge, each mapped to (plain sort, counted sort)."""
        self.assertEqual(list(ALGORITHMS), ["bubble", "selection", "merge"])
        self.assertEqual(ALGORITHMS["bubble"], (bubble_sort, counted_bubble_sort))
        self.assertEqual(ALGORITHMS["selection"], (selection_sort, counted_selection_sort))
        self.assertEqual(ALGORITHMS["merge"], (merge_sort, counted_merge_sort))

    def test_case_row_flattens_a_case(self):
        """case_row(case) has the CASE_FIELDS keys; median_s etc. come from get_timing(); swaps None for merge."""
        row = case_row(self.case)
        self.assertEqual(tuple(row), CASE_FIELDS)
        self.assertEqual(row, self.expected_row)
        self.assertIsNone(case_row(self.merge_case)["swaps"])

    def test_round_trip_returns_equal_values(self):
        """write_cases then read_cases -> equal labels, counts and timings."""
        write_cases([self.case, self.merge_case], self.case_path)
        rows = read_cases(self.case_path)
        self.assertEqual(rows, [self.expected_row, case_row(self.merge_case)])
        for row in rows:
            for field in ("input_size", "comparisons", "writes", "sorts_per_batch"):
                self.assertIs(type(row[field]), int)
            for field in ("median_s", "min_s", "max_s"):
                self.assertIs(type(row[field]), float)
        self.assertIs(type(rows[0]["swaps"]), int)

    def test_merge_swaps_written_as_na(self):
        """A merge case -> swaps 'n/a' in the CSV, None after read_cases."""
        write_cases([self.merge_case], self.case_path)
        with open(self.case_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            self.assertEqual(reader.fieldnames, list(CASE_FIELDS))
            self.assertEqual(next(reader)["swaps"], "n/a")
        self.assertIsNone(read_cases(self.case_path)[0]["swaps"])

    def test_empty_rows_write_header_only(self):
        """write_rows([], path, fields) -> a file with only the header."""
        fields = ("column", "rows", "missing")
        write_rows([], self.case_path, fields)
        with open(self.case_path, newline="", encoding="utf-8") as csv_file:
            self.assertEqual(list(csv.reader(csv_file)), [list(fields)])

    def test_runs_file_has_one_row_per_batch(self):
        """One case with 5 batch times -> 5 rows in timing_runs.csv."""
        write_runs([self.case], self.run_path)
        with open(self.run_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            self.assertEqual(reader.fieldnames, list(RUN_FIELDS))
            rows = list(reader)
        self.assertEqual(len(rows), 5)
        self.assertEqual([int(row["batch"]) for row in rows], [1, 2, 3, 4, 5])
        # Tiny-input times are already divided by repetitions; do not divide them again.
        self.assertEqual([float(row["seconds_per_sort"]) for row in rows], list(self.batch_times))
        for row in rows:
            self.assertEqual([row[field] for field in RUN_FIELDS[:5]],
                             ["scaling", "bubble", "median_income", "random", "5"])

    def test_malformed_number_raises(self):
        """'abc' in the input_size column -> ValueError."""
        row = self.expected_row.copy()
        row["input_size"] = "abc"
        write_rows([row], self.case_path, CASE_FIELDS)
        with self.assertRaises(ValueError):
            read_cases(self.case_path)

    def test_every_numeric_field_rejects_malformed_text(self):
        """Malformed text in any numeric column raises ValueError."""
        for field in CASE_FIELDS[4:]:
            with self.subTest(field=field):
                row = self.expected_row.copy()
                row[field] = "not a number"
                write_rows([row], self.case_path, CASE_FIELDS)
                with self.assertRaises(ValueError):
                    read_cases(self.case_path)

    def test_missing_numeric_cell_raises(self):
        """A row ending before its final numeric value raises ValueError."""
        with open(self.case_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(CASE_FIELDS)
            writer.writerow([self.expected_row[field] for field in CASE_FIELDS[:-1]])
        with self.assertRaises(ValueError):
            read_cases(self.case_path)

    def test_missing_file_raises(self):
        """Reading an absent cases.csv raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            read_cases(self.case_path)

    def test_empty_cases_and_runs_keep_their_headers(self):
        """Empty case lists write both headers, and read_cases returns an empty list."""
        write_cases([], self.case_path)
        write_runs([], self.run_path)
        for path, fields in ((self.case_path, CASE_FIELDS), (self.run_path, RUN_FIELDS)):
            with self.subTest(path=path):
                with open(path, newline="", encoding="utf-8") as csv_file:
                    self.assertEqual(list(csv.reader(csv_file)), [list(fields)])
        self.assertEqual(read_cases(self.case_path), [])

    def test_generic_writer_preserves_header_order_and_quoted_text(self):
        """Generic CSV writing preserves Unicode, commas, quotes, newlines and explicit column order."""
        rows = [{"note": 'A, "quoted" note\nNext line', "name": "بهاره"}]
        before = [row.copy() for row in rows]
        write_rows(rows, self.case_path, ("name", "note"))
        with open(self.case_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            self.assertEqual(reader.fieldnames, ["name", "note"])
            self.assertEqual(list(reader), rows)
        self.assertEqual(rows, before)

    def test_zero_swaps_stays_zero(self):
        """A zero swap count stays numeric zero, rather than becoming n/a."""
        case = CaseResult("order", "bubble", "median_income", "sorted", 5,
                          SortStats(4, 0, 0), self.timing)
        write_cases([case], self.case_path)
        self.assertEqual(read_cases(self.case_path)[0]["swaps"], 0)
        with open(self.case_path, newline="", encoding="utf-8") as csv_file:
            self.assertEqual(next(csv.DictReader(csv_file))["swaps"], "0")

    def test_run_numbers_restart_for_each_case(self):
        """Two cases keep their order, labels and all batches; each starts at batch 1."""
        write_runs([self.case, self.merge_case], self.run_path)
        with open(self.run_path, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 10)
        self.assertEqual([row["algorithm"] for row in rows], ["bubble"] * 5 + ["merge"] * 5)
        self.assertEqual([int(row["batch"]) for row in rows], [1, 2, 3, 4, 5] * 2)
        self.assertEqual([float(row["seconds_per_sort"]) for row in rows], list(self.batch_times) * 2)

    def test_writing_does_not_change_case_values(self):
        """Flattening and writing leave case labels, counts and batch timings unchanged."""
        cases = [self.case, self.merge_case]
        before = [case_row(case) for case in cases]
        write_cases(cases, self.case_path)
        write_runs(cases, self.run_path)
        self.assertEqual([case_row(case) for case in cases], before)
        self.assertEqual(self.timing.get_batch_seconds(), self.batch_times)
        self.assertIsNone(self.merge_case.get_sort_stats().get_swaps())

    def test_real_benchmark_results_can_be_saved_and_read(self):
        """Real measured results from all three algorithms round-trip with all batch times retained."""
        settings = Settings(timed_batches=5, small_input_repetitions=2)
        values = [3.0, 1.0, 2.0]
        cases = []
        for algorithm, functions in ALGORITHMS.items():
            plain_sort, counted_sort = functions
            timing, sort_stats = benchmark(plain_sort, counted_sort, values, settings)
            cases.append(CaseResult("scaling", algorithm, "median_income", "random", 3, sort_stats, timing))
        write_cases(cases, self.case_path)
        write_runs(cases, self.run_path)
        self.assertEqual(read_cases(self.case_path), [case_row(case) for case in cases])
        with open(self.run_path, newline="", encoding="utf-8") as csv_file:
            rows = list(csv.DictReader(csv_file))
        self.assertEqual(len(rows), 15)
        for case_index, case in enumerate(cases):
            saved_times = [float(row["seconds_per_sort"]) for row in rows[case_index * 5:(case_index + 1) * 5]]
            self.assertEqual(saved_times, list(case.get_timing().get_batch_seconds()))
        self.assertEqual(values, [3.0, 1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
