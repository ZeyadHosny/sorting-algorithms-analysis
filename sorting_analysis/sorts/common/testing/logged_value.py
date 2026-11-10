"""
Description:
- Test helper: numbers that record every comparison made with them.
- Used to check that a plain sort and its counted version make exactly the same comparisons
  (catches, e.g., a plain bubble sort without early termination).
"""


class LoggedValue:
    """
    Description:
    - A number that appends (operator, left number, right number) to a shared log on every <, <=, > or >=.

    Attributes:
        __number (float): PRIVATE. The wrapped number, e.g. 3.0.
        __log (list[tuple]): PRIVATE. Shared log of comparisons, e.g. [('>', 3.0, 1.0)].

    Methods:
        __init__: constructor.
        get_number: read the wrapped number.
        __lt__, __le__, __gt__, __ge__: compare and record the comparison.
    """

    # Constructor
    def __init__(self, number, log):
        """
        Description:
        - Constructor for the LoggedValue class.

        Input arguments:
           number (float): The wrapped number, e.g. 3.0.
           log (list[tuple]): Shared log of comparisons; appended to on every comparison.

        Return:
            None
        """
        self.__number = number
        self.__log = log

    # Method to read the wrapped number
    def get_number(self):
        """
        Description:
        - Return the wrapped number.

        Input arguments:
           None

        Return:
            float: e.g. 3.0.
        """
        return self.__number

    # Method to record one comparison and return its result
    def __compare(self, operator, other, result):
        """
        Description:
        - Append (operator, this number, other number) to the log and return result.

        Input arguments:
           operator (str): '<', '<=', '>' or '>='.
           other (LoggedValue): The value compared with.
           result (bool): Result of the comparison.

        Return:
            bool: result.
        """
        self.__log.append((operator, self.__number, other.get_number()))
        return result

    # Method for <
    def __lt__(self, other):
        """
        Description:
        - Record and evaluate self < other.

        Input arguments:
           other (LoggedValue): The value compared with.

        Return:
            bool: self < other.
        """
        return self.__compare("<", other, self.__number < other.get_number())

    # Method for <=
    def __le__(self, other):
        """
        Description:
        - Record and evaluate self <= other.

        Input arguments:
           other (LoggedValue): The value compared with.

        Return:
            bool: self <= other.
        """
        return self.__compare("<=", other, self.__number <= other.get_number())

    # Method for >
    def __gt__(self, other):
        """
        Description:
        - Record and evaluate self > other.

        Input arguments:
           other (LoggedValue): The value compared with.

        Return:
            bool: self > other.
        """
        return self.__compare(">", other, self.__number > other.get_number())

    # Method for >=
    def __ge__(self, other):
        """
        Description:
        - Record and evaluate self >= other.

        Input arguments:
           other (LoggedValue): The value compared with.

        Return:
            bool: self >= other.
        """
        return self.__compare(">=", other, self.__number >= other.get_number())


# Function to wrap numbers so their comparisons are logged
def logged_values(numbers, log):
    """
    Description:
    - Wrap each number in a LoggedValue that writes to log.

    Input arguments:
       numbers (list[float]): Numbers to wrap, e.g. [3, 1, 2].
       log (list[tuple]): Shared log of comparisons.

    Return:
        list[LoggedValue]: one wrapped value per number.
    """
    return [LoggedValue(number, log) for number in numbers]
