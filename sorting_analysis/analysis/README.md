# analysis

Derives the growth factors and the bubble sort runtime estimate from the scaling experiment's rows in `cases.csv`. Rows of the other experiments are never used.

| Feature | Purpose |
|---|---|
| `common/` | `scaling_cases`, the filter used by both features |
| `growth/` | Observed versus theoretical growth when n doubles |
| `extrapolation/` | Bubble sort runtime estimate for all 20,640 rows, by quadratic regression |

## Extrapolation method

As the instructor required, the estimate is a regression (curve fit):

1. Take bubble sort's median time T(n) at n = 250, 500, 1000, 2000, 4000 (random `median_income` samples).
2. Fit **T(n) = a₀ + a₁·n + a₂·n²** by least squares. The normal equations use the sums S[p] = Σnᵖ (p = 0…4) and Y[p] = Σ T·nᵖ (p = 0…2) and are solved with Cramer's rule (3×3 determinants, standard library only).
3. Estimate = a₀ + a₁·20,640 + a₂·20,640².

`extrapolation.csv` holds one row: the method, the sizes used, a₀, a₁, a₂, the target size and the estimate. `main.py analyze` also prints measured versus fitted times for the five sizes (the report table). The estimate is approximate: five measured points, and 20,640 is about 5× beyond the largest measured size.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `scaling_cases(cases)` | typed case rows | rows with `experiment == "scaling"` |
| `theoretical_factor(algorithm, smaller_size, larger_size)` | algorithm, sizes | (larger/smaller)² or the n log n ratio |
| `growth_factors(cases)` | typed case rows | rows with `GROWTH_FIELDS` for each doubling pair |
| `determinant_3x3(matrix)` | 3×3 list | determinant |
| `fit_quadratic(sizes, times)` | sizes, median times | `(a0, a1, a2)`; `ValueError` if fewer than 3 distinct sizes, lengths differ, or the system is singular |
| `predict_time(coefficients, input_size)` | `(a0, a1, a2)`, size | a0 + a1·n + a2·n² |
| `bubble_times(cases, base_sizes)` | typed case rows, sizes | bubble sort's scaling median times in `base_sizes` order; `ValueError` if a size is missing or duplicated, or a time is not positive and finite |
| `extrapolate_bubble(cases, target_size, base_sizes)` | rows, target, sizes | `(row with EXTRAPOLATION_FIELDS, rows with FITTED_FIELDS)` |
