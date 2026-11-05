"""
Description:
- Selection sort without operation counters.
"""


# Function to sort values with selection sort
def selection_sort(values):
    """
    Description:
    - Sort a copy of the input (values[:]).
    - For each position, find the minimum of the remaining values (strict <, so the first of equal
      values is kept) and swap it in only if it is not already in place.

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        list[float]: a new ascending list, e.g. [3, 1, 2] -> [1, 2, 3].
    """
    sorted_values = values[:]
    list_length = len(sorted_values)
    for position in range(list_length - 1):
        minimum_index = position
        for candidate_index in range(position + 1, list_length):
            if sorted_values[candidate_index] < sorted_values[minimum_index]:
                minimum_index = candidate_index
        if minimum_index != position:
            sorted_values[position], sorted_values[minimum_index] = (sorted_values[minimum_index],
                                                                     sorted_values[position])
    return sorted_values
