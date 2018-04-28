#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of restful-distributed-lock-manager released under the MIT license.
# See the LICENSE file for more information.

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

import functools
import logging
import signal
import time
import os.path

from rdlm.options import Options
from rdlm.hello_handler import HelloHandler
from rdlm.locks_handler import LocksHandler
from rdlm.lock_handler import LockHandler
from rdlm.resource_handler import ResourceHandler
from rdlm.resources_handler import ResourcesHandler
from rdlm.lock import LOCK_MANAGER_INSTANCE
from rdlm.hello_handler import AddResourceHandler
from rdlm.hello_handler import ShowAllResourcesHandler
from rdlm.hello_handler import ShowResourceHandler
from rdlm.hello_handler import RemoveResourceHandler
from rdlm.hello_handler import RequestLockHandler
from rdlm.hello_handler import ReleaseLockHandler


def on_every_second():
    '''
    @summary: function called by tornado/ioloop every second

    It's used to clear expired locks
    '''
    LOCK_MANAGER_INSTANCE.clean_expired_locks()


def get_app():
    '''
    @summary: returns the tornado application
    @param unit_testing: if True, we add some handler for unit testing only
    @result: the tornado application
    '''
    url_list = [
        tornado.web.URLSpec(r"/", HelloHandler, name="index"),
        tornado.web.URLSpec(r"/resources/([a-zA-Z0-9]+)", ResourceHandler, name="resource"),
        tornado.web.URLSpec(r"/resources", ResourcesHandler, name="resources"),
        tornado.web.URLSpec(r"/locks/([a-zA-Z0-9]+)", LocksHandler, name="locks"),
        tornado.web.URLSpec(r"/locks/([a-zA-Z0-9]+)/([a-zA-Z0-9]+)", LockHandler, name="lock"),
        tornado.web.URLSpec(r"/addresource", AddResourceHandler, name="addresources"),
        tornado.web.URLSpec(r"/showallresources", ShowAllResourcesHandler, name="showallresources"),
        tornado.web.URLSpec(r"/showresource/([a-zA-Z0-9]+)", ShowResourceHandler, name="showresource"),
        tornado.web.URLSpec(r"/removeresource", RemoveResourceHandler, name="removeresource"),
        tornado.web.URLSpec(r"/requestlock", RequestLockHandler, name="requestlock"),
        tornado.web.URLSpec(r"/releaselock", ReleaseLockHandler, name="releaselock")
    ]
    settings = dict(
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static")
    )
    application = tornado.web.Application(url_list, **settings)
    return application


def get_ioloop():
    '''
    @summary: returns a configured tornado ioloop
    '''
    iol = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(on_every_second, 1000, iol).start()
    return iol


def log_is_ready():
    '''
    @summary: simple callback just to log that the daemon is ready
    '''
    logging.info("RDLM daemon is ready !")


def sigterm_handler(server, loop, signum, frame):
    logging.info("SIGTERM signal catched => scheduling webserver stop...")
    loop.add_callback(functools.partial(stop_server, server, loop))


def stop_server(server, loop):
    logging.info("Stopping webserver...")
    server.stop()
    if loop:
        logging.info("Webserver stopped => scheduling main loop stop...")
        loop.add_timeout(time.time() + 5, functools.partial(stop_loop, loop))
    else:
        logging.info("Webserver stopped !")


def stop_loop(loop):
    logging.info("Stopping main loop...")
    loop.stop()
    logging.info("Main loop stopped !")


def main():
    '''
    @summary: main function (starts the daemon)
    '''
    application = get_app()
    tornado.options.parse_command_line()
    server = HTTPServer(application)
    server.listen(Options.port())
    iol = get_ioloop()
    iol.add_callback(log_is_ready)
    signal.signal(signal.SIGTERM, lambda s, f: sigterm_handler(server, iol, s, f))
    try:
        iol.start()
    except KeyboardInterrupt:
        stop_server(server, None)
    logging.info("RDLM daemon is stopped !")


if __name__ == '__main__':
    main()
