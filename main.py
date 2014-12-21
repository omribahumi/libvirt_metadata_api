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
    parser.add_argument('--plugin', action='append', help='Load this plugin. This simply imports the module. ' +
                                                          'See example for more details')
    args = parser.parse_args()

    if args.plugin:
        for plugin in args.plugin:
            __import__(plugin)

    application = tornado.web.Application(
        handlers.routes,
        machine_resolver=utils.machine_resolver.LibvirtMachineResolver(
            libvirt.openReadOnly(args.libvirt_connection_string))
    )

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.xheaders = args.enable_xheaders
    http_server.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
