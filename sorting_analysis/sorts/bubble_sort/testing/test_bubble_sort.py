"""Unit tests for bubble sort, plain and counted (drafts: each test is skipped until it is written)."""
import random
import unittest

from sorting_analysis.sorts import bubble_sort, counted_bubble_sort  # noqa: F401
from sorting_analysis.sorts.common.testing import logged_values  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestBubbleSort(unittest.TestCase):
    """Plain version (timed): correctness only."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        values = [3, 1, 2]
        original = values[:]

        result = bubble_sort(values)

        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_edge_cases(self):
        """[] -> [], [7] -> [7] (new lists); lists with duplicates sort correctly."""
        for values in ([], [7], [3, 1, 3, 2, 1], [4, 4, 4], [-2, 1.5, 0, -2]):
            with self.subTest(values=values):
                original = values[:]
                result = bubble_sort(values)
                self.assertEqual(result, sorted(original))
                self.assertEqual(values, original)
                self.assertIsNot(result, values)

    def test_matches_sorted_on_random_input(self):
        """100 seeded random values -> same as sorted()."""
        generator = random.Random(42)
        values = [generator.uniform(-100, 100) for index in range(100)]
        original = values[:]

        self.assertEqual(bubble_sort(values), sorted(original))
        self.assertEqual(values, original)


class TestCountedBubbleSort(unittest.TestCase):
    """Counted version: correctness, counts and early termination (full passes, as in the lecture)."""

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged."""
        values = [3, 1, 2]
        original = values[:]

        result, stats = counted_bubble_sort(values)

        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_counts_small_example(self):
        """[3, 1, 2] -> 4 comparisons (2 full passes), 2 swaps, 4 writes."""
        result, stats = counted_bubble_sort([3, 1, 2])

        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(stats.get_comparisons(), 4)
        self.assertEqual(stats.get_writes(), 4)
        self.assertEqual(stats.get_swaps(), 2)

    def test_sorted_input_stops_after_one_pass(self):
        """[1, 2, 3, 4, 5] -> 4 comparisons, 0 swaps, 0 writes."""
        result, stats = counted_bubble_sort([1, 2, 3, 4, 5])

        self.assertEqual(result, [1, 2, 3, 4, 5])
        self.assertEqual(stats.get_comparisons(), 4)
        self.assertEqual(stats.get_writes(), 0)
        self.assertEqual(stats.get_swaps(), 0)

    def test_reversed_input_worst_case(self):
        """[5, 4, 3, 2, 1] -> 20 comparisons (5 full passes x 4), 10 swaps, 20 writes."""
        result, stats = counted_bubble_sort([5, 4, 3, 2, 1])

        self.assertEqual(result, [1, 2, 3, 4, 5])
        self.assertEqual(stats.get_comparisons(), 20)
        self.assertEqual(stats.get_writes(), 20)
        self.assertEqual(stats.get_swaps(), 10)

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons, 0 writes, 0 swaps; equal neighbours are never swapped."""
        cases = (([], 0, 0, 0), ([7], 0, 0, 0), ([4, 4, 4], 2, 0, 0),
                 ([2, 1, 2, 1], 9, 6, 3))
        for values, comparisons, writes, swaps in cases:
            with self.subTest(values=values):
                original = values[:]
                result, stats = counted_bubble_sort(values)
                self.assertEqual(result, sorted(original))
                self.assertEqual(stats.get_comparisons(), comparisons)
                self.assertEqual(stats.get_writes(), writes)
                self.assertEqual(stats.get_swaps(), swaps)
                self.assertEqual(values, original)
                self.assertIsNot(result, values)

    def test_counts_are_reproducible(self):
        """Two runs on the same input -> the same comparisons, writes and swaps."""
        values = [3, 1, 2, 1, -2]
        first_result, first_stats = counted_bubble_sort(values)
        second_result, second_stats = counted_bubble_sort(values)

        self.assertEqual(first_result, second_result)
        self.assertEqual(first_stats.get_comparisons(), second_stats.get_comparisons())
        self.assertEqual(first_stats.get_writes(), second_stats.get_writes())
        self.assertEqual(first_stats.get_swaps(), second_stats.get_swaps())


class TestSameAlgorithm(unittest.TestCase):
    """The plain and counted versions run the same algorithm."""

    def test_same_comparisons_as_plain(self):
        """On logged_values of sorted, reversed, duplicated and seeded random lists, both versions log the
        same comparison sequence, and its length equals the counted comparisons."""
        generator = random.Random(42)
        cases = ([], [7], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1], [2, 1, 2, 1],
                 [4, 4, 4], [generator.randint(-10, 10) for index in range(30)])
        for values in cases:
            with self.subTest(values=values):
                plain_log = []
                counted_log = []
                plain_result = bubble_sort(logged_values(values, plain_log))
                counted_result, stats = counted_bubble_sort(logged_values(values, counted_log))

                self.assertEqual(plain_log, counted_log)
                self.assertEqual(len(counted_log), stats.get_comparisons())
                self.assertEqual([value.get_number() for value in plain_result], sorted(values))
                self.assertEqual([value.get_number() for value in counted_result], sorted(values))

    def test_same_output_as_plain(self):
        """Both versions return equal lists on the same inputs."""
        generator = random.Random(42)
        cases = ([], [7], [1, 2, 3], [3, 2, 1], [3, 1, 3, 2, 1],
                 [generator.uniform(-10, 10) for index in range(100)])
        for values in cases:
            with self.subTest(values=values):
                original = values[:]
                plain_result = bubble_sort(values)
                counted_result, stats = counted_bubble_sort(values)
                self.assertEqual(plain_result, counted_result)
                self.assertEqual(counted_result, sorted(original))
                self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
