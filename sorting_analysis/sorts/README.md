# sorts

The three sorting algorithms, implemented from scratch. Each algorithm has two files with the same loops:

- **plain** (`bubble_sort.py`, …): no counters; returns the new ascending list. This is the version that is **timed**.
- **counted** (`counted_bubble_sort.py`, …): the same algorithm with operation counters; returns the list and its `SortStats`. It is run outside the clock and supplies the **counts**.

Counters stay out of the timing. Both versions copy the input by slicing (`values[:]`) and never modify it.

| Feature | Purpose |
|---|---|
| `common/` | `SortStats`, the counts returned by every counted sort; `testing/logged_value.py`, a test helper that logs comparisons (`from sorting_analysis.sorts import logged_values`) |
| `bubble_sort/` | Bubble sort with early termination |
| `selection_sort/` | Selection sort, at most one swap per position |
| `merge_sort/` | Top-down merge sort, ties take the left value first |

## Algorithm rules

- **Bubble sort:** every pass compares each neighbouring pair over the whole list and swaps it if `a[j-1] > a[j]`; stop after a full pass with no swaps.
- **Selection sort:** find the minimum of the remaining values, swap only when it is not already in place.
- **Merge sort:** split by slicing, merge with `left[i] <= right[j]` so ties take the left value, then copy the leftover tail.

## Counting rules

- **Comparison:** one comparison between two data values.
- **Write:** each time a data value is stored into a list position. A swap is 2 writes (swaps are also reported separately). Each value placed into a merged list is 1 write, including leftover tails.
- Not counted: copies made only by splitting or slicing, including the initial `values[:]` copy.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `SortStats(comparisons, writes, swaps)` | counts | read-only record: `get_comparisons()`, `get_writes()`, `get_swaps()` (`None` for merge sort) |
| `bubble_sort(values)` / `counted_bubble_sort(values)` | `list[float]` | new list / `(new list, SortStats)`; `[3, 1, 2]` → 4 comparisons, 4 writes, 2 swaps |
| `selection_sort(values)` / `counted_selection_sort(values)` | `list[float]` | new list / `(new list, SortStats)`; `[3, 1, 2]` → 3 comparisons, 4 writes, 2 swaps |
| `merge_sort(values)` / `counted_merge_sort(values)` | `list[float]` | new list / `(new list, SortStats)`; `[2, 1]` → 1 comparison, 2 writes, swaps `None` |

Internal helpers of merge sort, in each file: `_merge_sort_recursive(sublist)` and `_merge(left_half, right_half)`; the counted helpers also return (comparisons, writes).

## Keeping the two versions identical

Each `testing/test_<algorithm>.py` runs both versions on `logged_values(...)` inputs and checks that they make exactly the same sequence of comparisons, and that its length equals the counted comparisons. This catches a plain version that drifts from the counted one (e.g. a missing early termination).
