from dataclasses import dataclass
from enum import StrEnum

import pandas as pd

from pe_bench.config.spec import Limits
from pe_bench.core.analysis import load_regulation_pct


class Status(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    ABORTED = "ABORTED"


@dataclass(frozen=True)
class CheckResult:
    name: str
    measured: float
    relation: str
    limit: float
    unit: str

    @property
    def passed(self) -> bool:
        return self.measured >= self.limit if self.relation == ">=" else self.measured <= self.limit


def evaluate(derived: pd.DataFrame, limits: Limits) -> list[CheckResult]:
    vout_error_pct = (
        100 * (derived.vout_v - limits.vout_nominal_v).abs().max() / limits.vout_nominal_v
    )
    loaded = derived[derived.load_set_a >= limits.efficiency_from_load_a]
    return [
        CheckResult(
            "Worst-case Vout error", float(vout_error_pct), "<=", limits.vout_tolerance_pct, "%"
        ),
        CheckResult(
            f"Min efficiency (load >= {limits.efficiency_from_load_a:g} A)",
            float(loaded.efficiency_pct.min()),
            ">=",
            limits.min_efficiency_pct,
            "%",
        ),
        CheckResult(
            "Load regulation",
            load_regulation_pct(derived),
            "<=",
            limits.max_load_regulation_pct,
            "%",
        ),
    ]


def status_of(checks: list[CheckResult], abort_reason: str | None) -> Status:
    if abort_reason:
        return Status.ABORTED
    return Status.PASS if all(check.passed for check in checks) else Status.FAIL
