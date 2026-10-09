from dataclasses import dataclass
from pathlib import Path

import numpy as np
import yaml


@dataclass(frozen=True)
class Resources:
    psu: str
    eload: str
    dmm: str


@dataclass(frozen=True)
class SweepSpec:
    start_a: float
    stop_a: float
    points: int
    settle_s: float
    samples: int

    def load_steps(self) -> list[float]:
        return np.linspace(self.start_a, self.stop_a, self.points).round(6).tolist()


@dataclass(frozen=True)
class Limits:
    vout_nominal_v: float
    vout_tolerance_pct: float
    min_efficiency_pct: float
    efficiency_from_load_a: float
    max_load_regulation_pct: float


@dataclass(frozen=True)
class TestSpec:
    __test__ = False

    name: str
    resources: Resources
    input_voltage_v: float
    input_current_limit_a: float
    sweep: SweepSpec
    limits: Limits


def load_spec(path: Path) -> TestSpec:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return TestSpec(
        **{
            **raw,
            "resources": Resources(**raw["resources"]),
            "sweep": SweepSpec(**raw["sweep"]),
            "limits": Limits(**raw["limits"]),
        }
    )
