import pytest

from pe_bench.cli import main
from pe_bench.config.spec import load_spec
from pe_bench.core.runner import run_test
from pe_bench.core.sweep import COLUMNS
from pe_bench.core.verdict import Status
from pe_bench.sim.bench import SimulatedBench

OUTCOMES = [
    ("buck_5v", Status.PASS, 0),
    ("buck_5v_marginal", Status.FAIL, 1),
    ("buck_5v_overcurrent", Status.ABORTED, 2),
]


@pytest.mark.parametrize(("spec_name", "status", "_exit_code"), OUTCOMES)
def test_run_reaches_expected_status(spec_dir, spec_name, status, _exit_code):
    result = run_test(load_spec(spec_dir / f"{spec_name}.yaml"), SimulatedBench())
    assert result.status is status


def test_full_sweep_captures_every_point(spec):
    result = run_test(spec, SimulatedBench())
    assert len(result.data) == spec.sweep.points
    assert list(result.data.columns[: len(COLUMNS)]) == COLUMNS


def test_abort_keeps_partial_data_and_turns_outputs_off(spec_dir):
    simulated = SimulatedBench()
    result = run_test(load_spec(spec_dir / "buck_5v_overcurrent.yaml"), simulated)
    assert 0 < len(result.data) < result.spec.sweep.points
    assert "limit exceeded" in result.abort_reason
    assert result.checks == []
    assert not simulated.psu_on and not simulated.load_on


def test_same_seed_gives_identical_measurements(spec):
    first = run_test(spec, SimulatedBench(seed=7)).data.drop(columns="timestamp")
    second = run_test(spec, SimulatedBench(seed=7)).data.drop(columns="timestamp")
    assert first.equals(second)


@pytest.mark.parametrize(("spec_name", "_status", "exit_code"), OUTCOMES)
def test_cli_exit_code_and_artifacts(spec_dir, tmp_path, spec_name, _status, exit_code):
    code = main([str(spec_dir / f"{spec_name}.yaml"), "--sim", "--out", str(tmp_path)])
    assert code == exit_code
    assert {path.suffix for path in tmp_path.iterdir()} == {".csv", ".html", ".png"}


def test_report_states_status_and_abort_reason(spec_dir, tmp_path):
    main([str(spec_dir / "buck_5v_overcurrent.yaml"), "--sim", "--out", str(tmp_path)])
    html = (tmp_path / "buck_5v_overcurrent_trip.html").read_text(encoding="utf-8")
    assert "ABORTED" in html
    assert "limit exceeded" in html
