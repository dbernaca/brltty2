from subprocess import check_output
from socket import inet_ntoa, inet_aton
from struct import pack
from ctypes import *

__all__ = ["get_arp_cache", "get_interface_ip", "get_interfaces", "query_service_config"]

class MIB_IPNETROW(Structure):
    _fields_ = [("dwIndex", c_ulong),
                ("dwPhysAddrLen", c_ulong),
                ("bPhysAddr", c_ubyte * 8),
                ("dwAddr", c_ulong),
                ("dwType", c_ulong)]

class MIB_IPNETTABLE(Structure):
    _fields_ = [("dwNumEntries", c_ulong),
                ("table", MIB_IPNETROW * 512)]

GetIpNetTable = windll.iphlpapi.GetIpNetTable
GetIpNetTable.argtypes = [POINTER(MIB_IPNETTABLE), POINTER(c_ulong), c_bool]
GetIpNetTable.restype  = c_ulong

MAX_ADAPTER_NAME_LENGTH = 256 
MAX_ADAPTER_ADDRESS_LENGTH = 8 
MAX_ADAPTER_DESCRIPTION_LENGTH = 128 

class IP_ADDR_STRING(Structure):
    pass
LP_IP_ADDR_STRING = POINTER(IP_ADDR_STRING) 
IP_ADDR_STRING._fields_ = [ 
    ("next", LP_IP_ADDR_STRING), 
    ("ipAddress", c_char * 16), 
    ("ipMask", c_char * 16), 
    ("context", c_ulong)]

class IP_ADAPTER_INFO (Structure):
    pass
LP_IP_ADAPTER_INFO = POINTER(IP_ADAPTER_INFO) 
IP_ADAPTER_INFO._fields_ = [ 
    ("next", LP_IP_ADAPTER_INFO), 
    ("comboIndex", c_ulong), 
    ("adapterName", c_char * (MAX_ADAPTER_NAME_LENGTH + 4)), 
    ("description", c_char * (MAX_ADAPTER_DESCRIPTION_LENGTH + 4)), 
    ("addressLength", c_uint), 
    ("address", c_ubyte * MAX_ADAPTER_ADDRESS_LENGTH), 
    ("index", c_ulong), 
    ("type", c_uint), 
    ("dhcpEnabled", c_uint), 
    ("currentIpAddress", LP_IP_ADDR_STRING), 
    ("ipAddressList", IP_ADDR_STRING), 
    ("gatewayList", IP_ADDR_STRING), 
    ("dhcpServer", IP_ADDR_STRING), 
    ("haveWins", c_uint), 
    ("primaryWinsServer", IP_ADDR_STRING), 
    ("secondaryWinsServer", IP_ADDR_STRING), 
    ("leaseObtained", c_ulong), 
    ("leaseExpires", c_ulong)] 

GetAdaptersInfo = windll.iphlpapi.GetAdaptersInfo 
GetAdaptersInfo.restype = c_ulong 
GetAdaptersInfo.argtypes = [LP_IP_ADAPTER_INFO, POINTER(c_ulong)] 

def get_arp_cache ():
    """
    Retrieve ARP cache on Windows using ctypes.
    """
    size = c_ulong()
    GetIpNetTable(None, byref(size), False)
    table = create_string_buffer(size.value)
    GetIpNetTable(cast(table, POINTER(MIB_IPNETTABLE)), byref(size), False)
    ip_net_table = cast(table, POINTER(MIB_IPNETTABLE)).contents
    arp_table = {}
    for x in range(ip_net_table.dwNumEntries):
        entry = ip_net_table.table[x]
        mac = [entry.bPhysAddr[y] for y in range(entry.dwPhysAddrLen)]
        if not any(mac):
            # Skip devices with all zeroes in MAC address
            continue
        ip = inet_ntoa(pack("<L", entry.dwAddr))
        arp_table[ip] = ":".join("%02x" % z for z in mac)
    return arp_table

def get_interface_ip (iface):
    adapterList = (IP_ADAPTER_INFO * 64)() 
    buflen = c_ulong(sizeof(adapterList)) 
    rc = GetAdaptersInfo(byref(adapterList[0]), byref(buflen)) 
    if rc != 0: 
        return
    for a in adapterList: 
        if iface==a.adapterName or iface.lower() in a.description.lower():
            ips = a.ipAddressList
            return ips.ipAddress
        if not a.next:
            break
        """
        adNode = a.ipAddressList 
        while True: 
            ipAddr = adNode.ipAddress 
            if ipAddr: 
                yield ipAddr 
            adNode = adNode.next 
            if not adNode: 
                break 
            adNode = adNode.contents
        """

def get_interfaces ():
    adapterList = (IP_ADAPTER_INFO * 64)() 
    buflen = c_ulong(sizeof(adapterList)) 
    rc = GetAdaptersInfo(byref(adapterList[0]), byref(buflen)) 
    ifaces = []
    if rc != 0: 
        return ifaces
    for a in adapterList: 
        ifaces.append((a.adapterName, a.description, a.type))
        if not a.next:
            break
    return ifaces

def query_service_config (name):
    d = {}
    try:
        lines = iter(check_output(["sc", "qc", name]).strip().splitlines())
    except:
        return d
    next(lines) # Skip the first one
    #next(lines) # We probably should skip the second one too, but don't, just in case
    for line in lines:
        line = line.strip()
        if not line:
            continue
        line  = line.decode("UTF-8").split(":", 1)
        key   = line[0].rstrip()
        value = line[1].lstrip() if len(line)==2 else ""
        d[key] = value
    return d
