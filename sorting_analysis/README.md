# sorting_analysis

The analysis package. Each area is a sub-package; each feature has `implementation/` (code, no `__init__.py`) and `testing/` (unit tests; its `__init__.py` is required for test discovery). The feature's own `__init__.py` re-exports its public names.

**Imports:** every area re-exports its public names, and every import, inside or outside an area, goes through the area:

```python
from sorting_analysis.data import load_csv, sample_indices
from sorting_analysis.sorts import bubble_sort, merge_sort, SortStats
from sorting_analysis.experiments import CaseResult, write_cases
```

Each area's `__init__.py` imports its `common/` first, because its features import those names back through the area (e.g. `counted_selection_sort.py` uses `from sorting_analysis.sorts import SortStats`). Run everything from the repository root.

| Area | Contents |
|---|---|
| [data/](data/README.md) | Load, inspect and sample the dataset; build input orders |
| [sorts/](sorts/README.md) | Bubble, selection and merge sort: plain versions (timed) and counted versions (operation counts) |
| [timing/](timing/README.md) | Repeated, verified timing of the plain sorts; counts from the counted sorts |
| [experiments/](experiments/README.md) | Scaling, input-order and repeated-values experiments; result CSV files |
| [analysis/](analysis/README.md) | Growth factors and bubble sort estimate (quadratic regression) |
| [plots/](plots/README.md) | Charts |

Allowed imports: `sorts` imports nothing outside `sorts`; `data` and `timing` may use `config` and `sorts.merge_sort`; `experiments` may use `data`, `sorts`, `timing`; `analysis` and `plots` use `experiments.common`. Only `plots` imports matplotlib.

## Interface: `config.py`

| Name | Description |
|---|---|
| `Settings(...)` | Every seed, size, column, path and timing value, read as attributes (`settings.order_sample_size`); values only, no methods |
| `DEFAULT_SETTINGS` | The official settings |

| Setting | Default |
|---|---|
| `csv_path`, `results_folder` | `"housing.csv"`, `"results"` |
| `selected_columns` | `("median_income", "housing_median_age", "median_house_value")` |
| `scaling_column`, `order_column` | `"median_income"`, `"median_income"` (one per experiment; `order_column` must be one of `selected_columns`) |
| `sample_seed`, `shuffle_seed`, `nearly_sorted_seed` | 42, 43, 44 |
| `scaling_sizes` | (5, 10, 20, 250, 500, 1000, 2000, 4000) |
| `order_sample_size`, `timed_batches` | 2000, 5 |
| `small_input_limit`, `small_input_repetitions`, `normal_input_repetitions` | 20, 1000, 1 |
| `extrapolation_target_size`, `extrapolation_base_sizes` | 20640, (250, 500, 1000, 2000, 4000) |
