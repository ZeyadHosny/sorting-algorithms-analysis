"""Unit tests for data.loader (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.data import column_values, complete_cases, load_csv, parse_value  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestLoadCsv(unittest.TestCase):
    """Reading the CSV file."""

    def test_reads_every_row_as_strings(self):
        """A temporary 3-row CSV -> 3 dicts with string values."""
        self.skipTest(NOT_WRITTEN)

    def test_missing_file_raises(self):
        """A path that does not exist -> FileNotFoundError."""
        self.skipTest(NOT_WRITTEN)


class TestParseValue(unittest.TestCase):
    """Converting one raw value."""

    def test_number_becomes_float(self):
        """'8.3' -> 8.3."""
        self.skipTest(NOT_WRITTEN)

    def test_blank_unparsable_and_non_finite_become_none(self):
        """'', 'abc', 'nan', 'inf' -> None."""
        self.skipTest(NOT_WRITTEN)


class TestCompleteCases(unittest.TestCase):
    """Excluding rows with missing values."""

    def test_row_with_blank_value_is_excluded(self):
        """A row with '' in median_income is not in the result."""
        self.skipTest(NOT_WRITTEN)

    def test_all_complete_rows_kept_in_order(self):
        """Three complete rows -> [0, 1, 2]."""
        self.skipTest(NOT_WRITTEN)


class TestColumnValues(unittest.TestCase):
    """Extracting one column."""

    def test_values_follow_index_order(self):
        """indices [2, 0] -> [value of row 2, value of row 0]."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
