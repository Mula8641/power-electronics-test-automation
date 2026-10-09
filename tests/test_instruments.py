import pytest

from pe_bench.core.bench import energized, open_bench
from pe_bench.instruments.psu import PowerSupply
from pe_bench.instruments.scpi import InstrumentError, ScpiInstrument


def test_identity_comes_from_the_instrument(sim):
    assert (
        PowerSupply(sim.open_resource("SIM::PSU"), "PSU").identity().startswith("PE-BENCH,SIM-PSU")
    )


def test_unknown_command_surfaces_the_error_queue(sim):
    instrument = ScpiInstrument(sim.open_resource("SIM::DMM"), "DMM")
    with pytest.raises(InstrumentError, match="Undefined header"):
        instrument.send("BOGUS:CMD 1")


def test_error_is_consumed_once_read(sim):
    instrument = ScpiInstrument(sim.open_resource("SIM::DMM"), "DMM")
    with pytest.raises(InstrumentError):
        instrument.send("BOGUS")
    instrument.send("*IDN?")


def test_unknown_address_is_rejected(sim):
    with pytest.raises(ValueError, match="SIM::SCOPE"):
        sim.open_resource("SIM::SCOPE")


def test_psu_trips_when_input_current_limit_is_exceeded(sim, spec):
    bench = open_bench(sim, spec.resources)
    bench.psu.configure(12.0, 0.2)
    bench.psu.output(True)
    bench.eload.output(True)
    bench.eload.set_current(3.0)
    with pytest.raises(InstrumentError, match="limit exceeded"):
        bench.psu.voltage()
    assert not sim.psu_on


def test_outputs_are_off_after_a_failure_inside_the_context(sim, spec):
    bench = open_bench(sim, spec.resources)
    with pytest.raises(RuntimeError, match="boom"), energized(bench, spec):
        assert sim.psu_on and sim.load_on
        raise RuntimeError("boom")
    assert not sim.psu_on and not sim.load_on
