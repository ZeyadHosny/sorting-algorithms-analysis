"""
Description:
- Dataset inspection (rows, missing and distinct values) and duplication statistics.
- Counting uses a dict; nothing is sorted. Spec: ARCHITECTURE.md F-INS-1 - F-INS-3.
"""

from sorting_analysis.data import complete_cases, parse_value


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
    results = []
    total_rows = len(rows)
    usable_indices = complete_cases(rows, columns)
    excluded_rows = total_rows - len(usable_indices)

    for column in columns:
        missing = 0
        frequencies = {}

        for row in rows:
            value = parse_value(row.get(column))

            if value is None:
                missing += 1
            else:
                frequencies[value] = frequencies.get(value, 0) + 1

        results.append({
            "column": column,
            "rows": total_rows,
            "missing": missing,
            "distinct": len(frequencies),
            "excluded_rows": excluded_rows,
        })

    return results


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
    frequencies = {}

    for value in values:
        frequencies[value] = frequencies.get(value, 0) + 1

    modal_value = None
    modal_count = 0
    repeated_distinct = 0
    repeated_observations = 0

    for value, frequency in frequencies.items():
        # Keep the first encountered value when frequencies tie.
        if frequency > modal_count:
            modal_value = value
            modal_count = frequency

        if frequency > 1:
            repeated_distinct += 1
            repeated_observations += frequency

    return {
        "sample_size": len(values),
        "distinct": len(frequencies),
        "modal_value": modal_value,
        "modal_count": modal_count,
        "repeated_distinct": repeated_distinct,
        "repeated_observations": repeated_observations,
    }
