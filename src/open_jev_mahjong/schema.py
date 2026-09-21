"""Helpers for the Mahjong typed-decision training format.

The student sees a bounded game state plus the exact legal-action set.
Choice labels are intentionally short and positional (a0, a1, ...); the original
action IDs are preserved in metadata for replay/evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

WORKFLOW = "riichi_mahjong"
ACTION_QUESTION = "action"
ACTION_INSTRUCTION = "Choose the strongest legal riichi-mahjong action."


@dataclass(frozen=True, slots=True)
class LegalActionSpec:
    """A legal action exposed to the typed decision model."""

    id: str
    description: str


def build_hard_label_sample(
    *,
    sample_id: str,
    state: Any,
    legal_actions: list[LegalActionSpec],
    selected_action_id: str,
    teacher: str = "mortal",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one hard-label distillation row.

    Mortal's selected action is represented as a one-hot target. This deliberately
    avoids interpreting arbitrary teacher Q-values as calibrated probabilities.
    """

    if not sample_id:
        raise ValueError("sample_id must not be empty")
    if not legal_actions:
        raise ValueError("legal_actions must not be empty")

    ids = [action.id for action in legal_actions]
    if len(ids) != len(set(ids)):
        raise ValueError("legal action IDs must be unique")
    if selected_action_id not in ids:
        raise ValueError("selected_action_id must be present in legal_actions")

    labels = [f"a{index}" for index in range(len(legal_actions))]
    action_map = {label: action.id for label, action in zip(labels, legal_actions, strict=True)}
    criteria = {
        label: action.description
        for label, action in zip(labels, legal_actions, strict=True)
    }
    selected_label = next(label for label, action_id in action_map.items() if action_id == selected_action_id)
    probabilities = {label: float(label == selected_label) for label in labels}

    row_metadata: dict[str, Any] = {
        "teacher": teacher,
        "actionMap": action_map,
    }
    if metadata:
        row_metadata.update(metadata)

    return {
        "id": sample_id,
        "workflow": WORKFLOW,
        "state": state,
        "questions": {
            ACTION_QUESTION: {
                "type": "choice",
                "instructions": ACTION_INSTRUCTION,
                "criteria": criteria,
            }
        },
        "gold": {
            ACTION_QUESTION: {
                "label": selected_label,
                "probabilities": probabilities,
            }
        },
        "metadata": row_metadata,
    }
