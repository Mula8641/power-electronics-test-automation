from pe_bench.instruments.scpi import ScpiInstrument


class PowerSupply(ScpiInstrument):
    def configure(self, volts: float, current_limit_a: float) -> None:
        self.send(f"VOLT {volts}")
        self.send(f"CURR {current_limit_a}")

    def output(self, on: bool) -> None:
        self.send(f"OUTP {'ON' if on else 'OFF'}")

    def voltage(self) -> float:
        return self.ask_float("MEAS:VOLT?")

    def current(self) -> float:
        return self.ask_float("MEAS:CURR?")
