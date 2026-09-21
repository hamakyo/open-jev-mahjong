from open_jev_mahjong.dataset import validate_row
from open_jev_mahjong.schema import LegalActionSpec, build_hard_label_sample


def test_build_hard_label_sample_uses_short_labels_and_one_hot_target() -> None:
    row = build_hard_label_sample(
        sample_id="game-1/turn-7/seat-0",
        state={"round": "E1"},
        legal_actions=[
            LegalActionSpec(id="discard-4p", description="Discard 4p"),
            LegalActionSpec(id="reach-4p", description="Declare riichi and discard 4p"),
        ],
        selected_action_id="reach-4p",
    )

    validate_row(row)

    assert row["questions"]["action"]["criteria"] == {
        "a0": "Discard 4p",
        "a1": "Declare riichi and discard 4p",
    }
    assert row["gold"]["action"]["label"] == "a1"
    assert row["gold"]["action"]["probabilities"] == {"a0": 0.0, "a1": 1.0}
    assert row["metadata"]["actionMap"] == {
        "a0": "discard-4p",
        "a1": "reach-4p",
    }


def test_selected_action_must_be_legal() -> None:
    try:
        build_hard_label_sample(
            sample_id="game-1/turn-8/seat-0",
            state={},
            legal_actions=[LegalActionSpec(id="discard-4p", description="Discard 4p")],
            selected_action_id="discard-9m",
        )
    except ValueError as error:
        assert "selected_action_id" in str(error)
    else:
        raise AssertionError("expected ValueError")
