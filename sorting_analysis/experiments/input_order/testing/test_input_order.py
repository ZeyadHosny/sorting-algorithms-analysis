"""Unit tests for experiments.input_order (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.experiments import run_input_order  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestRunInputOrder(unittest.TestCase):
    """Run on a small CSV with small Settings."""

    def test_twelve_cases(self):
        """3 algorithms x 4 orders -> 12 cases."""
        self.skipTest(NOT_WRITTEN)

    def test_bubble_on_sorted_input(self):
        """Sorted input of 10 values -> 9 bubble comparisons."""
        self.skipTest(NOT_WRITTEN)

    def test_selection_comparisons_fixed(self):
        """Every order of 10 values -> 45 selection comparisons."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
