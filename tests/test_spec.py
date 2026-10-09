import pytest
import yaml

from pe_bench.config.spec import load_spec


def test_load_steps_are_evenly_spaced_and_inclusive(spec):
    steps = spec.sweep.load_steps()
    assert len(steps) == spec.sweep.points
    assert steps[0] == spec.sweep.start_a
    assert steps[-1] == spec.sweep.stop_a


def test_unknown_key_is_rejected(spec_dir, tmp_path):
    raw = yaml.safe_load((spec_dir / "buck_5v.yaml").read_text())
    raw["limits"]["max_ripple_mv"] = 50
    broken = tmp_path / "broken.yaml"
    broken.write_text(yaml.safe_dump(raw))
    with pytest.raises(TypeError, match="max_ripple_mv"):
        load_spec(broken)
