"""
Description:
- Selection sort that swaps only when the minimum is not already in place.
- Spec: ARCHITECTURE.md F-SEL-1 - F-SEL-4.
"""

from sorting_analysis.sorts.common import SortStats  # noqa: F401  (returned by the sort)


# Function to sort values with selection sort
def selection_sort(values):
    """
    Description:
    - Copy the input, then selection sort the copy.
    - Every comparison made while searching for the minimum is counted.
    - Swap only when the minimum is not already in place; a swap is 2 writes.
    - The initial copy is not counted.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [3, 1, 2] -> ([1, 2, 3], 3 comparisons, 4 writes, 2 swaps).
    """
    raise NotImplementedError("selection_sort: not implemented yet")
