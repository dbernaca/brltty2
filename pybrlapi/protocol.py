"""
Part of pybrlapi library.
This module implements helper classes that describe needed packets
to realize the BrlAPI protocol (for now only version 8).
Based on libbrlapi and brltty source code and documentation from https://github.com/brltty/brltty
and also on many trials and errors.
"""

from .constants import *
const_lookup = dict((value, key) for key, value in vars().items() if key.isupper() and key.startswith("PACKET_"))
error_lookup = dict((code, key) for key, code in vars().items() if key.startswith("ERROR_") and isinstance(code, int))
from .keycodes import describeKeyCode
from struct import pack, unpack

class Packet:
    """
    Represents a single BRLAPI packet, supporting parsing and encoding.
    """
    def __init__ (self, type, payload=b""):
        self.type    = type    # Message type (version, auth, write, etc.)
        self.payload = payload # The actual data
    
    def __repr__ (self):
        return (f"{self.__class__.__name__}("
                f"{const_lookup[self.type]}, payload={repr(self.payload)})")

    @classmethod
    def from_bytes (cls, data):
        """
        Parses a received packet and returns an instance of Packet().
        The returned instance may be a subclass of Packet() if a suitable one is found for the packet type.
        """
        if len(data) < 8:
            raise ValueError("Packet too short (No header)")
        size, type = unpack("!II", data[:8])
        # Extract payload
        if len(data)-8!=size:
            print("Warning: Packet overflow!")
        payload = data[8:size+8]
        return packet_classes.get(type, cls)(type, payload)

    def to_bytes (self):
        """
        Encodes the Packet() into binary format for sending.
        """
        return pack("!II", len(self.payload), self.type) + self.payload

    # Helper methods do easily determine the type of packet
    # The type recognition depends on subclasses
    _negative   = lambda self: False
    _positive   = lambda self: True
    isError     = _negative
    isException = _negative
    isVersion   = _negative
    isAuth      = _negative
    isACK       = _negative
    isInfo      = _negative
    isKey       = _negative

class VersionPacket(Packet):
    """
    The PACKET_VERSION packets are exchanged at the beginning of the communication with brltty.
    This is the first packet ever that will be received from brltty.
    A response needs to be the same packet.
    Of course, the value may be different.
    With this packet brltty confirms its identity and tell us which protocol it wants to use.
    We respond thus letting it know that we talk BrlAPI and that we wish to use protocol we know.
    For now this is only version 8.
    """
    def __init__ (self, type=PACKET_VERSION, protocol=PROTOCOL_VERSION):
        protocol = protocol if isinstance(protocol, int) else unpack("!I", protocol)[0]
        payload = pack("!I", protocol)
        Packet.__init__(self, type, payload)
        self.protocol = protocol

    isVersion = Packet._positive

class AckPacket(Packet):
    """
    The PACKET_ACK is sent by brltty when it wishes us to know that something is OK.
    Usually authentication and entering and leaving working modes.
    """
    def __init__ (self, type=PACKET_ACK, payload=None):
        Packet.__init__(self, type, b"")

    isACK = Packet._positive

class ServerAuthPacket(Packet):
    """
    This packet is sent by brltty to request authentication right after we reply to PACKET_VERSION.
    The client replies with same type, but it may contain additional data like a key or credentials.
    So for practical reasons a class for the brltty's PACKET_AUTH
    and a clas for one pybrlapi needs to send back are separated.
    """
    def __init__ (self, type=PACKET_AUTH, method=pack("!I", AUTH_NONE)):
        method = unpack("!I", method)[0]
        payload = pack("!I", method)
        Packet.__init__(self, type, payload)
        self.method = method

    isAuth = Packet._positive

class ClientAuthPacket(Packet):
    """
    This packet is sent by pybrlapi to respond to brltty's request for authentication.
    Bot server and client send PACKET_AUTH, but client's may contain additional data like a key or credentials.
    So for practical reasons a class for the brltty's PACKET_AUTH
    and a clas for one pybrlapi needs to send back are separated.
    """
    def __init__ (self, type=PACKET_AUTH, method=AUTH_NONE, payload=None):
        method = method if isinstance(method, int) else unpack("!I", method)[0]
        payload = pack("!I", method)+payload if payload else pack("!I", method)
        Packet.__init__(self, type, payload)
        self.method = method

    isAuth = Packet._positive

class ErrorPacket(Packet):
    """
    The PACKET_ERROR is sent by brltty usually to complain about us sending garbage.
    Our protocol is now stabilized, so PACKET_ERROR will arrive
    usually if authentication failed for any reason.
    Also, if happens that brltty does not speak our protocol version.
    Lets hope this never happens though.
    """
    def __init__ (self, type=PACKET_ERROR, payload=b""):
        Packet.__init__(self, type, payload)
        self.code = unpack("!I", payload[:4])[0]
        # Warning: This may be wrong. The protocol documentation hints that content of PACKET_ERROR
        # may contain an error message, but I never saw it happen.
        self.message = payload[4:].decode() if payload[4:] else ERROR_DESCRIPTIONS.get(self.code, "Unknown")

    def __repr__ (self):
        return f"ErrorPacket({error_lookup.get(self.code, str(self.code))}, {repr(self.message)})"

    isError = Packet._positive

