"""Unit tests for data.inspection."""
import unittest
from sorting_analysis.data import INSPECTION_FIELDS

from sorting_analysis.data import duplicate_stats, inspect_data  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestInspectData(unittest.TestCase):
    """Rows, missing and distinct values per column."""

    def test_counts_rows_missing_and_distinct(self):
        """3 rows, one blank median_income -> rows 3, missing 1, distinct = number of different values."""
        rows = [
            {"median_income": "3.5", "housing_median_age": "20"},
            {"median_income": "", "housing_median_age": "30"},
            {"median_income": "3.5", "housing_median_age": "40"},
        ]
        columns = ("median_income", "housing_median_age")

        self.assertEqual(inspect_data(rows, columns), [
            {"column": "median_income", "rows": 3, "missing": 1,
             "distinct": 1, "excluded_rows": 1},
            {"column": "housing_median_age", "rows": 3, "missing": 0,
             "distinct": 3, "excluded_rows": 1},
        ])

        for raw_value in ("abc", "nan", "inf", "-inf", None, "   "):
            with self.subTest(raw_value=raw_value):
                result = inspect_data([{"median_income": raw_value}], ("median_income",))
                self.assertEqual(result[0]["missing"], 1)
                self.assertEqual(result[0]["distinct"], 0)
                self.assertEqual(result[0]["excluded_rows"], 1)

    def test_excluded_rows_counts_any_missing_selected_value(self):
        """Blank values in two different rows -> excluded_rows 2 on every column."""
        rows = [
            {"median_income": "", "housing_median_age": "20"},
            {"median_income": "3.0", "housing_median_age": ""},
            {"median_income": "4.0", "housing_median_age": "40"},
        ]

        results = inspect_data(rows, ("median_income", "housing_median_age"))

        for result in results:
            self.assertEqual(result["rows"], 3)
            self.assertEqual(result["missing"], 1)
            self.assertEqual(result["distinct"], 2)
            self.assertEqual(result["excluded_rows"], 2)

        self.assertEqual(rows[0]["median_income"], "")
        self.assertEqual(rows[1]["median_income"], "3.0")

    def test_returns_one_result_per_column(self):
        """3 columns -> 3 dicts with the INSPECTION_FIELDS keys."""
        columns = ("median_house_value", "median_income", "housing_median_age")
        rows = [{"median_income": "3.5", "housing_median_age": "20",
                 "median_house_value": "500001"}]

        results = inspect_data(rows, columns)

        self.assertEqual(len(results), 3)
        for index in range(len(columns)):
            self.assertEqual(results[index]["column"], columns[index])
            self.assertEqual(set(results[index]), set(INSPECTION_FIELDS))


class TestDuplicateStats(unittest.TestCase):
    """Duplication statistics."""

    def test_worked_example(self):
        """[1, 1, 2, 3, 3, 3] -> n 6, distinct 3, modal_value 3, modal_count 3, repeated_distinct 2, repeated_observations 5."""
        values = [1, 1, 2, 3, 3, 3]

        self.assertEqual(duplicate_stats(values), {
            "sample_size": 6,
            "distinct": 3,
            "modal_value": 3,
            "modal_count": 3,
            "repeated_distinct": 2,
            "repeated_observations": 5,
        })
        self.assertEqual(values, [1, 1, 2, 3, 3, 3])

    def test_no_duplicates(self):
        """[1, 2, 3] -> repeated_distinct 0, repeated_observations 0."""
        self.assertEqual(duplicate_stats([1, 2, 3]), {
            "sample_size": 3,
            "distinct": 3,
            "modal_value": 1,
            "modal_count": 1,
            "repeated_distinct": 0,
            "repeated_observations": 0,
        })


class TestInspectionEdgeCases(unittest.TestCase):
    """Check empty inputs, frequency ties and an all-equal sample."""

    # Check that requested columns are still reported for an empty dataset
    def test_empty_dataset(self):
        """Empty rows produce zero counts for each selected column."""
        self.assertEqual(inspect_data([], ("median_income",)), [
            {"column": "median_income", "rows": 0, "missing": 0,
             "distinct": 0, "excluded_rows": 0}
        ])
        self.assertEqual(inspect_data([], ()), [])

    # Check the explicit result when no mode exists
    def test_empty_sample(self):
        """An empty sample has zero counts and modal_value None."""
        self.assertEqual(duplicate_stats([]), {
            "sample_size": 0, "distinct": 0, "modal_value": None,
            "modal_count": 0, "repeated_distinct": 0,
            "repeated_observations": 0,
        })

    # Check the deterministic tie convention
    def test_frequency_tie_keeps_first_value(self):
        """Equal maximum frequencies select the first encountered value."""
        result = duplicate_stats([5, 2, 2, 5])
        self.assertEqual(result["modal_value"], 5)
        self.assertEqual(result["modal_count"], 2)
        self.assertEqual(result["repeated_distinct"], 2)
        self.assertEqual(result["repeated_observations"], 4)

    # Check that repeated observations include every occurrence of a repeated value
    def test_all_values_equal(self):
        """Three equal values give one repeated distinct value and three observations."""
        self.assertEqual(duplicate_stats([7, 7, 7]), {
            "sample_size": 3, "distinct": 1, "modal_value": 7,
            "modal_count": 3, "repeated_distinct": 1,
            "repeated_observations": 3,
        })


if __name__ == "__main__":
    unittest.main()
