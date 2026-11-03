"""
Description:
- Top-down merge sort without counters: the version that is timed. Ties take the left element first.
- Same structure as counted_merge_sort (and as the lecture, except <= on ties, which the PDF requires);
  the counters are the only difference.
- Spec: ARCHITECTURE.md F-MRG-1 - F-MRG-7.
"""


# Function to sort values with merge sort
def merge_sort(values):
    """
    Description:
    - Sort values with top-down merge sort. Splitting by slicing creates new lists,
      so the input is never modified.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        list[float]: a new ascending list, e.g. [2, 1] -> [1, 2].
    """
    raise NotImplementedError("merge_sort: not implemented yet")


# Function to sort one sublist recursively
def _merge_sort_recursive(sublist):
    """
    Description:
    - Return a copy (sublist[:]) if it has fewer than 2 values; otherwise split it in two by slicing,
      sort both halves, and merge them.

    Input arguments:
       sublist (list[float]): Sublist to sort.

    Return:
        list[float]: the sorted sublist.
    """
    raise NotImplementedError("_merge_sort_recursive: not implemented yet")


# Function to merge two sorted lists
def _merge(left_half, right_half):
    """
    Description:
    - Append the smaller front value while both halves have values; on ties (left_half[i] <= right_half[j])
      the left value is taken. Then append the leftover tail.

    Input arguments:
       left_half (list[float]): Sorted left half.
       right_half (list[float]): Sorted right half.

    Return:
        list[float]: the merged list, e.g. [1, 3], [2] -> [1, 2, 3].
    """
    raise NotImplementedError("_merge: not implemented yet")
