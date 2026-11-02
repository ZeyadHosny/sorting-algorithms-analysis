"""Unit tests for bubble sort (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import bubble_sort  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestBubbleSort(unittest.TestCase):
    """Correctness, counts and early termination."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_small_example(self):
        """[3, 1, 2] -> 3 comparisons, 2 swaps, 4 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_sorted_input_stops_after_one_pass(self):
        """[1, 2, 3, 4, 5] -> 4 comparisons, 0 swaps, 0 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_reversed_input_worst_case(self):
        """[5, 4, 3, 2, 1] -> 10 comparisons, 10 swaps, 20 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[], [7] and lists with duplicates sort correctly; [] -> 0 comparisons."""
        self.skipTest(NOT_WRITTEN)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_are_reproducible(self):
        """Two runs on the same input -> identical SortStats."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
