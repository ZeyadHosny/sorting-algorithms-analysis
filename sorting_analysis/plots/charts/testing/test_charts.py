"""Unit tests for plots.charts (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.plots import matplotlib_available, plot_input_order, plot_repeated_values, plot_scaling  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestCharts(unittest.TestCase):
    """Chart files (skipped automatically when matplotlib is missing)."""

    def test_matplotlib_available_returns_bool(self):
        """Returns True or False without raising."""
        self.skipTest(NOT_WRITTEN)

    def test_scaling_charts_written(self):
        """Small cases -> PNG files exist in a temporary folder."""
        self.skipTest(NOT_WRITTEN)

    def test_input_order_charts_written(self):
        """Small cases -> PNG files exist."""
        self.skipTest(NOT_WRITTEN)

    def test_repeated_values_charts_written(self):
        """Small cases -> PNG files exist."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
