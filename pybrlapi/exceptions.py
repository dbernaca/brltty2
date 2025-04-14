"""
Part of pybrlapi.
Contains all exceptions raised by the library.
"""
from .constants import ERROR_DESCRIPTIONS

class BrlAPIError(Exception):
    """
    Custom exception for BrlAPI errors.
    Needs refinement to report error origins better.
    """
    def __init__ (self, *args):
        if len(args)>1:
            self.errno = args[0]
            self.msg = " ".join(str(x) for x in args[1:])
        elif args and isinstance(args[0], int):
            self.errno = args[0]
            self.msg = ERROR_DESCRIPTIONS.get(args[0], "Unidentified BrlAPI error")
        else:
            self.errno = -1
            if args:
                self.msg = args[0]
            else:
                self.msg = ""
                Exception.__init__(self)
                return
        Exception.__init__(self, self.msg)

    @classmethod
    def from_packet (cls, packet):
        try:
            return cls(packet.code, packet.message)
        except AttributeError:
            return cls("Reported by "+repr(packet))

class TimedOut (Exception):
    """
    Raised when a Blocker() stops blocking because of a timeout.
    """
    def __init__ (self, source, timeout):
        self.timeout = timeout
        self.source  = source

    def __repr__ (self):
        return f"{self.source} timed out after {self.timeout} seconds"

class MultipleExceptions (Exception):
    """
    Used to report more than one exception that occurred.
    Shouldn't ever be needed, but if protocol gets somehow out of sync...
    Just know, if you ever see this raised, you are in deep trouble.
    This is somewhat similar to ExceptionGroup() from builtins.
    """
    def __init__ (self, *args):
        self.exceptions = e = []
        for x in args:
            if isinstance(x, MultipleExceptions):
                e += x.exceptions
            else:
                e.append(x)

    def __repr__ (self):
        excs = ',\n'.join(repr(x) for x in self.exceptions)
        return f"MultipleExceptions([{excs}])"

class Interrupted (Exception):
    """
    This is raised in *do* module within a system interrupted Task().
    Common cause: KeyboardInterrupt()
    """