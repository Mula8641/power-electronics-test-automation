import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from pe_bench.config.spec import Resources, TestSpec
from pe_bench.instruments.dmm import Multimeter
from pe_bench.instruments.eload import ElectronicLoad
from pe_bench.instruments.psu import PowerSupply

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Bench:
    psu: PowerSupply
    eload: ElectronicLoad
    dmm: Multimeter


def open_bench(resource_manager, resources: Resources) -> Bench:
    bench = Bench(
        psu=PowerSupply(resource_manager.open_resource(resources.psu), "PSU"),
        eload=ElectronicLoad(resource_manager.open_resource(resources.eload), "ELOAD"),
        dmm=Multimeter(resource_manager.open_resource(resources.dmm), "DMM"),
    )
    logger.info(
        "Bench open: %s | %s | %s",
        bench.psu.identity(),
        bench.eload.identity(),
        bench.dmm.identity(),
    )
    return bench


@contextmanager
def energized(bench: Bench, spec: TestSpec) -> Iterator[Bench]:
    bench.psu.configure(spec.input_voltage_v, spec.input_current_limit_a)
    bench.eload.use_constant_current()
    bench.eload.set_current(0.0)
    bench.psu.output(True)
    bench.eload.output(True)
    try:
        yield bench
    finally:
        try:
            bench.eload.output(False)
        finally:
            bench.psu.output(False)
            logger.info("Bench de-energized")
