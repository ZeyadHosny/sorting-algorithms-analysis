"""Unit and integration tests for analysis.growth; unit-test times are invented examples."""
import copy
import unittest

from sorting_analysis.analysis import GROWTH_FIELDS, growth_factors, theoretical_factor
from sorting_analysis.config import Settings
from sorting_analysis.experiments import run_scaling


# Function to make a minimal scaling row for growth unit tests
def scaling_row(algorithm, input_size, median_seconds):
    """
    Description:
    - Make an invented test row containing the fields used by growth_factors.

    Input arguments:
       algorithm (str): Sorting algorithm name.
       input_size (int): Number of input values.
       median_seconds (float): Invented median time for an arithmetic check.

    Return:
        dict: A scaling row for a unit test, not an experimental result.
    """
    return {"experiment": "scaling", "algorithm": algorithm, "column": "median_income",
            "order": "random", "input_size": input_size, "median_s": median_seconds}


class TestTheoreticalFactor(unittest.TestCase):
    """Expected growth."""

    def test_quadratic_doubling(self):
        """theoretical_factor('bubble', 1000, 2000) == 4.0."""
        for algorithm in ("bubble", "selection"):
            with self.subTest(algorithm=algorithm):
                self.assertEqual(theoretical_factor(algorithm, 1000, 2000), 4.0)

    def test_merge_doubling(self):
        """theoretical_factor('merge', 1000, 2000) is about 2.20."""
        self.assertAlmostEqual(theoretical_factor("merge", 1000, 2000), 2.2006866637759874)
        self.assertEqual(theoretical_factor("merge", 2, 4), 4.0)

    def test_other_size_ratios(self):
        """The theoretical helper uses its supplied sizes, even when the size ratio is not two."""
        self.assertEqual(theoretical_factor("selection", 100, 300), 9.0)
        self.assertEqual(theoretical_factor("merge", 2, 8), 12.0)

    def test_invalid_algorithm_or_size_raises(self):
        """Unknown algorithms and sizes outside the formulas' domains raise ValueError."""
        for arguments in (("other", 10, 20), ("bubble", 0, 20), ("selection", 10, -20),
                          ("merge", 1, 2), ("merge", 2, 1)):
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    theoretical_factor(*arguments)


