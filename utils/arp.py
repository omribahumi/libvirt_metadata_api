import re


def get_arp_table():
    with open('/proc/net/arp') as proc_net_arp:
        arp_data_raw = proc_net_arp.read(-1).split("\n")

    return {v[0]: dict(zip(('type', 'flags', 'hw_address', 'mask', 'device'), v[1:]))
            for v in (re.split('\s+', i) for i in arp_data_raw[1:-1])}


def get_mac_address(ip):
    arp_table = get_arp_table()
    if not ip in arp_table:
        return None
    else:
        return arp_table[ip]['hw_address']
