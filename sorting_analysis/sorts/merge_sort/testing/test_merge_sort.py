"""Unit tests for merge sort, plain and counted."""
import math
import random
import unittest

from sorting_analysis.sorts import counted_merge_sort, logged_values, merge_sort


class TestMergeSort(unittest.TestCase):
    """Plain version: correct output, input unchanged, new list, ties."""

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
        result = merge_sort(values)
        self.assertEqual(result, sorted(original))
        self.assertEqual(values, original)
        self.assertIsNot(result, values)

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        values = [3, 1, 2]
        self.assertEqual(merge_sort(values), [1, 2, 3])
        self.assertEqual(values, [3, 1, 2])
        self.check_sorts(values)

    def test_empty_and_single_value(self):
        """[] -> [] and [7] -> [7], each a new list."""
        self.check_sorts([])
        self.check_sorts([7])

    def test_two_values(self):
        """[2, 1] -> [1, 2] and [1, 2] -> [1, 2]."""
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

    def test_ties_take_left_first(self):
        """Equal values keep their left-before-right order: [2a, 1a, 2b, 1b] -> [1a, 1b, 2a, 2b]."""
        log = []
        values = logged_values([2, 1, 2, 1], log)
        result = merge_sort(values)
        self.assertEqual([value.get_number() for value in result], [1, 1, 2, 2])
        for result_value, expected_value in zip(result, [values[1], values[3], values[0], values[2]]):
            self.assertIs(result_value, expected_value)

    def test_ties_keep_order_on_many_duplicates(self):
        """200 values drawn from 0-3 -> output equals sorted(); equal values appear in their original order."""
        generator = random.Random(8)
        log = []
        numbers = [generator.randint(0, 3) for _ in range(200)]
        values = logged_values(numbers, log)
        result = merge_sort(values)
        self.assertEqual([value.get_number() for value in result], sorted(numbers))
        for number in range(4):
            originals = [id(value) for value in values if value.get_number() == number]
            self.assertEqual([id(value) for value in result if value.get_number() == number], originals)

    def test_matches_sorted_on_random_input(self):
        """300 seeded random lists (sizes 0-80, some with many repeats) -> same as sorted()."""
        generator = random.Random(1)
        for _ in range(200):
            self.check_sorts([generator.uniform(-100, 100) for _ in range(generator.randint(0, 80))])
        for _ in range(100):
            self.check_sorts([generator.randint(0, 3) for _ in range(generator.randint(0, 80))])

    def test_experiment_size(self):
        """4,000 seeded random values (the largest scaling size) -> same as sorted()."""
        generator = random.Random(2)
        self.check_sorts([generator.uniform(0.5, 15.0) for _ in range(4000)])

    def test_comparisons_use_left_first_rule(self):
        """Every comparison is left <= right; sorted input of n = 4, 8, 1024 -> exactly n/2 * log2(n)."""
        for size in (4, 8, 1024):
            log = []
            merge_sort(logged_values(list(range(size)), log))
            self.assertTrue(all(entry[0] == "<=" for entry in log))
            self.assertEqual(len(log), size // 2 * int(math.log2(size)))

    def test_comparisons_stay_within_n_log_n(self):
        """Random inputs of n = 1 - 300 -> at most n * ceil(log2 n) - n + 1 comparisons."""
        generator = random.Random(9)
        for size in range(1, 301):
            log = []
            merge_sort(logged_values([generator.uniform(0, 1) for _ in range(size)], log))
            self.assertLessEqual(len(log), size * math.ceil(math.log2(size)) - size + 1)


class TestCountedMergeSort(unittest.TestCase):
    """Counted version: correct output and the counting rules."""

    # Method to sort values with the counted version and return its counts
    def counts(self, values):
        """
        Description:
        - Run counted_merge_sort and read its SortStats.

        Input arguments:
           values (list[float]): Input to sort.

        Return:
            tuple: (comparisons, writes, swaps), e.g. [2, 1] -> (1, 2, None).
        """
        _, sort_stats = counted_merge_sort(values)
        return sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()

    def test_sorts_and_keeps_input(self):
        """[3, 1, 2] -> [1, 2, 3]; the input list is unchanged and the result is a new list."""
        values = [3, 1, 2]
        result, _ = counted_merge_sort(values)
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(values, [3, 1, 2])
        self.assertIsNot(result, values)

    def test_counts_two_values(self):
        """[2, 1] -> 1 comparison, 2 writes, swaps None."""
        self.assertEqual(self.counts([2, 1]), (1, 2, None))

    def test_counts_four_values(self):
        """[1, 2, 3, 4] -> 4 comparisons, 8 writes (leftover tails included)."""
        self.assertEqual(self.counts([1, 2, 3, 4]), (4, 8, None))

    def test_counts_odd_examples(self):
        """[3, 1, 2] -> 3 comparisons, 5 writes; [5, 4, 3, 2, 1] -> 7 comparisons, 12 writes."""
        self.assertEqual(self.counts([3, 1, 2]), (3, 5, None))
        self.assertEqual(self.counts([5, 4, 3, 2, 1]), (7, 12, None))

    def test_writes_are_n_log2_n_for_powers_of_two(self):
        """n = 2, 8, 1024 in any order -> n * log2(n) writes (each value placed once per merge level)."""
        generator = random.Random(10)
        for size in (2, 8, 1024):
            for values in (list(range(size)), list(range(size, 0, -1)),
                           [generator.uniform(0, 1) for _ in range(size)]):
                self.assertEqual(self.counts(values)[1], size * int(math.log2(size)))

    def test_writes_follow_the_merge_levels_for_every_size(self):
        """n = 1 - 300, sorted and random -> W(n) = W(n // 2) + W(n - n // 2) + n writes, W(0) = W(1) = 0."""
        generator = random.Random(14)
        expected_writes = [0, 0]
        for size in range(2, 301):
            expected_writes.append(expected_writes[size // 2] + expected_writes[size - size // 2] + size)
        for size in range(1, 301):
            self.assertEqual(self.counts(list(range(size)))[1], expected_writes[size])
            self.assertEqual(self.counts([generator.uniform(0, 1) for _ in range(size)])[1], expected_writes[size])

    def test_sorted_and_reversed_input_comparisons(self):
        """Sorted and reversed input of n = 4, 8, 1024 -> n/2 * log2(n) comparisons (each merge empties one half)."""
        for size in (4, 8, 1024):
            expected = size // 2 * int(math.log2(size))
            self.assertEqual(self.counts(list(range(size)))[0], expected)
            self.assertEqual(self.counts(list(range(size, 0, -1)))[0], expected)

    def test_ties_take_left_first(self):
        """[2a, 1a, 2b, 1b] -> [1a, 1b, 2a, 2b]."""
        log = []
        values = logged_values([2, 1, 2, 1], log)
        result, _ = counted_merge_sort(values)
        for result_value, expected_value in zip(result, [values[1], values[3], values[0], values[2]]):
            self.assertIs(result_value, expected_value)

    def test_edge_cases(self):
        """[] and [7] -> 0 comparisons, 0 writes, swaps None; the result is a new list."""
        for values in ([], [7]):
            result, _ = counted_merge_sort(values)
            self.assertEqual(result, values)
            self.assertIsNot(result, values)
            self.assertEqual(self.counts(values), (0, 0, None))

    def test_random_inputs(self):
        """300 seeded random lists -> output equals sorted(); input unchanged; comparisons < writes; swaps None."""
        generator = random.Random(11)
        for _ in range(300):
            values = [generator.randint(0, 9) for _ in range(generator.randint(2, 80))]
            original = values[:]
            result, sort_stats = counted_merge_sort(values)
            self.assertEqual(result, sorted(original))
            self.assertEqual(values, original)
            self.assertIsNot(result, values)
            self.assertLess(sort_stats.get_comparisons(), sort_stats.get_writes())
            self.assertIsNone(sort_stats.get_swaps())

    def test_experiment_size(self):
        """4,000 seeded random values -> output equals sorted(); input unchanged."""
        generator = random.Random(15)
        values = [generator.uniform(0.5, 15.0) for _ in range(4000)]
        original = values[:]
        result, _ = counted_merge_sort(values)
        self.assertEqual(result, sorted(original))
        self.assertEqual(values, original)

    def test_counts_are_reproducible(self):
        """Two runs on the same 2,000 random values -> the same comparisons and writes."""
        generator = random.Random(12)
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
        generator = random.Random(13)
        lists = [[], [7], [2, 1], list(range(20)), list(range(20, 0, -1)), [3, 1, 3, 1, 2, 2]]
        lists += [[generator.randint(0, 5) for _ in range(30)] for _ in range(20)]
        lists += [[generator.uniform(-10, 10) for _ in range(41)] for _ in range(20)]
        return lists

    def test_same_comparisons_as_plain(self):
        """Both versions log the same comparison sequence, and its length equals the counted comparisons."""
        for numbers in self.inputs():
            plain_log, counted_log = [], []
            merge_sort(logged_values(numbers, plain_log))
            _, sort_stats = counted_merge_sort(logged_values(numbers, counted_log))
            self.assertEqual(plain_log, counted_log)
            self.assertEqual(len(counted_log), sort_stats.get_comparisons())

    def test_same_output_as_plain(self):
        """Both versions return equal lists on the same inputs."""
        for numbers in self.inputs():
            self.assertEqual(merge_sort(numbers), counted_merge_sort(numbers)[0])


if __name__ == "__main__":
    unittest.main()
