"""
Description:
- Builds the four input orders of the input-order experiment.
- 'Already sorted' comes from our merge sort, never from sort() or sorted().
- Spec: ARCHITECTURE.md F-ORD-1 - F-ORD-5.
"""

import random

from sorting_analysis.sorts import merge_sort


# Function to sort values ascending with our merge sort
def ascending(values):
    """
    Description:
    - Return the new ascending list produced by our plain merge_sort (outside any timing).

    Input arguments:
       values (list[float]): Input values.

    Return:
        list[float]: e.g. [3, 1, 2] -> [1, 2, 3].
    """
    return merge_sort(values)


# Function to sort values descending
def descending(values):
    """
    Description:
    - Return the reverse of ascending(values).

    Input arguments:
       values (list[float]): Input values.

    Return:
        list[float]: e.g. [1, 2, 3] -> [3, 2, 1].
    """
    ordered_values = ascending(values)
    ordered_values.reverse()
    return ordered_values


# Function to build the nearly sorted input
def nearly_sorted(values, seed):
    """
    Description:
    - Sort ascending, then apply floor(0.01 * len(values)) swaps.
    - Each swap exchanges two distinct positions chosen uniformly at random;
    - a position may take part in several swaps.

    Input arguments:
       values (list[float]): Input values.
       seed (int): Random seed, e.g. 44.

    Return:
        list[float]: a new, nearly sorted list (2000 values -> 20 swaps).
    """
    ordered_values = ascending(values)
    generator = random.Random(seed)
    swap_count = len(ordered_values) // 100

    for swap_number in range(swap_count):
        first, second = generator.sample(range(len(ordered_values)), 2)
        ordered_values[first], ordered_values[second] = ordered_values[second], ordered_values[first]

    return ordered_values


# Function to build all four input orders
def make_orders(shuffled_values, nearly_sorted_seed):
    """
    Description:
    - Return the random, sorted, reversed and nearly sorted versions of the same values.

    Input arguments:
       shuffled_values (list[float]): Values already in the shared shuffled order; kept unchanged as 'random'.
       nearly_sorted_seed (int): Seed for nearly_sorted.

    Return:
        dict: {'random', 'sorted', 'reversed', 'nearly'} -> list[float].
    """
    return {
        'random': shuffled_values[:],
        'sorted': ascending(shuffled_values),
        'reversed': descending(shuffled_values),
        'nearly': nearly_sorted(shuffled_values, nearly_sorted_seed),
    }
