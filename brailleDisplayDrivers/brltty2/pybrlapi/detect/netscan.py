from ping import ping

ICMPTimeout = 0.02
pingCount   = 2

def expandnet (netip):
    if netip=="0.0.0.0": return []
    if not netip.strip(): return []
    ipstart = netip[:netip.rfind(".")]
    ips = []
    # Network and broadcast addresses excluded
    for y in list(range(50, 150))+list(range(1, 50))+list(range(150, 255)):
        ips.append("%s.%i" % (ipstart, y))
    return ips

def checkdelay (l):
    s = 0.0
    for x in l: s += x
    return s>=0.0

def scan (netip):
    res = []
    for x in expandnet(netip):
        r = ping(x, ICMPTimeout, pingCount)
        if checkdelay(r): res.append((x, r))
    return res

if __name__=="__main__":
    print(scan(input("NetIP: ")))
    input()
