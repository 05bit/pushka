# Copyright 2015 Alexey Kinev <rudy@05bit.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import configparser
import json
import os
import unittest
import logging

try:
    import tornado
    import tornado.platform.asyncio
    import tornado.testing
    from tornado.ioloop import IOLoop
except ImportError:
    tornado = None

try:
    import aiohttp
except ImportError:
    aiohttp = None

import pushka

CONFIG = {}


#####################
# Commons for tests #
#####################

def setUpModule():
    try:
        ini_path = os.path.join(os.path.dirname(__file__), 'tests.ini')
        ini_data = configparser.ConfigParser()
        ini_data.read([ini_path])
        CONFIG.update(ini_data['tests'])
    except KeyError:
        logging.warning("Can't read config from tests.ini")


def set_up_config(test):
    test.push_token = None
    test.mail_to = None

    if 'push_token' in CONFIG:
        test.push_token = CONFIG['push_token']

    if ('mail_to' in CONFIG) and ('mail_from' in CONFIG):
        test.mail_to = CONFIG['mail_to'].split(',')
        test.mail_from = CONFIG['mail_from']


def create_parse(loop):
    if 'parse_app_id' in CONFIG:
        return pushka.ParsePushService(
            app_id=CONFIG['parse_app_id'],
            api_key=CONFIG['parse_app_key'],
            loop=loop)


def create_twilio(loop):
    if 'twilio_account' in CONFIG:
        return pushka.TwilioSMSService(
            account=CONFIG['twilio_account'],
            token=CONFIG['twilio_token'],
            loop=loop)


def create_ses(loop):
    if 'ses_access_id' in CONFIG:
        return pushka.AmazonSESService(
            access_id=CONFIG['ses_access_id'],
            secret_key=CONFIG['ses_secret_key'],
            loop=loop)


@asyncio.coroutine
def send_sms(test):
    result = yield from test.sms.send_sms(text="Hello!",
                                          recipients=[CONFIG['twilio_to']],
                                          sender=CONFIG['twilio_sender'])
    test.assertEqual(result[0]['code'], 201)


@asyncio.coroutine
def register_and_send_push(test):
    # Register device
    register = yield from test.push_service.add_target(token=test.push_token,
                                                       device_type=CONFIG['push_device'])
    test.assertEqual(register['code'], 201)

    # Send notification
    resp = yield from test.push_service.send_push(token=test.push_token,
                                                  device_type=CONFIG['push_device'],
                                                  alert=CONFIG['push_alert'],
                                                  sound=CONFIG['push_sound'])
    
    test.assertEqual(resp['code'], 200)
    test.assertTrue('result' in json.loads(resp['body']))


@asyncio.coroutine
def send_mail(test):
    resp = yield from test.ses.send_mail(
        text="La-la-la", subject="Test", recipients=test.mail_to,
        sender=test.mail_from)

    test.assertEqual(resp['code'], 200)


#########################
# aiohttp powered tests #
#########################

if aiohttp:
    import pushka._http.aio


    class BaseAioTestCase(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.loop = asyncio.new_event_loop()

        def setUp(self):
            super().setUp()
            set_up_config(self)

        def run_coroutine(self, coroutine):
            return self.loop.run_until_complete(coroutine)


    class HTTPAioTestCase(BaseAioTestCase):
        def setUp(self):
            super().setUp()
            self.client = pushka._http.aio.AioHTTPClient(self.loop)

        def test_get_method(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.get('http://httpbin.org/get')
                self.assertEqual(result['code'], 200)

            self.run_coroutine(test())

        def test_get_404(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.get('http://httpbin.org/status/404')
                self.assertEqual(result['code'], 404)

            self.run_coroutine(test())

        def test_post_method(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.post('http://httpbin.org/post', data={})
                self.assertEqual(result['code'], 200)

            self.run_coroutine(test())


    class ParseAioTestCase(BaseAioTestCase):
        """Test Parse on Tornado.
        """
        def setUp(self):
            super().setUp()
            self.push_service = create_parse(self.loop)

            if not self.push_service:
                self.skipTest("Parse not configured")
            elif not self.push_token:
                self.skipTest("No push token")

        def test_register_and_send_push(self):
            self.run_coroutine(register_and_send_push(self))


    class TwilioAioTestCase(BaseAioTestCase):
        """Test Twilio on aiohttp.
        """
        def setUp(self):
            super().setUp()
            self.sms = create_twilio(self.loop)

            if not self.sms:
                self.skipTest("Twilio not configured")

        def test_register_and_send_push(self):
            self.run_coroutine(send_sms(self))


    class SesAioTestCase(BaseAioTestCase):
        """Test SES on aiohttp.
        """
        def setUp(self):
            super().setUp()
            self.ses = create_ses(self.loop)

            if not self.ses:
                self.skipTest("Amazon SES not configured")

        def test_send_mail(self):
            self.run_coroutine(send_mail(self))


#########################
# Tornado powered tests #
#########################

if tornado:
    import pushka._http.tornado
    
    IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')


    class BaseTornadoTestCase(tornado.testing.AsyncTestCase):
        def setUp(self):
            super().setUp()
            set_up_config(self)
            self.aio_loop = self.io_loop.asyncio_loop

        def run_coroutine(self, coroutine):
            """ Run coroutine on specified loop and set result
            to Tornado's Future object.
            """
            future = tornado.concurrent.Future()

            @asyncio.coroutine
            def run():
                try:
                    result = yield from coroutine
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)

            self.aio_loop.create_task(run())

            return future

    
    class HTTPTornadoTestCase(BaseTornadoTestCase):
        def setUp(self):
            super().setUp()
            self.client = pushka._http.tornado.TornadoHTTPClient(self.io_loop)

        @tornado.testing.gen_test
        def test_get_method(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.get('http://httpbin.org/get')
                self.assertEqual(result['code'], 200)

            yield self.run_coroutine(test())

        @tornado.testing.gen_test
        def test_get_404(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.get('http://httpbin.org/status/404')
                self.assertEqual(result['code'], 404)

            yield self.run_coroutine(test())

        @tornado.testing.gen_test
        def test_post_method(self):
            @asyncio.coroutine
            def test():
                result = yield from self.client.post('http://httpbin.org/post', data={})
                self.assertEqual(result['code'], 200)

            yield self.run_coroutine(test())


    class ParseTornadoTestCase(BaseTornadoTestCase):
        """
        Test Parse service client on Tornado.
        """
        def setUp(self):
            super().setUp()
            self.push_service = create_parse(self.io_loop)

            if not self.push_service:
                self.skipTest("Parse not configured")
            elif not self.push_token:
                self.skipTest("No push token")

        @tornado.testing.gen_test
        def test_register_and_send_push(self):
            yield self.run_coroutine(register_and_send_push(self))


    class TwilioTornadoTestCase(BaseTornadoTestCase):
        """Test Twilio on Tornado.
        """
        def setUp(self):
            super().setUp()
            self.sms = create_twilio(self.io_loop)

            if not self.sms:
                self.skipTest("Twilio not configured")

        @tornado.testing.gen_test
        def test_register_and_send_push(self):
            yield self.run_coroutine(send_sms(self))


    class SesTornadoTestCase(BaseTornadoTestCase):
        """Test SES on Tornado.
        """
        def setUp(self):
            super().setUp()
            self.ses = create_ses(self.io_loop)

            if not self.ses:
                self.skipTest("Amazon SES not configured")

        @tornado.testing.gen_test
        def test_send_mail(self):
            yield self.run_coroutine(send_mail(self))


if __name__ == '__main__':
    unittest.main()
