"""
Description:
- Bubble sort runtime estimate for the full dataset, by two methods. T(n) is the median time at size n.
- Method 'c': c = T(n) / n**2, estimate = c * target_size**2 (main estimate).
- Method 'growth': k = T(n) / T(n/2), b = log2(k), estimate = T(n) * (target_size / n) ** b (cross-check).
- Spec: ARCHITECTURE.md F-EXT-1 - F-EXT-5.
"""

from sorting_analysis.analysis.common import scaling_cases  # noqa: F401  (used by both methods)


# CSV header of extrapolation.csv.
EXTRAPOLATION_FIELDS = ("method", "half_size", "base_size", "base_time_s", "constant_c", "exponent_b",
                        "estimate_s")


# Function to estimate with the constant c
def extrapolate_bubble(cases, target_size, base_sizes):
    """
    Description:
    - For each measured base size n: c = T(n) / n**2 and estimate = c * target_size**2.

    Input arguments:
       cases (list[dict]): Case rows; only bubble sort scaling rows are used.
       target_size (int): Input size to estimate, e.g. 20640.
       base_sizes (tuple[int]): Measured sizes to start from, e.g. (1000, 2000, 4000).

    Return:
        list[dict]: one row per base size with the EXTRAPOLATION_FIELDS keys, [] if none was measured (raises ValueError on a zero or negative timing)
    """
    raise NotImplementedError("extrapolate_bubble: not implemented yet")


# Function to estimate with the measured growth
def extrapolate_bubble_growth(cases, target_size, base_sizes):
    """
    Description:
    - For each base size n with a measured n/2: b = log2(T(n) / T(n/2)),
    - estimate = T(n) * (target_size / n) ** b. Assumes the observed exponent holds up to target_size.

    Input arguments:
       cases (list[dict]): Case rows; only bubble sort scaling rows are used.
       target_size (int): Input size to estimate, e.g. 20640.
       base_sizes (tuple[int]): Measured sizes to start from, e.g. (1000, 2000, 4000).

    Return:
        list[dict]: one row per usable base size, [] if none (raises ValueError on a zero or negative timing)
    """
    raise NotImplementedError("extrapolate_bubble_growth: not implemented yet")


# Function to give the range of one method's estimates
def estimate_range(estimate_rows):
    """
    Description:
    - Return the smallest and largest estimate_s.

    Input arguments:
       estimate_rows (list[dict]): Estimate rows of ONE method.

    Return:
        tuple: (min, max) in seconds (raises ValueError if estimate_rows is empty)
    """
    raise NotImplementedError("estimate_range: not implemented yet")
