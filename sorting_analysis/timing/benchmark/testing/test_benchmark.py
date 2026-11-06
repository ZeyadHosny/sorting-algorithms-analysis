"""Unit tests for timing.benchmark."""
import gc
import random
import unittest
from unittest.mock import patch

from sorting_analysis.config import Settings
from sorting_analysis.sorts import (SortStats, bubble_sort, counted_bubble_sort, counted_merge_sort,
                                    counted_selection_sort, merge_sort, selection_sort)
from sorting_analysis.timing import TimingResult, VerificationError, benchmark, median_of, repetitions_for

# Module of the benchmark implementation, used only as a patch target (where its names are looked up).
BENCHMARK_MODULE = "sorting_analysis.timing.benchmark.implementation.benchmark"


class FakeClock:
    """
    Description:
    - Stand-in for time.perf_counter: returns preset start and stop times, so every batch lasts a
      known duration, and tracks whether the clock is running.

    Attributes:
        __times (list[float]): PRIVATE. Times still to return, in order (start, stop, start, stop, ...).
        __running (bool): PRIVATE. True between a start call and its stop call.

    Methods:
        __init__: constructor.
        perf_counter: return the next time and switch between running and stopped.
        is_running: whether the clock is running.
    """

    # Constructor
    def __init__(self, batch_durations):
        """
        Description:
        - Constructor for the FakeClock class: one start and one stop time per batch.

        Input arguments:
           batch_durations (list[float]): Seconds each batch lasts, e.g. [3.0, 1.0].

        Return:
            None
        """
        times = []
        now = 0.0
        for duration in batch_durations:
            times.append(now)
            now += duration
            times.append(now)
            now += 1.0
        self.__times = times
        self.__running = False

    # Method to return the next time, as time.perf_counter would
    def perf_counter(self):
        """
        Description:
        - Return the next preset time; each call starts or stops the clock.

        Input arguments:
           None

        Return:
            float: the next time, e.g. 0.0 then 3.0.
        """
        self.__running = not self.__running
        return self.__times.pop(0)

    # Method to read whether the clock is running
    def is_running(self):
        """
        Description:
        - Return whether the clock is running.

        Input arguments:
           None

        Return:
            bool: True between a start call and its stop call.
        """
        return self.__running


