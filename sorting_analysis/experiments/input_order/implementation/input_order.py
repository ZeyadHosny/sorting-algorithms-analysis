"""
Description:
- Input-order experiment: all three algorithms on random, sorted, reversed and nearly sorted input.
- Spec: ARCHITECTURE.md F-IOR-1 - F-IOR-3.
"""

from sorting_analysis.config import DEFAULT_SETTINGS


# Function to run the input-order experiment
def run_input_order(rows, usable_indices, settings=DEFAULT_SETTINGS):
    """
    Description:
    - Draw one order_sample_size sample of settings.order_column and put it in the shared order with
      shuffle_indices(..., shuffle_seed).
    - Build the four orders with make_orders and measure every algorithm on each with
      benchmark(plain, counted, values, settings), taking both functions from ALGORITHMS.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       usable_indices (list[int]): Indices of the usable rows (complete_cases).
       settings (Settings): Run settings (seeds, sizes, columns, timing).

    Return:
        list[CaseResult]: 12 cases, 3 algorithms x 4 orders (raises ValueError if order_sample_size exceeds the usable rows; VerificationError from benchmark)
    """
    raise NotImplementedError("run_input_order: not implemented yet")
