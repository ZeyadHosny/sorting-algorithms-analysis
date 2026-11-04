"""Unit tests for data.sampling (drafts: each test is skipped until it is written)."""
import random
import unittest

from sorting_analysis.data import sample_indices, shuffle_indices  # noqa: F401

# Skip message of the drafted tests that are not written yet.
NOT_WRITTEN = "test not implemented yet"


class TestSampleIndices(unittest.TestCase):
    """Seeded sampling without replacement."""

    def test_same_seed_gives_same_indices(self):
        """Two calls with seed 42 -> identical lists."""
        usable_indices = list(range(100))
        first = sample_indices(usable_indices, 10, 42)
        sample_indices(usable_indices, 5, 99)
        second = sample_indices(usable_indices, 10, 42)

        self.assertEqual(first, second)

    def test_indices_are_distinct_members_of_usable_indices(self):
        """sample_size 50 from range(100) -> 50 distinct values, all in usable_indices."""
        usable_indices = list(range(100))
        result = sample_indices(usable_indices, 50, 42)

        self.assertEqual(len(result), 50)
        self.assertEqual(len(set(result)), 50)
        for row_index in result:
            self.assertIn(row_index, usable_indices)

        nonconsecutive = [4, 17, 80, 350, 900]
        result = sample_indices(nonconsecutive, 3, 42)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(set(result)), 3)
        for row_index in result:
            self.assertIn(row_index, nonconsecutive)

    def test_usable_indices_are_unchanged(self):
        """usable_indices is equal before and after the call."""
        usable_indices = [4, 17, 80, 350, 900]
        original = usable_indices[:]

        result = sample_indices(usable_indices, 3, 42)

        self.assertEqual(usable_indices, original)
        self.assertIsNot(result, usable_indices)

    def test_too_large_sample_raises(self):
        """sample_size > len(usable_indices) -> ValueError."""
        with self.assertRaises(ValueError):
            sample_indices([2, 5, 9], 4, 42)


class TestShuffleIndices(unittest.TestCase):
    """Seeded shuffling."""

    def test_same_seed_gives_same_order(self):
        """Two calls with seed 43 -> identical order."""
        row_indices = list(range(20))
        first = shuffle_indices(row_indices, 43)
        shuffle_indices(row_indices, 99)
        second = shuffle_indices(row_indices, 43)

        self.assertEqual(first, second)

    def test_result_is_a_permutation_of_the_input(self):
        """Same multiset of indices; input list unchanged."""
        row_indices = [4, 17, 80, 350, 900]
        original = row_indices[:]

        result = shuffle_indices(row_indices, 43)

        self.assertCountEqual(result, original)
        self.assertEqual(row_indices, original)
        self.assertIsNot(result, row_indices)

        repeated_indices = [4, 4, 17, 80]
        self.assertCountEqual(shuffle_indices(repeated_indices, 43), repeated_indices)


class TestSamplingEdgeCases(unittest.TestCase):
    """Check size boundaries, short inputs and isolated random state."""

    # Check the smallest and largest valid sample sizes
    def test_zero_and_full_size_samples(self):
        """Zero returns an empty list; a full-size sample retains every index."""
        usable_indices = [4, 17, 80]
        self.assertEqual(sample_indices(usable_indices, 0, 42), [])
        self.assertEqual(sample_indices([], 0, 42), [])
        self.assertCountEqual(sample_indices(usable_indices, 3, 42), usable_indices)

    # Check that a negative requested size is rejected
    def test_negative_sample_size_raises(self):
        """A negative sample size raises ValueError."""
        with self.assertRaises(ValueError):
            sample_indices([4, 17, 80], -1, 42)

    # Check that even an unchanged order is returned as a new list
    def test_shuffle_empty_and_singleton(self):
        """Empty and singleton inputs return equal new lists."""
        for row_indices in ([], [17]):
            with self.subTest(row_indices=row_indices):
                result = shuffle_indices(row_indices, 43)
                self.assertEqual(result, row_indices)
                self.assertIsNot(result, row_indices)

    # Check that the functions do not alter the module-level random generator
    def test_global_random_state_is_unchanged(self):
        """Local seeded generators leave the global random state unchanged."""
        before = random.getstate()
        sample_indices(list(range(100)), 20, 42)
        shuffle_indices(list(range(100)), 43)
        self.assertEqual(random.getstate(), before)


if __name__ == "__main__":
    unittest.main()
