import pandas as pd
import pytest

from pe_bench.config.spec import Limits
from pe_bench.core.analysis import add_derived, load_regulation_pct
from pe_bench.core.verdict import CheckResult, Status, evaluate, status_of

LIMITS = Limits(
    vout_nominal_v=5.0,
    vout_tolerance_pct=2.0,
    min_efficiency_pct=90.0,
    efficiency_from_load_a=1.0,
    max_load_regulation_pct=1.0,
)


def measurements(vout_v: list[float], iin_a: list[float]) -> pd.DataFrame:
    loads = [0.5, 1.0, 2.0][: len(vout_v)]
    return pd.DataFrame(
        {"load_set_a": loads, "vin_v": 12.0, "iin_a": iin_a, "vout_v": vout_v, "iout_a": loads}
    )


def test_efficiency_is_output_power_over_input_power():
    derived = add_derived(measurements([5.0], [0.5]).assign(iout_a=1.0, load_set_a=1.0))
    assert derived.pin_w[0] == pytest.approx(6.0)
    assert derived.efficiency_pct[0] == pytest.approx(100 * 5.0 / 6.0)
    assert derived.loss_w[0] == pytest.approx(1.0)


def test_load_regulation_is_droop_over_light_load_voltage():
    derived = add_derived(measurements([5.0, 4.95, 4.9], [0.3, 0.5, 1.0]))
    assert load_regulation_pct(derived) == pytest.approx(2.0)


def test_good_unit_passes_every_check():
    derived = add_derived(measurements([5.0, 4.99, 4.98], [0.25, 0.46, 0.88]))
    checks = evaluate(derived, LIMITS)
    assert all(check.passed for check in checks)
    assert status_of(checks, None) is Status.PASS


def test_efficiency_limit_ignores_loads_below_the_cutoff():
    derived = add_derived(measurements([5.0, 4.99, 4.98], [0.5, 0.46, 0.88]))
    efficiency_check = evaluate(derived, LIMITS)[1]
    assert efficiency_check.measured > 90.0


def test_one_failing_check_fails_the_run():
    derived = add_derived(measurements([5.0, 4.9, 4.7], [0.25, 0.42, 0.80]))
    checks = evaluate(derived, LIMITS)
    assert [check.passed for check in checks] == [False, True, False]
    assert status_of(checks, None) is Status.FAIL


def test_abort_reason_overrides_checks():
    passing = [CheckResult("x", 1.0, "<=", 2.0, "%")]
    assert status_of(passing, "PSU tripped") is Status.ABORTED
