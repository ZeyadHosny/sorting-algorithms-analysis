"""
Description:
- Observed versus theoretical runtime growth when the input size doubles.
- Spec: ARCHITECTURE.md F-GRO-1, F-GRO-2.
"""

from sorting_analysis.analysis import scaling_cases  # noqa: F401  (used by growth_factors)


# CSV header of growth.csv.
GROWTH_FIELDS = ("algorithm", "size_from", "size_to", "time_from_s", "time_to_s", "observed_factor",
                 "theoretical_factor")


# Function to compute the expected runtime ratio
def theoretical_factor(algorithm, smaller_size, larger_size):
    """
    Description:
    - (larger_size / smaller_size) ** 2 for bubble and selection sort;
    - (larger_size log larger_size) / (smaller_size log smaller_size) for merge sort.

    Input arguments:
       algorithm (str): 'bubble', 'selection' or 'merge'.
       smaller_size (int): Smaller input size.
       larger_size (int): Larger input size.

    Return:
        float: e.g. ('bubble', 1000, 2000) -> 4.0; ('merge', 1000, 2000) -> about 2.2.
    """
    raise NotImplementedError("theoretical_factor: not implemented yet")


# Function to compute observed growth factors
def growth_factors(cases):
    """
    Description:
    - Return T(2n) / T(n) for every doubling pair of the scaling rows, next to the theoretical factor.
    - T(n) is the median time at size n. Non-doubling pairs (e.g. 20 -> 250) are skipped.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.

    Return:
        list[dict]: one row per algorithm and doubling pair, with the GROWTH_FIELDS keys.
    """
    raise NotImplementedError("growth_factors: not implemented yet")
