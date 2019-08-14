#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""httprint - print files via web

Copyright 2019 Davide Alberani <da@mimante.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import time
import random
import asyncio
import logging
import subprocess
import multiprocessing as mp

from tornado.ioloop import IOLoop
import tornado.httpserver
import tornado.options
from tornado.options import define, options
import tornado.web
from tornado import gen, escape


API_VERSION = '1.0'
UPLOAD_PATH = 'uploads'
PRINT_CMD = ['lp']
PROCESS_TIMEOUT = 60
ENCODING = 'utf-8'

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class HTTPrintBaseException(Exception):
    """Base class for httprint custom exceptions.

    :param message: text message
    :type message: str
    :param status: numeric http status code
    :type status: int"""
    def __init__(self, message, status=400):
        super(HTTPrintBaseException, self).__init__(message)
        self.message = message
        self.status = status


class BaseHandler(tornado.web.RequestHandler):
    """Base class for request handlers."""
    # A property to access the first value of each argument.
    arguments = property(lambda self: dict([(k, v[0].decode('utf-8'))
                                            for k, v in self.request.arguments.items()]))

    @property
    def clean_body(self):
        """Return a clean dictionary from a JSON body, suitable for a query on MongoDB.

        :returns: a clean copy of the body arguments
        :rtype: dict"""
        return escape.json_decode(self.request.body or '{}')

    def write_error(self, status_code, **kwargs):
        """Default error handler."""
        if isinstance(kwargs.get('exc_info', (None, None))[1], HTTPrintBaseException):
            exc = kwargs['exc_info'][1]
            status_code = exc.status
            message = exc.message
        else:
            message = 'internal error'
        self.build_error(message, status=status_code)

    def initialize(self, **kwargs):
        """Add every passed (key, value) as attributes of the instance."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def build_error(self, message='', status=400):
        """Build and write an error message.

        :param message: textual message
        :type message: str
        :param status: HTTP status code
        :type status: int
        """
        self.set_status(status)
        self.write({'error': True, 'message': message})

    def build_success(self, message='', status=200):
        """Build and write a success message.

        :param message: textual message
        :type message: str
        :param status: HTTP status code
        :type status: int
        """
        self.set_status(status)
        self.write({'error': False, 'message': message})

    def _run(self, cmd):
        p = subprocess.Popen(cmd, close_fds=True)
        p.communicate()

    def run_subprocess(self, cmd):
        """Execute the given action.

        :param cmd: the command to be run with its command line arguments
        :type cmd: list
        """
        p = mp.Process(target=self._run, args=(cmd,))
        p.start()

class UploadHandler(BaseHandler):
    """Reset schedules handler."""
    @gen.coroutine
    def post(self):
        if not self.request.files.get('file'):
            self.build_error("no file uploaded")
            return
        fileinfo = self.request.files['file'][0]
        webFname = fileinfo['filename']
        extension = ''
        try:
            extension = os.path.splitext(webFname)[1]
        except Exception:
            pass
        if not os.path.isdir(UPLOAD_PATH):
            os.makedirs(UPLOAD_PATH)
        fname = '%s-%s%s' % (
            time.strftime('%Y%m%d%H%M%S'),
            '%04d' % random.randint(0, 9999),
            extension)
        pname = os.path.join(UPLOAD_PATH, fname)
        try:
            with open(pname, 'wb') as fd:
                fd.write(fileinfo['body'])
        except Exception as e:
            self.build_error("error writing file %s: %s" % (pname, e))
            return
        try:
            with open(pname + '.info', 'w') as fd:
                fd.write('originale file name: %s\n' % webFname)
        except Exception:
            pass
        cmd = PRINT_CMD + [pname]
        self.run_subprocess(cmd)
        self.build_success("file sent to printer")


class TemplateHandler(BaseHandler):
    """Handler for the template files in the / path."""
    @gen.coroutine
    def get(self, *args, **kwargs):
        """Get a template file."""
        page = 'index.html'
        if args and args[0]:
            page = args[0].strip('/')
        arguments = self.arguments
        self.render(page, **arguments)


def serve():
    """Read configuration and start the server."""
    define('port', default=7777, help='run on the given port', type=int)
    define('address', default='', help='bind the server at the given address', type=str)
    define('ssl_cert', default=os.path.join(os.path.dirname(__file__), 'ssl', 'httprint_cert.pem'),
            help='specify the SSL certificate to use for secure connections')
    define('ssl_key', default=os.path.join(os.path.dirname(__file__), 'ssl', 'httprint_key.pem'),
            help='specify the SSL private key to use for secure connections')
    define('debug', default=False, help='run in debug mode', type=bool)
    tornado.options.parse_command_line()

    if options.debug:
        logger.setLevel(logging.DEBUG)

    ssl_options = {}
    if os.path.isfile(options.ssl_key) and os.path.isfile(options.ssl_cert):
        ssl_options = dict(certfile=options.ssl_cert, keyfile=options.ssl_key)

    init_params = dict(listen_port=options.port, logger=logger, ssl_options=ssl_options)

    _upload_path = r'upload/?'
    application = tornado.web.Application([
            (r'/api/%s' % _upload_path, UploadHandler, init_params),
            (r'/api/v%s/%s' % (API_VERSION, _upload_path), UploadHandler, init_params),
            (r'/?(.*)', TemplateHandler, init_params),
        ],
        static_path=os.path.join(os.path.dirname(__file__), 'dist/static'),
        template_path=os.path.join(os.path.dirname(__file__), 'dist/'),
        debug=options.debug)
    http_server = tornado.httpserver.HTTPServer(application, ssl_options=ssl_options or None)
    logger.info('Start serving on %s://%s:%d', 'https' if ssl_options else 'http',
                                                 options.address if options.address else '127.0.0.1',
                                                 options.port)
    http_server.listen(options.port, options.address)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    serve()
