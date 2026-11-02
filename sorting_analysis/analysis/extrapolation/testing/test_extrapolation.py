"""Unit tests for analysis.extrapolation (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.analysis import estimate_range, extrapolate_bubble, extrapolate_bubble_growth  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestExtrapolateBubble(unittest.TestCase):
    """Main method c."""

    def test_worked_example(self):
        """T(2000) = 0.5 s -> c = 1.25e-7, estimate about 53.25 s for n = 20,640."""
        self.skipTest(NOT_WRITTEN)

    def test_no_base_returns_empty(self):
        """No bubble scaling row at a base size -> []."""
        self.skipTest(NOT_WRITTEN)

    def test_non_positive_timing_raises(self):
        """T = 0 -> ValueError."""
        self.skipTest(NOT_WRITTEN)


class TestExtrapolateBubbleGrowth(unittest.TestCase):
    """Cross-check from measured growth."""

    def test_worked_example(self):
        """T(2000) = 0.5, T(4000) = 2.1 -> b about 2.07, estimate about 63 s."""
        self.skipTest(NOT_WRITTEN)

    def test_base_without_half_size_skipped(self):
        """Base 1000 without T(500) -> no row."""
        self.skipTest(NOT_WRITTEN)


class TestEstimateRange(unittest.TestCase):
    """Range of one method."""

    def test_min_and_max(self):
        """estimates 51, 56, 53 -> (51, 56)."""
        self.skipTest(NOT_WRITTEN)

    def test_empty_rows_raise(self):
        """[] -> ValueError."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
