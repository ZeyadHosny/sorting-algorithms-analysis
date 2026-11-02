"""Unit tests for merge sort (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import merge_sort  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestMergeSort(unittest.TestCase):
    """Correctness, counts and stability."""

    def test_sorts_and_keeps_input(self):
        """[2, 1] -> [1, 2]; the input list is unchanged."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_two_values(self):
        """[2, 1] -> 1 comparison, 2 writes, swaps None."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_four_values(self):
        """[1, 2, 3, 4] -> 4 comparisons, 8 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_ties_take_left_first(self):
        """Equal keys keep their left-before-right order."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[], [7] and lists with duplicates sort correctly."""
        self.skipTest(NOT_WRITTEN)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
