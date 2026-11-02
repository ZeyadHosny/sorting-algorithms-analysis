# analysis

Derives the growth factors and the bubble sort runtime estimate from the scaling experiment's rows in `cases.csv`. Rows of the other experiments are never used.

| Feature | Purpose |
|---|---|
| `common/` | `scaling_cases`, the filter used by both features |
| `growth/` | Observed versus theoretical growth when n doubles |
| `extrapolation/` | Bubble sort runtime estimate for all 20,640 rows |

## Extrapolation methods

| Method | Formula | Role |
|---|---|---|
| `c` | c = T(n) / n², estimate = c · 20,640² | main estimate, for n = 1000, 2000, 4000 |
| `growth` | k = T(n) / T(n/2), b = log₂ k, estimate = T(n) · (20,640 / n)^b | cross-check; assumes the observed exponent holds |

Both methods report every estimate and their range.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `scaling_cases(cases)` | typed case rows | rows with `experiment == "scaling"` |
| `theoretical_factor(algorithm, smaller_size, larger_size)` | algorithm, sizes | (larger/smaller)² or the n log n ratio |
| `growth_factors(cases)` | typed case rows | rows with `GROWTH_FIELDS` for each doubling pair |
| `extrapolate_bubble(cases, target_size, base_sizes)` | rows, target, bases | rows with `EXTRAPOLATION_FIELDS`, method `c`; `[]` if no base |
| `extrapolate_bubble_growth(cases, target_size, base_sizes)` | same | method `growth`; `[]` if no pair |
| `estimate_range(estimate_rows)` | rows of one method | `(min, max)`; `ValueError` if empty |

Both extrapolation functions raise `ValueError` on a zero or negative timing.
