import re
import tornado.web
import utils


class ApiBaseHandler(tornado.web.RequestHandler):
    """
    Base class for all API methods

    Populates self.request.machine with a utils.machine_resolver.Machine implementing instance
    """

    def prepare(self):
        self.require_setting('machine_resolver')

        self.request.machine =\
            self.settings['machine_resolver'].get_machine(self.request.remote_ip)

        assert isinstance(self.request.machine, utils.machine_resolver.Machine)


class NullHandler(ApiBaseHandler):
    """
    Some API calls simply return 200 with an empty body

    i.e.:
        /latest
        /latest/meta-data
    """

    def get(self):
        pass


class ApiRootHandler(ApiBaseHandler):
    """
    Handles calls to /

    Lists supported API versions
    """

    def get(self):
        versions = ['1.0', '2007-01-19', '2007-03-01', '2007-08-29', '2007-10-10', '2007-12-15', '2008-02-01',
                    '2008-09-01', '2009-04-04', '2011-01-01', '2011-05-01', '2012-01-12', 'latest']

        self.write("\n".join(versions))


class ApiVersionRootHandler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/

    Lists supported APIs
    """

    def get(self):
        apis = ['meta-data', 'user-data']

        self.write("\n".join(apis))


class MetadataHandler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/meta-data/

    Lists supported API calls by walking the URLSpecs for this application
    """

    def get(self):
        urls = []

        for urlspec in self.application.handlers[0][1]:
            if '/meta-data/' in urlspec.regex.pattern and not urlspec.regex.pattern.endswith('/meta-data/$'):
                match = re.search(r'/meta-data/([^/]+/?)\??\$$', urlspec.regex.pattern)
                if match:
                    urls.append(match.group(1))

        self.write("\n".join(urls))


class InstanceIdHandler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/meta-data/instance-id

    Returns the instance-id as returned by the Machine object
    """

    def get(self):
        self.write(self.request.machine.get_instance_id())


class LocalIpv4Handler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/meta-data/local-ipv4

    Returns the local IPv4 as returned by the Machine object
    """

    def get(self):
        self.write(self.request.machine.get_local_ipv4())


class PublicIpv4Handler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/meta-data/public-ipv4

    Returns the public IPv4 as returned by the Machine object
    """

    def get(self):
        self.write(self.request.machine.get_public_ipv4())


class UserDataHandler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/user-data
        /<version>/user-data/

    Returns the user-data as returned by the Machine object
    """

    def get(self):
        self.write(self.request.machine.get_userdata())

class PublicKeysHandler(ApiBaseHandler):
    """
    Handles calls to
        /<version>/meta-data/public-keys
        /<version>/meta-data/public-keys/
        /<version>/meta-data/public-keys/<number>
        /<version>/meta-data/public-keys/<number>/
        /<version>/meta-data/public-keys/<number>/<key_format>

    See inline documentation for behaviour specification
    """

    def get(self, number=None, key_format=None):
        if not number is None:
            number = int(number)

        if number is None and key_format is None:
            # if nothing was given, list the key number + key names as returned by the Machine object's get_keys() call

            keys = ["%d=%s" % (i, key_name) for i, key_name in enumerate(self.request.machine.get_keys())]

            self.write("\n".join(keys))
        elif key_format is None:
            # if only a number was given, list the valid formats for this key number

            key = self.request.machine.get_keys().values()[number]

            self.write("\n".join(key.keys()))
        else:
            # if both a number and a format were given, return the key in the requested format

            key = self.request.machine.get_keys().values()[number]

            self.write(key[key_format])