class ExceptionPacket(Packet):
    """
    Essentially same as PACKET_ERROR but it returns the offending packet back.
    I.e. if sent PACKET_WRITE is malformed the PACKET_EXCEPTION is returned and it contains the malformed PACKET_WRITE that caused it.
    PACKET_EXCEPTION is more serious in a sense that it is strictly caused by programming errors.
    Although it is serious, brltty does not terminate the connection and we may continue the communication.
    However we need to treat it more seriously on our side.
    """
    def __init__ (self, type=PACKET_ERROR, payload=b""):
        Packet.__init__(self, type, payload)
        self.code, self.cause = unpack("!II", payload[:8])
        self.message = ERROR_DESCRIPTIONS.get(self.code, "Unknown")
        self.content = payload[8:]

    def __repr__ (self):
        return f"ExceptionPacket({error_lookup.get(self.code, str(self.code))}, {const_lookup[self.cause]}, {repr(self.message)})"

    isError     = Packet._positive
    isException = Packet._positive

class InfoPacket (Packet):
    """
    This encapsulate three packets:
    PACKET_GETDRIVERNAME, PACKET_GETMODELID, PACKET_GETDISPLAYSIZE.
    They cary info about the connected braille display.
    After we send one of those, brltty replies with the same type of packet that caries the requested data.
    """
    def __init__ (self, type, payload=b""):
        Packet.__init__(self, type, payload)
        if payload and (type==PACKET_GETDRIVERNAME or type==PACKET_GETMODELID):
            self.info = payload.rstrip(b"\x00").decode()
        elif payload and type==PACKET_GETDISPLAYSIZE:
            self.info = unpack("!II", payload)
        else:
            self.info = None

    isInfo = Packet._positive

class KeyPacket (Packet):
    """
    The PACKET_KEY is sent asynchronously by brltty when user presses a key on a braille display.
    This class also offers an extra method and attribute to parse the received code into human readable components that later can easily be used
    to control e.g. a screen reader or keyboard input.
    """
    def __init__ (self, type=PACKET_KEY, keycode=b"\x00\x00\x00\x00\x00\x00\x00\x00"):
        Packet.__init__(self, type, keycode)
        self.command = unpack("!Q", keycode)[0]

    def __getattr__ (self, a):
        if a!="description":
            raise AttributeError("KeyPacket() instance has no attribute '%s'" % a) 
        self.description = d = describeKeyCode(self.command)
        return d

    expandKeyCode = lambda self: self.description

    def __repr__ (self):
        try:
            d = self.description
            return f"KeyPacket(KEY_{d['type']}_{d['command']}, {d['argument']}, {repr(d['flags'])})"
        except:
            return Packet.__repr__(self)

    isKey = Packet._positive

class WritePacket(Packet):
    """
    A PACKET_WRITE is sent to brltty to write text to braille display.
    """
    def __init__ (self, type=PACKET_WRITE, payload=b""):
        Packet.__init__(self, type, payload)

    @classmethod
    def from_params (cls, displayNumber=DEFAULT_DISPLAY, regionBegin=1, regionSize=None, text="", andMask=None, orMask=None, cursor=CURSOR_OFF, charset="UTF-8"):
        """
        This does not work yet. Needs to be adjusted some more.
        But it will be mighty helpful in the future.
        """
        fmt = "!IiIi"
        flags = WF_DISPLAYNUMBER|WF_TEXT|WF_CURSOR|WF_CHARSET|WF_REGION
        if regionSize is None:
            regionSize = len(text)
        args = [displayNumber, regionBegin, regionSize, len(text), text.encode("UTF-8")+b"\x00"]
        fmt += "I%is" % len(text)
        if andMask is not None:
            flags |= WF_ATTR_AND
            fmt += "%is" % regionSize
            args.append(andMask)
        if orMask is not None:
            flags |= WF_ATTR_OR
            fmt += "%is" % regionSize
            args.append(orMask)
        fmt += "i%is" % len(charset)
        args = [fmt, flags]+args
        args.append(cursor)
        args.append(charset.encode("ASCII"))
        return cls(PACKET_WRITE, pack(*args))

packet_classes = {
    PACKET_VERSION: VersionPacket,
    PACKET_ACK: AckPacket,
    PACKET_AUTH: ServerAuthPacket,
    PACKET_ERROR: ErrorPacket,
    PACKET_EXCEPTION: ExceptionPacket,
    PACKET_GETDRIVERNAME: InfoPacket,
    PACKET_GETMODELID: InfoPacket,
    PACKET_GETDISPLAYSIZE: InfoPacket,
    PACKET_KEY: KeyPacket
    }


