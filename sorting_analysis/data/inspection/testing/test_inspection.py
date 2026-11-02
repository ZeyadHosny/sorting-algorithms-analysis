"""Unit tests for data.inspection (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.data import duplicate_stats, inspect_data  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestInspectData(unittest.TestCase):
    """Rows, missing and distinct values per column."""

    def test_counts_rows_missing_and_distinct(self):
        """3 rows, one blank median_income -> rows 3, missing 1, distinct = number of different values."""
        self.skipTest(NOT_WRITTEN)

    def test_excluded_rows_counts_any_missing_selected_value(self):
        """Blank values in two different rows -> excluded_rows 2 on every column."""
        self.skipTest(NOT_WRITTEN)

    def test_returns_one_result_per_column(self):
        """3 columns -> 3 dicts with the INSPECTION_FIELDS keys."""
        self.skipTest(NOT_WRITTEN)


class TestDuplicateStats(unittest.TestCase):
    """Duplication statistics."""

    def test_worked_example(self):
        """[1, 1, 2, 3, 3, 3] -> n 6, distinct 3, modal_value 3, modal_count 3, repeated_distinct 2, repeated_observations 5."""
        self.skipTest(NOT_WRITTEN)

    def test_no_duplicates(self):
        """[1, 2, 3] -> repeated_distinct 0, repeated_observations 0."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
