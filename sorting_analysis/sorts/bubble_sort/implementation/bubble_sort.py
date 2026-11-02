"""
Description:
- Bubble sort with early termination. Spec: ARCHITECTURE.md F-BUB-1 - F-BUB-6.
"""

from sorting_analysis.sorts.common import SortStats  # noqa: F401  (returned by the sort)


# Function to sort values with bubble sort
def bubble_sort(values):
    """
    Description:
    - Copy the input, then bubble sort the copy.
    - Each a[j] > a[j+1] is 1 comparison; each swap is 2 writes and 1 swap.
    - The inner range shrinks by one per pass; stop after a pass with no swaps.
    - The initial copy is not counted. Counters are local integers.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [3, 1, 2] -> ([1, 2, 3], 3 comparisons, 4 writes, 2 swaps).
    """
    raise NotImplementedError("bubble_sort: not implemented yet")
