"""
Description:
- Scaling experiment: all three algorithms on increasing sample sizes of the scaling column.
"""

from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.data import column_values, sample_indices
from sorting_analysis.experiments import ALGORITHMS, CaseResult
from sorting_analysis.timing import benchmark


# Function to run the scaling experiment
def run_scaling(rows, usable_indices, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Draw one seeded sample per size in settings.scaling_sizes (seed settings.sample_seed) and read
      its settings.scaling_column values.
    - Measure every algorithm on the same sample with benchmark(plain, counted, values, settings),
      taking both functions from ALGORITHMS.
    - Every size is checked against the usable rows before any timing starts.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       usable_indices (list[int]): Indices of the usable rows (complete_cases).
       settings (Settings): Run settings (seeds, sizes, columns, timing).

    Return:
        list[CaseResult]: one per algorithm and size, 24 with the default sizes (raises ValueError if a
        size exceeds the usable rows; VerificationError from benchmark)
    """
    for input_size in settings.scaling_sizes:
        if input_size > len(usable_indices):
            raise ValueError(f"Scaling size {input_size} exceeds the {len(usable_indices)} usable rows.")

    cases = []
    for input_size in settings.scaling_sizes:
        row_indices = sample_indices(usable_indices, input_size, settings.sample_seed)
        values = column_values(rows, settings.scaling_column, row_indices)
        for algorithm, (sort_function, counted_sort_function) in ALGORITHMS.items():
            timing, sort_stats = benchmark(sort_function, counted_sort_function, values, settings)
            cases.append(CaseResult("scaling", algorithm, settings.scaling_column, "random", input_size,
                                    sort_stats, timing))
    return cases
