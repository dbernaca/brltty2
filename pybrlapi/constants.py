"""
Part of pybrlapi library.
Constants needed for communication with brltty daemon/service.
And those needed to construct packets of BrlAPI protocol as well.
From brltty and libbrlapi source code at https://github.com/brltty/brltty
ChatGPT helped with extraction and necessary adjustments.
"""

# General Constants
DEFAULT_HOST     = "localhost"
DEFAULT_PORT     = 4101

PROTOCOL_VERSION = 8
MAX_PACKET_SIZE  = 4096

DEFAULT_TTY      = -1
DEFAULT_DISPLAY  = -1

# Packet Type Constants
PACKET_VERSION = ord('v')
PACKET_AUTH = ord('a')
PACKET_GETDRIVERNAME = ord('n')
PACKET_GETMODELID = ord('d')
PACKET_GETDISPLAYSIZE = ord('s')
PACKET_ENTERTTYMODE = ord('t')
PACKET_SETFOCUS = ord('F')
PACKET_LEAVETTYMODE = ord('L')
PACKET_KEY = ord('k')
PACKET_IGNOREKEYRANGES = ord('m')
PACKET_ACCEPTKEYRANGES = ord('u')
PACKET_WRITE = ord('w')
PACKET_ENTERRAWMODE = ord('*')
PACKET_LEAVERAWMODE = ord('#')
PACKET_PACKET = ord('p')
PACKET_ACK = ord('A')
PACKET_ERROR = ord('e')
PACKET_EXCEPTION = ord('E')
PACKET_SUSPENDDRIVER = ord('S')
PACKET_RESUMEDRIVER = ord('R')
PACKET_SYNCHRONIZE = ord('Z')

# Authorization Types
AUTH_NONE = ord('N')
AUTH_KEY = ord('K')
AUTH_CRED = ord('C')

# Device Magic Number
DEVICE_MAGIC = 0xdeadbeef

# Error Codes
ERROR_SUCCESS = 0  # Success
ERROR_NOMEM = 1  # Not enough memory
ERROR_TTYBUSY = 2  # A connection is already running in this tty
ERROR_DEVICEBUSY = 3  # A connection is already using RAW or suspend mode
ERROR_UNKNOWN_INSTRUCTION = 4  # Not implemented in protocol
ERROR_ILLEGAL_INSTRUCTION = 5  # Forbidden in current mode
ERROR_INVALID_PARAMETER = 6  # Out of range or have no sense
ERROR_INVALID_PACKET = 7  # Invalid size
ERROR_CONNREFUSED = 8  # Connection refused
ERROR_OPNOTSUPP = 9  # Operation not supported
ERROR_GAIERR = 10  # Getaddrinfo error
ERROR_LIBCERR = 11  # Libc error
ERROR_UNKNOWNTTY = 12  # Couldn't find out the tty number
ERROR_PROTOCOL_VERSION = 13  # Bad protocol version
ERROR_EOF = 14  # Unexpected end of file
ERROR_EMPTYKEY = 15  # Key file empty
ERROR_DRIVERERROR = 16  # Packet returned by driver too large
ERROR_AUTHENTICATION = 17  # Authentication failed
ERROR_READONLY_PARAMETER = 18  # Parameter cannot be changed

# Dictionary Mapping of Errors to Descriptions
ERROR_DESCRIPTIONS = {
    ERROR_SUCCESS: "Success",
    ERROR_NOMEM: "Not enough memory",
    ERROR_TTYBUSY: "A connection is already running in this tty",
    ERROR_DEVICEBUSY: "A connection is already using RAW or suspend mode",
    ERROR_UNKNOWN_INSTRUCTION: "Not implemented in protocol",
    ERROR_ILLEGAL_INSTRUCTION: "Forbidden in current mode",
    ERROR_INVALID_PARAMETER: "Out of range or have no sense",
    ERROR_INVALID_PACKET: "Invalid size",
    ERROR_CONNREFUSED: "Connection refused",
    ERROR_OPNOTSUPP: "Operation not supported",
    ERROR_GAIERR: "Getaddrinfo error",
    ERROR_LIBCERR: "Libc error",
    ERROR_UNKNOWNTTY: "Couldn't find out the tty number",
    ERROR_PROTOCOL_VERSION: "Bad protocol version",
    ERROR_EOF: "Unexpected end of file",
    ERROR_EMPTYKEY: "Key file empty",
    ERROR_DRIVERERROR: "Packet returned by driver too large",
    ERROR_AUTHENTICATION: "Authentication failed",
    ERROR_READONLY_PARAMETER: "Parameter cannot be changed",
    }

# Flags for writing
WF_DISPLAYNUMBER = 0x01 # Display number
WF_REGION        = 0x02 # Region parameter 
WF_TEXT          = 0x04 # Contains some text
WF_ATTR_AND      = 0x08 # And attributes
WF_ATTR_OR       = 0x10 # Or attributes
WF_CURSOR        = 0x20 # Cursor position
WF_CHARSET       = 0x40 # Charset

CURSOR_LEAVE = -1
CURSOR_OFF   = 0

