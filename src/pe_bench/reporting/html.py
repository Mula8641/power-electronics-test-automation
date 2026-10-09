import base64
from html import escape
from pathlib import Path

import pandas as pd

from pe_bench.core.runner import TestResult
from pe_bench.core.verdict import CheckResult, Status

STATUS_COLOR = {Status.PASS: "#0a7a0a", Status.FAIL: "#c03030", Status.ABORTED: "#8a5a00"}

STYLE = """
body{font:15px/1.5 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#0b0b0b;background:#f9f9f7}
h1{margin:0 0 .25rem} h2{margin-top:2rem}
.banner{display:inline-block;color:#fff;font-weight:700;padding:.35rem 1rem;border-radius:6px;letter-spacing:.05em}
table{border-collapse:collapse;width:100%;font-size:13px;background:#fcfcfb}
th,td{border-bottom:1px solid #e4e3df;padding:.35rem .6rem;text-align:right}
th:first-child,td:first-child{text-align:left}
img{max-width:100%;border:1px solid #e4e3df;border-radius:6px;margin:.5rem 0}
.meta{color:#52514e} .bad{color:#c03030;font-weight:600}
"""


def embed_png(path: Path) -> str:
    return f'<img alt="{escape(path.stem)}" src="data:image/png;base64,{base64.b64encode(path.read_bytes()).decode()}">'


def checks_table(checks: list[CheckResult]) -> str:
    rows = "".join(
        f"<tr><td>{escape(check.name)}</td><td>{check.measured:.3f} {check.unit}</td>"
        f"<td>{check.relation} {check.limit:g} {check.unit}</td>"
        f"<td class='{'' if check.passed else 'bad'}'>{'PASS' if check.passed else 'FAIL'}</td></tr>"
        for check in checks
    )
    return f"<table><tr><th>Check</th><th>Measured</th><th>Limit</th><th>Result</th></tr>{rows}</table>"


def data_table(derived: pd.DataFrame) -> str:
    columns = [
        "load_set_a",
        "vin_v",
        "iin_a",
        "vout_v",
        "iout_a",
        "pin_w",
        "pout_w",
        "loss_w",
        "efficiency_pct",
    ]
    return derived[columns].to_html(
        index=False, float_format=lambda value: f"{value:.4f}", border=0
    )


def render_report(result: TestResult, plot_paths: list[Path]) -> str:
    spec = result.spec
    abort_note = (
        f"<p class='bad'>Sweep aborted: {escape(result.abort_reason)}</p>"
        if result.abort_reason
        else ""
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{escape(spec.name)} - {result.status}</title><style>{STYLE}</style></head><body>
<h1>{escape(spec.name)}</h1>
<span class="banner" style="background:{STATUS_COLOR[result.status]}">{result.status}</span>
<p class="meta">Vin {spec.input_voltage_v:g} V, input limit {spec.input_current_limit_a:g} A,
sweep {spec.sweep.start_a:g}-{spec.sweep.stop_a:g} A in {spec.sweep.points} steps, {spec.sweep.samples} samples/point.
{len(result.data)} of {spec.sweep.points} points captured.</p>{abort_note}
<h2>Checks</h2>{checks_table(result.checks) if result.checks else "<p class='meta'>Not evaluated.</p>"}
<h2>Plots</h2>{"".join(embed_png(path) for path in plot_paths)}
<h2>Measurements</h2>{data_table(result.data)}
</body></html>"""
