import re
import tornado.web
import utils


class ApiBaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self.request.machine =\
            self.settings['machine_resolver'].get_machine(self.request.remote_ip)

        assert isinstance(self.request.machine, utils.machine_resolver.Machine)


class NullHandler(ApiBaseHandler):
    def get(self):
        pass


class ApiRootHandler(ApiBaseHandler):
    def get(self):
        versions = ['1.0', '2007-01-19', '2007-03-01', '2007-08-29', '2007-10-10', '2007-12-15', '2008-02-01',
                    '2008-09-01', '2009-04-04', '2011-01-01', '2011-05-01', '2012-01-12', 'latest']

        self.write("\n".join(versions))


class ApiVersionRootHandler(ApiBaseHandler):
    def get(self):
        apis = ['meta-data', 'user-data']

        self.write("\n".join(apis))

class MetadataHandler(ApiBaseHandler):
    def get(self):
        urls = []

        for urlspec in self.application.handlers[0][1]:
            if '/meta-data/' in urlspec.regex.pattern and not urlspec.regex.pattern.endswith('/meta-data/$'):
                match = re.search(r'/meta-data/([^/]+/?)\??\$$', urlspec.regex.pattern)
                if match:
                    urls.append(match.group(1))

        self.write("\n".join(urls))


class InstanceIdHandler(ApiBaseHandler):
    def get(self):
        self.write(self.request.machine.get_instance_id())


class LocalIpv4Handler(ApiBaseHandler):
    def get(self):
        self.write(self.request.machine.get_local_ipv4())


class PublicIpv4Handler(ApiBaseHandler):
    def get(self):
        self.write(self.request.machine.get_public_ipv4())


class UserDataHandler(ApiBaseHandler):
    def get(self):
        self.write(self.request.machine.get_userdata())

class PublicKeysHandler(ApiBaseHandler):
    def get(self, number=None, key_format=None):
        if not number is None:
            number = int(number)

        if number is None and key_format is None:
            keys = ["%d=%s" % (i, key_name) for i, key_name in enumerate(self.request.machine.get_keys())]

            self.write("\n".join(keys))
        elif key_format is None:
            key = self.request.machine.get_keys().values()[number]

            self.write("\n".join(key.keys()))
        else:
            key = self.request.machine.get_keys().values()[number]

            self.write(key[key_format])
