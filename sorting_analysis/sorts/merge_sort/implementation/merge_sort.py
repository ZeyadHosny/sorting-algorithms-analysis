"""
Description:
- Top-down merge sort; ties take the left element first.
- Spec: ARCHITECTURE.md F-MRG-1 - F-MRG-6, F-MRG-1b.
"""

from sorting_analysis.sorts.common import SortStats  # noqa: F401  (returned by the sort)


# Function to sort values with merge sort
def merge_sort(values):
    """
    Description:
    - Sort values with top-down merge sort.
    - Splitting by slicing creates new lists; slicing is not counted.
    - Every value placed into a merged list is 1 write, including leftover tails.
    - swaps is None: merge sort performs no swaps.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [2, 1] -> ([1, 2], 1 comparison, 2 writes, swaps None).
    """
    raise NotImplementedError("merge_sort: not implemented yet")


# Function to sort one sublist recursively
def _merge_sort_recursive(sublist):
    """
    Description:
    - Split sublist in two, sort both halves, merge them.
    - Each call returns its own counts; the parent adds them up.

    Input arguments:
       sublist (list[float]): Sublist to sort.

    Return:
        tuple: (sorted list, comparisons, writes).
    """
    raise NotImplementedError("_merge_sort_recursive: not implemented yet")


# Function to merge two sorted lists
def _merge(left_half, right_half):
    """
    Description:
    - Each executed left_half[i] <= right_half[j] is 1 comparison; on ties the left element is taken.
    - Copying a leftover tail costs writes but no comparisons.

    Input arguments:
       left_half (list[float]): Sorted left half.
       right_half (list[float]): Sorted right half.

    Return:
        tuple: (merged list, comparisons, writes), e.g. [1, 3], [2] -> ([1, 2, 3], 2, 3).
    """
    raise NotImplementedError("_merge: not implemented yet")
