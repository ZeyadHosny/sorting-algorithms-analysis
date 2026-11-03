"""
Description:
- The result record of one measured case and the CSV files built from it.
- Spec: ARCHITECTURE.md F-REC-1 - F-REC-5.
"""

from sorting_analysis.sorts import (bubble_sort, counted_bubble_sort, counted_merge_sort, counted_selection_sort,
                                    merge_sort, selection_sort)


# Algorithm name -> (plain sort, timed; counted sort, gives the counts), in the order used everywhere.
ALGORITHMS = {
    "bubble": (bubble_sort, counted_bubble_sort),
    "selection": (selection_sort, counted_selection_sort),
    "merge": (merge_sort, counted_merge_sort),
}
# CSV header of cases.csv.
CASE_FIELDS = ("experiment", "algorithm", "column", "order", "input_size", "comparisons", "writes", "swaps",
               "sorts_per_batch", "median_s", "min_s", "max_s")
# CSV header of timing_runs.csv.
RUN_FIELDS = ("experiment", "algorithm", "column", "order", "input_size", "batch", "seconds_per_sort")
# How a missing swap count (merge sort) is written in the CSV.
NOT_APPLICABLE = "n/a"


class CaseResult:
    """
    Description:
    - One algorithm measured on one input. Read-only.

    Attributes:
        __experiment (str): PRIVATE. 'scaling', 'order' or 'dupes'.
        __algorithm (str): PRIVATE. 'bubble', 'selection' or 'merge'.
        __column (str): PRIVATE. Dataset column of the input, e.g. 'median_income'.
        __order (str): PRIVATE. 'random', 'sorted', 'reversed' or 'nearly'.
        __input_size (int): PRIVATE. Number of values sorted, e.g. 2000.
        __sort_stats (SortStats): PRIVATE. Operation counts.
        __timing (TimingResult): PRIVATE. Timings of the batches.

    Methods:
        __init__: constructor.
        get_experiment, get_algorithm, get_column, get_order, get_input_size, get_sort_stats,
            get_timing: the only way to read each attribute.
    """

    # Constructor
    def __init__(self, experiment, algorithm, column, order, input_size, sort_stats, timing):
        """
        Description:
        - Constructor for the CaseResult class.

        Input arguments:
           experiment (str): 'scaling', 'order' or 'dupes'.
           algorithm (str): 'bubble', 'selection' or 'merge'.
           column (str): Dataset column of the input, e.g. 'median_income'.
           order (str): 'random', 'sorted', 'reversed' or 'nearly'.
           input_size (int): Number of values sorted, e.g. 2000.
           sort_stats (SortStats): Operation counts.
           timing (TimingResult): Timings of the batches.

        Return:
            None
        """
        self.__experiment = experiment
        self.__algorithm = algorithm
        self.__column = column
        self.__order = order
        self.__input_size = input_size
        self.__sort_stats = sort_stats
        self.__timing = timing

    # Method to read the experiment name
    def get_experiment(self):
        """
        Description:
        - Return the experiment name.

        Input arguments:
           None

        Return:
            str: 'scaling', 'order' or 'dupes'.
        """
        return self.__experiment

    # Method to read the algorithm name
    def get_algorithm(self):
        """
        Description:
        - Return the algorithm name.

        Input arguments:
           None

        Return:
            str: 'bubble', 'selection' or 'merge'.
        """
        return self.__algorithm

    # Method to read the column
    def get_column(self):
        """
        Description:
        - Return the column.

        Input arguments:
           None

        Return:
            str: Dataset column of the input, e.g. 'median_income'.
        """
        return self.__column

    # Method to read the input order
    def get_order(self):
        """
        Description:
        - Return the input order.

        Input arguments:
           None

        Return:
            str: 'random', 'sorted', 'reversed' or 'nearly'.
        """
        return self.__order

    # Method to read the input size
    def get_input_size(self):
        """
        Description:
        - Return the input size.

        Input arguments:
           None

        Return:
            int: Number of values sorted, e.g. 2000.
        """
        return self.__input_size

    # Method to read the counts
    def get_sort_stats(self):
        """
        Description:
        - Return the counts.

        Input arguments:
           None

        Return:
            SortStats: Operation counts.
        """
        return self.__sort_stats

    # Method to read the timings
    def get_timing(self):
        """
        Description:
        - Return the timings.

        Input arguments:
           None

        Return:
            TimingResult: Timings of the batches.
        """
        return self.__timing


# Function to flatten one case into a CSV row
def case_row(case):
    """
    Description:
    - Return the labels, the counts (get_sort_stats) and the timings (get_timing) as one row.

    Input arguments:
       case (CaseResult): Measured case.

    Return:
        dict: the CASE_FIELDS keys; swaps stays None for merge sort.
    """
    raise NotImplementedError("case_row: not implemented yet")


# Function to write cases.csv
def write_cases(cases, path):
    """
    Description:
    - Write case_row(case) for every case with the CASE_FIELDS header; swaps None is written as 'n/a'.

    Input arguments:
       cases (list[CaseResult]): Measured cases.
       path (str): Output CSV path.

    Return:
        None
    """
    raise NotImplementedError("write_cases: not implemented yet")


# Function to write timing_runs.csv
def write_runs(cases, path):
    """
    Description:
    - Write one row per timed batch with the RUN_FIELDS header.

    Input arguments:
       cases (list[CaseResult]): Measured cases.
       path (str): Output CSV path.

    Return:
        None
    """
    raise NotImplementedError("write_runs: not implemented yet")


# Function to write any list of rows to a CSV
def write_rows(rows, path, fieldnames):
    """
    Description:
    - Write the rows with csv.DictWriter and an explicit header.

    Input arguments:
       rows (list[dict]): Rows to write; an empty list writes a header-only file.
       path (str): Output CSV path.
       fieldnames (tuple[str]): Column order of the header.

    Return:
        None
    """
    raise NotImplementedError("write_rows: not implemented yet")


# Function to read cases.csv back with typed values
def read_cases(path):
    """
    Description:
    - Convert input_size, comparisons, writes, sorts_per_batch to int; median_s, min_s, max_s to float;
    - swaps to int, or None for 'n/a'.

    Input arguments:
       path (str): CSV written by write_cases.

    Return:
        list[dict]: one row per case (raises FileNotFoundError if missing, ValueError on a malformed number).
    """
    raise NotImplementedError("read_cases: not implemented yet")
