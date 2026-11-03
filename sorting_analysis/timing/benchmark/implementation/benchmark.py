"""
Description:
- Repeated, verified timing of one sort on one input.
- Only the plain sort (no counters) is timed. The timed region holds only its calls and storing
  their outputs; verification against sorted() runs after the clock stops.
- The counted sort supplies the operation counts; it runs outside the clock.
- Garbage collection is off while timing.
- Spec: ARCHITECTURE.md F-BEN-1 - F-BEN-10.
"""

from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.sorts import merge_sort  # noqa: F401  (used by median_of)


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
    raise NotImplementedError("repetitions_for: not implemented yet")


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
        tuple: (TimingResult, SortStats) (raises VerificationError if any check fails)
    """
    raise NotImplementedError("benchmark: not implemented yet")


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
    raise NotImplementedError("median_of: not implemented yet")
