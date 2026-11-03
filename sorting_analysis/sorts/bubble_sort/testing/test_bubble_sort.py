"""Unit tests for bubble sort, plain and counted (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import bubble_sort, counted_bubble_sort  # noqa: F401
from sorting_analysis.sorts.common.testing import logged_values  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestBubbleSort(unittest.TestCase):
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


class TestCountedBubbleSort(unittest.TestCase):
    """Counted version: correctness, counts and early termination (full passes, as in the lecture)."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_small_example(self):
        """[3, 1, 2] -> 4 comparisons (2 full passes), 2 swaps, 4 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_sorted_input_stops_after_one_pass(self):
        """[1, 2, 3, 4, 5] -> 4 comparisons, 0 swaps, 0 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_reversed_input_worst_case(self):
        """[5, 4, 3, 2, 1] -> 20 comparisons (5 full passes x 4), 10 swaps, 20 writes."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons, 0 writes, 0 swaps; equal neighbours are never swapped."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_are_reproducible(self):
        """Two runs on the same input -> the same comparisons, writes and swaps."""
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
