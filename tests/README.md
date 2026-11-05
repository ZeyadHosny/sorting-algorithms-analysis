# tests

End-to-end tests of `main.py`. Unit tests live next to each feature, in its `testing/` folder.

| Test class | Checks |
|---|---|
| `TestMockRun` | While steps are mocked: every command succeeds, `metadata.json` is never written, outputs default to `results/dev/`; a missing dataset and `plot` without matplotlib give exit code 2 |
| `TestEndToEnd` | Once nothing is mocked: `main all` on a tiny CSV with small settings writes every output; failures write no `metadata.json`; `results/` is never touched |

## Running

```
python -m unittest discover
```

Run from the repository root (the folder with `main.py`); a single test file runs as a module, e.g. `python -m sorting_analysis.sorts.selection_sort.testing.test_selection_sort`. Drafted tests are reported as skipped until they are written; a run in which every test is skipped is not a pass.
