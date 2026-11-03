"""Unit tests for merge sort, plain and counted (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.sorts import counted_merge_sort, merge_sort  # noqa: F401
from sorting_analysis.sorts.common.testing import logged_values  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestMergeSort(unittest.TestCase):
    """Plain version (timed): correctness and ties."""

    def test_sorts_and_keeps_input(self):
        """[2, 1] -> [1, 2]; the input list is unchanged and the result is a new list."""
        self.skipTest(NOT_WRITTEN)

    def test_ties_take_left_first(self):
        """Equal values keep their left-before-right order (checked by object identity of logged_values)."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[] -> [], [7] -> [7] (new lists); lists with duplicates sort correctly."""
        self.skipTest(NOT_WRITTEN)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        self.skipTest(NOT_WRITTEN)


class TestCountedMergeSort(unittest.TestCase):
    """Counted version: correctness and counts."""

    def test_counts_two_values(self):
        """[2, 1] -> [1, 2], 1 comparison, 2 writes, swaps None."""
        self.skipTest(NOT_WRITTEN)

    def test_counts_four_values(self):
        """[1, 2, 3, 4] -> 4 comparisons, 8 writes (leftover tails included)."""
        self.skipTest(NOT_WRITTEN)

    def test_ties_take_left_first(self):
        """Equal values keep their left-before-right order."""
        self.skipTest(NOT_WRITTEN)

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons, 0 writes; the input is unchanged."""
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
