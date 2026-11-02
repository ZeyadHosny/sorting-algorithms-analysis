"""Unit tests for config: the agreed default values and overriding them."""
import unittest

from sorting_analysis.config import DEFAULT_SETTINGS, Settings


class TestSettings(unittest.TestCase):
    """Default values and overriding them."""

    def test_defaults_match_the_agreed_settings(self):
        """Seeds 42/43/44, the eight scaling sizes, sample size 2000, 5 timed batches."""
        self.assertEqual((DEFAULT_SETTINGS.sample_seed, DEFAULT_SETTINGS.shuffle_seed,
                          DEFAULT_SETTINGS.nearly_sorted_seed), (42, 43, 44))
        self.assertEqual(DEFAULT_SETTINGS.scaling_sizes, (5, 10, 20, 250, 500, 1000, 2000, 4000))
        self.assertEqual(DEFAULT_SETTINGS.order_sample_size, 2000)
        self.assertEqual(DEFAULT_SETTINGS.timed_batches, 5)

    def test_override_changes_only_the_given_value(self):
        """Settings(order_sample_size=10) keeps every other default."""
        small = Settings(order_sample_size=10)
        self.assertEqual(small.order_sample_size, 10)
        self.assertEqual(small.scaling_sizes, DEFAULT_SETTINGS.scaling_sizes)
        self.assertEqual(small.csv_path, "housing.csv")


if __name__ == "__main__":
    unittest.main()
