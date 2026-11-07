"""Unit tests for analysis.extrapolation."""
import math
import unittest
from unittest.mock import patch

from sorting_analysis.analysis import (EXTRAPOLATION_FIELDS, FIT_METHOD, FITTED_FIELDS, bubble_times,
                                       determinant_3x3, extrapolate_bubble, fit_quadratic, predict_time)
from sorting_analysis.config import Settings
from sorting_analysis.experiments import case_row, run_scaling
# Patch target of the module under test (patching only, never imported directly).
EXTRAPOLATION_MODULE = "sorting_analysis.analysis.extrapolation.implementation.extrapolation"
# Worked example of F-EXT-2: exact times of T(n) = 0.001 + 2e-6 n + 1e-7 n^2.
BASE_SIZES = (250, 500, 1000, 2000, 4000)
EXACT_TIMES = (0.00775, 0.027, 0.103, 0.405, 1.609)


# Function to make a minimal case row for the extrapolation tests
def case(algorithm, input_size, median_seconds, experiment="scaling"):
    """
    Description:
    - Make an invented case row with the fields bubble_times reads.

    Input arguments:
       algorithm (str): 'bubble', 'selection' or 'merge'.
       input_size (int): Number of values sorted.
       median_seconds (float): Invented median time.
       experiment (str): 'scaling', 'order' or 'dupes'.

    Return:
        dict: a case row for a unit test, not an experimental result.
    """
    return {"experiment": experiment, "algorithm": algorithm, "column": "median_income", "order": "random",
            "input_size": input_size, "median_s": median_seconds}


# Function to make the worked-example bubble scaling rows
def exact_cases():
    """
    Description:
    - Bubble scaling rows at the base sizes with the exact quadratic times.

    Input arguments:
       None

    Return:
        list[dict]: five case rows.
    """
    return [case("bubble", size, time) for size, time in zip(BASE_SIZES, EXACT_TIMES)]


class TestDeterminant(unittest.TestCase):
    """3x3 determinant."""

    def test_diagonal_matrix(self):
        """[[1, 0, 0], [0, 2, 0], [0, 0, 3]] -> 6."""
        self.assertEqual(determinant_3x3([[1, 0, 0], [0, 2, 0], [0, 0, 3]]), 6)

    def test_singular_matrix(self):
        """Two equal rows -> 0."""
        self.assertEqual(determinant_3x3([[1, 2, 3], [4, 5, 6], [1, 2, 3]]), 0)

    def test_general_matrix(self):
        """[[2, -3, 1], [2, 0, -1], [1, 4, 5]] -> 49, so every cofactor sign is checked."""
        self.assertEqual(determinant_3x3([[2, -3, 1], [2, 0, -1], [1, 4, 5]]), 49)

    def test_row_swap_changes_sign(self):
        """Swapping two rows negates the determinant."""
        matrix = [[2, -3, 1], [2, 0, -1], [1, 4, 5]]
        self.assertEqual(determinant_3x3([matrix[1], matrix[0], matrix[2]]), -49)


