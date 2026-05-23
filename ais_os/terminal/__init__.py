__all__ = ["TerminalREPL"]


def __getattr__(name: str):
    if name == "TerminalREPL":
        from ais_os.terminal.repl import TerminalREPL

        return TerminalREPL
    raise AttributeError(name)
