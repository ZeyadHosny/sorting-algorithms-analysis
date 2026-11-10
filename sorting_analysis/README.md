# sorting_analysis

The analysis package. Each area is a sub-package with one folder per feature: `implementation/` holds the code and `testing/` the unit tests (its `__init__.py` is required for test discovery).

| Area | Contents |
|---|---|
| `data/` | Load, inspect and sample the dataset; build the input orders |
| `sorts/` | Bubble, selection and merge sort, each with a plain (timed) and a counted version |
| `timing/` | Repeated, verified timing of the plain sorts |
| `experiments/` | Scaling, input-order and repeated-values experiments; result CSV files |
| `analysis/` | Growth factors and the bubble sort estimate |
| `plots/` | Charts and result tables |
| `config.py` | Every path, column, seed, size and timing value |

## Imports

Each area's `__init__.py` re-exports its public names. Code imports through the area; only a feature's `__init__.py` imports from its `implementation/` folder:

```python
from sorting_analysis.data import load_csv, sample_indices
from sorting_analysis.sorts import bubble_sort, merge_sort, SortStats
from sorting_analysis.experiments import CaseResult, write_cases
```

`sorts`, `experiments` and `analysis` import their `common/` folder first, because their features import those names back through the area.

| Area | Uses |
|---|---|
| `sorts`, `analysis` | no other area |
| `data` | `sorts` |
| `timing` | `config`, `sorts` |
| `experiments` | `config`, `data`, `sorts`, `timing` |
| `plots` | `config`, `experiments`; the only area that imports matplotlib |

## config.py

`Settings(...)` holds every value as an attribute, e.g. `settings.order_sample_size`; `DEFAULT_SETTINGS` holds the default values. Tests pass a smaller `Settings(...)`.
