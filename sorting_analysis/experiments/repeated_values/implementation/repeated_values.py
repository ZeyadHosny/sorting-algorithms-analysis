"""
Description:
- Repeated-values experiment: all three algorithms on the three columns, same rows in the same order.
"""

from sorting_analysis.config import DEFAULT_SETTINGS
from sorting_analysis.data import column_values, duplicate_stats, sample_indices, shuffle_indices
from sorting_analysis.experiments import ALGORITHMS, CaseResult
from sorting_analysis.timing import benchmark


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
        tuple: (9 CaseResults, one duplicate_stats dict per column) (raises ValueError if
        order_sample_size exceeds the usable rows; VerificationError from benchmark)
    """
    sampled_indices = sample_indices(usable_indices, settings.order_sample_size, settings.sample_seed)
    shuffled_indices = shuffle_indices(sampled_indices, settings.shuffle_seed)
    cases = []
    statistics = []

    for column in settings.selected_columns:
        values = column_values(rows, column, shuffled_indices)
        column_statistics = duplicate_stats(values)
        column_statistics['column'] = column
        statistics.append(column_statistics)

        for algorithm_name, functions in ALGORITHMS.items():
            plain_sort, counted_sort = functions
            timing, sort_stats = benchmark(plain_sort, counted_sort, values, settings)
            cases.append(CaseResult(
                'dupes', algorithm_name, column, 'random', len(values), sort_stats, timing,
            ))

    return cases, statistics
