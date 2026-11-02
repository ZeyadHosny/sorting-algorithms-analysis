"""Unit tests for config (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.config import DEFAULT_SETTINGS, Settings  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestSettings(unittest.TestCase):
    """Default values and the repetition tiers."""

    def test_defaults_match_the_agreed_settings(self):
        """get_sample_seed() == 42, get_scaling_sizes() == (5, 10, 20, 250, 500, 1000, 2000, 4000), get_order_sample_size() == 2000."""
        self.skipTest(NOT_WRITTEN)

    def test_repetitions_for_small_inputs(self):
        """repetitions_for(5), repetitions_for(20) -> 1000."""
        self.skipTest(NOT_WRITTEN)

    def test_repetitions_for_normal_inputs(self):
        """repetitions_for(21), repetitions_for(250) -> 1."""
        self.skipTest(NOT_WRITTEN)

    def test_with_csv_path_returns_a_copy(self):
        """Settings has getters only; with_csv_path returns a copy and leaves the original unchanged."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
