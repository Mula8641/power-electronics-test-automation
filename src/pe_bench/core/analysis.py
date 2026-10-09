import pandas as pd


def add_derived(measurements: pd.DataFrame) -> pd.DataFrame:
    return measurements.assign(
        pin_w=lambda df: df.vin_v * df.iin_a,
        pout_w=lambda df: df.vout_v * df.iout_a,
    ).assign(
        loss_w=lambda df: df.pin_w - df.pout_w,
        efficiency_pct=lambda df: 100 * df.pout_w / df.pin_w,
    )


def load_regulation_pct(derived: pd.DataFrame) -> float:
    light, heavy = derived.vout_v.iloc[0], derived.vout_v.iloc[-1]
    return float(100 * (light - heavy) / light)
