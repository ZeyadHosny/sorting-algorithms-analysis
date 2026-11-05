# Contributing

## Setup

- Clone the shared repository. Both members use Python 3.10 or newer.
- The dataset `housing.csv` is included in the repository root. Never modify it.
- Run everything from the repository root (the folder with `main.py`). Run `python -m unittest discover` there to confirm the setup works.

## Workflow

1. Pull the latest `main` before starting any work.
2. Create a branch: `feature/<description>`, `fix/<description>` or `docs/<description>`.
3. Change only the files of the feature you are working on.
4. Function signatures, shared modules and settings are agreed between both members. Do not change them alone; update the architecture document first, then the code.
5. Add or update unit tests in the feature's `testing/` folder.
6. Run all tests from the repository root and review your changes. A run with zero tests is not a pass.
7. Commit small, focused changes with clear messages, e.g. `Add bubble sort with early termination`.
8. Push the branch and open a pull request describing what changed, how it was tested and any known issues.
9. The other member reviews before merging. Resolve conflicts line by line, never by accepting one whole version.

## Naming

- Folders, files, functions and variables: `snake_case`.
- Classes: `PascalCase`. Constants: `UPPER_SNAKE_CASE`.
- Test files: `test_<feature>.py`. Test methods: `test_<behaviour>`.
- No duplicate copies such as `final`, `new` or `v2`.

## Code style

- No type hints, `@property` or `@dataclass`. Types are given in the docstrings.
- Every function and method has a comment above it (`# Function to ...`, `# Method to ...`) and a docstring with **Description**, **Input arguments** (`name (type): meaning`) and **Return** (`type: meaning (raises X if ...)`).
- Result records are plain classes with private attributes set once in the constructor and read with `get_<attribute>()`. `config.py` holds values only.
- Every module constant has a comment. Names describe their meaning (`order_sample_size`, not `n2`).
- Exceptions: test methods use a one-line docstring stating the expected result, and the temporary `mock_*` functions in `main.py` have only a one-line comment, because they are deleted once the real step exists.
- Every import uses an area's `__init__.py`: `from sorting_analysis.<area> import <name>` (e.g. `from sorting_analysis.sorts import SortStats`), also inside the area. Each area's `__init__.py` imports its `common/` first, because the features import its names back through the area.
- Everything runs from the repository root (the folder with `main.py`): `python main.py ...`, `python -m unittest discover`, or one test file as a module, e.g. `python -m sorting_analysis.sorts.selection_sort.testing.test_selection_sort`. All paths are relative to the root.

## Project rules

- Use only the Python standard library. `matplotlib` is allowed only for plots.
- Never use `sort()` or `sorted()`, except `sorted()` to verify that an output is correct.
- Sorting functions copy their input by slicing (`values[:]`), return a new list and never modify the input.
- Each algorithm has two versions with the same loops: a plain version, which is timed, and a counted version, which supplies the operation counts. Change both together; the comparison-trace tests must keep passing.
- Bubble sort follows the lecture code (full passes, stop after a pass with no swaps). Selection sort swaps at most once per position, and merge sort takes the left value on ties (`<=`), as the PDF requires.
- Count comparisons and writes exactly as defined: a swap is two writes; each value placed into a merged list is one write, including leftover tails; the initial copy of the input and the lists created by slicing are not counted.
- Measure time with `time.perf_counter()` only. Only the plain sorts are timed; counters, loading, sampling and preparing inputs are never timed.
- Seeds, sample sizes and timing settings are defined once in `config.py` and never hard-coded elsewhere.

## Shared rules

- Each feature has one implementation (for a sort: its plain and counted files). Shared code belongs in `common/`.
- Official results are produced only by `python main.py all`, run once on one machine. Development runs write to `results/dev/`.
- Never edit result files by hand.
- Any change to an agreed assumption requires both members' approval and is documented before it is implemented.
- Do not commit `__pycache__/`, virtual environments or editor settings.
- After the code freeze, merge only bug fixes, each through a reviewed pull request.
