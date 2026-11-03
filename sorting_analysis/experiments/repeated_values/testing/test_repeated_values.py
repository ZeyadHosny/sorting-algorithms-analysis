"""Unit tests for experiments.repeated_values (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.experiments import run_repeated_values  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestRunRepeatedValues(unittest.TestCase):
    """Run on a small CSV with small Settings."""

    def test_nine_cases_and_three_stats(self):
        """3 columns x 3 algorithms -> 9 cases; 3 duplicate_stats rows."""
        self.skipTest(NOT_WRITTEN)

    def test_income_input_equals_input_order_random(self):
        """The median_income input equals the input-order experiment's random input."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
