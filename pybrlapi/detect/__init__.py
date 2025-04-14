"""
Part of pybrlapi.

This package deals with detection of serving brltty instances on the network,
and finding brltty executables on the system that might be used.

For now Windows only and a partial solution.

Still needs:
* Executable finder
* Checking that brltty is really the found service at the end of a network endpoint
* Performing an ARP scan so that the OS's ARP cache can be updated before grabing ips
* Performing a ping sweep to increase a chance of detection in network segments after ARP
* Everything above implemented for POSIX
"""
from ..constants import DEFAULT_PORT, PROTOCOL_VERSION
from ..protocol import Packet, PACKET_VERSION
from ipaddress import ip_address
from socket import create_connection
import os

if os.name=="nt":
    from .win32 import *

    def brltty_binaries ():
        ps = set()
        # If brlapi service is registered, we can get the binary path from it.
        # This will be so if:
        # * brltty was installed using official installer and service install was selected;
        # * if the service install flag was called on the brltty binary and/or
        # * Microsoft's distro of brltty is present on the system for Narator to use
        # Get the brlapi service path first:
        sc = query_service_config("brlapi").get("BINARY_PATH_NAME", "")
        ps.add(os.path.abspath(sc[:sc.lower().find(".exe")+4]))
        # Add the official MS brltty distro default exe to test in case sc found nothing
        # or the custom installation overrode the original service installed by Microsoft
        ps.add(os.path.join(os.environ.get("WINDIR", ""), "brltty", "bin", "brltty.exe"))
        # See if this pybrlapi is carying brltty with it
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ps.update((os.path.join(base, "brltty.exe"), os.path.join(base, "brltty", "brltty.exe"), os.path.join(base, "brltty", "bin", "brltty.exe")))
        # Search for installation of brltty in usual places
        base = os.environ.get("PROGRAMFILES", "")
        ps.add(os.path.join(base, "brltty", "bin", "brltty.exe"))
        base = os.environ.get("PROGRAMFILES(X86)", "")
        ps.add(os.path.join(base, "brltty", "bin", "brltty.exe"))
        # Some people like to install/extract brltty on home or system drive partition
        base = os.environ.get("HOMEDRIVE", "")
        ps.add(os.path.join(base, "brltty", "bin", "brltty.exe"))
        base = os.environ.get("SYSTEMDRIVE", "")
        ps.add(os.path.join(base, "brltty", "bin", "brltty.exe"))
        # Some may want brltty in their user's home
        base = os.environ.get("USERPROFILE", "")
        ps.add(os.path.join(base, "brltty", "bin", "brltty.exe"))
        return [p for p in ps if os.path.isfile(p)]

def check (host, port, timeout=0.4):
    pair = (host, port)
    try:
        with create_connection(pair, timeout) as conn:
            data = conn.recv(1024)
            if data and len(data)<12 and data[-1]==PACKET_VERSION:
                # Sometimes the packet payload does not arrive immediately with the header, so try again, just in case
                data += conn.recv(1024)
            if len(data)!=12:
                # brltty sends only the PACKET_VERSION at the contact and nothing else
                return
    except:
        return
    try:
        p = Packet.from_bytes(data)
        if p.isVersion():
            return pair, p.protocol
    except:
        pass

def arp_scan ():
    # We need to implement here sending of ARP request through each LAN facing adapter
    # That shall update the OS's ARP cache
    # Then we pick ips of devices that answered from it:
    for ip in get_arp_cache().keys():
        ipo = ip_address(ip)
        if ipo.is_global or ipo.is_multicast or ipo.is_reserved:
            continue
        yield ip

def brltty_instances (ports=(DEFAULT_PORT,), localhost=True, interfaces=True, lan_arp_scan=True, lan_ping_sweep=True):
    do_nothing = ()
    detected = []
    for port in (ports if localhost else do_nothing):
        pair = check("localhost", port)
        if pair:
            detected.append(pair)
    for ip in ((get_interface_ip(iface[0]) for iface in get_interfaces())
               if interfaces else do_nothing):
        for port in ports:
            pair = check(ip, port)
            if pair:
                detected.append(pair)
    for ip in (arp_scan() if lan_arp_scan else do_nothing):
        for port in ports:
            pair = check(ip, port)
            if pair:
                detected.append(pair)
    return detected
