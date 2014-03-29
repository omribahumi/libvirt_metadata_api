#!/usr/bin/env python
import tornado.ioloop
import tornado.web
import tornado.httpserver
import libvirt
import logging
import argparse
import utils
import handlers


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=1024)
    parser.add_argument('-c', '--connect', dest='libvirt_connection_string', default='qemu:///system')
    parser.add_argument('--enable-xheaders', default=False, action='store_true')
    args = parser.parse_args()

    application = tornado.web.Application(
        [
            (r"/", handlers.ApiRootHandler),
            (r"/[^\/]+", handlers.NullHandler),  # so we don't return 404 on this
            (r"/[^\/]+/", handlers.ApiVersionRootHandler),
            (r"/[^\/]+/meta-data", handlers.NullHandler),
            (r"/[^\/]+/meta-data/", handlers.MetadataHandler),  # so we don't return 404 on this
            (r"/[^\/]+/meta-data/instance-id", handlers.InstanceIdHandler),
            (r"/[^\/]+/meta-data/local-ipv4", handlers.LocalIpv4Handler),
            (r"/[^\/]+/meta-data/public-ipv4", handlers.PublicIpv4Handler),
            (r"/[^\/]+/meta-data/public-keys/?", handlers.PublicKeysHandler),
            (r"/[^\/]+/meta-data/public-keys/(?P<number>\d+)/?", handlers.PublicKeysHandler),
            (r"/[^\/]+/meta-data/public-keys/(?P<number>\d+)/(?P<key_format>[^/]+)", handlers.PublicKeysHandler),
            (r"/[^\/]+/user-data/?", handlers.UserDataHandler)
        ],
        machine_resolver=utils.machine_resolver.LibvirtMachineResolver(
            libvirt.openReadOnly(args.libvirt_connection_string))
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.xheaders = args.enable_xheaders
    http_server.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
