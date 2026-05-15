"""Shared contracts and aliases for vision pipeline modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Mapping, Sequence, Tuple

FACE_ORDER: Tuple[str, str, str, str, str, str] = ("U", "R", "F", "D", "L", "B")
VALID_FACE_SET = set(FACE_ORDER)

CubeState = Dict[str, list[str]]
PartialScan = Dict[str, list[str]]
CaptureFn = Callable[[Iterable[str]], Mapping[str, Sequence[str]]]


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    message: str
