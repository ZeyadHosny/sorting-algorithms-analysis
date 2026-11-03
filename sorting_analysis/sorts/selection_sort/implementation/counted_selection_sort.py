"""
Description:
- Selection sort with operation counters: the version that supplies the counts.
- Same loops as selection_sort; it is never timed. Spec: ARCHITECTURE.md F-SEL-1 - F-SEL-5.
"""

from sorting_analysis.sorts.common import SortStats  # noqa: F401  (returned by the sort)


# Function to sort values with selection sort and count its operations
def counted_selection_sort(values):
    """
    Description:
    - Same algorithm as selection_sort.
    - Every comparison made while searching for the minimum is 1 comparison.
    - Swap only when the minimum is not already in place; a swap is 2 writes and 1 swap.
    - The initial copy (values[:]) is a slicing copy and is not counted. Counters are local integers.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [3, 1, 2] -> ([1, 2, 3], 3 comparisons, 4 writes, 2 swaps).
    """
    raise NotImplementedError("counted_selection_sort: not implemented yet")
