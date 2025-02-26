"""
Part of pybrlapi.
Contains all exceptions raised by the library.
"""

class BrlAPIError(Exception):
    """
    Custom exception for BrlAPI errors.
    Needs refinement to report error origins better.
    """

    @classmethod
    def from_packet (cls, packet):
        msg = "Received: "+repr(packet)
        return cls(msg)


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

