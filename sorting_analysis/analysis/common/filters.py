"""
Description:
- Row filters shared by the analysis features. Spec: ARCHITECTURE.md F-FLT-1.
"""


# Function to keep only the scaling rows
def scaling_cases(cases):
    """
    Description:
    - Return the rows of the scaling experiment.
    - Rows of the other experiments with the same size are never used for growth or extrapolation.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.

    Return:
        list[dict]: the rows with experiment == 'scaling'.
    """
    scaling_rows = []
    for row in cases:
        if row["experiment"] == "scaling":
            scaling_rows.append(row)
    return scaling_rows
