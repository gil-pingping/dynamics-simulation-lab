from __future__ import annotations

from dataclasses import asdict
import csv
from pathlib import Path
from typing import Callable, Sequence, TypeAlias

State: TypeAlias = list[float]
DerivativeFunction: TypeAlias = Callable[[float, State], State]


def rk4_step(derivative: DerivativeFunction, time: float, state: State, dt: float) -> State:
    k1 = derivative(time, state)
    k2 = derivative(time + 0.5 * dt, _combine(state, k1, 0.5 * dt))
    k3 = derivative(time + 0.5 * dt, _combine(state, k2, 0.5 * dt))
    k4 = derivative(time + dt, _combine(state, k3, dt))
    return [
        value + (dt / 6.0) * (delta_1 + 2.0 * delta_2 + 2.0 * delta_3 + delta_4)
        for value, delta_1, delta_2, delta_3, delta_4 in zip(state, k1, k2, k3, k4, strict=True)
    ]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def write_dataclass_rows_csv(path: Path, rows: Sequence[object]) -> None:
    if not rows:
        raise ValueError("At least one row is required to write a CSV file.")

    fieldnames = list(asdict(rows[0]).keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _combine(state: State, derivative: State, scale: float) -> State:
    return [value + scale * delta for value, delta in zip(state, derivative, strict=True)]
