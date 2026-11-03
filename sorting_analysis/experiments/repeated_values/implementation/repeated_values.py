"""
Description:
- Repeated-values experiment: all three algorithms on the three columns, same rows in the same order.
- Spec: ARCHITECTURE.md F-REP-1 - F-REP-4.
"""

from sorting_analysis.config import DEFAULT_SETTINGS


# Function to run the repeated-values experiment
def run_repeated_values(rows, usable_indices, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Use the input-order experiment's row indices, in the same shuffled order, for each column.
    - Record duplicate_stats per column and measure every algorithm on each column with
      benchmark(plain, counted, values, settings), taking both functions from ALGORITHMS.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       usable_indices (list[int]): Indices of the usable rows (complete_cases).
       settings (Settings): Run settings (seeds, sizes, columns, timing).

    Return:
        tuple: (9 CaseResults, one duplicate_stats dict per column) (raises ValueError if order_sample_size exceeds the usable rows; VerificationError from benchmark)
    """
    raise NotImplementedError("run_repeated_values: not implemented yet")
