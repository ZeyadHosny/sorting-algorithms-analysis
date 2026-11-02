# sorting_analysis

The analysis package. Each area is a sub-package; each feature has `implementation/` (code) and `testing/` (unit tests).

**Imports:** every area re-exports its public names, so code outside an area imports from the area directly:

```python
from sorting_analysis.data import load_csv, sample_indices
from sorting_analysis.sorts import bubble_sort, merge_sort, SortStats
from sorting_analysis.experiments import CaseResult, write_cases
```

Inside an area, implementation files import the specific module (e.g. `from sorting_analysis.sorts.common import SortStats`) to avoid circular imports.

| Area | Contents |
|---|---|
| [data/](data/README.md) | Load, inspect and sample the dataset; build input orders |
| [sorts/](sorts/README.md) | Bubble, selection and merge sort with operation counts |
| [timing/](timing/README.md) | Repeated, verified timing |
| [experiments/](experiments/README.md) | Scaling, input-order and repeated-values experiments; result CSV files |
| [analysis/](analysis/README.md) | Growth factors and bubble sort extrapolation |
| [plots/](plots/README.md) | Charts |

Allowed imports: `sorts` imports nothing outside `sorts`; `data` and `timing` may use `config` and `sorts.merge_sort`; `experiments` may use `data`, `sorts`, `timing`; `analysis` and `plots` use `experiments.common`. Only `plots` imports matplotlib.

## Interface: `config.py`

| Name | Description |
|---|---|
| `Settings(...)` | Every seed, size, column, path and timing value; read with `get_<name>()` |
| `settings.repetitions_for(input_size)` | Sorts per timed batch: 1,000 if input_size ≤ 20, else 1 |
| `settings.with_csv_path(csv_path)` | A copy with another dataset path |
| `DEFAULT_SETTINGS` | The official settings |

| Setting | Default |
|---|---|
| `csv_path`, `results_folder` | `"housing.csv"`, `"results"` |
| `selected_columns` | `("median_income", "housing_median_age", "median_house_value")` |
| `scaling_column` | `"median_income"` |
| `sample_seed`, `shuffle_seed`, `nearly_sorted_seed` | 42, 43, 44 |
| `scaling_sizes` | (5, 10, 20, 250, 500, 1000, 2000, 4000) |
| `order_sample_size`, `timed_batches` | 2000, 5 |
| `small_input_limit`, `small_input_repetitions`, `normal_input_repetitions` | 20, 1000, 1 |
| `extrapolation_target_size`, `extrapolation_base_sizes` | 20640, (1000, 2000, 4000) |
