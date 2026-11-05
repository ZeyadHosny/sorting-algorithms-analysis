"""
Description:
- Bubble sort runtime estimate for the full dataset by quadratic regression (curve fitting).
- Fit T(n) = a0 + a1*n + a2*n**2 by least squares to bubble sort's median times at the base sizes
  (250, 500, 1000, 2000, 4000), solved with Cramer's rule, then evaluate it at the target size (20,640).
- T(n) is the median time at size n from the scaling experiment (random median_income samples).
- Spec: ARCHITECTURE.md F-EXT-1 - F-EXT-5.
"""

from sorting_analysis.analysis import scaling_cases  # noqa: F401  (used by bubble_times)


# Name of the estimation method written to extrapolation.csv.
FIT_METHOD = "quadratic_fit"
# CSV header of extrapolation.csv (one row).
EXTRAPOLATION_FIELDS = ("method", "sizes_used", "a0", "a1", "a2", "target_size", "estimate_s")
# Keys of the measured-versus-fitted rows printed by main.py for the report table.
FITTED_FIELDS = ("input_size", "measured_s", "fitted_s")


# Function to compute the determinant of a 3x3 matrix
def determinant_3x3(matrix):
    """
    Description:
    - Expand along the first row.

    Input arguments:
       matrix (list[list[float]]): Three rows of three numbers.

    Return:
        float: e.g. [[1, 0, 0], [0, 2, 0], [0, 0, 3]] -> 6.
    """
    raise NotImplementedError("determinant_3x3: not implemented yet")


# Function to fit T = a0 + a1*n + a2*n**2 to measured times by least squares
def fit_quadratic(sizes, times):
    """
    Description:
    - Build the least-squares (normal) equations from the sums S[p] = sum(n**p), p = 0..4, and
      Y[p] = sum(T * n**p), p = 0..2, and solve them with Cramer's rule:
      each coefficient = determinant with one column replaced by Y / determinant of the sums matrix.

    Input arguments:
       sizes (list[int]): Input sizes, at least 3 distinct, e.g. [250, 500, 1000, 2000, 4000].
       times (list[float]): Median seconds per sort at each size, same order as sizes.

    Return:
        tuple: (a0, a1, a2), e.g. times 0.001 + 2e-6*n + 1e-7*n**2 -> (0.001, 2e-6, 1e-7)
               (raises ValueError if fewer than 3 distinct sizes, lengths differ, or the determinant is 0)
    """
    raise NotImplementedError("fit_quadratic: not implemented yet")


# Function to evaluate the fitted curve at one size
def predict_time(coefficients, input_size):
    """
    Description:
    - Return a0 + a1*input_size + a2*input_size**2.

    Input arguments:
       coefficients (tuple[float]): (a0, a1, a2) from fit_quadratic.
       input_size (int): Size to evaluate, e.g. 20640.

    Return:
        float: predicted seconds per sort, e.g. 42.64324 for (0.001, 2e-6, 1e-7) at 20640.
    """
    raise NotImplementedError("predict_time: not implemented yet")


# Function to collect bubble sort's median times at the base sizes
def bubble_times(cases, base_sizes):
    """
    Description:
    - From the scaling rows (scaling_cases), take bubble sort's median_s at each base size.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       base_sizes (tuple[int]): Sizes used by the fit, e.g. (250, 500, 1000, 2000, 4000).

    Return:
        list[float]: one median time per base size, in base_sizes order
                     (raises ValueError if a size is missing or duplicated, or a time is not a positive finite number)
    """
    raise NotImplementedError("bubble_times: not implemented yet")


# Function to estimate bubble sort's runtime at the target size
def extrapolate_bubble(cases, target_size, base_sizes):
    """
    Description:
    - Fit the quadratic to bubble_times(cases, base_sizes) and evaluate it at target_size.
    - The estimate row has method FIT_METHOD, sizes_used as text (e.g. '250;500;1000;2000;4000'),
      a0, a1, a2, target_size and estimate_s = predict_time((a0, a1, a2), target_size).
    - Also return measured versus fitted times at each base size, for the report table.

    Input arguments:
       cases (list[dict]): Case rows; only bubble sort scaling rows are used.
       target_size (int): Input size to estimate, e.g. 20640.
       base_sizes (tuple[int]): Measured sizes used by the fit, e.g. (250, 500, 1000, 2000, 4000).

    Return:
        tuple: (estimate row with the EXTRAPOLATION_FIELDS keys, list of rows with the FITTED_FIELDS keys)
               (raises ValueError from bubble_times or fit_quadratic)
    """
    raise NotImplementedError("extrapolate_bubble: not implemented yet")
