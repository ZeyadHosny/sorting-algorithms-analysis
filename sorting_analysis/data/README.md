# data

Prepares the inputs: reads the CSV, inspects the selected columns, draws seeded samples and builds the four input orders. Nothing here is timed. Standard library only; no `sort()` or `sorted()`.

| Feature | Purpose |
|---|---|
| `loader/` | Read the CSV and convert values to floats |
| `inspection/` | Rows, missing and distinct values per column; duplication statistics |
| `sampling/` | Seeded sampling and shuffling of row indices |
| `orders/` | Random, sorted, reversed and nearly sorted inputs |

## Interfaces

### loader

| Function | Input | Output |
|---|---|---|
| `load_csv(path)` | CSV path | `list[dict[str, str]]` raw rows; `FileNotFoundError` if missing |
| `parse_value(raw_value)` | raw string | `float`, or `None` if blank, unparsable or not finite |
| `complete_cases(rows, columns)` | raw rows, selected columns | indices of rows with every selected value valid |
| `column_values(rows, column, row_indices)` | raw rows, column, row indices | `list[float]` in index order |

### inspection

| Name | Input | Output |
|---|---|---|
| `inspect_data(rows, columns)` | raw rows, selected columns | one dict per column: `column, rows, missing, distinct, excluded_rows` |
| `duplicate_stats(values)` | sample values | `sample_size, distinct, modal_value, modal_count, repeated_distinct, repeated_observations` |
| `INSPECTION_FIELDS`, `DUPES_FIELDS` | — | CSV headers of the two results |

### sampling

| Function | Input | Output |
|---|---|---|
| `sample_indices(usable_indices, sample_size, seed)` | usable indices, size, seed | distinct indices; `ValueError` if the sample is too large |
| `shuffle_indices(row_indices, seed)` | indices, seed | new list in seeded random order |

### orders

| Function | Input | Output |
|---|---|---|
| `ascending(values)` | values | sorted copy (our merge sort) |
| `descending(values)` | values | reverse of `ascending` |
| `nearly_sorted(values, seed)` | values, seed | ascending with floor(0.01 · len(values)) random swaps |
| `make_orders(shuffled_values, nearly_sorted_seed)` | shuffled values, seed | `{"random", "sorted", "reversed", "nearly"}`; `"random"` unchanged |
