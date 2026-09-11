from vision.reconstruction import reconstruct
from vision.warp_sampling import SampledFace, StickerSample


BGR = {
    "U": (245, 245, 245), "R": (20, 20, 230), "F": (20, 180, 20),
    "D": (0, 220, 245), "L": (10, 120, 245), "B": (220, 100, 20),
}


def _face(label):
    samples = tuple(StickerSample(i // 3, i % 3, BGR[label], BGR[label], 0.0) for i in range(9))
    return SampledFace(label, label, samples, None)


def test_solved_observations_reconstruct_solved_state():
    result = reconstruct([_face(x) for x in ("U", "F", "R")], [_face(x) for x in ("D", "B", "L")])
    assert result.cube_string == "".join(face * 9 for face in "URFDLB")
    assert result.structurally_valid