class TestFitQuadratic(unittest.TestCase):
    """Least-squares quadratic fit, beta = (X^T X)^-1 X^T y."""

    def test_exact_quadratic_data(self):
        """sizes (250, 500, 1000, 2000, 4000), times (0.00775, 0.027, 0.103, 0.405, 1.609)
        -> a0 = 0.001, a1 = 2e-6, a2 = 1e-7 (within 1e-9 relative)."""
        coefficients = fit_quadratic(list(BASE_SIZES), list(EXACT_TIMES))
        self.assertEqual(len(coefficients), 3)
        for actual, expected in zip(coefficients, (0.001, 2e-6, 1e-7)):
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-9), (actual, expected))

    def test_pure_square_data(self):
        """times = 1e-7 * n**2 -> a0 = 0, a1 = 0, a2 = 1e-7."""
        a0, a1, a2 = fit_quadratic(list(BASE_SIZES), [1e-7 * size ** 2 for size in BASE_SIZES])
        self.assertAlmostEqual(a0, 0, places=12)
        self.assertAlmostEqual(a1, 0, places=15)
        self.assertTrue(math.isclose(a2, 1e-7, rel_tol=1e-9))

    def test_three_points_are_interpolated(self):
        """Exactly 3 distinct sizes -> the curve passes through all three points."""
        sizes, times = [10, 20, 40], [0.5, 0.2, 0.9]
        coefficients = fit_quadratic(sizes, times)
        for size, time in zip(sizes, times):
            self.assertAlmostEqual(predict_time(coefficients, size), time, places=12)

    def test_noisy_data_satisfy_the_normal_equations(self):
        """Non-quadratic times -> residuals are orthogonal to 1, n and n^2 (least squares, not interpolation)."""
        times = [time + noise for time, noise in zip(EXACT_TIMES, (0.002, -0.003, 0.004, -0.001, 0.003))]
        coefficients = fit_quadratic(list(BASE_SIZES), times)
        residuals = [time - predict_time(coefficients, size) for size, time in zip(BASE_SIZES, times)]
        self.assertGreater(max(abs(residual) for residual in residuals), 1e-4)
        for power in range(3):
            weighted = sum(residual * size ** power for size, residual in zip(BASE_SIZES, residuals))
            scale = sum(abs(time) * size ** power for size, time in zip(BASE_SIZES, times))
            self.assertLess(abs(weighted), 1e-9 * scale)

    def test_sizes_in_any_order(self):
        """Shuffled (size, time) pairs give the same coefficients."""
        order = (3, 0, 4, 1, 2)
        expected = fit_quadratic(list(BASE_SIZES), list(EXACT_TIMES))
        shuffled = fit_quadratic([BASE_SIZES[i] for i in order], [EXACT_TIMES[i] for i in order])
        for actual, wanted in zip(shuffled, expected):
            self.assertTrue(math.isclose(actual, wanted, rel_tol=1e-12))

    def test_too_few_distinct_sizes_raise(self):
        """sizes (5, 10) or (5, 5, 10) -> ValueError naming the 3 distinct sizes, before the singular check."""
        for sizes in ([5, 10], [5, 5, 10]):
            with self.subTest(sizes=sizes):
                with self.assertRaisesRegex(ValueError, "at least 3 distinct sizes, got 2"):
                    fit_quadratic(sizes, [1.0] * len(sizes))

    def test_length_mismatch_raises(self):
        """3 sizes, 2 times -> ValueError."""
        with self.assertRaises(ValueError):
            fit_quadratic([5, 10, 20], [1.0, 2.0])

    def test_non_finite_time_raises(self):
        """A nan or infinite time -> ValueError."""
        for bad_time in (float("nan"), float("inf"), -float("inf")):
            with self.subTest(bad_time=bad_time):
                with self.assertRaises(ValueError):
                    fit_quadratic([5, 10, 20], [1.0, bad_time, 2.0])

    def test_zero_determinant_raises(self):
        """A singular sums matrix -> ValueError."""
        with patch(f"{EXTRAPOLATION_MODULE}.determinant_3x3", return_value=0):
            with self.assertRaises(ValueError):
                fit_quadratic([5, 10, 20], [1.0, 2.0, 3.0])

    def test_inputs_unchanged(self):
        """The sizes and times lists are not modified."""
        sizes, times = list(BASE_SIZES), list(EXACT_TIMES)
        fit_quadratic(sizes, times)
        self.assertEqual((sizes, times), (list(BASE_SIZES), list(EXACT_TIMES)))


