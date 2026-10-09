from pe_bench.instruments.scpi import ScpiInstrument


class ElectronicLoad(ScpiInstrument):
    def use_constant_current(self) -> None:
        self.send("FUNC CURR")

    def set_current(self, amps: float) -> None:
        self.send(f"CURR {amps}")

    def output(self, on: bool) -> None:
        self.send(f"INP {'ON' if on else 'OFF'}")

    def current(self) -> float:
        return self.ask_float("MEAS:CURR?")