class FakeSorts:
    """
    Description:
    - A plain and a counted sort that record each call (clock and garbage-collection state) and can be
      told to fail on purpose. Correct outputs come from our merge_sort.

    Attributes:
        __clock (FakeClock or None): PRIVATE. Clock to read during each call, or None.
        __wrong_plain_calls (tuple[int]): PRIVATE. Plain calls (1 = first) that return an unsorted list.
        __wrong_counted_calls (tuple[int]): PRIVATE. Counted calls (1 = first) that return an unsorted list.
        __changed_count (str or None): PRIVATE. 'comparisons', 'writes' or 'swaps': that count changes
            from the second counted call on.
        __modify_input (str or None): PRIVATE. 'plain' or 'counted': that version sorts its input in place.
        __failing_plain_call (int or None): PRIVATE. Plain call that raises RuntimeError.
        __plain_calls (list[bool]): PRIVATE. Whether the clock was running, one value per plain call.
        __counted_calls (list[bool]): PRIVATE. Whether the clock was running, one value per counted call.
        __plain_gc_states (list[bool]): PRIVATE. Whether garbage collection was on, one value per plain call.
        __counted_gc_states (list[bool]): PRIVATE. Whether garbage collection was on, one value per counted call.

    Methods:
        __init__: constructor.
        plain, counted: the two sort versions passed to benchmark.
        get_plain_calls, get_counted_calls, get_plain_gc_states, get_counted_gc_states: the recorded calls.
    """

    # Constructor
    def __init__(self, clock=None, wrong_plain_calls=(), wrong_counted_calls=(), changed_count=None,
                 modify_input=None, failing_plain_call=None):
        """
        Description:
        - Constructor for the FakeSorts class.

        Input arguments:
           clock (FakeClock or None): Clock to read during each call.
           wrong_plain_calls (tuple[int]): Plain calls that return an unsorted list, e.g. (1,).
           wrong_counted_calls (tuple[int]): Counted calls that return an unsorted list, e.g. (3,).
           changed_count (str or None): 'comparisons', 'writes' or 'swaps' changes from the second counted call.
           modify_input (str or None): 'plain' or 'counted' sorts its input in place (output stays correct).
           failing_plain_call (int or None): Plain call that raises RuntimeError, e.g. 500.

        Return:
            None
        """
        self.__clock = clock
        self.__wrong_plain_calls = wrong_plain_calls
        self.__wrong_counted_calls = wrong_counted_calls
        self.__changed_count = changed_count
        self.__modify_input = modify_input
        self.__failing_plain_call = failing_plain_call
        self.__plain_calls = []
        self.__counted_calls = []
        self.__plain_gc_states = []
        self.__counted_gc_states = []

    # Method used as the plain sort
    def plain(self, values):
        """
        Description:
        - Record the call, then return a sorted copy (or an unsorted one, or raise, if this call is set to fail).

        Input arguments:
           values (list[float]): Input to sort.

        Return:
            list[float]: the output.
        """
        self.__plain_calls.append(self.__clock is not None and self.__clock.is_running())
        self.__plain_gc_states.append(gc.isenabled())
        if len(self.__plain_calls) == self.__failing_plain_call:
            raise RuntimeError("plain sort failed")
        if self.__modify_input == "plain":
            values[:] = merge_sort(values)
        if len(self.__plain_calls) in self.__wrong_plain_calls:
            return merge_sort(values)[::-1]
        return merge_sort(values)

    # Method used as the counted sort
    def counted(self, values):
        """
        Description:
        - Record the call, then return a sorted copy and the counts (3, 4, 2), or the configured fault.

        Input arguments:
           values (list[float]): Input to sort.

        Return:
            tuple: (output, SortStats).
        """
        self.__counted_calls.append(self.__clock is not None and self.__clock.is_running())
        self.__counted_gc_states.append(gc.isenabled())
        call_number = len(self.__counted_calls)
        if self.__modify_input == "counted":
            values[:] = merge_sort(values)
        output = merge_sort(values)
        if call_number in self.__wrong_counted_calls:
            output = output[::-1]
        extra = 1 if call_number > 1 else 0
        comparisons = 3 + (extra if self.__changed_count == "comparisons" else 0)
        writes = 4 + (extra if self.__changed_count == "writes" else 0)
        swaps = 2 + (extra if self.__changed_count == "swaps" else 0)
        return output, SortStats(comparisons, writes, swaps)

    # Method to read the recorded plain calls
    def get_plain_calls(self):
        """
        Description:
        - Return the recorded plain calls.

        Input arguments:
           None

        Return:
            list[bool]: whether the clock was running, one value per plain call.
        """
        return self.__plain_calls

    # Method to read the recorded counted calls
    def get_counted_calls(self):
        """
        Description:
        - Return the recorded counted calls.

        Input arguments:
           None

        Return:
            list[bool]: whether the clock was running, one value per counted call.
        """
        return self.__counted_calls

    # Method to read the garbage-collection state of the plain calls
    def get_plain_gc_states(self):
        """
        Description:
        - Return the garbage-collection state recorded in each plain call.

        Input arguments:
           None

        Return:
            list[bool]: whether garbage collection was on, one value per plain call.
        """
        return self.__plain_gc_states

    # Method to read the garbage-collection state of the counted calls
    def get_counted_gc_states(self):
        """
        Description:
        - Return the garbage-collection state recorded in each counted call.

        Input arguments:
           None

        Return:
            list[bool]: whether garbage collection was on, one value per counted call.
        """
        return self.__counted_gc_states


class TestRepetitionsFor(unittest.TestCase):
    """Sorts per timed batch for each input size."""

    def test_very_small_inputs(self):
        """repetitions_for(0), (1), (5), (20) -> 1000 with the default settings."""
        for input_size in (0, 1, 5, 20):
            self.assertEqual(repetitions_for(input_size), 1000)

    def test_normal_inputs(self):
        """repetitions_for(21), (250), (4000) -> 1 with the default settings."""
        for input_size in (21, 250, 4000):
            self.assertEqual(repetitions_for(input_size), 1)

    def test_uses_the_settings(self):
        """Limit 5, 10 small and 2 normal repetitions -> 5 values give 10, 6 values give 2."""
        settings = Settings(small_input_limit=5, small_input_repetitions=10, normal_input_repetitions=2)
        self.assertEqual(repetitions_for(5, settings), 10)
        self.assertEqual(repetitions_for(6, settings), 2)


