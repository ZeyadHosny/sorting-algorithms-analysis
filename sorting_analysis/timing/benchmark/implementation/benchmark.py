"""
Description:
- Repeated, verified timing of one sort on one input.
- Only the plain sort (no counters) is timed. The timed region holds only its calls and storing
  their outputs; the timed outputs are verified against sorted() after the clock stops.
- The counted sort supplies the operation counts; it runs and is verified outside the clock.
- Garbage collection is off while timing.
- Spec: ARCHITECTURE.md F-BEN-1 - F-BEN-10.
"""

import gc
import time

from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.sorts import merge_sort


class TimingResult:
    """
    Description:
    - The timings of one case, filled in once by benchmark. Times are seconds per sort.

    Attributes:
        __batch_seconds (tuple[float]): PRIVATE. Seconds per sort, one value per timed batch, e.g. (2.1e-06, 2.0e-06).
        __sorts_per_batch (int): PRIVATE. Sorts per batch, e.g. 1000.
        __median_seconds (float): PRIVATE. Median of batch_seconds (computed with median_of).
        __min_seconds (float): PRIVATE. Fastest batch.
        __max_seconds (float): PRIVATE. Slowest batch.

    Methods:
        __init__: constructor.
        get_batch_seconds, get_sorts_per_batch, get_median_seconds, get_min_seconds,
            get_max_seconds: the only way to read each attribute.
    """

    # Constructor
    def __init__(self, batch_seconds, sorts_per_batch, median_seconds, min_seconds, max_seconds):
        """
        Description:
        - Constructor for the TimingResult class.

        Input arguments:
           batch_seconds (tuple[float]): Seconds per sort, one value per timed batch, e.g. (2.1e-06, 2.0e-06).
           sorts_per_batch (int): Sorts per batch, e.g. 1000.
           median_seconds (float): Median of batch_seconds (computed with median_of).
           min_seconds (float): Fastest batch.
           max_seconds (float): Slowest batch.

        Return:
            None
        """
        self.__batch_seconds = batch_seconds
        self.__sorts_per_batch = sorts_per_batch
        self.__median_seconds = median_seconds
        self.__min_seconds = min_seconds
        self.__max_seconds = max_seconds

    # Method to read the batch times
    def get_batch_seconds(self):
        """
        Description:
        - Return the batch times.

        Input arguments:
           None

        Return:
            tuple[float]: Seconds per sort, one value per timed batch, e.g. (2.1e-06, 2.0e-06).
        """
        return self.__batch_seconds

    # Method to read the sorts per batch
    def get_sorts_per_batch(self):
        """
        Description:
        - Return the sorts per batch.

        Input arguments:
           None

        Return:
            int: Sorts per batch, e.g. 1000.
        """
        return self.__sorts_per_batch

    # Method to read the median time
    def get_median_seconds(self):
        """
        Description:
        - Return the median time.

        Input arguments:
           None

        Return:
            float: Median of batch_seconds (computed with median_of).
        """
        return self.__median_seconds

    # Method to read the fastest time
    def get_min_seconds(self):
        """
        Description:
        - Return the fastest time.

        Input arguments:
           None

        Return:
            float: Fastest batch.
        """
        return self.__min_seconds

    # Method to read the slowest time
    def get_max_seconds(self):
        """
        Description:
        - Return the slowest time.

        Input arguments:
           None

        Return:
            float: Slowest batch.
        """
        return self.__max_seconds


class VerificationError(Exception):
    """
    Description:
    - Raised when an output differs from sorted(), the counts differ between runs,
      or the input list was modified.
    """


