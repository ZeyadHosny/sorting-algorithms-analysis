"""Unit tests for experiments.common.records (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.experiments import ALGORITHMS, read_cases, write_cases, write_rows, write_runs  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestRecords(unittest.TestCase):
    """CSV writing and reading of results."""

    def test_algorithms_map_to_the_three_sorts(self):
        """ALGORITHMS has keys bubble, selection, merge."""
        self.skipTest(NOT_WRITTEN)

    def test_case_row_flattens_a_case(self):
        """case_row(case) has the CASE_FIELDS keys; median_s etc. come from get_timing(); swaps None for merge."""
        self.skipTest(NOT_WRITTEN)

    def test_round_trip_returns_equal_values(self):
        """write_cases then read_cases -> equal labels, counts and timings."""
        self.skipTest(NOT_WRITTEN)

    def test_merge_swaps_written_as_na(self):
        """A merge case -> swaps 'n/a' in the CSV, None after read_cases."""
        self.skipTest(NOT_WRITTEN)

    def test_empty_rows_write_header_only(self):
        """write_rows([], path, fields) -> a file with only the header."""
        self.skipTest(NOT_WRITTEN)

    def test_runs_file_has_one_row_per_batch(self):
        """One case with 5 batch times -> 5 rows in timing_runs.csv."""
        self.skipTest(NOT_WRITTEN)

    def test_malformed_number_raises(self):
        """'abc' in the input_size column -> ValueError."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
