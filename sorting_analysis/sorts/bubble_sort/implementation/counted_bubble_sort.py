"""
Description:
- Bubble sort with early termination and operation counters: the version that supplies the counts.
- Same loops as bubble_sort; it is never timed. Spec: ARCHITECTURE.md F-BUB-1 - F-BUB-7.
"""

from sorting_analysis.sorts.common import SortStats  # noqa: F401  (returned by the sort)


# Function to sort values with bubble sort and count its operations
def counted_bubble_sort(values):
    """
    Description:
    - Same algorithm as bubble_sort: full passes over the whole list, stop after a full pass with no swaps.
    - Each a[j-1] > a[j] is 1 comparison; each swap is 2 writes and 1 swap.
    - The initial copy (values[:]) is a slicing copy and is not counted. Counters are local integers.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [3, 1, 2] -> ([1, 2, 3], 4 comparisons, 4 writes, 2 swaps).
    """
    a = values[:]
    comparisons = 0
    writes = 0
    swaps = 0
    swapped = True

    while swapped:
        swapped = False
        for j in range(1, len(a)):
            comparisons += 1
            if a[j - 1] > a[j]:
                a[j - 1], a[j] = a[j], a[j - 1]
                writes += 2
                swaps += 1
                swapped = True

    return a, SortStats(comparisons, writes, swaps)
