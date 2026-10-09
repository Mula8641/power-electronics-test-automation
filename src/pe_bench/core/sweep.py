import logging
import time
from collections.abc import Callable, Iterator
from datetime import datetime
from statistics import fmean

from pe_bench.config.spec import SweepSpec
from pe_bench.core.bench import Bench

logger = logging.getLogger(__name__)

COLUMNS = ["timestamp", "load_set_a", "vin_v", "iin_a", "vout_v", "iout_a"]


def averaged(read: Callable[[], float], samples: int) -> float:
    return fmean(read() for _ in range(samples))


def measure_point(bench: Bench, load_a: float, sweep: SweepSpec) -> dict:
    bench.eload.set_current(load_a)
    time.sleep(sweep.settle_s)
    return {
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "load_set_a": load_a,
        "vin_v": averaged(bench.psu.voltage, sweep.samples),
        "iin_a": averaged(bench.psu.current, sweep.samples),
        "vout_v": averaged(bench.dmm.dc_voltage, sweep.samples),
        "iout_a": averaged(bench.eload.current, sweep.samples),
    }


def iter_sweep(bench: Bench, sweep: SweepSpec) -> Iterator[dict]:
    for load_a in sweep.load_steps():
        row = measure_point(bench, load_a, sweep)
        logger.info("load %.3f A -> Vout %.4f V, Iin %.4f A", load_a, row["vout_v"], row["iin_a"])
        yield row
