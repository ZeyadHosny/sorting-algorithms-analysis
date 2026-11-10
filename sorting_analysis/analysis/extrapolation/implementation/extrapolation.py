"""
Description:
- Bubble sort runtime estimate for the full dataset by quadratic regression (curve fitting).
- Fit T(n) = a0 + a1*n + a2*n**2 to bubble sort's median times at the base sizes (250 ... 4000) by
  least squares, beta = (X^T X)^-1 X^T y, then evaluate it at the target size (20,640).
- T(n) is the median time at size n from the scaling experiment (random median_income samples).
"""

import math
from fractions import Fraction

from sorting_analysis.analysis import scaling_cases


# Name of the estimation method written to extrapolation.csv.
FIT_METHOD = "quadratic_fit"
# CSV header of extrapolation.csv (one row).
EXTRAPOLATION_FIELDS = ("method", "sizes_used", "a0", "a1", "a2", "target_size", "estimate_s")
# Keys of the measured-versus-fitted rows printed by main.py.
FITTED_FIELDS = ("input_size", "measured_s", "fitted_s")


# Function to compute the determinant of a 3x3 matrix
def determinant_3x3(matrix):
    """
    Description:
    - Expand along the first row.

    Input arguments:
       matrix (list[list]): Three rows of three numbers (int, float or Fraction).

    Return:
        number: determinant of the matrix, e.g. [[1, 0, 0], [0, 2, 0], [0, 0, 3]] -> 6.
    """
    top, middle, bottom = matrix
    return (top[0] * (middle[1] * bottom[2] - middle[2] * bottom[1])
            - top[1] * (middle[0] * bottom[2] - middle[2] * bottom[0])
            + top[2] * (middle[0] * bottom[1] - middle[1] * bottom[0]))


# Function to fit T = a0 + a1*n + a2*n**2 to measured times by least squares
def fit_quadratic(sizes, times):
    """
    Description:
    - Least squares: beta = (X^T X)^-1 X^T y, with beta = (a0, a1, a2), X the feature matrix with rows
      (1, n, n**2) and y the measured times.
    - Exact fractions keep the products and the inverse free of rounding, so the zero check is exact.

    Input arguments:
       sizes (list[int]): Input sizes, at least 3 distinct, e.g. [250, 500, 1000, 2000, 4000].
       times (list[float]): Median seconds per sort at each size, same order as sizes.

    Return:
        tuple: (a0, a1, a2), e.g. times 0.001 + 2e-6*n + 1e-7*n**2 -> (0.001, 2e-6, 1e-7)
               (raises ValueError if fewer than 3 distinct sizes, lengths differ, a time is not finite,
               or det(X^T X) is 0)
    """
    if len(sizes) != len(times):
        raise ValueError(f"Got {len(sizes)} sizes but {len(times)} times.")
    if len(set(sizes)) < 3:
        raise ValueError(f"The quadratic fit needs at least 3 distinct sizes, got {len(set(sizes))}.")
    for time in times:
        if not math.isfinite(time):
            raise ValueError(f"Times must be finite numbers, got {time}.")
    # X: one row (1, n, n**2) per size; y: the measured times as one column.
    feature_matrix = [[Fraction(1), Fraction(size), Fraction(size) ** 2] for size in sizes]
    measured_times = [[Fraction(time)] for time in times]
    feature_transposed = _transpose(feature_matrix)
    # X^T X and its determinant.
    normal_matrix = _matrix_product(feature_transposed, feature_matrix)
    normal_determinant = determinant_3x3(normal_matrix)
    if normal_determinant == 0:
        raise ValueError("X^T X is singular; the sizes cannot determine a quadratic.")
    # beta = (X^T X)^-1 X^T y.
    beta = _matrix_product(_inverse_3x3(normal_matrix, normal_determinant),
                           _matrix_product(feature_transposed, measured_times))
    return tuple(float(row[0]) for row in beta)


# Function to transpose a matrix
def _transpose(matrix):
    """
    Description:
    - Swap rows and columns.

    Input arguments:
       matrix (list[list]): Rows of equal length.

    Return:
        list[list]: e.g. [[1, 2, 3], [4, 5, 6]] -> [[1, 4], [2, 5], [3, 6]].
    """
    return [[row[column] for row in matrix] for column in range(len(matrix[0]))]


