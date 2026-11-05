"""
Description:
- Top-down merge sort with operation counters.
"""

from sorting_analysis.sorts import SortStats


# Function to sort values with merge sort and count its operations
def counted_merge_sort(values):
    """
    Description:
    - Sort the values with the same steps as merge_sort and count the operations.
    - Comparisons: each comparison of two values while merging.
    - Writes: each value appended to a merged list, including the leftover values.
    - Copies made by splitting or slicing are not counted. Merge sort makes no swaps (None).

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [2, 1] -> ([1, 2], 1 comparison, 2 writes, swaps None).
    """
    sorted_values, comparisons, writes = _merge_sort_recursive(values)
    return sorted_values, SortStats(comparisons, writes, None)


# Function to sort one sublist recursively and count its operations
def _merge_sort_recursive(sublist):
    """
    Description:
    - Return a copy (sublist[:]) if it has fewer than 2 values; otherwise split it in two by slicing,
      sort both halves, and merge them.
    - Each call returns its own counts; the parent adds them up.

    Input arguments:
       sublist (list[float]): Sublist to sort.

    Return:
        tuple: (sorted sublist, comparisons, writes).
    """
    if len(sublist) < 2:
        return sublist[:], 0, 0
    middle = len(sublist) // 2
    left_half, left_comparisons, left_writes = _merge_sort_recursive(sublist[:middle])
    right_half, right_comparisons, right_writes = _merge_sort_recursive(sublist[middle:])
    merged, merge_comparisons, merge_writes = _merge(left_half, right_half)
    comparisons = left_comparisons + right_comparisons + merge_comparisons
    writes = left_writes + right_writes + merge_writes
    return merged, comparisons, writes


# Function to merge two sorted lists and count its operations
def _merge(left_half, right_half):
    """
    Description:
    - Compare the first remaining value of each half and append the smaller one to the result;
      if they are equal, append the left one first.
    - When one half runs out, append the remaining values of the other half.
    - Each comparison is 1 comparison; each appended value is 1 write.

    Input arguments:
       left_half (list[float]): Sorted left half.
       right_half (list[float]): Sorted right half.

    Return:
        tuple: (merged list, comparisons, writes), e.g. [1, 3], [2] -> ([1, 2, 3], 2, 3).
    """
    merged = []
    left_index, right_index = 0, 0
    comparisons = 0
    writes = 0
    while left_index < len(left_half) and right_index < len(right_half):
        comparisons += 1
        if left_half[left_index] <= right_half[right_index]:
            merged.append(left_half[left_index])
            left_index += 1
        else:
            merged.append(right_half[right_index])
            right_index += 1
        writes += 1
    while left_index < len(left_half):
        merged.append(left_half[left_index])
        left_index += 1
        writes += 1
    while right_index < len(right_half):
        merged.append(right_half[right_index])
        right_index += 1
        writes += 1
    return merged, comparisons, writes
