"""
Description:
- Bubble sort with early termination, without counters: the version that is timed.
- Same loops as counted_bubble_sort; the counters are the only difference.
- Spec: ARCHITECTURE.md F-BUB-1 - F-BUB-7.
"""


# Function to sort values with bubble sort
def bubble_sort(values):
    """
    Description:
    - Copy the input by slicing (values[:]), then bubble sort the copy as in the lecture:
      every pass compares each neighbouring pair over the whole list and swaps it if
      sorted_values[right_index-1] > sorted_values[right_index];
      stop after a full pass with no swaps.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        list[float]: a new ascending list, e.g. [3, 1, 2] -> [1, 2, 3].
    """
    sorted_values = values[:]
    swapped = True

    while swapped:
        swapped = False
        for right_index in range(1, len(sorted_values)):
            if sorted_values[right_index - 1] > sorted_values[right_index]:
                sorted_values[right_index - 1], sorted_values[right_index] = (
                    sorted_values[right_index],
                    sorted_values[right_index - 1],
                )
                swapped = True

    return sorted_values
