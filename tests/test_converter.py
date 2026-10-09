import pytest

from pe_bench.sim.converter import BuckConverter

converter = BuckConverter()


def efficiency_pct(vin_v: float, iout_a: float) -> float:
    point = converter.operating_point(vin_v, iout_a)
    return 100 * point.vout_v * iout_a / (vin_v * point.iin_a)


def test_efficiency_peaks_mid_load():
    light, mid, heavy = efficiency_pct(12, 0.1), efficiency_pct(12, 2.0), efficiency_pct(12, 5.0)
    assert light < heavy < mid


def test_output_droops_linearly_with_load():
    droop_v = converter.vout_nominal_v - converter.operating_point(12, 5.0).vout_v
    assert droop_v == pytest.approx(5.0 * converter.output_resistance_ohm)


def test_no_input_voltage_means_no_output():
    assert converter.operating_point(0.0, 3.0).vout_v == 0.0
