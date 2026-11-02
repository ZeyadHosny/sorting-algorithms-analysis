# timing

Measures the runtime of one sort on one input and verifies every output.

| Feature | Purpose |
|---|---|
| `benchmark/` | Timed batches, verification and the median |

## Timing rule

| Input size | Sorts per batch | Batches | Reported |
|---|---|---|---|
| n ≤ 20 | 1,000 | 5 | median of (batch time ÷ 1,000) |
| n > 20 | 1 | 5 | median of the 5 times |

The timed region (`time.perf_counter()`) contains only the sort calls and storing their outputs. Verification against `sorted()` runs after the clock stops. Garbage collection is disabled while timing and restored afterwards.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `benchmark(sort_function, values, settings)` | sort function, input, settings | `(TimingResult, SortStats)`; `VerificationError` on a wrong output, changing counts or a modified input |
| `TimingResult(batch_seconds, sorts_per_batch, median_seconds, min_seconds, max_seconds)` | seconds per sort per batch, sorts per batch, and their median, min, max | read-only record with a getter per value, filled in once by `benchmark` |
| `median_of(values)` | `list[float]` | median, computed with our merge sort |
| `VerificationError` | — | raised when verification fails |
