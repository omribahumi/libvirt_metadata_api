import StringIO
import lxml.etree
import utils
from utils.machine_resolver.base import *


__all__ = ['LibvirtMachine', 'LibvirtMachineResolver']

class LibvirtMachine(Machine):
    def __init__(self, ip, domain_etree):
        self.ip = ip
        self.domain_etree = domain_etree

    def get_userdata(self):
        return utils.xml.fix_indent(self.domain_etree.find('/metadata/userdata').text)

    def get_instance_id(self):
        return self.domain_etree.find('/metadata/instance-id').text

    def get_public_ipv4(self):
        return self.ip

    def get_local_ipv4(self):
        return self.ip


class LibvirtMachineResolver(MachineResolver):
    def __init__(self, connection):
        self.connection = connection

    def get_domain_etree_by_id(self, domain_id):
        domain = self.connection.lookupByID(domain_id)
        domain_etree = lxml.etree.parse(StringIO.StringIO(domain.XMLDesc(0)))

        return domain_etree

    def get_domain_etree_by_mac_address(self, mac):
        for domain_id in self.connection.listDomainsID():
            domain_etree = self.get_domain_etree_by_id(domain_id)
            macs = domain_etree.xpath('/domain/devices/interface/mac/@address')

            if macs and mac in macs:
                return domain_etree
        else:
            raise MachineResolverException(
                "Unable to locate a libvirt domain for MAC address %s" % (mac,))

    def get_domain_etree_by_ip_address(self, ip):
        mac = utils.arp.get_mac_address(ip)
        if not mac:
            raise MachineResolverException("Unable to find a MAC address for IP %s" % (ip,))
        else:
            return self.get_domain_etree_by_mac_address(mac)

    def get_machine(self, ip):
        return LibvirtMachine(ip, self.get_domain_etree_by_ip_address(ip))
