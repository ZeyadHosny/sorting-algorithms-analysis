"""Unit tests for experiments.scaling."""
import copy
import unittest
from unittest.mock import patch

from sorting_analysis.config import DEFAULT_SETTINGS, Settings
from sorting_analysis.data import column_values, sample_indices
from sorting_analysis.experiments import ALGORITHMS, run_scaling
from sorting_analysis.sorts import SortStats
from sorting_analysis.timing import TimingResult, VerificationError, benchmark

# Module of the scaling implementation, used only as a patch target (where its names are looked up).
SCALING_MODULE = "sorting_analysis.experiments.scaling.implementation.scaling"


# Function to build a small dataset whose values show which row they come from
def make_rows(row_count):
    """
    Description:
    - Row i holds median_income 'i.5' and housing_median_age 'i+1000', so every value is distinct
      and shows its row.

    Input arguments:
       row_count (int): Number of rows, e.g. 40.

    Return:
        list[dict]: raw rows as load_csv returns them, e.g. {'median_income': '0.5', 'housing_median_age': '1000'}.
    """
    rows = []
    for row_index in range(row_count):
        rows.append({"median_income": f"{row_index}.5", "housing_median_age": str(row_index + 1000)})
    return rows


# Function to build small, fast settings for the tests
def small_settings(scaling_sizes=(5, 10), **changes):
    """
    Description:
    - Settings with few batches and repetitions, so the real benchmark runs quickly.

    Input arguments:
       scaling_sizes (tuple[int]): Sizes to run, e.g. (5, 10).
       changes (dict): Other Settings values to change, e.g. sample_seed=7.

    Return:
        Settings: the test settings.
    """
    return Settings(scaling_sizes=scaling_sizes, timed_batches=2, small_input_repetitions=3, **changes)


# Function used in place of benchmark when the timing itself is not under test
def fake_benchmark(sort_function, counted_sort_function, values, settings):
    """
    Description:
    - Return fixed results without timing anything.

    Input arguments:
       sort_function, counted_sort_function, values, settings: as in benchmark.

    Return:
        tuple: (TimingResult with one 1-second batch, SortStats(0, 0, 0)).
    """
    return TimingResult((1.0,), 1, 1.0, 1.0, 1.0), SortStats(0, 0, 0)