class TestPredictTime(unittest.TestCase):
    """Evaluating the fitted curve."""

    def test_worked_example(self):
        """predict_time((0.001, 2e-6, 1e-7), 20640) == 42.64324 (within 1e-9 relative)."""
        self.assertTrue(math.isclose(predict_time((0.001, 2e-6, 1e-7), 20640), 42.64324, rel_tol=1e-9))

    def test_each_coefficient_term(self):
        """(1, 0, 0) -> 1, (0, 1, 0) -> n, (0, 0, 1) -> n^2 at n = 3."""
        self.assertEqual([predict_time(coefficients, 3) for coefficients in ((1, 0, 0), (0, 1, 0), (0, 0, 1))],
                         [1, 3, 9])

    def test_fit_then_predict_reproduces_the_estimate(self):
        """Fitting the worked-example times and predicting at 20640 -> 42.64324 (within 1e-9 relative)."""
        coefficients = fit_quadratic(list(BASE_SIZES), list(EXACT_TIMES))
        self.assertTrue(math.isclose(predict_time(coefficients, 20640), 42.64324, rel_tol=1e-9))


class TestBubbleTimes(unittest.TestCase):
    """Selecting the measurements used by the fit."""

    def test_takes_bubble_scaling_rows_only(self):
        """Order and dupes rows at n = 2000, selection/merge rows and non-base sizes are ignored."""
        cases = exact_cases() + [case("bubble", 2000, 99.0, "order"), case("bubble", 2000, 98.0, "dupes"),
                                 case("bubble", 20, float("nan"))]
        cases += [case(algorithm, size, 50.0) for algorithm in ("selection", "merge") for size in BASE_SIZES]
        self.assertEqual(bubble_times(cases, BASE_SIZES), list(EXACT_TIMES))

    def test_follows_base_sizes_order(self):
        """Rows in any order -> one time per base size, in base_sizes order."""
        cases = exact_cases()[::-1]
        self.assertEqual(bubble_times(cases, (4000, 250, 1000)), [1.609, 0.00775, 0.103])

    def test_missing_size_raises(self):
        """No bubble scaling row at n = 250 -> ValueError."""
        with self.assertRaisesRegex(ValueError, "n = 250"):
            bubble_times(exact_cases()[1:], BASE_SIZES)

    def test_duplicate_size_raises(self):
        """Two bubble scaling rows at n = 500 -> ValueError."""
        with self.assertRaisesRegex(ValueError, "Duplicate bubble scaling row at n = 500"):
            bubble_times(exact_cases() + [case("bubble", 500, 0.027)], BASE_SIZES)

    def test_duplicate_base_size_raises(self):
        """base_sizes (250, 250, 500) -> ValueError."""
        with self.assertRaisesRegex(ValueError, "distinct"):
            bubble_times(exact_cases(), (250, 250, 500))

    def test_non_positive_or_non_finite_time_raises(self):
        """median_s 0, -1, inf or nan -> ValueError."""
        for bad_time in (0.0, -1.0, float("inf"), float("nan")):
            with self.subTest(bad_time=bad_time):
                cases = exact_cases()
                cases[2] = case("bubble", 1000, bad_time)
                with self.assertRaisesRegex(ValueError, "n = 1000"):
                    bubble_times(cases, BASE_SIZES)

    def test_input_rows_unchanged(self):
        """The case rows are not modified."""
        cases = exact_cases()
        bubble_times(cases, BASE_SIZES)
        self.assertEqual(cases, exact_cases())


