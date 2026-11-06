"""Unit tests for analysis.common.filters."""
import copy
import unittest

from sorting_analysis.analysis import scaling_cases


class TestScalingCases(unittest.TestCase):
    """Selecting scaling rows."""

    def test_keeps_only_scaling_rows(self):
        """input_size 2000 present in scaling, order and dupes -> only the scaling row is kept."""
        scaling_row = {"experiment": "scaling", "algorithm": "bubble", "input_size": 2000}
        order_row = {"experiment": "order", "algorithm": "bubble", "input_size": 2000}
        dupes_row = {"experiment": "dupes", "algorithm": "bubble", "input_size": 2000}
        self.assertEqual(scaling_cases([order_row, scaling_row, dupes_row]), [scaling_row])

    def test_empty_input(self):
        """[] -> []."""
        self.assertEqual(scaling_cases([]), [])

    def test_no_scaling_rows(self):
        """Rows from only order and dupes experiments produce an empty list."""
        rows = [{"experiment": "order", "input_size": 1000},
                {"experiment": "dupes", "input_size": 2000}]
        self.assertEqual(scaling_cases(rows), [])

    def test_keeps_all_scaling_rows_in_original_order_without_changing_input(self):
        """Filtering preserves all scaling algorithms, sizes, repeated rows and their input order."""
        first = {"experiment": "scaling", "algorithm": "merge", "input_size": 2000,
                 "column": "median_income", "order": "random", "median_s": 0.02}
        second = {"experiment": "scaling", "algorithm": "bubble", "input_size": 500,
                  "column": "median_income", "order": "random", "median_s": 0.03}
        third = {"experiment": "scaling", "algorithm": "selection", "input_size": 1000,
                 "column": "median_income", "order": "random", "median_s": 0.04}
        rows = [first, {"experiment": "order", "input_size": 2000}, second,
                {"experiment": "dupes", "input_size": 500}, third, first.copy()]
        before = copy.deepcopy(rows)
        selected = scaling_cases(rows)
        self.assertEqual(selected, [first, second, third, first])
        self.assertEqual(rows, before)
        self.assertIsNot(selected, rows)


if __name__ == "__main__":
    unittest.main()
