"""Unit tests for timing.benchmark (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.timing import TimingResult, VerificationError, benchmark, median_of, repetitions_for  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestRepetitionsFor(unittest.TestCase):
    """Sorts per timed batch for each input size."""

    def test_very_small_inputs(self):
        """repetitions_for(5), repetitions_for(20) -> 1000 with the default settings."""
        self.skipTest(NOT_WRITTEN)

    def test_normal_inputs(self):
        """repetitions_for(21), repetitions_for(250) -> 1 with the default settings."""
        self.skipTest(NOT_WRITTEN)


class TestMedianOf(unittest.TestCase):
    """Median without sorted()."""

    def test_odd_count(self):
        """median_of([3, 1, 2]) == 2."""
        self.skipTest(NOT_WRITTEN)

    def test_even_count(self):
        """median_of([4, 1, 3, 2]) == 2.5."""
        self.skipTest(NOT_WRITTEN)


class TestTimingResult(unittest.TestCase):
    """Statistics filled in by benchmark."""

    def test_benchmark_fills_median_min_max(self):
        """get_median_seconds() == median_of(batch_seconds); get_min_seconds() and get_max_seconds() are the extremes."""
        self.skipTest(NOT_WRITTEN)


class TestBenchmark(unittest.TestCase):
    """Batches, verification and side effects."""

    def test_small_input_uses_small_reps(self):
        """5 values with default settings -> sorts_per_batch 1000, 5 batch times."""
        self.skipTest(NOT_WRITTEN)

    def test_normal_input_uses_one_rep(self):
        """250 values -> sorts_per_batch 1, 5 batch times."""
        self.skipTest(NOT_WRITTEN)

    def test_wrong_output_raises(self):
        """A sort returning an unsorted list -> VerificationError."""
        self.skipTest(NOT_WRITTEN)

    def test_every_repetition_is_verified(self):
        """A sort that is wrong only on its first call and correct afterwards -> VerificationError."""
        self.skipTest(NOT_WRITTEN)

    def test_changing_counts_raise(self):
        """A sort whose counts differ between calls -> VerificationError."""
        self.skipTest(NOT_WRITTEN)

    def test_modified_input_raises(self):
        """A sort that mutates its input -> VerificationError."""
        self.skipTest(NOT_WRITTEN)

    def test_garbage_collection_state_is_restored(self):
        """gc enabled before -> enabled after; disabled before -> disabled after."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
