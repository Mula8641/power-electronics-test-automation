import logging
import random

from pe_bench.sim.converter import BuckConverter, OperatingPoint

logger = logging.getLogger(__name__)

OVERCURRENT = (301, '"Input current limit exceeded, output tripped"')
UNDEFINED_HEADER = (-113, '"Undefined header"')


class SimulatedBench:
    """Stands in for pyvisa.ResourceManager; one shared converter couples PSU, load and DMM."""

    def __init__(
        self, converter: BuckConverter | None = None, noise_fraction: float = 0.0005, seed: int = 0
    ):
        self.converter = converter or BuckConverter()
        self.noise_fraction = noise_fraction
        self.rng = random.Random(seed)
        self.vin_set_v = 0.0
        self.input_current_limit_a = 0.0
        self.psu_on = False
        self.load_set_a = 0.0
        self.load_on = False
        self.errors: dict[str, list[tuple[int, str]]] = {"PSU": [], "ELOAD": [], "DMM": []}
        self.commands = {
            ("PSU", "VOLT"): lambda arg: self._set("vin_set_v", float(arg)),
            ("PSU", "CURR"): lambda arg: self._set("input_current_limit_a", float(arg)),
            ("PSU", "OUTP"): lambda arg: self._set("psu_on", arg == "ON"),
            ("PSU", "MEAS:VOLT?"): lambda _: self._measure(self._vin()),
            ("PSU", "MEAS:CURR?"): lambda _: self._measure(self._operating_point().iin_a),
            ("ELOAD", "FUNC"): lambda _: "",
            ("ELOAD", "CURR"): lambda arg: self._set("load_set_a", float(arg)),
            ("ELOAD", "INP"): lambda arg: self._set("load_on", arg == "ON"),
            ("ELOAD", "MEAS:CURR?"): lambda _: self._measure(self._load_a()),
            ("DMM", "MEAS:VOLT:DC?"): lambda _: self._measure(self._operating_point().vout_v),
        }

    def open_resource(self, address: str) -> "SimResource":
        role = address.removeprefix("SIM::")
        if role not in self.errors:
            raise ValueError(f"Unknown simulated instrument {address!r}")
        return SimResource(self, role)

    def handle(self, role: str, command: str) -> str:
        header, _, argument = command.partition(" ")
        header = header.upper()
        if header == "*IDN?":
            return f"PE-BENCH,SIM-{role},0,1.0"
        if header == "SYST:ERR?":
            code, message = self.errors[role].pop(0) if self.errors[role] else (0, '"No error"')
            return f"{code},{message}"
        action = self.commands.get((role, header))
        if action is None:
            self.errors[role].append(UNDEFINED_HEADER)
            return ""
        return action(argument.strip().upper())

    def _set(self, attribute: str, value) -> str:
        setattr(self, attribute, value)
        self._trip_on_overcurrent()
        return ""

    def _trip_on_overcurrent(self) -> None:
        if self.psu_on and self._operating_point().iin_a > self.input_current_limit_a:
            self.psu_on = False
            self.errors["PSU"].append(OVERCURRENT)
            logger.warning("Simulated PSU tripped at load %.3f A", self.load_set_a)

    def _vin(self) -> float:
        return self.vin_set_v if self.psu_on else 0.0

    def _load_a(self) -> float:
        return self.load_set_a if self.load_on and self.psu_on else 0.0

    def _operating_point(self) -> OperatingPoint:
        return self.converter.operating_point(self._vin(), self._load_a())

    def _measure(self, true_value: float) -> str:
        return f"{true_value * (1 + self.rng.gauss(0, self.noise_fraction)):.6f}"


class SimResource:
    def __init__(self, bench: SimulatedBench, role: str):
        self.bench = bench
        self.role = role

    def write(self, command: str) -> None:
        self.bench.handle(self.role, command)

    def query(self, command: str) -> str:
        return self.bench.handle(self.role, command)
