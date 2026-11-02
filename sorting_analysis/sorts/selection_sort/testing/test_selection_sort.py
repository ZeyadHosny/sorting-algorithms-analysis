"""Unit tests for selection sort (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import selection_sort  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestSelectionSort(unittest.TestCase):
    """Correctness and counts."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged."""
        self.skipTest(NOT_WRITTEN)

    def test_comparisons_do_not_depend_on_order(self):
        """Any input with n = 5 -> 10 comparisons."""
        self.skipTest(NOT_WRITTEN)

    def test_sorted_input_needs_no_writes(self):
        """[1, 2, 3] -> 0 swaps, 0 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_small_example(self):
        """[3, 1, 2] -> 2 swaps, 4 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[], [7] and lists with duplicates sort correctly."""
        self.skipTest(NOT_WRITTEN)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
