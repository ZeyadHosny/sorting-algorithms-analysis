"""
Description:
- Dataset inspection (rows, missing and distinct values) and duplication statistics.
- Counting uses a dict; nothing is sorted. Spec: ARCHITECTURE.md F-INS-1 - F-INS-3.
"""


# CSV header of inspection.csv (one row per selected column).
INSPECTION_FIELDS = ("column", "rows", "missing", "distinct", "excluded_rows")
# CSV header of dupes_stats.csv (one row per column of the repeated-values experiment).
DUPES_FIELDS = ("column", "sample_size", "distinct", "modal_value", "modal_count", "repeated_distinct",
                "repeated_observations")


# Function to inspect the selected columns
def inspect_data(rows, columns):
    """
    Description:
    - Inspect the raw rows, one result per selected column, using the loader's parse_value rule.
    - excluded_rows is the number of rows complete_cases drops (same value on every row).

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       columns (tuple[str]): Selected columns.

    Return:
        list[dict]: one dict per column with the INSPECTION_FIELDS keys, e.g. {'column': 'median_income', 'rows': 20640, 'missing': 0, 'distinct': 12928, 'excluded_rows': 0}.
    """
    raise NotImplementedError("inspect_data: not implemented yet")


# Function to describe the duplication of one sample
def duplicate_stats(values):
    """
    Description:
    - Count distinct values, the most frequent value, the distinct values that occur more than once,
    - and the observations that belong to those repeated values.

    Input arguments:
       values (list[float]): Sample values, e.g. [1, 1, 2, 3, 3, 3].

    Return:
        dict: sample_size, distinct, modal_value, modal_count, repeated_distinct, repeated_observations; e.g. [1, 1, 2, 3, 3, 3] -> 6, 3, 3, 3, 2, 5.
    """
    raise NotImplementedError("duplicate_stats: not implemented yet")
