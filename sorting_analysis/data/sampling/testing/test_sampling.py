"""Unit tests for data.sampling (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.data import sample_indices, shuffle_indices  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestSampleIndices(unittest.TestCase):
    """Seeded sampling without replacement."""

    def test_same_seed_gives_same_indices(self):
        """Two calls with seed 42 -> identical lists."""
        self.skipTest(NOT_WRITTEN)

    def test_indices_are_distinct_members_of_usable_indices(self):
        """sample_size 50 from range(100) -> 50 distinct values, all in usable_indices."""
        self.skipTest(NOT_WRITTEN)

    def test_usable_indices_are_unchanged(self):
        """usable_indices is equal before and after the call."""
        self.skipTest(NOT_WRITTEN)

    def test_too_large_sample_raises(self):
        """sample_size > len(usable_indices) -> ValueError."""
        self.skipTest(NOT_WRITTEN)


class TestShuffleIndices(unittest.TestCase):
    """Seeded shuffling."""

    def test_same_seed_gives_same_order(self):
        """Two calls with seed 43 -> identical order."""
        self.skipTest(NOT_WRITTEN)

    def test_result_is_a_permutation_of_the_input(self):
        """Same multiset of indices; input list unchanged."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
