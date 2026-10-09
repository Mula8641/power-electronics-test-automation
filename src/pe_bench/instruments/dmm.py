from pe_bench.instruments.scpi import ScpiInstrument


class Multimeter(ScpiInstrument):
    def dc_voltage(self) -> float:
        return self.ask_float("MEAS:VOLT:DC?")
