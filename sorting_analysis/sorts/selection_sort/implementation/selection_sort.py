"""
Description:
- Selection sort that swaps only when the minimum is not already in place, without counters:
  the version that is timed.
- Same loops as counted_selection_sort; the counters are the only difference.
- Spec: ARCHITECTURE.md F-SEL-1 - F-SEL-5.
"""


# Function to sort values with selection sort
def selection_sort(values):
    """
    Description:
    - Copy the input by slicing (values[:]), then for each position find the index of the minimum
      of the remaining values and swap it into place only if it is not already there (at most one swap
      per position, as the PDF requires; the lecture version swaps on every smaller value).

    Input arguments:
       values (list[float]): Values to sort; never modified.

    Return:
        list[float]: a new ascending list, e.g. [3, 1, 2] -> [1, 2, 3].
    """
    raise NotImplementedError("selection_sort: not implemented yet")
