"""
Description:
- Top-down merge sort without operation counters.
"""


# Function to sort values with merge sort
def merge_sort(values):
    """
    Description:
    - Sort the values with top-down merge sort. Splitting by slicing creates new lists,
      so the input is never modified.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        list[float]: a new ascending list, e.g. [2, 1] -> [1, 2].
    """
    return _merge_sort_recursive(values)


# Function to sort one sublist recursively
def _merge_sort_recursive(sublist):
    """
    Description:
    - Return a copy (sublist[:]) if it has fewer than 2 values; otherwise split it in two by slicing,
      sort both halves, and merge them.

    Input arguments:
       sublist (list[float]): Sublist to sort.

    Return:
        list[float]: the sorted sublist, a new list.
    """
    if len(sublist) < 2:
        return sublist[:]
    middle = len(sublist) // 2
    left_half = _merge_sort_recursive(sublist[:middle])
    right_half = _merge_sort_recursive(sublist[middle:])
    return _merge(left_half, right_half)


# Function to merge two sorted lists
def _merge(left_half, right_half):
    """
    Description:
    - Compare the first remaining value of each half and append the smaller one to the result;
      if they are equal, append the left one first.
    - When one half runs out, append the remaining values of the other half.

    Input arguments:
       left_half (list[float]): Sorted left half.
       right_half (list[float]): Sorted right half.

    Return:
        list[float]: the merged list, e.g. [1, 3], [2] -> [1, 2, 3].
    """
    merged = []
    left_index, right_index = 0, 0
    while left_index < len(left_half) and right_index < len(right_half):
        if left_half[left_index] <= right_half[right_index]:
            merged.append(left_half[left_index])
            left_index += 1
        else:
            merged.append(right_half[right_index])
            right_index += 1
    while left_index < len(left_half):
        merged.append(left_half[left_index])
        left_index += 1
    while right_index < len(right_half):
        merged.append(right_half[right_index])
        right_index += 1
    return merged
