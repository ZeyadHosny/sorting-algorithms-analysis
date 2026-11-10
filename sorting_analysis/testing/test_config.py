"""Unit tests for config: the default values and overriding them."""
import unittest

from sorting_analysis.config import DEFAULT_SETTINGS, Settings


class TestSettings(unittest.TestCase):
    """Default values and overriding them."""

    def test_default_settings(self):
        """Default seeds, scaling sizes, sample size, timed batches, fitted sizes and experiment columns."""
        self.assertEqual((DEFAULT_SETTINGS.sample_seed, DEFAULT_SETTINGS.shuffle_seed,
                          DEFAULT_SETTINGS.nearly_sorted_seed), (42, 43, 44))
        self.assertEqual(DEFAULT_SETTINGS.scaling_sizes, (5, 10, 20, 250, 500, 1000, 2000, 4000))
        self.assertEqual(DEFAULT_SETTINGS.order_sample_size, 2000)
        self.assertEqual(DEFAULT_SETTINGS.timed_batches, 5)
        self.assertEqual(DEFAULT_SETTINGS.extrapolation_base_sizes, (250, 500, 1000, 2000, 4000))
        self.assertEqual((DEFAULT_SETTINGS.scaling_column, DEFAULT_SETTINGS.order_column),
                         ("median_income", "median_income"))
        self.assertIn(DEFAULT_SETTINGS.order_column, DEFAULT_SETTINGS.selected_columns)

    def test_override_changes_only_the_given_value(self):
        """Settings(order_sample_size=10) keeps every other default."""
        small = Settings(order_sample_size=10)
        self.assertEqual(small.order_sample_size, 10)
        self.assertEqual(small.scaling_sizes, DEFAULT_SETTINGS.scaling_sizes)
        self.assertEqual(small.csv_path, "housing.csv")


if __name__ == "__main__":
    unittest.main()
