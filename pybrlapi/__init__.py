"""
This is a pure Python implementation of BrlAPI.
Copyright (C) 2025 by Dalen Bernaca, GPL license applies

This is still in proof of concept phase, nothing is guaranteed!
Although, tests, even with this low error handling, are very promising.
In fact, while I am writing this, I am using NVDA screen reader with this library behind the braille display driver
and the braille display device itself is connected to a different OS, where brltty is happily running, so the communication goes over LAN.
Works like a charm. I know there are bugs just waiting to emerge though.

This library works by talking directly to brltty daemon/service over TCP
instead of loading provided libbrlapi by loading brlapi.dll via ctypes or importing the cython compiled *.pyd that comes with it and brltty.
This gives us a few advantages.
Mainly, using the provided Python bindings limits us to the Python version they were built on,
or forces us to build whole BrlAPI ourselves which require substantial preparations of a specific dev environment.
Why not ctypes and the DLL then at least? Well, a 64 bit and 32 bit compatibility is one possible reason.
Second one is that you do not need to worry about including it separately when packaging your app.
Third one is, that this implementation is fully asynchronous, meaning that a Python function is called as soon as user presses the key on a braille display.
No waiting for a keypress or consuming an event queue, although this is supported as well.
Python is so much flexible on its own and this can be easily extended by anyone, no compiling and stuff necessary.
And so on.

Note: This API is not completely compatible with original BrlAPI and needs some minor adjustments if replacing it with this implementation.

Big thanks to geniuses who created an maintain brltty:
 *   Dave Mielke
 *   Samuel Thibault
 *   Sébastien Hinderer
please continue your excellent work and don't be angry at me because of this little library.

TODO:
 * Ensure no freezes are possible because of any reason (introduce timeouts and so on)
 * Implement a special lock for waiting and managing exceptions (all in one)
 * Implement autodetection of every brltty serving BrlAPI in a local network
 * See how to detect braille display disconnect or change (poll using PACKET_GETDRIVERNAME or something)
 * Improve BrlAPIError() exception class
 * Search for a key file in more than one place (cross-platform compatible)
"""

from collections import deque
from struct import pack, unpack
from .constants import *
from .keycodes import *
from .protocol import *
import threading
import os

# asyncore is on its way of being deprecated in favour of asyncio which is a complete nonsense
# the module does need refreshing, but it is extra useful and writing asynchronous clients and servers
# with it is extra fast, efficient, readable, connectable to other event loops etc.
# For deprecation reasons and because NVDA does not pack asyncore a local copy of it is provided
try:
    import asyncore
except:
    from . import asyncore

class BrlAPIError(Exception):
    """
    Custom exception for BrlAPI errors.
    """

    @classmethod
    def from_packet (cls, packet):
        msg = "Received: "+repr(packet)
        return cls(msg)

