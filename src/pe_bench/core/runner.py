import logging
from dataclasses import dataclass

import pandas as pd

from pe_bench.config.spec import TestSpec
from pe_bench.core.analysis import add_derived
from pe_bench.core.bench import energized, open_bench
from pe_bench.core.sweep import COLUMNS, iter_sweep
from pe_bench.core.verdict import CheckResult, Status, evaluate, status_of
from pe_bench.instruments.scpi import InstrumentError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TestResult:
    __test__ = False

    spec: TestSpec
    data: pd.DataFrame
    checks: list[CheckResult]
    status: Status
    abort_reason: str | None


def run_test(spec: TestSpec, resource_manager) -> TestResult:
    logger.info("Starting %s", spec.name)
    rows: list[dict] = []
    abort_reason = None
    bench = open_bench(resource_manager, spec.resources)
    try:
        with energized(bench, spec):
            rows.extend(iter_sweep(bench, spec.sweep))
    except InstrumentError as error:
        abort_reason = str(error)
        logger.error("Sweep aborted after %d points: %s", len(rows), abort_reason)
    data = add_derived(pd.DataFrame(rows, columns=COLUMNS))
    checks = [] if abort_reason else evaluate(data, spec.limits)
    status = status_of(checks, abort_reason)
    logger.info("Finished %s: %s", spec.name, status)
    return TestResult(spec, data, checks, status, abort_reason)
