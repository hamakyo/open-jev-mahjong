"""Minimal JSONL helpers for generated Mahjong distillation data."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any


def validate_row(row: dict[str, Any]) -> None:
    """Validate the minimum contract needed by the first training pipeline."""

    for key in ("id", "workflow", "state", "questions", "gold"):
        if key not in row:
            raise ValueError(f"missing required field: {key}")

    questions = row["questions"]
    gold = row["gold"]
    if not isinstance(questions, dict) or "action" not in questions:
        raise ValueError("questions.action is required")
    if not isinstance(gold, dict) or "action" not in gold:
        raise ValueError("gold.action is required")

    action_question = questions["action"]
    action_gold = gold["action"]
    if action_question.get("type") != "choice":
        raise ValueError("questions.action.type must be 'choice'")

    criteria = action_question.get("criteria")
    probabilities = action_gold.get("probabilities")
    selected = action_gold.get("label")
    if not isinstance(criteria, dict) or not criteria:
        raise ValueError("questions.action.criteria must be a non-empty object")
    if not isinstance(probabilities, dict):
        raise TypeError("gold.action.probabilities must be an object")
    if set(criteria) != set(probabilities):
        raise ValueError("criteria labels and probability labels must match")
    if selected not in criteria:
        raise ValueError("gold.action.label must be one of the legal choice labels")

    total = sum(float(value) for value in probabilities.values())
    if abs(total - 1.0) > 1e-6:
        raise ValueError(f"gold probabilities must sum to 1.0, got {total}")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise TypeError(f"line {line_number}: expected JSON object")
            validate_row(row)
            rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> int:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            validate_row(row)
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            count += 1
    return count
