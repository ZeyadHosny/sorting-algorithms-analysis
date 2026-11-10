# tests

End-to-end tests of `main.py` on a 30-row dataset with small settings; outputs go to temporary folders. Unit tests are in each feature's `testing/` folder.

| Test class | Checks |
|---|---|
| `TestDevelopmentCommands` | `check`, the single experiments, `analyze` and `plot`: output folders, no `metadata.json`, and input errors (exit code 2) |
| `TestEndToEnd` | The official run: every output, `python main.py` without a command, figures only with matplotlib, removal of old outputs, no `metadata.json` after a failure, and `results/` never touched |

## Running

```
python -m unittest discover
```

Run from the repository folder; one test file runs as a module, e.g. `python -m tests.test_end_to_end`. The suite runs 263 tests; without matplotlib, 25 are skipped.