class TestRunScaling(unittest.TestCase):
    """Cases, samples, settings and errors of the scaling experiment."""

    def test_one_case_per_algorithm_and_size(self):
        """sizes (5, 10) -> 6 cases: size 5 then 10, each with bubble, selection, merge; labels scaling / random."""
        settings = small_settings()
        cases = run_scaling(make_rows(40), list(range(40)), settings)
        self.assertEqual([(case.get_input_size(), case.get_algorithm()) for case in cases],
                         [(5, "bubble"), (5, "selection"), (5, "merge"), (10, "bubble"), (10, "selection"),
                          (10, "merge")])
        for case in cases:
            self.assertEqual(case.get_experiment(), "scaling")
            self.assertEqual(case.get_column(), "median_income")
            self.assertEqual(case.get_order(), "random")

    def test_default_settings_give_24_cases(self):
        """Default settings (8 sizes up to 4000) on 4000 rows -> 24 cases (benchmark replaced by a fake)."""
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark):
            cases = run_scaling(make_rows(4000), list(range(4000)))
        self.assertEqual(len(cases), 24)
        self.assertEqual([case.get_input_size() for case in cases][::3], list(DEFAULT_SETTINGS.scaling_sizes))

    def test_same_sample_for_every_algorithm(self):
        """At each size, all three algorithms receive the very same values list."""
        with patch(SCALING_MODULE + ".benchmark", wraps=benchmark) as benchmark_spy:
            run_scaling(make_rows(40), list(range(40)), small_settings())
        calls = benchmark_spy.call_args_list
        self.assertEqual(len(calls), 6)
        for first_call in (0, 3):
            size_values = calls[first_call].args[2]
            for call in calls[first_call:first_call + 3]:
                self.assertIs(call.args[2], size_values)

    def test_sample_is_the_seeded_draw(self):
        """Each size sorts column_values of sample_indices(usable, size, sample_seed); another seed gives other values."""
        rows = make_rows(40)
        usable_indices = list(range(40))
        for seed in (42, 7):
            with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
                run_scaling(rows, usable_indices, small_settings(sample_seed=seed))
            for call in benchmark_spy.call_args_list:
                size = len(call.args[2])
                expected = column_values(rows, "median_income", sample_indices(usable_indices, size, seed))
                self.assertEqual(call.args[2], expected)
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as seed_42_spy:
            run_scaling(rows, usable_indices, small_settings(sample_seed=42))
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as seed_7_spy:
            run_scaling(rows, usable_indices, small_settings(sample_seed=7))
        self.assertNotEqual(seed_42_spy.call_args_list[3].args[2], seed_7_spy.call_args_list[3].args[2])

    def test_samples_only_usable_rows(self):
        """Usable rows are the even rows only -> every sorted value comes from an even row."""
        usable_indices = list(range(0, 40, 2))
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
            run_scaling(make_rows(40), usable_indices, small_settings())
        for call in benchmark_spy.call_args_list:
            for value in call.args[2]:
                self.assertIn(int(value), usable_indices)

    def test_uses_the_scaling_column(self):
        """scaling_column 'housing_median_age' -> values from that column and case column label to match."""
        settings = small_settings(scaling_column="housing_median_age")
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
            cases = run_scaling(make_rows(40), list(range(40)), settings)
        for call in benchmark_spy.call_args_list:
            self.assertTrue(all(value >= 1000 for value in call.args[2]))
        self.assertTrue(all(case.get_column() == "housing_median_age" for case in cases))

    def test_passes_both_sort_versions_and_the_settings(self):
        """benchmark gets the plain and counted function of each algorithm from ALGORITHMS, and the same settings."""
        settings = small_settings()
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
            run_scaling(make_rows(40), list(range(40)), settings)
        expected_functions = list(ALGORITHMS.values()) * 2
        for call, (sort_function, counted_sort_function) in zip(benchmark_spy.call_args_list, expected_functions):
            self.assertIs(call.args[0], sort_function)
            self.assertIs(call.args[1], counted_sort_function)
            self.assertIs(call.args[3], settings)

    def test_case_holds_the_benchmark_results(self):
        """Each case keeps the TimingResult and SortStats that benchmark returned."""
        timing_result = TimingResult((2.0,), 1, 2.0, 2.0, 2.0)
        sort_stats = SortStats(1, 2, 3)
        with patch(SCALING_MODULE + ".benchmark", return_value=(timing_result, sort_stats)):
            cases = run_scaling(make_rows(40), list(range(40)), small_settings())
        for case in cases:
            self.assertIs(case.get_timing(), timing_result)
            self.assertIs(case.get_sort_stats(), sort_stats)

    def test_counts_match_the_counted_sorts(self):
        """With the real benchmark, each case's counts equal its counted sort run directly on the same sample."""
        rows = make_rows(40)
        usable_indices = list(range(40))
        settings = small_settings()
        cases = run_scaling(rows, usable_indices, settings)
        for case in cases:
            values = column_values(rows, "median_income",
                                   sample_indices(usable_indices, case.get_input_size(), settings.sample_seed))
            output, expected_stats = ALGORITHMS[case.get_algorithm()][1](values)
            sort_stats = case.get_sort_stats()
            self.assertEqual((sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()),
                             (expected_stats.get_comparisons(), expected_stats.get_writes(),
                              expected_stats.get_swaps()))
            self.assertEqual(case.get_timing().get_sorts_per_batch(), 3)

    def test_reproducible_with_same_seed(self):
        """Two runs with the same settings -> identical labels and counts (runtimes are not compared)."""
        rows = make_rows(40)
        first_run = run_scaling(rows, list(range(40)), small_settings())
        second_run = run_scaling(rows, list(range(40)), small_settings())
        self.assertEqual(len(first_run), len(second_run))
        for first_case, second_case in zip(first_run, second_run):
            first_stats, second_stats = first_case.get_sort_stats(), second_case.get_sort_stats()
            self.assertEqual((first_case.get_input_size(), first_case.get_algorithm()),
                             (second_case.get_input_size(), second_case.get_algorithm()))
            self.assertEqual((first_stats.get_comparisons(), first_stats.get_writes(), first_stats.get_swaps()),
                             (second_stats.get_comparisons(), second_stats.get_writes(), second_stats.get_swaps()))

    def test_oversized_size_rejected_before_timing(self):
        """sizes (5, 31) with 30 usable rows -> ValueError, and benchmark is never called (not even for size 5)."""
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
            with self.assertRaises(ValueError):
                run_scaling(make_rows(40), list(range(30)), small_settings(scaling_sizes=(5, 31)))
        benchmark_spy.assert_not_called()

    def test_size_equal_to_usable_rows_is_allowed(self):
        """size 30 with exactly 30 usable rows -> 3 cases, each on all 30 rows."""
        with patch(SCALING_MODULE + ".benchmark", side_effect=fake_benchmark) as benchmark_spy:
            cases = run_scaling(make_rows(40), list(range(30)), small_settings(scaling_sizes=(30,)))
        self.assertEqual(len(cases), 3)
        self.assertEqual(len(benchmark_spy.call_args_list[0].args[2]), 30)

    def test_inputs_are_unchanged(self):
        """rows and usable_indices are the same after the run."""
        rows = make_rows(40)
        usable_indices = list(range(40))
        rows_before = copy.deepcopy(rows)
        run_scaling(rows, usable_indices, small_settings())
        self.assertEqual(rows, rows_before)
        self.assertEqual(usable_indices, list(range(40)))

    def test_verification_error_propagates(self):
        """benchmark raising VerificationError -> run_scaling raises it too."""
        with patch(SCALING_MODULE + ".benchmark", side_effect=VerificationError("wrong output")):
            with self.assertRaises(VerificationError):
                run_scaling(make_rows(40), list(range(40)), small_settings())


if __name__ == "__main__":
    unittest.main()
