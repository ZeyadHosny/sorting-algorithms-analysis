"""Unit tests for selection sort, plain and counted (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import counted_selection_sort, selection_sort  # noqa: F401
from sorting_analysis.sorts.common.testing import logged_values  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestSelectionSort(unittest.TestCase):
    """Plain version (timed): correctness only."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[] -> [], [7] -> [7] (new lists); lists with duplicates sort correctly."""
        self.skipTest(NOT_WRITTEN)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        self.skipTest(NOT_WRITTEN)


class TestCountedSelectionSort(unittest.TestCase):
    """Counted version: correctness and counts."""

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
        """[3, 1, 2] -> 3 comparisons, 2 swaps, 4 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_at_most_one_swap_per_position(self):
        """n values -> at most n - 1 swaps."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons; lists with duplicates sort correctly."""
        self.skipTest(NOT_WRITTEN)


class TestSameAlgorithm(unittest.TestCase):
    """The plain and counted versions run the same algorithm."""

    def test_same_comparisons_as_plain(self):
        """On logged_values of sorted, reversed, duplicated and seeded random lists, both versions log the
        same comparison sequence, and its length equals the counted comparisons."""
        self.skipTest(NOT_WRITTEN)

    def test_same_output_as_plain(self):
        """Both versions return equal lists on the same inputs."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
