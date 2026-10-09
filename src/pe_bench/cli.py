import argparse
import logging
import sys
from pathlib import Path

from pe_bench.config.spec import load_spec
from pe_bench.core.runner import run_test
from pe_bench.core.verdict import Status
from pe_bench.reporting.artifacts import save_outputs
from pe_bench.sim.bench import SimulatedBench

EXIT_CODES = {Status.PASS: 0, Status.FAIL: 1, Status.ABORTED: 2}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pe-bench", description="Run a converter bench test and write a report."
    )
    parser.add_argument("spec", type=Path, help="YAML test spec")
    parser.add_argument(
        "--sim",
        action="store_true",
        help="use the built-in simulated bench instead of VISA hardware",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("results"), help="output directory (default: results)"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    if args.sim:
        resource_manager = SimulatedBench()
    else:
        import pyvisa

        resource_manager = pyvisa.ResourceManager()
    result = run_test(load_spec(args.spec), resource_manager)
    paths = save_outputs(result, args.out)
    print(f"{result.status}  report: {paths['report']}")
    return EXIT_CODES[result.status]


if __name__ == "__main__":
    sys.exit(main())
