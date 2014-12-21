import re
import json
from handlers import routes, ApiBaseHandler, NullHandler, ApiVersionRootHandler


class ExampleAdditionalHandler(ApiBaseHandler):
    """
    Handles calls to:
        /<version>/example/

    Lists supported API calls by walking the URLSpecs for this application
    """

    def get(self):
        urls = []

        for urlspec in self.application.handlers[0][1]:
            if '/example/' in urlspec.regex.pattern and not urlspec.regex.pattern.endswith('/example/$'):
                match = re.search(r'/example/([^/]+/?)\??\$$', urlspec.regex.pattern)
                if match:
                    urls.append(match.group(1))

        self.write("\n".join(urls))


class ExampleTagsHandler(ApiBaseHandler):
    def get(self):
        additional_metadata = self.request.machine.get_additional_metadata()

        self.write(
            json.dumps(additional_metadata.get('tags', []) if additional_metadata else [])
        )

ApiVersionRootHandler.apis += ['example']

routes += [
    (r"/[^\/]+/example", NullHandler),
    (r"/[^\/]+/example/", ExampleAdditionalHandler),
    (r"/[^\/]+/example/tags", ExampleTagsHandler)
]