class TestMedianOf(unittest.TestCase):
    """Median without sorted()."""

    def test_odd_count(self):
        """median_of([3, 1, 2]) == 2."""
        self.assertEqual(median_of([3, 1, 2]), 2)

    def test_even_count(self):
        """median_of([4, 1, 3, 2]) == 2.5."""
        self.assertEqual(median_of([4, 1, 3, 2]), 2.5)

    def test_single_value_and_duplicates(self):
        """median_of([7]) == 7; median_of([5, 1, 5, 3]) == 4.0; median_of([2, 2, 2]) == 2."""
        self.assertEqual(median_of([7]), 7)
        self.assertEqual(median_of([5, 1, 5, 3]), 4.0)
        self.assertEqual(median_of([2, 2, 2]), 2)

    def test_keeps_input_and_uses_merge_sort(self):
        """The input list is unchanged, merge_sort is called once on it, and sorted() is never used."""
        values = [9.0, 1.0, 5.0, 3.0, 7.0]
        with patch(BENCHMARK_MODULE + ".merge_sort", wraps=merge_sort) as merge_sort_spy:
            with patch("builtins.sorted", side_effect=AssertionError("sorted() used")):
                self.assertEqual(median_of(values), 5.0)
        merge_sort_spy.assert_called_once_with(values)
        self.assertEqual(values, [9.0, 1.0, 5.0, 3.0, 7.0])


class TestTimingResult(unittest.TestCase):
    """Statistics filled in by benchmark."""

    def test_getters_return_the_constructor_values(self):
        """TimingResult((2.0, 1.0), 1000, 1.5, 1.0, 2.0) -> each getter returns its value."""
        timing_result = TimingResult((2.0, 1.0), 1000, 1.5, 1.0, 2.0)
        self.assertEqual(timing_result.get_batch_seconds(), (2.0, 1.0))
        self.assertEqual(timing_result.get_sorts_per_batch(), 1000)
        self.assertEqual(timing_result.get_median_seconds(), 1.5)
        self.assertEqual(timing_result.get_min_seconds(), 1.0)
        self.assertEqual(timing_result.get_max_seconds(), 2.0)

    def test_benchmark_fills_median_min_max(self):
        """Batches of 3, 1, 2, 5, 4 s with 1000 sorts -> 0.003, 0.001, 0.002, 0.005, 0.004 s per sort;
        median 0.003, min 0.001, max 0.005."""
        clock = FakeClock([3.0, 1.0, 2.0, 5.0, 4.0])
        fake_sorts = FakeSorts(clock)
        with patch("time.perf_counter", clock.perf_counter):
            timing_result, sort_stats = benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
        expected = (0.003, 0.001, 0.002, 0.005, 0.004)
        self.assertEqual(len(timing_result.get_batch_seconds()), len(expected))
        for batch_time, expected_time in zip(timing_result.get_batch_seconds(), expected):
            self.assertAlmostEqual(batch_time, expected_time)
        self.assertIsInstance(timing_result.get_batch_seconds(), tuple)
        self.assertEqual(timing_result.get_sorts_per_batch(), 1000)
        self.assertAlmostEqual(timing_result.get_median_seconds(), 0.003)
        self.assertAlmostEqual(timing_result.get_min_seconds(), 0.001)
        self.assertAlmostEqual(timing_result.get_max_seconds(), 0.005)

    def test_even_number_of_batches(self):
        """4 batches of 1, 2, 3, 4 s with 1 sort each -> median 2.5 s."""
        clock = FakeClock([1.0, 2.0, 3.0, 4.0])
        fake_sorts = FakeSorts(clock)
        values = list(range(250, 0, -1))
        with patch("time.perf_counter", clock.perf_counter):
            timing_result, sort_stats = benchmark(fake_sorts.plain, fake_sorts.counted, values,
                                                  Settings(timed_batches=4))
        self.assertEqual(timing_result.get_sorts_per_batch(), 1)
        self.assertAlmostEqual(timing_result.get_median_seconds(), 2.5)