class TestExtrapolateBubble(unittest.TestCase):
    """The estimate row and the measured-versus-fitted rows."""

    def test_worked_example(self):
        """Bubble scaling rows with the exact quadratic times -> estimate_s 42.64324, method 'quadratic_fit',
        sizes_used '250;500;1000;2000;4000', target_size 20640."""
        estimate, fitted = extrapolate_bubble(exact_cases(), 20640, BASE_SIZES)
        self.assertEqual(tuple(estimate), EXTRAPOLATION_FIELDS)
        self.assertEqual((estimate["method"], estimate["sizes_used"], estimate["target_size"]),
                         (FIT_METHOD, "250;500;1000;2000;4000", 20640))
        self.assertEqual(FIT_METHOD, "quadratic_fit")
        self.assertTrue(math.isclose(estimate["estimate_s"], 42.64324, rel_tol=1e-9))
        for field, expected in (("a0", 0.001), ("a1", 2e-6), ("a2", 1e-7)):
            self.assertTrue(math.isclose(estimate[field], expected, rel_tol=1e-9), field)

    def test_fitted_rows(self):
        """One FITTED_FIELDS row per base size; with exact quadratic times, fitted_s == measured_s."""
        estimate, fitted = extrapolate_bubble(exact_cases(), 20640, BASE_SIZES)
        self.assertEqual([tuple(row) for row in fitted], [FITTED_FIELDS] * 5)
        self.assertEqual([row["input_size"] for row in fitted], list(BASE_SIZES))
        self.assertEqual([row["measured_s"] for row in fitted], list(EXACT_TIMES))
        for row in fitted:
            self.assertTrue(math.isclose(row["fitted_s"], row["measured_s"], rel_tol=1e-9), row)

    def test_outputs_match_the_coefficients_exactly(self):
        """estimate_s and every fitted_s equal predict_time with the reported coefficients."""
        times = [time * factor for time, factor in zip(EXACT_TIMES, (1.02, 0.97, 1.01, 0.99, 1.03))]
        cases = [case("bubble", size, time) for size, time in zip(BASE_SIZES, times)]
        estimate, fitted = extrapolate_bubble(cases, 20640, BASE_SIZES)
        coefficients = (estimate["a0"], estimate["a1"], estimate["a2"])
        self.assertEqual(estimate["estimate_s"], predict_time(coefficients, 20640))
        for row in fitted:
            self.assertEqual(row["fitted_s"], predict_time(coefficients, row["input_size"]))
        self.assertEqual([row["measured_s"] for row in fitted], times)

    def test_other_experiments_and_algorithms_do_not_change_the_estimate(self):
        """Order and dupes bubble rows at n = 2000 and selection rows -> same estimate as bubble scaling alone."""
        expected = extrapolate_bubble(exact_cases(), 20640, BASE_SIZES)
        cases = exact_cases() + [case("bubble", 2000, 9.0, "order"), case("bubble", 2000, 8.0, "dupes")]
        cases += [case("selection", size, 7.0) for size in BASE_SIZES]
        self.assertEqual(extrapolate_bubble(cases, 20640, BASE_SIZES), expected)

    def test_missing_base_size_raises(self):
        """No bubble scaling row at n = 4000 -> ValueError."""
        with self.assertRaisesRegex(ValueError, "n = 4000"):
            extrapolate_bubble(exact_cases()[:4], 20640, BASE_SIZES)

    def test_real_scaling_cases(self):
        """Real tiny scaling run, target 40 -> measured_s are bubble's medians and the estimate is at n = 40."""
        rows = [{"median_income": str(value)} for value in range(20, 0, -1)]
        settings = Settings(scaling_sizes=(5, 10, 20), small_input_repetitions=2)
        cases = [case_row(scaling_case) for scaling_case in run_scaling(rows, list(range(20)), settings)]
        estimate, fitted = extrapolate_bubble(cases, 40, (5, 10, 20))
        medians = {row["input_size"]: row["median_s"] for row in cases if row["algorithm"] == "bubble"}
        self.assertEqual([row["measured_s"] for row in fitted], [medians[5], medians[10], medians[20]])
        self.assertEqual((estimate["sizes_used"], estimate["target_size"]), ("5;10;20", 40))
        coefficients = (estimate["a0"], estimate["a1"], estimate["a2"])
        self.assertEqual(estimate["estimate_s"], predict_time(coefficients, 40))
        self.assertTrue(math.isfinite(estimate["estimate_s"]))


if __name__ == "__main__":
    unittest.main()
