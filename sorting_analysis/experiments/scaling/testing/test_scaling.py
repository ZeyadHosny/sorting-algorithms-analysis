"""Unit tests for experiments.scaling (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.experiments import run_scaling  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestRunScaling(unittest.TestCase):
    """Run on a small CSV with small Settings."""

    def test_one_case_per_algorithm_and_size(self):
        """sizes (5, 10) -> 6 cases."""
        self.skipTest(NOT_WRITTEN)

    def test_same_sample_for_every_algorithm(self):
        """All algorithms of one size see the same values."""
        self.skipTest(NOT_WRITTEN)

    def test_reproducible_with_same_seed(self):
        """Two runs -> identical counts."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