class TestBenchmark(unittest.TestCase):
    """Batches, the two sort versions, verification and side effects."""

    def test_small_input_uses_small_reps(self):
        """5 values with default settings -> sorts_per_batch 1000, 5 batch times, 5000 plain calls."""
        fake_sorts = FakeSorts()
        timing_result, sort_stats = benchmark(fake_sorts.plain, fake_sorts.counted, [5, 4, 3, 2, 1])
        self.assertEqual(timing_result.get_sorts_per_batch(), 1000)
        self.assertEqual(len(timing_result.get_batch_seconds()), 5)
        self.assertEqual(len(fake_sorts.get_plain_calls()), 5000)

    def test_normal_input_uses_one_rep(self):
        """250 values -> sorts_per_batch 1, 5 batch times, 5 plain calls."""
        fake_sorts = FakeSorts()
        timing_result, sort_stats = benchmark(fake_sorts.plain, fake_sorts.counted, list(range(250)))
        self.assertEqual(timing_result.get_sorts_per_batch(), 1)
        self.assertEqual(len(timing_result.get_batch_seconds()), 5)
        self.assertEqual(len(fake_sorts.get_plain_calls()), 5)

    def test_only_plain_sort_is_timed(self):
        """A fake clock records when each sort runs: every plain call is inside the timed region,
        every counted call outside it."""
        clock = FakeClock([1.0] * 5)
        fake_sorts = FakeSorts(clock)
        with patch("time.perf_counter", clock.perf_counter):
            benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
        self.assertEqual(len(fake_sorts.get_plain_calls()), 5000)
        self.assertTrue(all(fake_sorts.get_plain_calls()))
        self.assertEqual(len(fake_sorts.get_counted_calls()), 5)
        self.assertFalse(any(fake_sorts.get_counted_calls()))
        self.assertFalse(clock.is_running())

    def test_counted_sort_runs_once_per_batch(self):
        """5 batches -> counted_sort_function called 5 times; the returned SortStats has its counts (3, 4, 2)."""
        fake_sorts = FakeSorts()
        timing_result, sort_stats = benchmark(fake_sorts.plain, fake_sorts.counted, list(range(250)))
        self.assertEqual(len(fake_sorts.get_counted_calls()), 5)
        self.assertEqual((sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()), (3, 4, 2))

    def test_wrong_output_raises(self):
        """A plain sort wrong on its first call, or a counted sort wrong on its first or third call -> VerificationError."""
        for fake_sorts in (FakeSorts(wrong_plain_calls=(1,)), FakeSorts(wrong_counted_calls=(1,)),
                           FakeSorts(wrong_counted_calls=(3,))):
            with self.assertRaises(VerificationError):
                benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])

    def test_every_repetition_is_verified(self):
        """A plain sort that is wrong only on its first, its 500th or its last (5000th) call -> VerificationError."""
        for wrong_call in (1, 500, 5000):
            fake_sorts = FakeSorts(wrong_plain_calls=(wrong_call,))
            with self.assertRaises(VerificationError):
                benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])

    def test_timed_outputs_are_verified_after_the_clock_stops(self):
        """A wrong timed output is reported only after the clock has stopped."""
        clock = FakeClock([1.0] * 5)
        fake_sorts = FakeSorts(clock, wrong_plain_calls=(1,))
        with patch("time.perf_counter", clock.perf_counter):
            with self.assertRaises(VerificationError):
                benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
        self.assertFalse(clock.is_running())
        self.assertEqual(len(fake_sorts.get_plain_calls()), 1000)

    def test_every_check_runs_outside_the_clock(self):
        """Every output check (5 counted + 5000 timed) and the sorted() call run while the clock is stopped."""
        clock = FakeClock([1.0] * 5)
        fake_sorts = FakeSorts(clock)
        check_states = []
        sorted_states = []
        real_sorted = sorted

        # Function to record the clock state of one output check
        def record_check(output, expected_output, values, original_values):
            """
            Description:
            - Stand-in for _check_output: record whether the clock is running.

            Input arguments:
               output, expected_output, values, original_values: as in _check_output.

            Return:
                None
            """
            check_states.append(clock.is_running())

        # Function to record the clock state of one sorted() call
        def record_sorted(values):
            """
            Description:
            - Stand-in for sorted(): record whether the clock is running, then sort with the real sorted().

            Input arguments:
               values (list[float]): Values to sort.

            Return:
                list[float]: the sorted values.
            """
            sorted_states.append(clock.is_running())
            return real_sorted(values)

        with patch("time.perf_counter", clock.perf_counter):
            with patch(BENCHMARK_MODULE + "._check_output", side_effect=record_check):
                with patch("builtins.sorted", side_effect=record_sorted):
                    benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
        self.assertEqual(len(check_states), 5005)
        self.assertFalse(any(check_states))
        self.assertTrue(len(sorted_states) >= 1)
        self.assertFalse(any(sorted_states))

    def test_changing_counts_raise(self):
        """Only the comparisons, only the writes or only the swaps change from the second batch -> VerificationError."""
        for count_name in ("comparisons", "writes", "swaps"):
            fake_sorts = FakeSorts(changed_count=count_name)
            with self.assertRaises(VerificationError):
                benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
            self.assertEqual(len(fake_sorts.get_counted_calls()), 2)

    def test_modified_input_raises(self):
        """A plain or counted sort that sorts its input in place but returns a correct output -> VerificationError."""
        for version in ("plain", "counted"):
            fake_sorts = FakeSorts(modify_input=version)
            with self.assertRaises(VerificationError):
                benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])

    def test_invalid_settings_raise_before_any_sort(self):
        """0 or -1 batches, 0 or -3 small repetitions, 0 normal repetitions -> ValueError, and neither sort is called."""
        cases = ((Settings(timed_batches=0), [3, 1, 2]), (Settings(timed_batches=-1), [3, 1, 2]),
                 (Settings(small_input_repetitions=0), [3, 1, 2]), (Settings(small_input_repetitions=-3), [3, 1, 2]),
                 (Settings(normal_input_repetitions=0), list(range(250))))
        for settings, values in cases:
            fake_sorts = FakeSorts()
            with self.assertRaises(ValueError):
                benchmark(fake_sorts.plain, fake_sorts.counted, values, settings)
            self.assertEqual(fake_sorts.get_plain_calls(), [])
            self.assertEqual(fake_sorts.get_counted_calls(), [])

    def test_garbage_collection_state_is_restored(self):
        """gc enabled before -> enabled after; disabled before -> disabled after; also after a failed check."""
        gc_was_enabled = gc.isenabled()
        try:
            for start_enabled in (True, False):
                for fake_sorts in (FakeSorts(), FakeSorts(wrong_plain_calls=(1,))):
                    if start_enabled:
                        gc.enable()
                    else:
                        gc.disable()
                    try:
                        benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
                    except VerificationError:
                        pass
                    self.assertEqual(gc.isenabled(), start_enabled)
        finally:
            if gc_was_enabled:
                gc.enable()
            else:
                gc.disable()

    def test_garbage_collection_is_off_only_while_timing(self):
        """gc enabled before -> off in every plain call, on in every counted call."""
        gc_was_enabled = gc.isenabled()
        gc.enable()
        try:
            fake_sorts = FakeSorts()
            benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
        finally:
            if not gc_was_enabled:
                gc.disable()
        self.assertEqual(len(fake_sorts.get_plain_gc_states()), 5000)
        self.assertFalse(any(fake_sorts.get_plain_gc_states()))
        self.assertEqual(len(fake_sorts.get_counted_gc_states()), 5)
        self.assertTrue(all(fake_sorts.get_counted_gc_states()))

    def test_garbage_collection_restored_after_error_while_timing(self):
        """A plain sort that raises on its 500th call -> the error propagates and gc is back to its previous state."""
        gc_was_enabled = gc.isenabled()
        try:
            for start_enabled in (True, False):
                if start_enabled:
                    gc.enable()
                else:
                    gc.disable()
                fake_sorts = FakeSorts(failing_plain_call=500)
                with self.assertRaises(RuntimeError):
                    benchmark(fake_sorts.plain, fake_sorts.counted, [3, 1, 2])
                self.assertEqual(gc.isenabled(), start_enabled)
        finally:
            if gc_was_enabled:
                gc.enable()
            else:
                gc.disable()

    def test_empty_and_single_value(self):
        """[] and [7] with the real sorts -> 1000 sorts per batch, counts (0, 0, 0)."""
        for values in ([], [7.0]):
            original = values[:]
            timing_result, sort_stats = benchmark(bubble_sort, counted_bubble_sort, values)
            self.assertEqual(timing_result.get_sorts_per_batch(), 1000)
            self.assertEqual((sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()), (0, 0, 0))
            self.assertEqual(values, original)

    def test_real_sorts(self):
        """Bubble, selection and merge sort on 250 seeded random values -> 5 positive batch times,
        the counted version's counts, and the input unchanged."""
        generator = random.Random(1)
        values = [generator.uniform(0.5, 15.0) for i in range(250)]
        original = values[:]
        for sort_function, counted_sort_function in ((bubble_sort, counted_bubble_sort),
                                                     (selection_sort, counted_selection_sort),
                                                     (merge_sort, counted_merge_sort)):
            timing_result, sort_stats = benchmark(sort_function, counted_sort_function, values)
            output, expected_stats = counted_sort_function(values)
            self.assertEqual(len(timing_result.get_batch_seconds()), 5)
            self.assertTrue(all(batch_time > 0 for batch_time in timing_result.get_batch_seconds()))
            self.assertEqual((sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()),
                             (expected_stats.get_comparisons(), expected_stats.get_writes(),
                              expected_stats.get_swaps()))
            self.assertEqual(values, original)


if __name__ == "__main__":
    unittest.main()
