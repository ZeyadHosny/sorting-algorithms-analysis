"""
Description:
- Reads the dataset CSV with csv.DictReader and converts selected values to floats.
- Standard library only. Spec: ARCHITECTURE.md F-LOAD-1 - F-LOAD-5.
"""


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
    raise NotImplementedError("load_csv: not implemented yet")


# Function to convert one raw value
def parse_value(raw_value):
    """
    Description:
    - Convert one raw value to a float.
    - Blank, unparsable and non-finite text ('nan', 'inf') count as missing.

    Input arguments:
       raw_value (str): Raw CSV value, e.g. '8.3252'.

    Return:
        float: the value, or None when it is missing.
    """
    raise NotImplementedError("parse_value: not implemented yet")


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
    raise NotImplementedError("complete_cases: not implemented yet")


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
        list[float]: e.g. [8.3252, 7.2574].
    """
    raise NotImplementedError("column_values: not implemented yet")
