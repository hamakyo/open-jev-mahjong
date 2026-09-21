<div align="center">

# Open Jev Mahjong

**Distill Mortal's riichi-mahjong decisions into a small, local typed decision model.**

A research project for training a Mahjong-specialized Open Jev / ModernBERT model from Mortal teacher decisions, then evaluating it in real games with [jev-mahjong-bench](https://github.com/hamakyo/jev-mahjong-bench).

</div>

## Research question

> How much of a strong mahjong agent's decision policy can be compressed into a ~150M-parameter encoder-only typed decision model?

The initial target is deliberately simple:

```text
MJAI logs / generated games
        ↓
jev-mahjong-bench + RiichiEnv
        ↓
bounded state + legal actions
        ↓
Mortal teacher action
        ↓
typed-decision JSONL
        ↓
ModernBERT-base (~150M) fine-tuning
        ↓
Mahjong Open Jev
        ↓
jev-mahjong-bench evaluation / tournaments
```

This repository owns **dataset construction, distillation, training, calibration, and local inference**.

[jev-mahjong-bench](https://github.com/hamakyo/jev-mahjong-bench) remains the neutral evaluation/tournament harness.

## Why this is interesting

Mortal is a mahjong-specific agent. Open Jev is a small encoder-only decision model that consumes a state plus a dynamic set of typed candidate labels and produces a decision with confidence.

That makes a natural distillation experiment:

- Mortal supplies the teacher action.
- Open Jev learns to choose among the same legal actions.
- The student can run locally with no per-call API cost.
- The student exposes confidence, enabling later routing/fallback experiments.
- The same benchmark harness can compare the student against Mortal, TypeSafe Jev, GPT-class models, and other providers.

## Phase 1: hard-label distillation

The MVP uses Mortal's **selected action** as the teacher label.

A training sample is shaped like:

```json
{
  "id": "game-123/turn-456/seat-2",
  "workflow": "riichi_mahjong",
  "state": {
    "...": "bounded public/current game state"
  },
  "questions": {
    "action": {
      "type": "choice",
      "instructions": "Choose the strongest legal riichi-mahjong action.",
      "criteria": {
        "a0": "Discard 4p. MJAI: {...}",
        "a1": "Declare riichi and discard 4p. MJAI: {...}",
        "a2": "Discard 1m. MJAI: {...}"
      }
    }
  },
  "gold": {
    "action": {
      "label": "a1",
      "probabilities": {
        "a0": 0.0,
        "a1": 1.0,
        "a2": 0.0
      }
    }
  }
}
```

Short labels such as `a0`, `a1`, ... are used for the choice keys. Human/model-readable action semantics live in the descriptions.

The first version intentionally uses one-hot teacher targets. We should **not treat arbitrary Mortal Q-values as calibrated action probabilities** without validating that interpretation.

## Phase 2: soft distillation

After the hard-label baseline is established, investigate a policy-oriented teacher that can provide a meaningful action distribution.

Possible directions include Mortal-Policy or another policy model whose outputs have clear probabilistic semantics.

The goal is then to train against soft targets such as:

```text
discard 5p   0.52
discard 3m   0.27
reach        0.18
other        0.03
```

This aligns better with Open Jev's calibration-oriented training objective.

## Dataset principles

A useful dataset must preserve the benchmark contract:

- only information legally visible to the acting player
- bounded current state rather than unbounded event history for the student
- the exact legal-action set available at that decision
- deterministic mapping from short choice labels to original action IDs
- game-level train/validation/test splitting to avoid leakage across decisions from the same game
- action-type statistics so common discards do not silently overwhelm rare calls, riichi, wins, and kan decisions
- reproducible teacher/model/version metadata

Large generated datasets and model checkpoints should not be committed directly to Git.

## Target milestones

| Stage | Approx. decisions | Purpose |
| --- | ---: | --- |
| Smoke | 5,000 | Validate the complete export → train → infer loop |
| Prototype | 50,000 | Determine whether Mortal agreement rises meaningfully |
| Scale | 200,000–500,000 | Train/evaluate a serious specialist model |

These are experiment targets, not claims about the amount of data required for strong play.

## Evaluation

Offline metrics:

- Mortal action agreement
- agreement by action type
- confidence / calibration metrics
- coverage at confidence thresholds
- inference latency
- model memory footprint

Full-game metrics via `jev-mahjong-bench`:

- average rank / score
- win rate
- deal-in rate
- riichi rate
- call rate
- decision latency
- error / fallback rate

A useful comparison set is:

```text
Mortal
TypeSafe Jev
Open Jev (generic, zero-shot)
Mahjong Open Jev (Mortal-distilled)
GPT-class LLM
Random baseline
```

## Planned repository shape

```text
open-jev-mahjong/
├── data/
│   └── README.md
├── docs/
│   └── architecture.md
├── src/
│   └── open_jev_mahjong/
│       ├── __init__.py
│       ├── dataset.py
│       └── schema.py
├── tests/
│   └── test_schema.py
├── pyproject.toml
└── README.md
```

Training code will be added after the dataset contract is proven. The upstream reference implementation is [intikhab49/open-jev-typed-decision-engine](https://github.com/intikhab49/open-jev-typed-decision-engine).

## Roadmap

- [#1 Export Mortal hard-label distillation dataset](https://github.com/hamakyo/open-jev-mahjong/issues/1)
- [#2 Train ModernBERT student from local Mahjong JSONL](https://github.com/hamakyo/open-jev-mahjong/issues/2)
- [#3 Run 5k and 50k distillation baselines](https://github.com/hamakyo/open-jev-mahjong/issues/3)
- [#4 Serve the student and integrate with jev-mahjong-bench](https://github.com/hamakyo/open-jev-mahjong/issues/4)
- [#5 Evaluate against Mortal, Jev, GPT and random](https://github.com/hamakyo/open-jev-mahjong/issues/5)
- [#6 Investigate soft-label distillation](https://github.com/hamakyo/open-jev-mahjong/issues/6)

## Status

Early scaffold. No trained Mahjong checkpoint is published yet.

The first milestone is a reproducible hard-label dataset exported from Mortal decisions and a small smoke-training run.
