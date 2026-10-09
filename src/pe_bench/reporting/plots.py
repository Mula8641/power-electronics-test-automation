from pathlib import Path

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from pe_bench.config.spec import Limits

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#f0efec"
SERIES = "#2a78d6"


def styled_axes(title: str, ylabel: str) -> tuple[Figure, Axes]:
    figure = Figure(figsize=(6.4, 3.6), dpi=150, facecolor=SURFACE)
    axes = figure.subplots()
    axes.set_facecolor(SURFACE)
    axes.set_title(title, loc="left", color=INK, fontsize=11, fontweight="semibold")
    axes.set_xlabel("Load current (A)", color=INK_SECONDARY, fontsize=9)
    axes.set_ylabel(ylabel, color=INK_SECONDARY, fontsize=9)
    axes.grid(axis="y", color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    axes.tick_params(colors=INK_MUTED, labelsize=8, length=0)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color(INK_MUTED)
    return figure, axes


def plot_efficiency(derived: pd.DataFrame, limits: Limits, path: Path) -> Path:
    figure, axes = styled_axes("Efficiency vs load", "Efficiency (%)")
    axes.plot(
        derived.load_set_a,
        derived.efficiency_pct,
        color=SERIES,
        linewidth=2,
        marker="o",
        markersize=4,
        markeredgecolor=SURFACE,
        markeredgewidth=1.5,
    )
    axes.hlines(
        limits.min_efficiency_pct,
        limits.efficiency_from_load_a,
        axes.get_xlim()[1],
        color=INK_SECONDARY,
        linestyle="--",
        linewidth=1,
    )
    axes.annotate(
        f"min {limits.min_efficiency_pct:g} % from {limits.efficiency_from_load_a:g} A",
        (limits.efficiency_from_load_a, limits.min_efficiency_pct),
        textcoords="offset points",
        xytext=(4, -12),
        color=INK_SECONDARY,
        fontsize=8,
    )
    figure.tight_layout()
    figure.savefig(path, facecolor=SURFACE)
    return path


def plot_regulation(derived: pd.DataFrame, limits: Limits, path: Path) -> Path:
    figure, axes = styled_axes("Output voltage vs load", "Vout (V)")
    tolerance_v = limits.vout_nominal_v * limits.vout_tolerance_pct / 100
    axes.axhspan(
        limits.vout_nominal_v - tolerance_v,
        limits.vout_nominal_v + tolerance_v,
        color=GRID,
        zorder=0,
    )
    axes.annotate(
        f"±{limits.vout_tolerance_pct:g} % band",
        (0, limits.vout_nominal_v + tolerance_v),
        xycoords=("axes fraction", "data"),
        textcoords="offset points",
        xytext=(4, -11),
        color=INK_SECONDARY,
        fontsize=8,
    )
    axes.plot(
        derived.load_set_a,
        derived.vout_v,
        color=SERIES,
        linewidth=2,
        marker="o",
        markersize=4,
        markeredgecolor=SURFACE,
        markeredgewidth=1.5,
    )
    figure.tight_layout()
    figure.savefig(path, facecolor=SURFACE)
    return path
