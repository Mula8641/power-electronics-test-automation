import logging

logger = logging.getLogger(__name__)

NO_ERROR_CODE = 0


class InstrumentError(RuntimeError):
    pass


class ScpiInstrument:
    """Wraps any object with pyvisa's write/query interface (real or simulated)."""

    def __init__(self, resource, name: str):
        self.resource = resource
        self.name = name

    def send(self, command: str) -> None:
        self.resource.write(command)
        self._raise_if_queued_error(command)

    def ask(self, command: str) -> str:
        reply = self.resource.query(command).strip()
        self._raise_if_queued_error(command)
        return reply

    def ask_float(self, command: str) -> float:
        return float(self.ask(command))

    def identity(self) -> str:
        return self.ask("*IDN?")

    def _raise_if_queued_error(self, command: str) -> None:
        code, _, message = self.resource.query("SYST:ERR?").partition(",")
        if int(code) != NO_ERROR_CODE:
            reason = message.strip().strip('"')
            logger.error("%s rejected %r: %s %s", self.name, command, code, reason)
            raise InstrumentError(f"{self.name}: {reason} (code {code}) after {command!r}")
