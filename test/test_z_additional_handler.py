import tornado.testing
import handlers
import utils
import json
import lxml.etree


class MockMachineResolver(utils.machine_resolver.MachineResolver):
    def get_machine(self, ip):
        assert ip == "127.0.0.1"
        return utils.machine_resolver.LibvirtMachine('192.168.0.1',
                                                     lxml.etree.parse(open('test/static/metadata_domain.xml')))


class AdditionalHandlerTestCase(tornado.testing.AsyncHTTPTestCase):
    """
    This test must be running last since it modifies the routers and the list of APIs available
    """

    def setUp(self):
        # this import can break previous tests, that's why we have it here and not on top
        __import__('handlers.example_additional_handler')

        super(AdditionalHandlerTestCase, self).setUp()

    def get_app(self):
        return tornado.web.Application(
            handlers.routes,
            machine_resolver=MockMachineResolver()
        )

    def get(self, path):
        self.http_client.fetch(self.get_url(path), self.stop)

        return self.wait()

    def test_latest_api(self):
        response = self.get('/latest/')
        from handlers import ApiVersionRootHandler
        self.assertListEqual(ApiVersionRootHandler.apis, ['meta-data', 'user-data', 'example'])
        self.assertListEqual(response.body.split("\n"), ['meta-data', 'user-data', 'example'])

    def test_instance_tags(self):
        response = self.get('/latest/example/tags')
        self.assertListEqual(json.loads(response.body), ['tag_a', 'tag_b', 'tag_c'])