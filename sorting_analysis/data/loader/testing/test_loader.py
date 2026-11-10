"""Unit tests for CSV loading, numeric conversion and row selection."""

import os
import tempfile
import unittest

from sorting_analysis.data import column_values, complete_cases, load_csv, parse_value


class TestLoadCsv(unittest.TestCase):
    """Check how CSV files are read."""

    # Check row count, dictionary keys and raw string values
    def test_reads_every_row_as_strings(self):
        """A three-row CSV produces three dictionaries with string values."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "housing.csv")

            with open(path, "w", newline="", encoding="utf-8") as file:
                file.write("median_income,housing_median_age\n")
                file.write("8.3252,41\n7.2574,21\n3.5,30\n")

            rows = load_csv(path)

        self.assertEqual(len(rows), 3)
        self.assertEqual(
            rows[0],
            {"median_income": "8.3252", "housing_median_age": "41"}
        )

        for row in rows:
            for value in row.values():
                self.assertIsInstance(value, str)

    # Check that missing files are reported to the caller
    def test_missing_file_raises(self):
        """A path that does not exist raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "missing.csv")

            with self.assertRaises(FileNotFoundError):
                load_csv(path)

    # Check CSV quoting and preservation of blank cells
    def test_quoted_field_and_blank_cell(self):
        """A comma inside quotes stays in one field; a blank cell stays blank."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "small.csv")

            with open(path, "w", newline="", encoding="utf-8") as file:
                file.write('label,income\n"Block, A",3.5\nBlock B,\n')

            rows = load_csv(path)

        self.assertEqual(rows[0], {"label": "Block, A", "income": "3.5"})
        self.assertEqual(rows[1], {"label": "Block B", "income": ""})

    # Check a valid CSV containing only column names
    def test_header_only_returns_empty_list(self):
        """A header-only CSV contains no data rows and returns an empty list."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "empty.csv")

            with open(path, "w", newline="", encoding="utf-8") as file:
                file.write("median_income,housing_median_age\n")

            self.assertEqual(load_csv(path), [])


class TestParseValue(unittest.TestCase):
    """Check numeric conversion and the missing-value rule."""

    # Check ordinary numbers, surrounding spaces, zero and exponent notation
    def test_number_becomes_float(self):
        """Valid numeric text becomes a finite float, including zero."""
        examples = [("8.3", 8.3), (" -2.5 ", -2.5), ("0", 0.0), ("1e3", 1000.0)]

        for raw_value, expected in examples:
            with self.subTest(raw_value=raw_value):
                actual = parse_value(raw_value)
                self.assertEqual(actual, expected)
                self.assertIsInstance(actual, float)

    # Check every form of missing value
    def test_blank_unparsable_and_non_finite_become_none(self):
        """Blank, absent, invalid, NaN and infinite values return None."""
        examples = ["", "   ", None, "abc", "nan", "NaN", "inf", "-inf", "1e309"]

        for raw_value in examples:
            with self.subTest(raw_value=raw_value):
                self.assertIsNone(parse_value(raw_value))


class TestCompleteCases(unittest.TestCase):
    """Check that only rows valid in every selected column are retained."""

    # Check invalid values in different selected columns
    def test_row_with_blank_value_is_excluded(self):
        """A blank, invalid or absent selected cell excludes its row."""
        rows = [
            {"income": "3.5", "age": "20"},
            {"income": "", "age": "30"},
            {"income": "4.2", "age": "nan"},
            {"income": "5.0"},
            {"income": "0", "age": "0"},
        ]

        self.assertEqual(complete_cases(rows, ("income", "age")), [0, 4])

    # Check original row order, duplicate retention and unchanged raw data
    def test_all_complete_rows_kept_in_order(self):
        """Complete rows, including duplicates, retain their order and contents."""
        rows = [{"income": "3.5"}, {"income": "3.5"}, {"income": "7.2"}]
        expected_rows = [{"income": "3.5"}, {"income": "3.5"}, {"income": "7.2"}]

        self.assertEqual(complete_cases(rows, ("income",)), [0, 1, 2])
        self.assertEqual(rows, expected_rows)
        self.assertEqual(complete_cases([], ("income",)), [])


class TestColumnValues(unittest.TestCase):
    """Check ordered extraction and failure on invalid requested cells."""

    # Check the requested order rather than the original CSV order
    def test_values_follow_index_order(self):
        """Indices [2, 0, 1] preserve their order and keep duplicate values."""
        rows = [{"income": "8.3"}, {"income": "8.3"}, {"income": "4.2"}]

        self.assertEqual(column_values(rows, "income", [2, 0, 1]), [4.2, 8.3, 8.3])
        self.assertEqual(column_values(rows, "income", []), [])
        self.assertEqual(rows[0]["income"], "8.3")

    # Prevent silently shortening an experimental input
    def test_invalid_requested_value_raises(self):
        """An invalid requested cell raises ValueError instead of being skipped."""
        rows = [{"income": "3.5"}, {"income": ""}]

        with self.assertRaises(ValueError):
            column_values(rows, "income", [0, 1])


if __name__ == "__main__":
    unittest.main()
