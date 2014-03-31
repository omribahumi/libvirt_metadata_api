import tornado.testing
import handlers
import utils
import lxml.etree


class MockMachineResolver(utils.machine_resolver.MachineResolver):
    def get_machine(self, ip):
        assert ip == "127.0.0.1"
        return utils.machine_resolver.LibvirtMachine('192.168.0.1', lxml.etree.parse(open('test/static/metadata_domain.xml')))


class MyHTTPTest(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return tornado.web.Application(
            handlers.routes,
            machine_resolver=MockMachineResolver()
        )

    def get(self, path):
        self.http_client.fetch(self.get_url(path), self.stop)

        return self.wait()

    def test_root(self):
        response = self.get('/')
        self.assertListEqual(
            response.body.split("\n"),
            ['1.0', '2007-01-19', '2007-03-01', '2007-08-29', '2007-10-10', '2007-12-15', '2008-02-01',
             '2008-09-01', '2009-04-04', '2011-01-01', '2011-05-01', '2012-01-12', 'latest']
        )

    def test_latest_api(self):
        response = self.get('/latest')
        self.assertEqual(response.body, '')

        response = self.get('/latest/')
        self.assertListEqual(response.body.split("\n"), ['meta-data', 'user-data'])

    def test_metadata_base(self):
        response = self.get('/latest/meta-data')
        self.assertEqual(response.body, '')

        response = self.get('/latest/meta-data/')
        self.assertListEqual(response.body.split("\n"), ['instance-id', 'local-ipv4', 'public-ipv4', 'public-keys/'])

    def test_metadata_instance_id(self):
        machine = self.get_app().settings['machine_resolver'].get_machine('127.0.0.1')
        response = self.get('/latest/meta-data/instance-id')

        self.assertEqual(response.body, machine.get_instance_id())

    def test_metadata_public_ip(self):
        machine = self.get_app().settings['machine_resolver'].get_machine('127.0.0.1')
        response = self.get('/latest/meta-data/public-ipv4')

        self.assertEqual(response.body, machine.get_public_ipv4())

    def test_metadata_local_ip(self):
        machine = self.get_app().settings['machine_resolver'].get_machine('127.0.0.1')
        response = self.get('/latest/meta-data/local-ipv4')

        self.assertEqual(response.body, machine.get_local_ipv4())

    def test_metadata_public_keys(self):
        machine = self.get_app().settings['machine_resolver'].get_machine('127.0.0.1')

        response = self.get('/latest/meta-data/public-keys')
        self.assertListEqual(response.body.split("\n"),
                             ["%d=%s" % (i, key_name) for i, key_name in enumerate(machine.get_keys())])

        for number, key in enumerate(machine.get_keys().values()):
            response = self.get('/latest/meta-data/public-keys/%d' % (number,))
            self.assertListEqual(response.body.split("\n"),
                                 machine.get_keys().values()[number].keys())

            for key_type, key_value in key.iteritems():
                response = self.get('/latest/meta-data/public-keys/%d/%s' % (number, key_type))
                self.assertEqual(response.body, key_value)

    def test_userdata(self):
        machine = self.get_app().settings['machine_resolver'].get_machine('127.0.0.1')

        response = self.get('/latest/user-data')
        self.assertEqual(response.body, machine.get_userdata())

