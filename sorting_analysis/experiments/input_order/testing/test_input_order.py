"""Unit and integration tests for experiments.input_order."""
import unittest
from unittest.mock import patch

from sorting_analysis.config import Settings
from sorting_analysis.data import column_values, make_orders, sample_indices, shuffle_indices
from sorting_analysis.experiments import ALGORITHMS, run_input_order
from sorting_analysis.sorts import SortStats
from sorting_analysis.timing import TimingResult, VerificationError

# Patch the name used by the experiment, leaving the real timing module unchanged.
BENCHMARK_PATH = 'sorting_analysis.experiments.input_order.implementation.input_order.benchmark'


# Function to supply actual operation counts and placeholder times in unit tests
def benchmark_stub(plain_sort, counted_sort, values, settings):
    """
    Description:
    - Run the actual counted sort, without measuring time.
    - Zero times are test placeholders only; they are never experimental results.

    Input arguments:
       plain_sort (function): Plain sort supplied by the driver.
       counted_sort (function): Counted sort used to obtain operation counts.
       values (list[float]): Values supplied by the experiment.
       settings (Settings): Test settings.

    Return:
        tuple: (TimingResult with placeholder times, actual SortStats).
    """
    _, sort_stats = counted_sort(values)
    repetitions = (settings.small_input_repetitions if len(values) <= settings.small_input_limit
                   else settings.normal_input_repetitions)
    timing = TimingResult((0.0,) * settings.timed_batches, repetitions, 0.0, 0.0, 0.0)
    return timing, sort_stats


