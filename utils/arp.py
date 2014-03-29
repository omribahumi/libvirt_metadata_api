import re


def get_arp_table():
    """
    Parse the host's ARP table

    :return: Machine readable ARP table (see the Linux Kernel documentation on /proc/net/arp for more information)
    :rtype: dict {'ip_address':
                    {'type': '', 'flags': '', 'hw_address': '<mac_address>', 'mask': '', 'device': '<nic>'},
                    ...
                }
    """

    # TODO: add support for more operating systems other than Linux
    with open('/proc/net/arp') as proc_net_arp:
        arp_data_raw = proc_net_arp.read(-1).split("\n")

    return {v[0]: dict(zip(('type', 'flags', 'hw_address', 'mask', 'device'), v[1:]))
            for v in (re.split('\s+', i) for i in arp_data_raw[1:-1])}


def get_mac_address(ip):
    """
    Get MAC address for a given IP address by looking it up in the host's ARP table

    :param ip: IP address to look up
    :type ip: str
    :return: MAC address
    :rtype: str
    """

    arp_table = get_arp_table()
    if not ip in arp_table:
        return None
    else:
        return arp_table[ip]['hw_address']
