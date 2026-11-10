# Contributing

DATA 5010 - Project 2: Sorting Algorithm Analysis
Last updated: 2026-11-10

## Pull requests

All changes reach `main` through a pull request approved by the other team member. Nobody approves their own work. After the code freeze, only bug fixes and documentation are merged.

A pull request description states what changed, which requirement it covers, and how it was tested. Mention in the title if it changes a shared file: `main.py`, `sorting_analysis/config.py`, any area's `__init__.py` or `common/` folder, or a sorting algorithm.

Function signatures, shared modules and agreed assumptions change only with both members' approval, and the change is documented before it is implemented.

## Branches and commits

Branch: `<type>/<short-description>`, lowercase with hyphens, e.g. `docs/cleaning-docs`.
Types: `feat`, `fix`, `test`, `docs`, `chore`.

Commit: a short imperative summary, e.g. `add result tables and refine charts`.

Pull `main` before starting, and delete a branch after it is merged.

## Package layout

Each area under `sorting_analysis/` (`data`, `sorts`, `timing`, `experiments`, `analysis`, `plots`) contains:

```
README.md          what the area does and its interfaces
__init__.py        the names other code may import; imports common/ first, if present
common/            code shared by the area's features (optional)
<feature>/
    __init__.py
    implementation/    code
    testing/           unit tests (must contain __init__.py)
```

Import from the area, also inside it. Only a feature's `__init__.py` imports from its `implementation/` folder:

```python
from sorting_analysis.sorts import bubble_sort                                   # yes
from sorting_analysis.sorts.bubble_sort.implementation.bubble_sort import bubble_sort  # no
```

Seeds, sizes, columns and timing values are defined once in `sorting_analysis/config.py` and never hard-coded elsewhere.

## Code rules

- Standard library only; `matplotlib` only in `plots/`.
- Never use `sort()` or `sorted()`, except `sorted()` to verify an output.
- Sorting functions copy their input (`values[:]`) and never modify it. The plain version, which is timed, returns a new sorted list; the counted version, with the same loops, returns `(sorted_values, SortStats)`. Change both together.
- Count and time exactly as defined in the README: a swap is 2 writes, slicing is not counted, only the plain sorts are timed, with `time.perf_counter()`.
- `snake_case` for modules, functions and variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants, each with a comment. Names describe their meaning (`order_sample_size`, not `n2`).
- No type hints, `@property` or `@dataclass`. Result records set private attributes once and expose `get_<attribute>()` methods.
- Every function has a comment above it (`# Function to ...` or `# Method to ...`) and a docstring with **Description**, **Input arguments** (`name (type): meaning`) and **Return**. Test methods use a short docstring stating the expected result.

## Data and outputs

- `housing.csv` is never edited.
- `results/` holds the official outputs, written only by `python main.py`. Commit them after an official run, and never edit them by hand.
- Development commands write to `results/dev/`, which Git ignores, as are `__pycache__/`, `.venv/` and `.vscode/`.

## Tests

Run from the repository folder before opening a pull request:

```bash
python -m unittest discover
```

The current result is `Ran 263 tests ... OK`. Check the number of tests, not only `OK`; a `testing/` folder without `__init__.py` is skipped silently.

## Quick reference

```
BRANCH   docs/cleaning-docs
COMMIT   add result tables and refine charts
REVIEW   one approval, never your own
IMPORT   from sorting_analysis.<area> import <name>
SETTINGS sorting_analysis/config.py
RUN      python main.py                (official results in results/)
TESTS    python -m unittest discover   (263 tests)
```
