"""
Description:
- Scaling experiment: all three algorithms on increasing sample sizes of the scaling column.
- Spec: ARCHITECTURE.md F-SCL-1 - F-SCL-4.
"""

from sorting_analysis.config import DEFAULT_SETTINGS


# Function to run the scaling experiment
def run_scaling(rows, usable_indices, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Draw one seeded sample per size in settings.scaling_sizes.
    - Measure every algorithm on the same sample with benchmark.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       usable_indices (list[int]): Indices of the usable rows (complete_cases).
       settings (Settings): Run settings (seeds, sizes, columns, timing).

    Return:
        list[CaseResult]: one per algorithm and size, 24 with the default sizes (raises ValueError if a size exceeds the usable rows; VerificationError from benchmark)
    """
    raise NotImplementedError("run_scaling: not implemented yet")
