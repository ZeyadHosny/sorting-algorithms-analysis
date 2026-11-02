"""
Description:
- Builds the four input orders of the input-order experiment.
- 'Already sorted' comes from our merge sort, never from sort() or sorted().
- Spec: ARCHITECTURE.md F-ORD-1 - F-ORD-5.
"""

from sorting_analysis.sorts import merge_sort  # noqa: F401  (used by ascending)


# Function to sort values ascending with our merge sort
def ascending(values):
    """
    Description:
    - Return a sorted copy produced by merge_sort.

    Input arguments:
       values (list[float]): Input values.

    Return:
        list[float]: e.g. [3, 1, 2] -> [1, 2, 3].
    """
    raise NotImplementedError("ascending: not implemented yet")


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
    raise NotImplementedError("descending: not implemented yet")


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
    raise NotImplementedError("nearly_sorted: not implemented yet")


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
    raise NotImplementedError("make_orders: not implemented yet")