class TestGrowthFactors(unittest.TestCase):
    """Observed growth."""

    def test_ratio_of_doubling_pair(self):
        """T(1000) = 1, T(2000) = 4 -> observed_factor 4.0."""
        rows = [scaling_row("bubble", 1000, 1.0), scaling_row("bubble", 2000, 4.0)]
        expected = {"algorithm": "bubble", "size_from": 1000, "size_to": 2000,
                    "time_from_s": 1.0, "time_to_s": 4.0, "observed_factor": 4.0,
                    "theoretical_factor": 4.0}
        result = growth_factors(rows)
        self.assertEqual(result, [expected])
        self.assertEqual(tuple(result[0]), GROWTH_FIELDS)

    def test_non_doubling_pairs_skipped(self):
        """Sizes 20 and 250 -> no row."""
        self.assertEqual(growth_factors([scaling_row("bubble", 20, 0.1),
                                         scaling_row("bubble", 250, 0.5)]), [])

    def test_ignores_other_experiments(self):
        """Order and dupes rows do not change the result."""
        rows = [scaling_row("bubble", 1000, 1.0), scaling_row("bubble", 2000, 4.0)]
        expected = growth_factors(rows)
        for experiment in ("order", "dupes"):
            for size in (1000, 2000):
                extra_row = scaling_row("bubble", size, 100.0)
                extra_row["experiment"] = experiment
                rows.append(extra_row)
        self.assertEqual(growth_factors(rows), expected)

    def test_empty_and_single_sizes(self):
        """No rows, no scaling rows, or one size for an algorithm produce no growth row."""
        for rows in ([], [{"experiment": "order"}], [scaling_row("selection", 1000, 1.0)]):
            with self.subTest(rows=rows):
                self.assertEqual(growth_factors(rows), [])

    def test_all_algorithms_use_their_own_times_in_unsorted_input(self):
        """Interleaved sizes and algorithms produce every doubling pair without mixing timings."""
        rows = [scaling_row("merge", 20, 0.006), scaling_row("bubble", 10, 0.01),
                scaling_row("selection", 20, 0.04), scaling_row("merge", 10, 0.004),
                scaling_row("bubble", 20, 0.03), scaling_row("selection", 10, 0.02)]
        before = copy.deepcopy(rows)
        result = growth_factors(rows)
        self.assertEqual([row["algorithm"] for row in result], ["merge", "bubble", "selection"])
        self.assertEqual([row["observed_factor"] for row in result], [1.5, 3.0, 2.0])
        self.assertEqual([row["size_from"] for row in result], [10, 10, 10])
        self.assertEqual([row["size_to"] for row in result], [20, 20, 20])
        self.assertEqual(rows, before)

    def test_finds_doubling_pairs_even_when_not_adjacent(self):
        """Sizes 10, 15, 20, 40 give 10->20 and 20->40, without requiring adjacency."""
        rows = [scaling_row("bubble", size, seconds)
                for size, seconds in ((10, 0.01), (15, 0.02), (20, 0.04), (40, 0.16))]
        result = growth_factors(rows)
        self.assertEqual([(row["size_from"], row["size_to"]) for row in result], [(10, 20), (20, 40)])
        self.assertEqual([row["observed_factor"] for row in result], [4.0, 4.0])

    def test_missing_size_does_not_join_different_algorithms(self):
        """Bubble at 1000 and selection at 2000 do not form a growth pair."""
        rows = [scaling_row("bubble", 1000, 1.0), scaling_row("selection", 2000, 4.0)]
        self.assertEqual(growth_factors(rows), [])

    def test_duplicate_algorithm_size_raises(self):
        """Duplicate scaling observations for the same algorithm and size are rejected."""
        rows = [scaling_row("bubble", 1000, 1.0), scaling_row("bubble", 1000, 2.0),
                scaling_row("bubble", 2000, 4.0)]
        with self.assertRaises(ValueError):
            growth_factors(rows)

    def test_invalid_median_times_raise(self):
        """Zero, negative and non-finite medians are rejected before a growth ratio is reported."""
        for seconds in (0.0, -1.0, float("nan"), float("inf"), -float("inf")):
            with self.subTest(seconds=seconds):
                rows = [scaling_row("bubble", 1000, seconds), scaling_row("bubble", 2000, 1.0)]
                with self.assertRaises(ValueError):
                    growth_factors(rows)

    def test_invalid_algorithm_or_nonpositive_size_raises(self):
        """Growth rows with an unknown algorithm or a non-positive size raise ValueError."""
        for row in (scaling_row("other", 10, 0.1), scaling_row("bubble", 0, 0.1),
                    scaling_row("selection", -5, 0.1)):
            with self.subTest(row=row):
                with self.assertRaises(ValueError):
                    growth_factors([row])

    def test_real_scaling_benchmark_integration(self):
        """Real tiny scaling cases yield six growth rows with each measured ratio computed correctly."""
        rows = [{"median_income": str(value)} for value in range(20, 0, -1)]
        settings = Settings(scaling_sizes=(5, 10, 20), small_input_repetitions=2)
        cases = run_scaling(rows, list(range(20)), settings)
        # Build only the fields Growth needs, without depending on the separate Records feature.
        direct_rows = [{"experiment": case.get_experiment(), "algorithm": case.get_algorithm(),
                        "input_size": case.get_input_size(), "median_s": case.get_timing().get_median_seconds()}
                       for case in cases]
        direct_growth = growth_factors(direct_rows)
        self.assertEqual(len(direct_growth), 6)
        self.assertEqual({(row["algorithm"], row["size_from"], row["size_to"]) for row in direct_growth},
                         {(algorithm, smaller, 2 * smaller)
                          for algorithm in ("bubble", "selection", "merge") for smaller in (5, 10)})
        for row in direct_growth:
            self.assertGreater(row["observed_factor"], 0)
            self.assertAlmostEqual(row["observed_factor"], row["time_to_s"] / row["time_from_s"])


if __name__ == "__main__":
    unittest.main()
