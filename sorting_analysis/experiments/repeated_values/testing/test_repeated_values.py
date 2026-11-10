"""Unit and integration tests for experiments.repeated_values."""
import unittest
from unittest.mock import patch

from sorting_analysis.config import Settings
from sorting_analysis.data import DUPES_FIELDS, column_values, duplicate_stats, sample_indices, shuffle_indices
from sorting_analysis.experiments import ALGORITHMS, run_input_order, run_repeated_values
from sorting_analysis.sorts import SortStats
from sorting_analysis.timing import TimingResult, VerificationError

# Patch the benchmark reference used by the repeated-values experiment.
BENCHMARK_PATH = 'sorting_analysis.experiments.repeated_values.implementation.repeated_values.benchmark'
# Patch the separate reference used by the input-order experiment for the cross-experiment check.
ORDER_BENCHMARK_PATH = 'sorting_analysis.experiments.input_order.implementation.input_order.benchmark'


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


class TestRunRepeatedValues(unittest.TestCase):
    """Run on a small CSV with small Settings."""

    # Method to prepare rows with distinct incomes, repeated ages and capped house values
    def setUp(self):
        """
        Description:
        - Build twelve raw rows and settings that select all twelve.

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
        self.settings = Settings(order_sample_size=12, sample_seed=17, shuffle_seed=29)

    def test_nine_cases_and_three_stats(self):
        """3 columns x 3 algorithms -> 9 cases; 3 duplicate_stats rows."""
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
            cases, statistics = run_repeated_values(self.rows, self.usable_indices, self.settings)
        self.assertEqual(len(cases), 9)
        self.assertEqual(len(statistics), 3)
        self.assertEqual(measure.call_count, 9)
        expected = {(column, algorithm) for column in self.settings.selected_columns
                    for algorithm in ALGORITHMS}
        self.assertEqual({(case.get_column(), case.get_algorithm()) for case in cases}, expected)
        indices = shuffle_indices(sample_indices(self.usable_indices, 12, 17), 29)
        for case, call in zip(cases, measure.call_args_list):
            self.assertEqual(case.get_experiment(), 'dupes')
            self.assertEqual(case.get_order(), 'random')
            self.assertEqual(case.get_input_size(), 12)
            self.assertEqual(call.args[:2], ALGORITHMS[case.get_algorithm()])
            self.assertEqual(call.args[2], column_values(self.rows, case.get_column(), indices))
            self.assertIs(call.args[3], self.settings)
        for statistics_row in statistics:
            self.assertEqual(set(statistics_row), set(DUPES_FIELDS))

    def test_income_input_equals_input_order_random(self):
        """The median_income input equals the input-order experiment's random input."""
        with patch(ORDER_BENCHMARK_PATH, side_effect=benchmark_stub) as order_measure:
            order_cases = run_input_order(self.rows, self.usable_indices, self.settings)
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as repeated_measure:
            repeated_cases, statistics = run_repeated_values(self.rows, self.usable_indices, self.settings)
        order_inputs = {case.get_algorithm(): call.args[2]
                        for case, call in zip(order_cases, order_measure.call_args_list)
                        if case.get_order() == 'random'}
        for case, call in zip(repeated_cases, repeated_measure.call_args_list):
            if case.get_column() == self.settings.order_column:
                self.assertEqual(call.args[2], order_inputs[case.get_algorithm()])

    # Check duplication statistics independently using known frequencies
    def test_repeated_and_capped_values_are_retained(self):
        """All twelve values remain: ages have four of each value; the capped house value occurs nine times."""
        with patch(BENCHMARK_PATH, side_effect=benchmark_stub):
            cases, statistics = run_repeated_values(self.rows, self.usable_indices, self.settings)
        by_column = {row['column']: row for row in statistics}
        income = by_column['median_income']
        self.assertEqual((income['distinct'], income['modal_count'], income['repeated_distinct']),
                         (12, 1, 0))
        age = by_column['housing_median_age']
        self.assertEqual((age['distinct'], age['modal_count'], age['repeated_distinct'],
                          age['repeated_observations']), (3, 4, 3, 12))
        house_value = by_column['median_house_value']
        self.assertEqual((house_value['distinct'], house_value['modal_value'],
                          house_value['modal_count'], house_value['repeated_distinct'],
                          house_value['repeated_observations']), (2, 500001.0, 9, 2, 12))
        self.assertTrue(all(row['sample_size'] == 12 for row in statistics))

    # Check that repeated runs preserve source inputs and return the same samples and counts
    def test_inputs_unchanged_and_results_reproducible(self):
        """Raw rows and usable indices stay unchanged; the same seeds reproduce samples, stats and counts."""
        original_rows = [row.copy() for row in self.rows]
        original_indices = self.usable_indices[:]
        runs = []
        for run_number in range(2):
            with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
                cases, statistics = run_repeated_values(self.rows, self.usable_indices, self.settings)
            signatures = [(case.get_column(), case.get_algorithm(), call.args[2][:],
                           case.get_sort_stats().get_comparisons(), case.get_sort_stats().get_writes(),
                           case.get_sort_stats().get_swaps())
                          for case, call in zip(cases, measure.call_args_list)]
            runs.append((signatures, statistics))
        self.assertEqual(runs[0], runs[1])
        self.assertEqual(self.rows, original_rows)
        self.assertEqual(self.usable_indices, original_indices)

    # Check that only usable rows of the selected columns are sampled, for the inputs and the statistics
    def test_samples_only_usable_rows_of_the_selected_columns(self):
        """Usable rows are the even rows and selected_columns are age and house value -> 6 cases and 2 statistics
        rows, all from that sample."""
        rows = [{'median_income': f'{index}.5', 'housing_median_age': str(index + 1000),
                 'median_house_value': str(2000 + index // 4)} for index in range(40)]
        usable_indices = list(range(0, 40, 2))
        columns = ('housing_median_age', 'median_house_value')
        settings = Settings(order_sample_size=10, selected_columns=columns)
        indices = shuffle_indices(sample_indices(usable_indices, 10, settings.sample_seed), settings.shuffle_seed)

        with patch(BENCHMARK_PATH, side_effect=benchmark_stub) as measure:
            cases, statistics = run_repeated_values(rows, usable_indices, settings)

        self.assertEqual(len(cases), 6)
        self.assertEqual([row['column'] for row in statistics], list(columns))
        for case, call in zip(cases, measure.call_args_list):
            self.assertEqual(call.args[2], column_values(rows, case.get_column(), indices))
        for value in column_values(rows, 'housing_median_age', indices):
            self.assertIn(int(value) - 1000, usable_indices)
        for statistics_row in statistics:
            expected = duplicate_stats(column_values(rows, statistics_row['column'], indices))
            expected['column'] = statistics_row['column']
            self.assertEqual(statistics_row, expected)

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
            cases, statistics = run_repeated_values(self.rows, self.usable_indices, self.settings)

        self.assertEqual(len(cases), len(returned))
        for case, (timing, sort_stats) in zip(cases, returned):
            self.assertIs(case.get_timing(), timing)
            self.assertIs(case.get_sort_stats(), sort_stats)

    # Check that an oversized request fails before any timing call
    def test_sample_too_large_raises(self):
        """A sample larger than the usable rows raises ValueError without calling benchmark."""
        with patch(BENCHMARK_PATH) as measure:
            with self.assertRaises(ValueError):
                run_repeated_values(self.rows, self.usable_indices, Settings(order_sample_size=13))
        measure.assert_not_called()

    # Check that failed verification is not converted to a successful case
    def test_verification_errors_propagate(self):
        """A VerificationError from benchmark reaches the caller."""
        with patch(BENCHMARK_PATH, side_effect=VerificationError('unit-test failure')):
            with self.assertRaises(VerificationError):
                run_repeated_values(self.rows, self.usable_indices, self.settings)


class TestRepeatedValuesIntegration(unittest.TestCase):
    """The driver together with the real benchmark."""

    # Check the driver with the real benchmark and small development settings
    def test_real_benchmark(self):
        """The real benchmark returns nine cases and three statistics rows, each case with one timed batch."""
        rows = [{'median_income': str(index + 1), 'housing_median_age': '20',
                 'median_house_value': '500001'} for index in range(10)]
        settings = Settings(order_sample_size=10, timed_batches=1, small_input_repetitions=1)
        cases, statistics = run_repeated_values(rows, list(range(10)), settings)
        self.assertEqual(len(cases), 9)
        self.assertEqual(len(statistics), 3)
        for case in cases:
            self.assertEqual(len(case.get_timing().get_batch_seconds()), 1)
            self.assertGreaterEqual(case.get_timing().get_median_seconds(), 0)


if __name__ == '__main__':
    unittest.main()
