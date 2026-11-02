"""
Description:
- Charts of the experiment results. The only module that uses matplotlib.
- matplotlib is optional: it is imported inside the functions, never at module level.
- Spec: ARCHITECTURE.md F-PLT-1 - F-PLT-4.
"""


# Function to check whether matplotlib is installed
def matplotlib_available():
    """
    Description:
    - Try to import matplotlib.

    Input arguments:
       None

    Return:
        bool: True if the charts can be drawn.
    """
    raise NotImplementedError("matplotlib_available: not implemented yet")


# Function to draw the scaling charts
def plot_scaling(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes versus input size for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    raise NotImplementedError("plot_scaling: not implemented yet")


# Function to draw the input-order charts
def plot_input_order(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes per input order for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    raise NotImplementedError("plot_input_order: not implemented yet")


# Function to draw the repeated-values charts
def plot_repeated_values(cases, output_folder):
    """
    Description:
    - Runtime, comparisons and writes per column for each algorithm.

    Input arguments:
       cases (list[dict]): Case rows from case_row or read_cases.
       output_folder (str): Folder for the PNG files.

    Return:
        list[str]: paths of the files written.
    """
    raise NotImplementedError("plot_repeated_values: not implemented yet")
