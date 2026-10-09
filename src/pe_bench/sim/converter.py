from dataclasses import dataclass


@dataclass(frozen=True)
class OperatingPoint:
    vout_v: float
    iin_a: float


@dataclass(frozen=True)
class BuckConverter:
    """Losses: conduction (I^2R), switching (~Vin*Iout), fixed gate-drive/quiescent."""

    vout_nominal_v: float = 5.0
    output_resistance_ohm: float = 0.015
    conduction_resistance_ohm: float = 0.04
    switching_loss_per_vin_iout: float = 0.008
    fixed_loss_w: float = 0.15

    def operating_point(self, vin_v: float, iout_a: float) -> OperatingPoint:
        if vin_v <= 0:
            return OperatingPoint(vout_v=0.0, iin_a=0.0)
        vout_v = self.vout_nominal_v - iout_a * self.output_resistance_ohm
        loss_w = (
            iout_a**2 * self.conduction_resistance_ohm
            + self.switching_loss_per_vin_iout * vin_v * iout_a
            + self.fixed_loss_w
        )
        return OperatingPoint(vout_v=vout_v, iin_a=(vout_v * iout_a + loss_w) / vin_v)
