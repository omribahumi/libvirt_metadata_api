import unittest
import utils
import mock


class ArpTestCase(unittest.TestCase):
    def setUp(self):
        self.data = ('IP address       HW type     Flags       HW address            Mask     Device\n' +
                     '192.168.0.94     0x1         0x2         aa:aa:aa:aa:aa:aa     *        br0\n' +
                     '192.168.0.92     0x1         0x2         bb:bb:bb:bb:bb:bb     *        br0\n' +
                     '192.168.0.200    0x1         0x2         cc:cc:cc:cc:cc:cc     *        br0\n' +
                     '192.168.0.254    0x1         0x2         ee:ee:ee:ee:ee:ee     *        br0\n')

    def test_get_arp_table(self):
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.data)):
            self.assertDictEqual(
                utils.arp.get_arp_table(),
                {'192.168.0.94':
                     {'hw_address': 'aa:aa:aa:aa:aa:aa', 'flags': '0x2', 'device': 'br0', 'type': '0x1', 'mask': '*'},
                 '192.168.0.200':
                     {'hw_address': 'cc:cc:cc:cc:cc:cc', 'flags': '0x2', 'device': 'br0', 'type': '0x1', 'mask': '*'},
                 '192.168.0.92': {
                     'hw_address': 'bb:bb:bb:bb:bb:bb', 'flags': '0x2', 'device': 'br0', 'type': '0x1', 'mask': '*'},
                 '192.168.0.254': {
                     'hw_address': 'ee:ee:ee:ee:ee:ee', 'flags': '0x2', 'device': 'br0', 'type': '0x1', 'mask': '*'}
                }
            )

    def test_get_mac_address(self):
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.data)):
            self.assertEqual(utils.arp.get_mac_address('192.168.0.94'), 'aa:aa:aa:aa:aa:aa')
