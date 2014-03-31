import sys
import re
import subprocess


def get_arp_table_darwin():
    """
    Parse the host's ARP table on an OSX machine

    :return: Machine readable ARP table (by running the "arp -a -n" command)
    :rtype: dict {'ip_address': 'mac_address'}
    """

    arp_data_re = re.compile(r'^\S+ \((?P<ip_address>[^\)]+)\) at (?P<hw_address>(?:[0-9a-f]{2}:){5}(?:[0-9a-f]{2})) on (?P<device>\S+) ifscope \[(?P<type>\S+)\]$')

    arp_data_raw = subprocess.check_output(['arp', '-a', '-n']).split("\n")[:-1]
    parsed_arp_table = (arp_data_re.match(i).groupdict() for i in arp_data_raw)

    return {d['ip_address']: d['hw_address'] for d in parsed_arp_table}


def get_arp_table_linux():
    """
    Parse the host's ARP table on a Linux machine

    :return: Machine readable ARP table (see the Linux Kernel documentation on /proc/net/arp for more information)
    :rtype: dict {'ip_address': 'mac_address'}
    """

    with open('/proc/net/arp') as proc_net_arp:
        arp_data_raw = proc_net_arp.read(-1).split("\n")[1:-1]

    parsed_arp_table = (dict(zip(('ip_address', 'type', 'flags', 'hw_address', 'mask', 'device'), v))
                        for v in (re.split('\s+', i) for i in arp_data_raw))

    return {d['ip_address']: d['hw_address'] for d in parsed_arp_table}


def get_arp_table():
    """
    Parse the host's ARP table

    :return: Machine readable ARP table (see the Linux Kernel documentation on /proc/net/arp for more information)
    :rtype: dict {'ip_address': 'mac_address'}
    """

    if sys.platform in ('linux', 'linux2'):
        return get_arp_table_linux()
    elif sys.platform == 'darwin':
        return get_arp_table_darwin()
    else:
        raise Exception("Unable to fetch ARP table on %s" % (sys.platform,))




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
        return arp_table[ip]
