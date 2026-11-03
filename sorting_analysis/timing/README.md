# timing

Measures the runtime of one sort on one input, collects its operation counts, and verifies every output.

| Feature | Purpose |
|---|---|
| `benchmark/` | Timed batches, counts, verification and the median |

## Timing rule

| Input size | Sorts per batch | Batches | Reported |
|---|---|---|---|
| n ≤ 20 (very small: 5, 10, 20) | 1,000 | 5 | median of (batch time ÷ 1,000) |
| n > 20 | 1 | 5 | median of the 5 times |

Only the **plain** sort (no counters) is timed, as the instructor required. The timed region (`time.perf_counter()`) contains only its calls and storing their outputs. The **counted** sort runs once per batch outside the clock and supplies the counts. Verification against `sorted()` runs after the clock stops. Garbage collection is disabled while timing and restored afterwards.

## Interfaces

| Name | Input | Output |
|---|---|---|
| `benchmark(sort_function, counted_sort_function, values, settings)` | plain sort, counted sort, input, settings | `(TimingResult, SortStats)`; `VerificationError` on a wrong output, changing counts or a modified input |
| `TimingResult(batch_seconds, sorts_per_batch, median_seconds, min_seconds, max_seconds)` | seconds per sort per batch, sorts per batch, and their median, min, max | read-only record with a getter per value, filled in once by `benchmark` |
| `repetitions_for(input_size, settings)` | input size, settings | sorts per batch: 1,000 if input_size ≤ 20, else 1 |
| `median_of(values)` | `list[float]` | median, computed with our plain merge sort |
| `VerificationError` | — | raised when verification fails |
