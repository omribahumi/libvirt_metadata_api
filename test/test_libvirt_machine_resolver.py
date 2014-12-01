import unittest
import utils
import lxml.etree
import mock


class MockLibvirtDomain(object):
    def __init__(self, xml):
        self.xml = xml

    def XMLDesc(self, flags=0):
        assert flags == 0

        return self.xml


class MockLibvirt(object):
    def listDomainsID(self):
        return [123]

    def lookupByID(self, id):
        assert id in self.listDomainsID()

        return MockLibvirtDomain(open('test/static/full_domain.xml').read(-1))


class LibvirtMachineResolverTestCase(unittest.TestCase):
    def setUp(self):
        self.machine_resolver = utils.machine_resolver.LibvirtMachineResolver(MockLibvirt())

    def assertValidDomainEtree(self, domain):
        assert isinstance(domain, lxml.etree._ElementTree)

        self.assertValidMachine(utils.machine_resolver.LibvirtMachine('1.2.3.4', domain))

    def assertValidMachine(self, machine):
        self.assertEqual(machine.get_instance_id(), 'i-12345678')

    def test_get_domain_etree_by_id(self):
        self.assertValidDomainEtree(self.machine_resolver.get_domain_etree_by_id(123))

    def test_get_domain_etree_by_mac_address(self):
        self.assertValidDomainEtree(self.machine_resolver.get_domain_etree_by_mac_address('aa:bb:cc:dd:ee:ff'))
        self.assertRaisesRegexp(
            utils.machine_resolver.MachineResolverException,
            '^Unable to locate a libvirt domain for MAC address ',
            self.machine_resolver.get_domain_etree_by_mac_address,
            'aa:aa:aa:aa:aa:aa'
        )

    def test_get_domain_etree_by_ip_address(self):
        with mock.patch('utils.arp.get_mac_address', return_value='aa:bb:cc:dd:ee:ff'):
            self.assertValidDomainEtree(self.machine_resolver.get_domain_etree_by_ip_address('1.2.3.4'))

        with mock.patch('utils.arp.get_mac_address', return_value=None):
            self.assertRaisesRegexp(
                utils.machine_resolver.MachineResolverException,
                '^Unable to find a MAC address for IP ',
                self.machine_resolver.get_domain_etree_by_ip_address,
                '1.2.3.4'
            )

    def test_get_machine(self):
        with mock.patch('utils.arp.get_mac_address', return_value='aa:bb:cc:dd:ee:ff'):
            self.assertValidMachine(self.machine_resolver.get_machine('1.2.3.4'))
