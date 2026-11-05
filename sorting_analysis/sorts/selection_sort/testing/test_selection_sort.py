"""Unit tests for selection sort, plain and counted."""
import random
import unittest

from sorting_analysis.sorts import counted_selection_sort, selection_sort
from sorting_analysis.sorts import logged_values


class TestSelectionSort(unittest.TestCase):
    """Plain version: correct output, input unchanged, new list."""

    # Method to check one input: sorted output, input unchanged, a new list returned
    def check_sorts(self, values):
        """
        Description:
        - Sort values and compare the result with sorted() (used only to verify).

        Input arguments:
           values (list[float]): Input to sort.

        Return:
            None (fails the test on a wrong result)
        """
        original = values[:]
        result = selection_sort(values)
        self.assertEqual(result, sorted(original))
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        values = [3, 1, 2]
        self.assertEqual(selection_sort(values), [1, 2, 3])
        self.assertEqual(values, [3, 1, 2])
        self.check_sorts(values)

    def test_empty_and_single_value(self):
        """[] -> [] and [7] -> [7], each a new list."""
        self.check_sorts([])
        self.check_sorts([7])

    def test_two_values(self):
        """[2, 1] -> [1, 2] and [1, 2] -> [1, 2]: the smallest inputs where a swap can or cannot happen."""
        self.check_sorts([2, 1])
        self.check_sorts([1, 2])

    def test_sorted_and_reversed_input(self):
        """[1, 2, 3, 4, 5] and [5, 4, 3, 2, 1] -> [1, 2, 3, 4, 5]."""
        self.check_sorts([1, 2, 3, 4, 5])
        self.check_sorts([5, 4, 3, 2, 1])

    def test_duplicates_negatives_and_floats(self):
        """Repeated values, negative numbers and floats sort correctly."""
        self.check_sorts([2, 2, 1, 1, 3, 3])
        self.check_sorts([0.5, -2.0, 0.5, 3.25, -2.0])
        self.check_sorts([4, 4, 4, 4])

    def test_equal_values_keep_their_order(self):
        """Equal values found later never replace the first one as the minimum (strict <)."""
        log = []
        values = logged_values([2, 1, 1], log)
        result = selection_sort(values)
        self.assertEqual([value.get_number() for value in result], [1, 1, 2])
        self.assertIs(result[0], values[1])

    def test_matches_sorted_on_random_input(self):
        """300 seeded random lists (sizes 0-60, some with many repeats) -> same as sorted()."""
        generator = random.Random(1)
        for _ in range(200):
            self.check_sorts([generator.uniform(-100, 100) for _ in range(generator.randint(0, 60))])
        for _ in range(100):
            self.check_sorts([generator.randint(0, 3) for _ in range(generator.randint(0, 60))])

    def test_experiment_size(self):
        """2,000 seeded random values (the input-order sample size) -> same as sorted()."""
        generator = random.Random(2)
        self.check_sorts([generator.uniform(0.5, 15.0) for _ in range(2000)])

    def test_comparisons_are_n_times_n_minus_1_over_2(self):
        """Sorted, reversed and random inputs of n = 1, 2, 5, 50 -> exactly n(n - 1)/2 comparisons, all '<'."""
        generator = random.Random(3)
        for size in (1, 2, 5, 50):
            for numbers in (list(range(size)), list(range(size, 0, -1)),
                            [generator.uniform(0, 1) for _ in range(size)]):
                log = []
                selection_sort(logged_values(numbers, log))
                self.assertEqual(len(log), size * (size - 1) // 2)
                self.assertTrue(all(entry[0] == "<" for entry in log))


class TestCountedSelectionSort(unittest.TestCase):
    """Counted version: correct output and the counting rules."""

    # Method to sort values with the counted version and return its counts
    def counts(self, values):
        """
        Description:
        - Run counted_selection_sort and read its SortStats.

        Input arguments:
           values (list[float]): Input to sort.

        Return:
            tuple: (comparisons, writes, swaps), e.g. [3, 1, 2] -> (3, 4, 2).
        """
        _, sort_stats = counted_selection_sort(values)
        return sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        values = [3, 1, 2]
        result, _ = counted_selection_sort(values)
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(values, [3, 1, 2])
        self.assertIsNot(result, values)

    def test_counts_small_example(self):
        """[3, 1, 2] -> 3 comparisons, 4 writes, 2 swaps."""
        self.assertEqual(self.counts([3, 1, 2]), (3, 4, 2))

    def test_counts_reversed_example(self):
        """[5, 4, 3, 2, 1] -> 10 comparisons, 4 writes, 2 swaps (5 <-> 1, 4 <-> 2; 3 is already in place)."""
        self.assertEqual(self.counts([5, 4, 3, 2, 1]), (10, 4, 2))

    def test_comparisons_do_not_depend_on_order(self):
        """Sorted, reversed, all-equal and random inputs of n = 5 and n = 2000 -> n(n - 1)/2 comparisons."""
        generator = random.Random(4)
        for size in (5, 2000):
            for values in (list(range(size)), list(range(size, 0, -1)), [7] * size,
                           [generator.uniform(0, 1) for _ in range(size)]):
                self.assertEqual(self.counts(values)[0], size * (size - 1) // 2)

    def test_values_in_place_are_never_swapped(self):
        """[1, 2, 3, 4, 5] and [4, 4, 4, 4] -> 0 swaps, 0 writes."""
        self.assertEqual(self.counts([1, 2, 3, 4, 5]), (10, 0, 0))
        self.assertEqual(self.counts([4, 4, 4, 4]), (6, 0, 0))

    def test_swap_is_two_writes_and_at_most_one_per_position(self):
        """300 seeded random lists -> writes == 2 * swaps and swaps <= n - 1; output equals sorted()."""
        generator = random.Random(5)
        for _ in range(300):
            values = [generator.randint(0, 9) for _ in range(generator.randint(0, 60))]
            result, sort_stats = counted_selection_sort(values)
            self.assertEqual(result, sorted(values))
            self.assertEqual(sort_stats.get_writes(), 2 * sort_stats.get_swaps())
            self.assertLessEqual(sort_stats.get_swaps(), max(len(values) - 1, 0))

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons, 0 writes, 0 swaps; [2, 1] -> 1 comparison, 2 writes, 1 swap."""
        self.assertEqual(self.counts([]), (0, 0, 0))
        self.assertEqual(self.counts([7]), (0, 0, 0))
        self.assertEqual(self.counts([2, 1]), (1, 2, 1))

    def test_counts_are_reproducible(self):
        """Two runs on the same 2,000 random values -> the same comparisons, writes and swaps."""
        generator = random.Random(6)
        values = [generator.uniform(0.5, 15.0) for _ in range(2000)]
        self.assertEqual(self.counts(values), self.counts(values))


class TestSameAlgorithm(unittest.TestCase):
    """The plain and counted versions run the same algorithm."""

    # Method to build the inputs shared by both checks
    def inputs(self):
        """
        Description:
        - Sorted, reversed, duplicated and seeded random lists.

        Input arguments:
           None

        Return:
            list[list[float]]: the input lists.
        """
        generator = random.Random(7)
        lists = [[], [7], [2, 1], list(range(20)), list(range(20, 0, -1)), [3, 1, 3, 1, 2, 2]]
        lists += [[generator.randint(0, 5) for _ in range(30)] for _ in range(20)]
        lists += [[generator.uniform(-10, 10) for _ in range(40)] for _ in range(20)]
        return lists

    def test_same_comparisons_as_plain(self):
        """Both versions log the same comparison sequence, and its length equals the counted comparisons."""
        for numbers in self.inputs():
            plain_log, counted_log = [], []
            selection_sort(logged_values(numbers, plain_log))
            _, sort_stats = counted_selection_sort(logged_values(numbers, counted_log))
            self.assertEqual(plain_log, counted_log)
            self.assertEqual(len(counted_log), sort_stats.get_comparisons())

    def test_same_output_as_plain(self):
        """Both versions return equal lists on the same inputs."""
        for numbers in self.inputs():
            self.assertEqual(selection_sort(numbers), counted_selection_sort(numbers)[0])


if __name__ == "__main__":
    unittest.main()
