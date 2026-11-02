"""Unit tests for data.orders (drafts: each test is skipped until it is written)."""
import unittest

from sorting_analysis.data import ascending, descending, make_orders, nearly_sorted  # noqa: F401

NOT_WRITTEN = "test not implemented yet"


class TestOrders(unittest.TestCase):
    """The four input orders."""

    def test_ascending(self):
        """[3, 1, 2] -> [1, 2, 3]."""
        self.skipTest(NOT_WRITTEN)

    def test_descending(self):
        """[1, 2, 3] -> [3, 2, 1]."""
        self.skipTest(NOT_WRITTEN)

    def test_nearly_sorted_applies_one_percent_swaps(self):
        """2000 values -> exactly 20 swaps (at most 40 positions differ from ascending)."""
        self.skipTest(NOT_WRITTEN)

    def test_nearly_sorted_is_reproducible(self):
        """Same seed -> same list."""
        self.skipTest(NOT_WRITTEN)

    def test_random_order_is_returned_unchanged(self):
        """make_orders([3, 1, 2], 44)['random'] == [3, 1, 2]."""
        self.skipTest(NOT_WRITTEN)

    def test_all_orders_hold_the_same_values(self):
        """All four lists are permutations of the input."""
        self.skipTest(NOT_WRITTEN)

    def test_input_is_not_modified(self):
        """The input list is equal before and after make_orders."""
        self.skipTest(NOT_WRITTEN)


if __name__ == "__main__":
    unittest.main()
