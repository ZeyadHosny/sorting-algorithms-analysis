# analysis

Derives the growth factors and the bubble sort runtime estimate from the scaling experiment's rows in `cases.csv`. Rows of the other experiments are never used.

| Feature | Purpose |
|---|---|
| `common/` | `scaling_cases`, the filter used by both features |
| `growth/` | Observed versus theoretical growth when n doubles |
| `extrapolation/` | Bubble sort runtime estimate for all 20,640 rows, by quadratic regression |

## Extrapolation method

The estimate is a least-squares curve fit:

1. Take bubble sort's median time T(n) at n = 250, 500, 1000, 2000, 4000 (random `median_income` samples).
2. Fit **T(n) = a₀ + a₁·n + a₂·n²** by least squares, β = (XᵀX)⁻¹Xᵀy, where each row of X is (1, n, n²) and y holds the times. The matrices use exact `Fraction` arithmetic; the coefficients are returned as floats.
3. Estimate = a₀ + a₁·20,640 + a₂·20,640².

`extrapolation.csv` holds one row: the method, the sizes used, a₀, a₁, a₂, the target size and the estimate. `main.py analyze` also prints the measured and fitted times for the five sizes. The estimate is approximate: five measured points, and 20,640 is about 5× beyond the largest measured size.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `scaling_cases(cases)` | typed case rows | rows with `experiment == "scaling"` |
| `theoretical_factor(algorithm, smaller_size, larger_size)` | algorithm, sizes | (larger/smaller)² or the n log n ratio |
| `growth_factors(cases)` | typed case rows | rows with `GROWTH_FIELDS` for each doubling pair |
| `determinant_3x3(matrix)` | 3×3 list | determinant |
| `fit_quadratic(sizes, times)` | sizes, median times | `(a0, a1, a2)`; `ValueError` if fewer than 3 distinct sizes, lengths differ, a time is not finite, or XᵀX is singular |
| `predict_time(coefficients, input_size)` | `(a0, a1, a2)`, size | a0 + a1·n + a2·n² |
| `bubble_times(cases, base_sizes)` | typed case rows, sizes | bubble sort's scaling median times in `base_sizes` order; `ValueError` if a size is missing or duplicated, or a time is not positive and finite |
| `extrapolate_bubble(cases, target_size, base_sizes)` | rows, target, sizes | `(row with EXTRAPOLATION_FIELDS, rows with FITTED_FIELDS)` |