class TestRunInputOrder(unittest.TestCase):
    """Run on a small CSV with small Settings."""

    # Method to prepare numeric CSV strings and a small sample size
    def setUp(self):
        """
        Description:
        - Build twelve raw rows and settings that draw ten rows.

        Input arguments:
           None

        Return:
            None
        """
        self.rows = [
            {'median_income': str(index + 1), 'housing_median_age': str(index % 3 + 1),
             'median_house_value': str(100000 if index % 4 == 0 else 500001)}
            for index in range(12)
        ]
        self.usable_indices = list(range(12))
        self.settings = Settings(order_sample_size=10)

    def test_twelve_cases(self):
        """3 algorithms x 4 orders -> 12 cases."""
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
            cases = run_input_order(self.rows, self.usable_indices, self.settings)

        self.assertEqual(len(cases), 12)
        self.assertEqual(measure.call_count, 12)
        expected = {(algorithm, order) for algorithm in ALGORITHMS
                    for order in ('random', 'sorted', 'reversed', 'nearly')}
        self.assertEqual({(case.get_algorithm(), case.get_order()) for case in cases}, expected)
        for case in cases:
            self.assertEqual(case.get_experiment(), 'order')
            self.assertEqual(case.get_column(), self.settings.order_column)
            self.assertEqual(case.get_input_size(), 10)

    def test_bubble_on_sorted_input(self):
        """Sorted input of 10 values -> 9 bubble comparisons."""
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub):
            cases = run_input_order(self.rows, self.usable_indices, self.settings)
        case = next(case for case in cases
                    if case.get_algorithm() == 'bubble' and case.get_order() == 'sorted')
        self.assertEqual(case.get_sort_stats().get_comparisons(), 9)
        self.assertEqual(case.get_sort_stats().get_writes(), 0)
        self.assertEqual(case.get_sort_stats().get_swaps(), 0)

    def test_selection_comparisons_fixed(self):
        """Every order of 10 values -> 45 selection comparisons."""
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub):
            cases = run_input_order(self.rows, self.usable_indices, self.settings)
        selection_cases = [case for case in cases if case.get_algorithm() == 'selection']
        self.assertEqual(len(selection_cases), 4)
        for case in selection_cases:
            self.assertEqual(case.get_sort_stats().get_comparisons(), 45)

    # Check shared inputs, nondefault seeds and the functions passed to benchmark
    def test_expected_inputs_are_shared_across_algorithms(self):
        """All algorithms receive identical prepared values for each order and the requested settings."""
        rows = [{'median_income': str(index + 1)} for index in range(220)]
        usable_indices = list(range(220))
        settings = Settings(order_sample_size=200, sample_seed=17, shuffle_seed=29,
                            nearly_sorted_seed=31)
        indices = shuffle_indices(sample_indices(usable_indices, 200, 17), 29)
        values = column_values(rows, settings.order_column, indices)
        expected = make_orders(values, 31)

        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
            cases = run_input_order(rows, usable_indices, settings)

        for case, call in zip(cases, measure.call_args_list):
            plain_sort, counted_sort, actual_values, actual_settings = call.args
            self.assertEqual((plain_sort, counted_sort), ALGORITHMS[case.get_algorithm()])
            self.assertEqual(actual_values, expected[case.get_order()])
            self.assertIs(actual_settings, settings)
        for order in expected:
            inputs = [call.args[2] for case, call in zip(cases, measure.call_args_list)
                      if case.get_order() == order]
            self.assertEqual(len(inputs), 3)
            self.assertTrue(all(values == inputs[0] for values in inputs))

    # Check that repeated runs preserve the raw data and produce identical case labels and counts
    def test_inputs_unchanged_and_results_reproducible(self):
        """Raw rows and usable indices stay unchanged; the same settings reproduce inputs and counts."""
        original_rows = [row.copy() for row in self.rows]
        original_indices = self.usable_indices[:]
        runs = []
        for run_number in range(2):
            with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
                cases = run_input_order(self.rows, self.usable_indices, self.settings)
            runs.append([(case.get_algorithm(), case.get_order(), call.args[2][:],
                          case.get_sort_stats().get_comparisons(), case.get_sort_stats().get_writes(),
                          case.get_sort_stats().get_swaps())
                         for case, call in zip(cases, measure.call_args_list)])
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(self.rows, original_rows)
        self.assertEqual(self.usable_indices, original_indices)

    # Check that only usable rows of the configured column are sampled
    def test_samples_only_usable_rows_of_the_order_column(self):
        """Usable rows are the even rows and order_column is housing_median_age -> inputs come only from those."""
        rows = [{'median_income': f'{index}.5', 'housing_median_age': str(index + 1000)} for index in range(40)]
        usable_indices = list(range(0, 40, 2))
        settings = Settings(order_sample_size=10, order_column='housing_median_age')
        indices = shuffle_indices(sample_indices(usable_indices, 10, settings.sample_seed), settings.shuffle_seed)
        expected = make_orders(column_values(rows, 'housing_median_age', indices), settings.nearly_sorted_seed)

        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
            cases = run_input_order(rows, usable_indices, settings)

        for case, call in zip(cases, measure.call_args_list):
            self.assertEqual(call.args[2], expected[case.get_order()])
            self.assertEqual(case.get_column(), 'housing_median_age')
            for value in call.args[2]:
                self.assertIn(int(value) - 1000, usable_indices)

    # Check that each case keeps the results of its own benchmark call
    def test_each_case_keeps_its_own_results(self):
        """Every benchmark call returns new TimingResult and SortStats objects -> case i holds those of call i."""
        returned = []

        # Function to return new result objects on every call
        def distinct_results(plain_sort, counted_sort, values, settings):
            """
            Description:
            - Stand-in for benchmark: return a new TimingResult and SortStats each call and record them.

            Input arguments:
               plain_sort, counted_sort, values, settings: as in benchmark.

            Return:
                tuple: (TimingResult, SortStats), different objects on every call.
            """
            call_number = len(returned) + 1
            results = (TimingResult((float(call_number),), 1, float(call_number), float(call_number),
                                    float(call_number)), SortStats(call_number, call_number, call_number))
            returned.append(results)
            return results

        with patch(BENCHMARK_PATH, side_effect=distinct_results):
            cases = run_input_order(self.rows, self.usable_indices, self.settings)

        self.assertEqual(len(cases), len(returned))
        for case, (timing, sort_stats) in zip(cases, returned):
            self.assertIs(case.get_timing(), timing)
            self.assertIs(case.get_sort_stats(), sort_stats)

    # Check that an oversized sample fails before timing starts
    def test_sample_too_large_raises(self):
        """A requested sample larger than the usable rows raises ValueError without calling benchmark."""
        with patch(BENCHMARK_PATH) as measure:
            with self.assertRaises(ValueError):
                run_input_order(self.rows, self.usable_indices, Settings(order_sample_size=13))
        measure.assert_not_called()

    # Check that the driver does not hide a failed verification
    def test_verification_errors_propagate(self):
        """A VerificationError from benchmark reaches the caller."""
        with patch(BENCHMARK_PATH, side_effect=VerificationError('unit-test failure')):
            with self.assertRaises(VerificationError):
                run_input_order(self.rows, self.usable_indices, self.settings)


class TestInputOrderIntegration(unittest.TestCase):
    """The driver together with the real benchmark."""

    # Check the driver with the real benchmark and short development settings
    def test_real_benchmark(self):
        """The real benchmark returns twelve cases, each with one timed batch."""
        rows = [{'median_income': str(index + 1)} for index in range(10)]
        settings = Settings(order_sample_size=10, timed_batches=1, small_input_repetitions=1)
        cases = run_input_order(rows, list(range(10)), settings)
        self.assertEqual(len(cases), 12)
        for case in cases:
            self.assertEqual(len(case.get_timing().get_batch_seconds()), 1)
            self.assertGreaterEqual(case.get_timing().get_median_seconds(), 0)


if __name__ == '__main__':
    unittest.main()
