"""Unit tests for analysis.growth (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.analysis import growth_factors, theoretical_factor  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestTheoreticalFactor(unittest.TestCase):
    """Expected growth."""

    def test_quadratic_doubling(self):
        """theoretical_factor('bubble', 1000, 2000) == 4.0."""
        self.skipTest(NOT_WRITTEN)

    def test_merge_doubling(self):
        """theoretical_factor('merge', 1000, 2000) is about 2.20."""
        self.skipTest(NOT_WRITTEN)


class TestGrowthFactors(unittest.TestCase):
    """Observed growth."""

    def test_ratio_of_doubling_pair(self):
        """T(1000) = 1, T(2000) = 4 -> observed_factor 4.0."""
        self.skipTest(NOT_WRITTEN)

    def test_non_doubling_pairs_skipped(self):
        """Sizes 20 and 250 -> no row."""
        self.skipTest(NOT_WRITTEN)

    def test_ignores_other_experiments(self):
        """Order and dupes rows do not change the result."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
