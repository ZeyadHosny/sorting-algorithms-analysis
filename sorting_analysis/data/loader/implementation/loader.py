"""
Description:
- Reads the dataset CSV with csv.DictReader and converts selected values to floats.
- Standard library only. Spec: ARCHITECTURE.md F-LOAD-1 - F-LOAD-5.
"""

import csv
import math


# Function to read every row of the CSV
def load_csv(path):
    """
    Description:
    - Read every data row with csv.DictReader; values stay as strings.

    Input arguments:
       path (str): Path of the CSV file, e.g. 'housing.csv'.

    Return:
        list[dict]: one dict per row, column name -> raw string (raises FileNotFoundError if the file is missing)
    """
    rows = []

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            rows.append(row)

    return rows


# Function to convert one raw value
def parse_value(raw_value):
    """
    Description:
    - Convert one raw value to a float.
    - Blank, unparsable and non-finite text ('nan', 'inf') count as missing.

    Input arguments:
       raw_value (str or None): Raw CSV value, e.g. '8.3252'; None when the column is absent.

    Return:
        float or None: the value, or None when it is missing.
    """
    if raw_value is None:
        return None

    text = raw_value.strip()

    if text == "":
        return None

    try:
        value = float(text)
    except ValueError:
        return None

    if not math.isfinite(value):
        return None

    return value


# Function to find the usable rows
def complete_cases(rows, columns):
    """
    Description:
    - Return the indices of the rows whose selected columns all parse.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       columns (tuple[str]): Columns that must all hold a valid value.

    Return:
        list[int]: ascending row indices, e.g. [0, 1, 3].
    """
    usable_indices = []

    for row_index in range(len(rows)):
        row = rows[row_index]
        is_complete = True

        for column in columns:
            value = parse_value(row.get(column))

            if value is None:
                is_complete = False
                break

        if is_complete:
            usable_indices.append(row_index)

    return usable_indices


# Function to extract one column
def column_values(rows, column, row_indices):
    """
    Description:
    - Return the parsed values of one column for the given rows, in the order of row_indices.

    Input arguments:
       rows (list[dict]): Raw rows from load_csv (column name -> string).
       column (str): Column name, e.g. 'median_income'.
       row_indices (list[int]): Row indices, e.g. from complete_cases or the sampling functions.

    Return:
        list[float]: e.g. [8.3252, 7.2574]
        (raises ValueError if a requested value is missing or invalid).
    """
    values = []

    for row_index in row_indices:
        value = parse_value(rows[row_index].get(column))

        if value is None:
            raise ValueError(
                f"Missing or invalid value in column '{column}' "
                f"at row index {row_index}."
            )

        values.append(value)

    return values
