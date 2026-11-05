"""Unit and integration tests for data.orders."""
import random
import unittest
from unittest.mock import patch

from sorting_analysis.data import ascending, descending, make_orders, nearly_sorted  # noqa: F401

# Unit tests supply fixed merge-sort outputs to check Orders independently.
# The integration test below uses the real implementation when available.
class TestOrders(unittest.TestCase):
    """The four input orders."""

    def test_ascending(self):
        """[3, 1, 2] -> [1, 2, 3]."""
        values = [3, 1, 2]
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   return_value=[1, 2, 3]) as merge:
            result = ascending(values)

        merge.assert_called_once_with(values)
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(values, [3, 1, 2])

    def test_descending(self):
        """[1, 2, 3] -> [3, 2, 1]."""
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   return_value=[1, 2, 3]):
            result = descending([1, 2, 3])

        self.assertEqual(result, [3, 2, 1])

    def test_nearly_sorted_applies_one_percent_swaps(self):
        """2000 values -> exactly 20 swaps (at most 40 positions differ from ascending)."""
        ordered_values = list(range(2000))
        values = ordered_values[::-1]
        generator = random.Random(44)

        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   return_value=ordered_values[:]), \
             patch('sorting_analysis.data.orders.implementation.orders.random.Random',
                   return_value=generator), \
             patch.object(generator, 'sample', wraps=generator.sample) as draw:
            result = nearly_sorted(values, 44)

        self.assertEqual(draw.call_count, 20)
        for call in draw.call_args_list:
            self.assertEqual(call.args, (range(2000), 2))

        expected = ordered_values[:]
        reference_generator = random.Random(44)
        for swap_number in range(20):
            first, second = reference_generator.sample(range(2000), 2)
            self.assertNotEqual(first, second)
            expected[first], expected[second] = expected[second], expected[first]

        self.assertEqual(result, expected)
        self.assertCountEqual(result, values)
        displaced = sum(result[index] != ordered_values[index] for index in range(2000))
        self.assertLessEqual(displaced, 40)
        self.assertEqual(values, ordered_values[::-1])

    def test_nearly_sorted_is_reproducible(self):
        """Same seed -> same list."""
        values = list(range(200))[::-1]
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   side_effect=lambda values: list(range(200))):
            first = nearly_sorted(values, 44)
            nearly_sorted(values, 99)
            second = nearly_sorted(values, 44)

        self.assertEqual(first, second)

    def test_random_order_is_returned_unchanged(self):
        """make_orders([3, 1, 2], 44)['random'] == [3, 1, 2]."""
        values = [3, 1, 2]
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   side_effect=lambda values: [1, 2, 3]):
            result = make_orders(values, 44)

        self.assertEqual(result['random'], [3, 1, 2])
        self.assertIsNot(result['random'], values)

    def test_all_orders_hold_the_same_values(self):
        """All four lists are permutations of the input."""
        values = [3, 1, 3, 2, 1]
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   side_effect=lambda values: [1, 1, 2, 3, 3]):
            result = make_orders(values, 44)

        self.assertEqual(set(result), {'random', 'sorted', 'reversed', 'nearly'})
        for order_values in result.values():
            self.assertCountEqual(order_values, values)
        self.assertEqual(result['sorted'], [1, 1, 2, 3, 3])
        self.assertEqual(result['reversed'], [3, 3, 2, 1, 1])
        self.assertEqual(result['nearly'], [1, 1, 2, 3, 3])

    def test_input_is_not_modified(self):
        """The input list is equal before and after make_orders."""
        values = [3, 1, 2]
        original = values[:]
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   side_effect=lambda values: [1, 2, 3]):
            for function in (ascending, descending):
                output = function(values)
                self.assertEqual(values, original)
                self.assertIsNot(output, values)
            output = nearly_sorted(values, 44)
            self.assertEqual(values, original)
            self.assertIsNot(output, values)
            result = make_orders(values, 44)

        self.assertEqual(values, original)
        outputs = list(result.values())
        for index, output in enumerate(outputs):
            self.assertIsNot(output, values)
            for other in outputs[index + 1:]:
                self.assertIsNot(output, other)
        result['random'][0] = -100
        self.assertEqual(values, original)
        self.assertEqual(result['sorted'], [1, 2, 3])


class TestOrdersEdgeCases(unittest.TestCase):
    """Short inputs and isolated random state."""

    # Check the number of swaps around multiples of one hundred
    def test_swap_count_boundaries(self):
        """Sizes 0, 1, 99, 100, 199 and 200 make 0, 0, 0, 1, 1 and 2 draws."""
        for size, expected_count in ((0, 0), (1, 0), (99, 0), (100, 1), (199, 1), (200, 2)):
            with self.subTest(size=size):
                ordered_values = list(range(size))
                generator = random.Random(44)
                with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                           return_value=ordered_values[:]), \
                     patch('sorting_analysis.data.orders.implementation.orders.random.Random',
                           return_value=generator), \
                     patch.object(generator, 'sample', wraps=generator.sample) as draw:
                    result = nearly_sorted(ordered_values[::-1], 44)
                self.assertEqual(draw.call_count, expected_count)
                self.assertCountEqual(result, ordered_values)

    # Check that seeded swaps do not change the module-level generator
    def test_global_random_state_is_unchanged(self):
        """Nearly sorted generation leaves the global random state unchanged."""
        before = random.getstate()
        with patch('sorting_analysis.data.orders.implementation.orders.merge_sort',
                   return_value=list(range(200))):
            nearly_sorted(list(range(200))[::-1], 44)
        self.assertEqual(random.getstate(), before)


class TestOrdersIntegration(unittest.TestCase):
    """Connect Orders to the actual merge sort without a substitute."""

    # Check the completed Orders and Merge Sort modules together
    def test_orders_with_real_merge_sort(self):
        """Real merge sort produces correct orders; skip only while it is unimplemented."""
        try:
            probe = ascending([3, 1, 2])
        except NotImplementedError:
            self.skipTest('Waiting for the real merge_sort implementation; unit tests run separately.')
        self.assertEqual(probe, [1, 2, 3])

        for values in ([], [2], [3, 1, 3, 2, 1], list(range(200))[::-1]):
            with self.subTest(size=len(values)):
                original = values[:]
                result = make_orders(values, 44)
                expected = sorted(values)
                self.assertEqual(result['random'], original)
                self.assertEqual(result['sorted'], expected)
                self.assertEqual(result['reversed'], expected[::-1])
                for output in result.values():
                    self.assertEqual(sorted(output), expected)
                    self.assertIsNot(output, values)
                self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