class Client(asyncore.dispatcher_with_send):
    """
    A BrlAPI client that talks to brltty.
    Implements most of original BrlAPI's functionalities.
    """
    def __init__ (self, host=DEFAULT_HOST, port=DEFAULT_PORT, auth_callback=None, key_callback=None, error_callback=None):
        asyncore.dispatcher_with_send.__init__(self)
        self.host = host
        self.port = port
        self.create_socket()
        self.key_callback = key_callback
        if error_callback:
            self.error_callback = error_callback
        if auth_callback:
            self.auth_callback = auth_callback

    error_callback = lambda self, error: None

    def auth_callback (self, method):
        if method==AUTH_NONE:
            return True
        elif method!=AUTH_KEY:
            return False
        try:
            k = open("/etc/brlapi.key", "rb").read()
        except Exception as e:
            self.close()
            self.exception = e
            self.error_callback(e)
            self.process_lock.release()

    def connect (self, runloop=True):
        try:
            asyncore.dispatcher_with_send.connect(self, (self.host, self.port))
        except Exception as e:
            self.exception = e
            self.error_callback(e)
            raise
        self.in_buffer    = b""
        self.mode         = "authorization"
        self.step         = 0
        self.exception    = None
        self.driver       = "NoBraille"
        self.model        = ""
        self.displaySize  = (0, 0)
        self.packetqueue  = deque()
        self.process_func = self.process_handshake
        self.process_lock = threading.Lock()
        self.receive_lock = threading.Lock()
        self.send_lock    = threading.Lock()
        self.keywait_lock = threading.Lock()
        self.process_lock.acquire()
        if runloop:
            def loopy ():
                try:
                    asyncore.loop()
                except OSError:
                    pass
                print("asyncore.loop() ended")
            self.looper = t = threading.Thread(target=loopy)
            t.daemon = True
            t.start()
        self.process_lock.acquire()
        self.process_lock.release()
        self._excheck()

    def _excheck (self):
        if self.exception:
            e = self.exception
            self.exception = None
            raise e

    def handle_connect (self):
        """Called when the connection is established."""
        print("[BrlAPI] Connected to BRLTTY.")

    def handle_close (self):
        """Handle socket closure."""
        print("[BrlAPI] Connection closing.")
        self.close()
        try:
            self.process_lock.release()
        except:
            pass

    def handle_read (self):
        """
        Read incoming data asynchronously.
        """
        data = self.recv(MAX_PACKET_SIZE)
        if not data:
            # Wait for data
            return
        #print(data)
        self.in_buffer += data
        self.process_func()

    def process_buffer (self):
        b = self.in_buffer
        try:
            size = unpack("!I", b[:4])[0]+8
        except:
            self.close()
            e = BrlAPIError("Probably not brltty on the other side")
            self.error_callback(e)
            raise e
        if size>MAX_PACKET_SIZE:
            self.close()
            e = BrlAPIError("Header indicates packet size bigger than MAX_PACKET_SIZE, this is not brltty talking for sure")
            self.error_callback(e)
            raise e
        l = len(b)
        if l<size:
            # Wait for whole packet to arrive
            return
        # Take a packet out of the buffer
        self.in_buffer = b[size:]
        return b[:size]

    def process_handshake (self):
        b = self.process_buffer()
        if b is None:
            # No packet in the buffer yet
            return
        try:
            packet = Packet.from_bytes(b)
        except Exception as e:
            self.exception = BrlAPIError("Unable to interpret a packet during the handshake: "+str(e))
            self.error_callback(self.exception)
            self.process_lock.release()
            return
        #print("Server: "+str(packet))
        if packet.isError():
            self.close()
            self.exception = e = BrlAPIError.from_packet(packet)
            self.error_callback(e)
            self.process_lock.release()
            return
        if packet.isVersion():
            self.step = 1
            self.send(VersionPacket())
        elif packet.isAuth():
            self.step = 2
            if packet.method==AUTH_KEY:
                k = self.auth_callback(AUTH_KEY)
                if k is None:
                    return
                k = k.encode() if isinstance(k, str) else k
                p = ClientAuthPacket(method=AUTH_KEY, payload=k)
                self.send(p)
            elif packet.method==AUTH_NONE:
                self.step = 3
                self.auth_callback(AUTH_NONE)
                self.mode         = "normal"
                self.process_func = self.process_data
                self.process_lock.release()
            else:
                self.close()
                self.exception = e = BrlAPIError("This port of BRLAPI supports only AUTH_NONE and AUTH_KEY authentication methods, %s requested" % ("AUTH_CRED" if packet.method==AUTH_CRED else str(packet.method)))
                self.error_callback(e)
                self.process_lock.release()
                return
        elif packet.isACK():
            self.step = 3
            self.mode         = "normal"
            self.process_func = self.process_data
            self.process_lock.release()
        else:
            self.close()
            self.exception = e = BrlAPIError("Unexpected packet arrived during handshake.")
            self.error_callback(e)
            self.process_lock.release()
            return
        # If there is already a next packet, process it as well
        if self.in_buffer:
            self.process_func()

    def process_data (self):
        b = self.process_buffer()
        if b is None:
            # Wait for a packet, buffer is empty
            return
        try:
            packet = Packet.from_bytes(b)
        except Exception as e:
            self.exception = e = BrlAPIError("Unable to deserialize packet: "+str(e))
            self.error_callback(e)
            # Wait for a next one, perhaps something funny happened
            return
        #print("Server: "+str(packet))
        if packet.isInfo():
            if packet.type==PACKET_GETDRIVERNAME:
                self.driver = packet.info
            elif packet.type==PACKET_GETMODELID:
                self.model = packet.info
            elif packet.type==PACKET_GETDISPLAYSIZE:
                self.displaySize = packet.info
        elif packet.isKey():
            if self.key_callback:
                self.key_callback(packet)
            else:
                self.packetqueue.append(packet)
                try:
                    self.keywait_lock.release()
                except:
                    pass
        elif packet.isError():
            self.exception = e = BrlAPIError.from_packet(packet)
            self.error_callback(e)
        if not packet.isKey():
            try:
                self.receive_lock.release()
            except:
                pass
        # Process the next packet if waiting
        if self.in_buffer:
            self.process_func()

    def send (self, data, blocking=False):
        data = Packet(data) if isinstance(data, int) else data
        #print("Client: "+repr(data))
        data = data.to_bytes() if isinstance(data, Packet) else data
        if blocking:
            self.receive_lock.acquire()
        with self.send_lock:
            asyncore.dispatcher_with_send.send(self, data)
        if blocking:
            self.receive_lock.acquire()
            self.receive_lock.release()

    def getDriverName (self):
        with self.process_lock:
            self.send(Packet(PACKET_GETDRIVERNAME), blocking=True)
        self._excheck()
        return self.driver

    def getModelIdentifier (self):
        with self.process_lock:
            self.send(PACKET_GETMODELID, blocking=True)
        self._excheck()
        return self.model

    def getDisplaySize (self):
        with self.process_lock:
            self.send(PACKET_GETDISPLAYSIZE, blocking=True)
        self._excheck()
        return self.displaySize

    def enterTTYMode (self, ttys=DEFAULT_TTY, driver=""):
        """Request control of a specific TTY."""
        ttys = (0,) if ttys==DEFAULT_TTY else ttys
        ttys = (ttys,) if isinstance(ttys, int) else ttys
        payload = pack("!I" +(len(ttys)*"I"), len(ttys), *ttys)
        if driver is None:
            driver = self.getDriverName()
        driver = driver.encode("ASCII") if isinstance(driver, str) else driver
        payload += pack("!B", len(driver))+driver
        with self.process_lock:
            self.send(Packet(PACKET_ENTERTTYMODE, payload), blocking=True)
        self._excheck()
        self.mode = "TTY:"+str(ttys[-1])

    def leaveTTYMode (self):
        """Release control of the current TTY."""
        with self.process_lock:
            self.send(PACKET_LEAVETTYMODE, blocking=True)
        self._excheck()
        self.mode = "normal"

    def writeText (self, text, encoding="UTF-8", cursor=CURSOR_OFF):
        if not self.mode.startswith("TTY"):
            raise BrlAPIError("Not permitted in %s mode" % self.mode)
        fmt = "!II%is" # flags, len(bytes(text)), bytes(text)
        flags = WF_TEXT|WF_CHARSET
        text = text.encode(encoding)
        encoding = encoding.encode("ASCII")
        lt = len(text); le = len(encoding)
        args = [0, lt, text]
        if cursor>=0:
            flags |= WF_CURSOR
            fmt += "I" # Cursor location or off
            args.append(cursor)
        fmt += "B%is" # len(encoding), bytes(encoding)
        args[0] = flags
        args.append(le)
        args.append(encoding)
        payload = pack(fmt % (lt, le), *args)
        self.send(WritePacket(payload=payload))

    def writeDots (self, content):
        if not self.mode.startswith("TTY"):
            raise BrlAPIError("Not permitted in %s mode" % self.mode)
        if self.displaySize==(0, 0):
            self.getDisplaySize()
        size = self.displaySize[0]*self.displaySize[1]
        if size==0:
            # Driver: NoBraille
            return
        flags = WF_REGION|WF_TEXT|WF_CURSOR|WF_ATTR_OR
        fmt = "!IIII%is%isI" % (size, size)
        payload = pack(fmt, flags, 1, size, size, size*b" ", content, 0)
        self.send(WritePacket(payload=payload))

    def writeRegion (self, content, start=1, cursor=CURSOR_OFF):
        if not self.mode.startswith("TTY"):
            raise BrlAPIError("Not permitted in %s mode" % self.mode)
        flags = WF_REGION|WF_TEXT
        fmt = "!IIII%is" % len(content)
        args = [0, start, len(content),  len(content), content]
        if cursor>=0:
            fmt += "I"
            flags |= WF_CURSOR
            args.append(cursor)
        args[0] = flags
        payload = pack(fmt, *args)
        self.send(WritePacket(payload=payload))

    def setCursor (self, cursor):
        if not self.mode.startswith("TTY"):
            raise BrlAPIError("Not permitted in %s mode" % self.mode)
        if cursor<0:
            return
        payload = pack("!II", WF_CURSOR, cursor)
        self.send(WritePacket(payload=payload))

    def readKey (self, blocking=True):
        if not self.mode.startswith("TTY"):
            self.packetqueue.clear()
            raise BrlAPIError("Not permitted in %s mode" % self.mode)
        if blocking and not self.packetqueue:
            self.keywait_lock.acquire()
            with self.keywait_lock:
                return self.packetqueue.pop()
        try:
            return self.packetqueue.pop()
        except:
            pass

    def close(self):
        """Close the connection properly."""
        super().close()
        print("[BrlAPI] Connection closed.")
