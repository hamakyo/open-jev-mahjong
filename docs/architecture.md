# Architecture

## Boundary between repositories

`open-jev-mahjong` is responsible for the student model lifecycle:

```text
dataset contract → distillation data → training → calibration → local inference
```

`jev-mahjong-bench` remains responsible for the environment and neutral evaluation:

```text
RiichiEnv → legal decisions → teacher/reference generation → tournaments → reports
```

Keeping these responsibilities separate makes it possible to benchmark the student without coupling the benchmark to its training implementation.

## Phase 1 data flow

```text
MJAI / seeded RiichiEnv games
          │
          ▼
jev-mahjong-bench
  bounded current state
  legal action set
          │
          ├─────────────► Mortal
          │                 │
          │                 ▼
          │           selected legal action
          │                 │
          └─────────────────┘
                    │
                    ▼
          typed-decision JSONL
                    │
                    ▼
          ModernBERT-base student
                    │
                    ▼
          Mahjong Open Jev checkpoint
                    │
                    ▼
        local typed-decision endpoint
                    │
                    ▼
          jev-mahjong-bench tournament
```

## State contract

The student must receive the same bounded decision state used for other LLM/decision agents in the benchmark.

The exporter must not leak:

- concealed opponent hands
- future wall information
- future events
- post-decision outcomes

Cumulative MJAI history can remain available to Mortal internally when required by its protocol, but the student training row should contain the bounded state contract.

## Legal-action representation

Every decision is one dynamic `choice` question.

Choice keys should be short positional labels:

```text
a0
a1
a2
...
```

Descriptions carry the semantic action representation. The original benchmark action ID is stored in metadata so predictions can be mapped back exactly.

This avoids making long opaque IDs part of the classification vocabulary.

## Teacher targets

### MVP

Use Mortal's final selected legal action as a one-hot distribution.

This gives an unambiguous first experiment and avoids claiming that internal Q-values are calibrated probabilities.

### Later research

A policy-oriented teacher may provide a meaningful soft action distribution. That can then be used directly with Open Jev's soft-target / calibration-oriented training objective.

Soft-label distillation must be evaluated separately from the hard-label baseline.

## Split strategy

Split at game level before materializing train/validation/test decision rows.

Why:

- decisions from the same hand are highly correlated
- adjacent states differ by only a few events
- decision-level random splitting would inflate offline agreement

Persist the split seed and source game IDs in dataset metadata.

## Evaluation ladder

1. Schema/unit tests.
2. 5k-decision smoke dataset.
3. Offline held-out Mortal agreement.
4. Agreement broken down by action type.
5. Confidence/calibration analysis.
6. 50k-decision prototype.
7. Full-game paired tournaments in `jev-mahjong-bench`.
8. Scale dataset/model only after the previous stages are stable.

## Reproducibility metadata

Each generated dataset should record, at minimum:

- exporter version / commit
- source benchmark commit
- RiichiEnv version
- Mortal configuration / policy identifier
- rule set
- game seeds or source game IDs
- state schema version
- action-description schema version
- split seed

Do not serialize credentials, machine-specific secrets, or private source paths.
