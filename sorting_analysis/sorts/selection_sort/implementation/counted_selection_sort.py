"""
Description:
- Selection sort with operation counters.
"""

from sorting_analysis.sorts import SortStats


# Function to sort values with selection sort and count its operations
def counted_selection_sort(values):
    """
    Description:
    - Sort a copy of the input (values[:]), with the same steps as selection_sort.
    - Comparisons: each comparison of two values while searching for the minimum.
    - Swaps: one when the minimum is not already in place; each swap is 2 writes.
    - The copy is made by slicing and is not counted.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        tuple: (new ascending list, SortStats), e.g. [3, 1, 2] -> ([1, 2, 3], 3 comparisons, 4 writes, 2 swaps).
    """
    sorted_values = values[:]
    list_length = len(sorted_values)
    comparisons = 0
    writes = 0
    swaps = 0
    for position in range(list_length - 1):
        minimum_index = position
        for candidate_index in range(position + 1, list_length):
            comparisons += 1
            if sorted_values[candidate_index] < sorted_values[minimum_index]:
                minimum_index = candidate_index
        if minimum_index != position:
            sorted_values[position], sorted_values[minimum_index] = (sorted_values[minimum_index],
                                                                     sorted_values[position])
            writes += 2
            swaps += 1
    return sorted_values, SortStats(comparisons, writes, swaps)
