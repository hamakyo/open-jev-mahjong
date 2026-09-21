# Data workspace

Generated training/evaluation datasets belong here locally, but JSON/JSONL files are ignored by Git.

The first dataset format is a typed-decision row with:

- bounded player-visible `state`
- dynamic legal actions encoded as a single `choice` question
- Mortal-selected action as a one-hot `gold` target
- metadata mapping short labels (`a0`, `a1`, ...) back to original benchmark action IDs

Recommended local layout:

```text
data/
├── raw/
├── train.jsonl
├── validation.jsonl
├── test.jsonl
└── stats.json
```

Splits should be performed by **game ID**, not by individual decision, so adjacent states from one game cannot leak across train/evaluation boundaries.

Do not commit generated datasets unless a deliberately small fixture is added under a future `tests/fixtures/` path.
