"""Unit tests for analysis.extrapolation (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.analysis import (bubble_times, determinant_3x3, extrapolate_bubble, fit_quadratic,  # noqa: F401
                                       predict_time)

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestDeterminant(unittest.TestCase):
    """3x3 determinant."""

    def test_diagonal_matrix(self):
        """[[1, 0, 0], [0, 2, 0], [0, 0, 3]] -> 6."""
        self.skipTest(NOT_WRITTEN)

    def test_singular_matrix(self):
        """Two equal rows -> 0."""
        self.skipTest(NOT_WRITTEN)


class TestFitQuadratic(unittest.TestCase):
    """Least-squares quadratic fit with Cramer's rule."""

    def test_exact_quadratic_data(self):
        """sizes (250, 500, 1000, 2000, 4000), times (0.00775, 0.027, 0.103, 0.405, 1.609)
        -> a0 = 0.001, a1 = 2e-6, a2 = 1e-7 (within 1e-9 relative)."""
        self.skipTest(NOT_WRITTEN)

    def test_pure_square_data(self):
        """times = 1e-7 * n**2 -> a0 = 0, a1 = 0, a2 = 1e-7."""
        self.skipTest(NOT_WRITTEN)

    def test_too_few_distinct_sizes_raise(self):
        """sizes (5, 10) or (5, 5, 10) -> ValueError."""
        self.skipTest(NOT_WRITTEN)

    def test_length_mismatch_raises(self):
        """3 sizes, 2 times -> ValueError."""
        self.skipTest(NOT_WRITTEN)


class TestPredictTime(unittest.TestCase):
    """Evaluating the fitted curve."""

    def test_worked_example(self):
        """predict_time((0.001, 2e-6, 1e-7), 20640) == 42.64324 (within 1e-9 relative)."""
        self.skipTest(NOT_WRITTEN)


class TestBubbleTimes(unittest.TestCase):
    """Selecting the measurements used by the fit."""

    def test_takes_bubble_scaling_rows_only(self):
        """Order and dupes rows at n = 2000 and selection/merge rows are ignored."""
        self.skipTest(NOT_WRITTEN)

    def test_missing_size_raises(self):
        """No bubble scaling row at n = 250 -> ValueError."""
        self.skipTest(NOT_WRITTEN)

    def test_duplicate_size_raises(self):
        """Two bubble scaling rows at n = 500 -> ValueError."""
        self.skipTest(NOT_WRITTEN)

    def test_non_positive_or_non_finite_time_raises(self):
        """median_s 0, -1, inf or nan -> ValueError."""
        self.skipTest(NOT_WRITTEN)


class TestExtrapolateBubble(unittest.TestCase):
    """The estimate row and the measured-versus-fitted rows."""

    def test_worked_example(self):
        """Bubble scaling rows with the exact quadratic times -> estimate_s 42.64324, method 'quadratic_fit',
        sizes_used '250;500;1000;2000;4000', target_size 20640."""
        self.skipTest(NOT_WRITTEN)

    def test_fitted_rows(self):
        """One FITTED_FIELDS row per base size; with exact quadratic times, fitted_s == measured_s."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
