"""
Description:
- Observed versus theoretical runtime growth when the input size doubles.
- Spec: ARCHITECTURE.md F-GRO-1, F-GRO-2.
"""

import math

from sorting_analysis.analysis import scaling_cases


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
    if algorithm not in ("bubble", "selection", "merge"):
        raise ValueError("Unknown sorting algorithm: " + str(algorithm))
    if smaller_size <= 0 or larger_size <= 0:
        raise ValueError("Input sizes must be positive")
    if algorithm == "merge":
        if smaller_size <= 1 or larger_size <= 1:
            raise ValueError("Merge sort growth requires sizes greater than 1")
        return (larger_size * math.log2(larger_size)) / (smaller_size * math.log2(smaller_size))
    return (larger_size / smaller_size) ** 2


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
    times_by_algorithm = {}
    for row in scaling_cases(cases):
        algorithm = row["algorithm"]
        input_size = row["input_size"]
        median_seconds = row["median_s"]
        if algorithm not in ("bubble", "selection", "merge"):
            raise ValueError("Unknown sorting algorithm: " + str(algorithm))
        if input_size <= 0:
            raise ValueError("Input sizes must be positive")
        if not math.isfinite(median_seconds) or median_seconds <= 0:
            raise ValueError("Median times must be positive finite numbers")
        if algorithm not in times_by_algorithm:
            times_by_algorithm[algorithm] = {}
        if input_size in times_by_algorithm[algorithm]:
            raise ValueError("Duplicate scaling size for " + algorithm + ": " + str(input_size))
        times_by_algorithm[algorithm][input_size] = median_seconds

    growth_rows = []
    # Keep the input's algorithm and size order; no library sorting is needed.
    for algorithm, times_by_size in times_by_algorithm.items():
        for smaller_size, smaller_time in times_by_size.items():
            larger_size = 2 * smaller_size
            if larger_size in times_by_size:
                larger_time = times_by_size[larger_size]
                growth_rows.append({
                    "algorithm": algorithm,
                    "size_from": smaller_size,
                    "size_to": larger_size,
                    "time_from_s": smaller_time,
                    "time_to_s": larger_time,
                    "observed_factor": larger_time / smaller_time,
                    "theoretical_factor": theoretical_factor(algorithm, smaller_size, larger_size),
                })
    return growth_rows
