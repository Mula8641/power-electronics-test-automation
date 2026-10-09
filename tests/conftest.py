from pathlib import Path

import pytest

from pe_bench.config.spec import load_spec
from pe_bench.sim.bench import SimulatedBench

SPEC_DIR = Path(__file__).parent.parent / "specs"


@pytest.fixture
def sim() -> SimulatedBench:
    return SimulatedBench()


@pytest.fixture
def spec():
    return load_spec(SPEC_DIR / "buck_5v.yaml")


@pytest.fixture
def spec_dir() -> Path:
    return SPEC_DIR