# Function to choose the number of sorts per timed batch
def repetitions_for(input_size, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Very small inputs are too fast to time once, so they are sorted many times per batch.
    - Return settings.small_input_repetitions if input_size <= settings.small_input_limit,
      otherwise settings.normal_input_repetitions.

    Input arguments:
       input_size (int): Number of values to sort, e.g. 5.
       settings (Settings): Run settings.

    Return:
        int: e.g. 1000 for 5 values, 1 for 250 values.
    """
    if input_size <= settings.small_input_limit:
        return settings.small_input_repetitions
    return settings.normal_input_repetitions


# Function to time one sort on one input and collect its counts
def benchmark(sort_function, counted_sort_function, values, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Run settings.timed_batches batches. In each batch:
      1. outside the clock, run counted_sort_function once; check its output against sorted(),
         that the input is unchanged, and that its counts equal the first batch's counts;
      2. time repetitions_for(len(values), settings) calls of sort_function with time.perf_counter(),
         storing each output;
      3. after the clock stops, verify every stored output against sorted() and that the input is unchanged.
    - Report seconds per sort for each batch, and their median, min and max.

    Input arguments:
       sort_function (function): Plain sort that is timed: bubble_sort, selection_sort or merge_sort.
       counted_sort_function (function): Its counted version: counted_bubble_sort, counted_selection_sort
          or counted_merge_sort.
       values (list[float]): Input values; must be unchanged afterwards.
       settings (Settings): Run settings (timed_batches and the repetition values).

    Return:
        tuple: (TimingResult, SortStats) (raises VerificationError if any check fails,
        and ValueError if the number of batches or sorts per batch is below 1)
    """
    sorts_per_batch = repetitions_for(len(values), settings)
    if settings.timed_batches < 1 or sorts_per_batch < 1:
        raise ValueError(f"Timed batches and sorts per batch must be at least 1, got "
                         f"{settings.timed_batches} and {sorts_per_batch}.")
    original_values = values[:]
    expected_output = sorted(original_values)
    batch_seconds = []
    first_stats = None

    for i in range(settings.timed_batches):
        # 1. Counted run, outside the clock.
        counted_output, sort_stats = counted_sort_function(values)
        _check_output(counted_output, expected_output, values, original_values)
        if first_stats is None:
            first_stats = sort_stats
        elif _counts_of(sort_stats) != _counts_of(first_stats):
            raise VerificationError(f"Counts changed between batches: {_counts_of(first_stats)} "
                                    f"then {_counts_of(sort_stats)}.")

        # 2. Timed run: only the plain sort and storing its outputs.
        outputs = [None] * sorts_per_batch
        gc_was_enabled = gc.isenabled()
        # Turn off garbage collection while timing, so its unpredictable pauses do not add to the measured time.
        gc.disable()
        try:
            start = time.perf_counter()
            for repetition in range(sorts_per_batch):
                outputs[repetition] = sort_function(values)
            elapsed = time.perf_counter() - start
        finally:
            if gc_was_enabled:
                gc.enable()

        # 3. Verification, after the clock stops.
        for output in outputs:
            _check_output(output, expected_output, values, original_values)
        batch_seconds.append(elapsed / sorts_per_batch)

    batch_seconds = tuple(batch_seconds)
    timing_result = TimingResult(batch_seconds, sorts_per_batch, median_of(list(batch_seconds)),
                                 min(batch_seconds), max(batch_seconds))
    return timing_result, first_stats


# Function to compute a median without sorted()
def median_of(values):
    """
    Description:
    - Sort the values with our plain merge_sort (sorted() is used only for verification) and take
      the middle value (the mean of the two middle values for an even count).

    Input arguments:
       values (list[float]): At least one value.

    Return:
        float: e.g. [3, 1, 2] -> 2.
    """
    ordered_values = merge_sort(values)
    middle = len(ordered_values) // 2
    if len(ordered_values) % 2 == 1:
        return ordered_values[middle]
    return (ordered_values[middle - 1] + ordered_values[middle]) / 2


# Function to check one sort output and the input after the sort
def _check_output(output, expected_output, values, original_values):
    """
    Description:
    - Check that the output equals sorted() of the input and that the input is unchanged.

    Input arguments:
       output (list[float]): Output of one sort.
       expected_output (list[float]): sorted() of the original input.
       values (list[float]): The input after the sort.
       original_values (list[float]): Copy of the input taken before any sort.

    Return:
        None (raises VerificationError if a check fails)
    """
    if output != expected_output:
        raise VerificationError("Sort output differs from sorted().")
    if values != original_values:
        raise VerificationError("The input list was modified by the sort.")


# Function to read the three counts of a SortStats
def _counts_of(sort_stats):
    """
    Description:
    - Return the counts of one counted run, to compare runs.

    Input arguments:
       sort_stats (SortStats): Counts of one counted run.

    Return:
        tuple: (comparisons, writes, swaps), e.g. (4, 4, 2).
    """
    return sort_stats.get_comparisons(), sort_stats.get_writes(), sort_stats.get_swaps()
