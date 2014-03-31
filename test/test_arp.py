import unittest
import utils
import mock


class ArpTestCase(unittest.TestCase):
    def setUp(self):
        self.linux_data = ('IP address       HW type     Flags       HW address            Mask     Device\n'
                           '192.168.0.94     0x1         0x2         aa:aa:aa:aa:aa:aa     *        br0\n'
                           '192.168.0.92     0x1         0x2         bb:bb:bb:bb:bb:bb     *        br0\n'
                           '192.168.0.200    0x1         0x2         cc:cc:cc:cc:cc:cc     *        br0\n'
                           '192.168.0.254    0x1         0x2         ee:ee:ee:ee:ee:ee     *        br0\n')

        self.darwin_data = ('? (192.168.0.1) at aa:aa:aa:aa:aa:aa on en0 ifscope [ethernet]\n'
                            '? (192.168.0.230) at cc:cc:cc:cc:cc:cc on en0 ifscope [ethernet]\n'
                            '? (192.168.0.250) at bb:bb:bb:bb:bb:bb on en0 ifscope [ethernet]\n')

    def test_get_arp_table_linux(self):
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.linux_data)):
            self.assertDictEqual(
                utils.arp.get_arp_table_linux(),
                {'192.168.0.94': 'aa:aa:aa:aa:aa:aa',
                 '192.168.0.200': 'cc:cc:cc:cc:cc:cc',
                 '192.168.0.92': 'bb:bb:bb:bb:bb:bb',
                 '192.168.0.254': 'ee:ee:ee:ee:ee:ee'}
            )

    def test_get_arp_table_darwin(self):
        with mock.patch('subprocess.check_output', return_value=self.darwin_data):
            self.assertDictEqual(
                utils.arp.get_arp_table_darwin(),
                {'192.168.0.230': 'cc:cc:cc:cc:cc:cc',
                 '192.168.0.250': 'bb:bb:bb:bb:bb:bb',
                 '192.168.0.1': 'aa:aa:aa:aa:aa:aa'}
            )

    def test_get_mac_address_linux(self):
        with mock.patch('__builtin__.open', mock.mock_open(read_data=self.linux_data)):
            for linux_platform in ('linux', 'linux2'):
                with mock.patch('sys.platform', new=linux_platform):
                    self.assertEqual(utils.arp.get_mac_address('192.168.0.94'), 'aa:aa:aa:aa:aa:aa')
                    self.assertEqual(utils.arp.get_mac_address('1.1.1.1'), None)

    def test_get_mac_address_darwin(self):
        with mock.patch('sys.platform', new='darwin'), mock.patch('subprocess.check_output', return_value=self.darwin_data):
            self.assertEqual(utils.arp.get_mac_address('192.168.0.250'), 'bb:bb:bb:bb:bb:bb')
            self.assertEqual(utils.arp.get_mac_address('1.1.1.1'), None)

    def test_get_mac_address_unsupported(self):
        with mock.patch('sys.platform', new='unsupported'):
            self.assertRaises(Exception, utils.arp.get_mac_address, '1.1.1.1')
