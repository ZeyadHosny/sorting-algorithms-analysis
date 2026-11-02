# sorts

The three sorting algorithms, implemented from scratch. Each returns a new ascending list and the operation counts of the run; the input is never modified.

| Feature | Purpose |
|---|---|
| `common/` | `SortStats`, the counts returned by every sort |
| `bubble_sort/` | Bubble sort with early termination |
| `selection_sort/` | Selection sort |
| `merge_sort/` | Top-down merge sort |

## Counting rules

- **Comparison:** one comparison between two data values.
- **Write:** one assignment of a value into a list position. A swap is 2 writes. Each value placed into a merged list is 1 write, including leftover tails.
- Not counted: the initial copy of the input, and copies made by slicing.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `SortStats(comparisons, writes, swaps)` | counts | read-only record: `get_comparisons()`, `get_writes()`, `get_swaps()` (`None` for merge sort) |
| `bubble_sort(values)` | `list[float]` | `(sorted list, SortStats)`; stops after a pass with no swaps; inner range shrinks by one per pass |
| `selection_sort(values)` | `list[float]` | `(sorted list, SortStats)`; swaps only when the minimum is not in place |
| `merge_sort(values)` | `list[float]` | `(sorted list, SortStats)`; ties take the left element first |

Internal helpers of merge sort: `_merge_sort_recursive(sublist)` returns (sorted, comparisons, writes); `_merge(left_half, right_half)` returns (merged, comparisons, writes).
