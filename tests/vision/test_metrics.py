from vision.metrics import evaluate_predictions


def test_perfect_reconstruction_metrics():
    state = "".join(face * 9 for face in "URFDLB")
    result = evaluate_predictions([state], [state])
    assert result.sticker_accuracy == 1
    assert result.macro_f1 == 1
    assert result.exact_cube_accuracy == 1
