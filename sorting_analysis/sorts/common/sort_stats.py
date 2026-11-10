"""
Description:
- Operation counts returned by every sorting algorithm.
"""


class SortStats:
    """
    Description:
    - The counts of one sort run. Read-only: values are set once by the constructor.

    Attributes:
        __comparisons (int): PRIVATE. Comparisons between two data values, e.g. 3.
        __writes (int): PRIVATE. Assignments into a list position; a swap counts as 2, e.g. 4.
        __swaps (int): PRIVATE. Swaps performed, e.g. 2; None for merge sort.

    Methods:
        __init__: constructor.
        get_comparisons, get_writes, get_swaps: the only way to read each attribute.
    """

    # Constructor
    def __init__(self, comparisons, writes, swaps):
        """
        Description:
        - Constructor for the SortStats class.

        Input arguments:
           comparisons (int): Comparisons between two data values, e.g. 3.
           writes (int): Assignments into a list position; a swap counts as 2, e.g. 4.
           swaps (int): Swaps performed, e.g. 2; None for merge sort.

        Return:
            None
        """
        self.__comparisons = comparisons
        self.__writes = writes
        self.__swaps = swaps

    # Method to read the comparison count
    def get_comparisons(self):
        """
        Description:
        - Return the comparison count.

        Input arguments:
           None

        Return:
            int: Comparisons between two data values, e.g. 3.
        """
        return self.__comparisons

    # Method to read the write count
    def get_writes(self):
        """
        Description:
        - Return the write count.

        Input arguments:
           None

        Return:
            int: Assignments into a list position; a swap counts as 2, e.g. 4.
        """
        return self.__writes

    # Method to read the swap count
    def get_swaps(self):
        """
        Description:
        - Return the swap count.

        Input arguments:
           None

        Return:
            int: Swaps performed, e.g. 2; None for merge sort.
        """
        return self.__swaps