# Function to multiply two matrices
def _matrix_product(left, right):
    """
    Description:
    - Entry (row, column) = sum of left[row][k] * right[k][column].

    Input arguments:
       left (list[list]): m x k matrix.
       right (list[list]): k x p matrix.

    Return:
        list[list]: m x p matrix, e.g. [[1, 2]] x [[3], [4]] -> [[11]].
    """
    return [[sum(left_value * right_row[column] for left_value, right_row in zip(left_row, right))
             for column in range(len(right[0]))] for left_row in left]


# Function to invert a 3x3 matrix
def _inverse_3x3(matrix, determinant):
    """
    Description:
    - Inverse = adjugate / determinant; the adjugate is the transposed matrix of cofactors.

    Input arguments:
       matrix (list[list]): Three rows of three numbers.
       determinant (number): determinant_3x3(matrix), not 0.

    Return:
        list[list]: the inverse, e.g. [[2, 0, 0], [0, 4, 0], [0, 0, 5]] -> [[1/2, 0, 0], [0, 1/4, 0], [0, 0, 1/5]].
    """
    inverse = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for row in range(3):
        for column in range(3):
            minor = [[matrix[minor_row][minor_column] for minor_column in range(3) if minor_column != column]
                     for minor_row in range(3) if minor_row != row]
            cofactor = (-1) ** (row + column) * (minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0])
            # Transposed position: the adjugate holds cofactor (row, column) at (column, row).
            inverse[column][row] = cofactor / determinant
    return inverse


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
    a0, a1, a2 = coefficients
    return a0 + a1 * input_size + a2 * input_size ** 2


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
    if len(set(base_sizes)) != len(base_sizes):
        raise ValueError(f"Base sizes must be distinct, got {base_sizes}.")
    times_by_size = {}
    for row in scaling_cases(cases):
        input_size = row["input_size"]
        if row["algorithm"] != "bubble" or input_size not in base_sizes:
            continue
        if input_size in times_by_size:
            raise ValueError(f"Duplicate bubble scaling row at n = {input_size}.")
        median_seconds = row["median_s"]
        if not math.isfinite(median_seconds) or median_seconds <= 0:
            raise ValueError(f"Bubble median time at n = {input_size} must be positive and finite, "
                             f"got {median_seconds}.")
        times_by_size[input_size] = median_seconds
    times = []
    for input_size in base_sizes:
        if input_size not in times_by_size:
            raise ValueError(f"No bubble scaling row at n = {input_size}.")
        times.append(times_by_size[input_size])
    return times


# Function to estimate bubble sort's runtime at the target size
def extrapolate_bubble(cases, target_size, base_sizes):
    """
    Description:
    - Fit the quadratic to bubble_times(cases, base_sizes) and evaluate it at target_size.
    - The estimate row has method FIT_METHOD, sizes_used as text (e.g. '250;500;1000;2000;4000'),
      a0, a1, a2, target_size and estimate_s = predict_time((a0, a1, a2), target_size).
    - Also return the measured and fitted times at each base size.

    Input arguments:
       cases (list[dict]): Case rows; only bubble sort scaling rows are used.
       target_size (int): Input size to estimate, e.g. 20640.
       base_sizes (tuple[int]): Measured sizes used by the fit, e.g. (250, 500, 1000, 2000, 4000).

    Return:
        tuple: (estimate row with the EXTRAPOLATION_FIELDS keys, list of rows with the FITTED_FIELDS keys)
               (raises ValueError from bubble_times or fit_quadratic)
    """
    times = bubble_times(cases, base_sizes)
    coefficients = fit_quadratic(list(base_sizes), times)
    a0, a1, a2 = coefficients
    estimate_row = {
        "method": FIT_METHOD,
        "sizes_used": ";".join(str(input_size) for input_size in base_sizes),
        "a0": a0,
        "a1": a1,
        "a2": a2,
        "target_size": target_size,
        "estimate_s": predict_time(coefficients, target_size),
    }
    # Full precision: the chart checks these values against the coefficients.
    fitted_rows = [{"input_size": input_size, "measured_s": time, "fitted_s": predict_time(coefficients, input_size)}
                   for input_size, time in zip(base_sizes, times)]
    return estimate_row, fitted_rows
