import logging
from pathlib import Path

from pe_bench.core.runner import TestResult
from pe_bench.reporting.html import render_report
from pe_bench.reporting.plots import plot_efficiency, plot_regulation

logger = logging.getLogger(__name__)


def save_outputs(result: TestResult, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = result.spec.name
    csv_path = out_dir / f"{stem}.csv"
    result.data.to_csv(csv_path, index=False)
    plot_paths = [
        plot_efficiency(result.data, result.spec.limits, out_dir / f"{stem}_efficiency.png"),
        plot_regulation(result.data, result.spec.limits, out_dir / f"{stem}_vout.png"),
    ]
    report_path = out_dir / f"{stem}.html"
    report_path.write_text(render_report(result, plot_paths), encoding="utf-8")
    logger.info("Wrote %s, %s", csv_path, report_path)
    return {"csv": csv_path, "report": report_path}
