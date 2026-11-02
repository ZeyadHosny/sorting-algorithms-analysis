"""Unit tests for analysis.common.filters (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.analysis import scaling_cases  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestScalingCases(unittest.TestCase):
    """Selecting scaling rows."""

    def test_keeps_only_scaling_rows(self):
        """input_size 2000 present in scaling, order and dupes -> only the scaling row is kept."""
        self.skipTest(NOT_WRITTEN)

    def test_empty_input(self):
        """[] -> []."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
