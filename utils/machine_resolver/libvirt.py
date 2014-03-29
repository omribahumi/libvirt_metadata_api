import StringIO
import lxml.etree
import utils
import collections
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

    def get_keys(self):
        """
        Example metadata:
        <metadata>
            <public-keys>
                <public-key name="my-public-key2">
                    <key format="openssh-key">ssh-rsa my-public-key2 foo@bar</key>
                    <key format="another-format">a different format</key>
                </public-key>
                <public-key name="my-public-key1">
                    <key format="openssh-key">ssh-rsa my-public-key1 foo@bar</key>
                </public-key>
            </public-keys>
        </metadata>
        """

        return collections.OrderedDict(
            [(public_key.attrib['name'], {key.attrib['format']: key.text for key in public_key.findall('./key')})
             for public_key in self.domain_etree.findall('/metadata/public-keys/public-key')]
        )


class LibvirtMachineResolver(MachineResolver):
    def __init__(self, connection):
        self.connection = connection

    def get_domain_etree_by_id(self, domain_id):
        """
        Returns the Domain XML ElementTree object for the given domain_id

        :param domain_id: domain_id to retrieve
        :type domain_id: int
        :return: the Domain XML root ElementTree
        :rtype: lxml.etree._ElementTree
        """

        domain = self.connection.lookupByID(domain_id)
        domain_etree = lxml.etree.parse(StringIO.StringIO(domain.XMLDesc(0)))

        return domain_etree

    def get_domain_etree_by_mac_address(self, mac):
        """
        Returns the Domain XML ElementTree for the given MAC address

        :param mac: Domain MAC address
        :type mac: str
        :return: the Domain XML root ElementTree
        :rtype: lxml.etree._ElementTree
        """

        for domain_id in self.connection.listDomainsID():
            domain_etree = self.get_domain_etree_by_id(domain_id)
            macs = domain_etree.xpath('/domain/devices/interface/mac/@address')

            if macs and mac in macs:
                return domain_etree
        else:
            raise MachineResolverException(
                "Unable to locate a libvirt domain for MAC address %s" % (mac,))

    def get_domain_etree_by_ip_address(self, ip):
        """
        Returns the Domain XML ElementTree for the given IP address

        :param ip: Domain IP address
        :type ip: str
        :return: the Domain XML root ElementTree
        :rtype: lxml.etree._ElementTree
        """

        mac = utils.arp.get_mac_address(ip)
        if not mac:
            raise MachineResolverException("Unable to find a MAC address for IP %s" % (ip,))
        else:
            return self.get_domain_etree_by_mac_address(mac)

    def get_machine(self, ip):
        """
        Returns the LibvirtMachine object for the given IP address

        :param ip: machine IP address
        :type ip: str
        :return: Machine object
        :rtype: LibvirtMachine
        """

        return LibvirtMachine(ip, self.get_domain_etree_by_ip_address(ip))
