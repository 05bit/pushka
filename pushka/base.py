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
"""Base classes for SMS, email, push notifications senders.
"""
import asyncio


class BaseService:
    """Base sender service class.

    Args:
        loop: asyncio event loop or Tornado IOLoop

    """
    def __init__(self, *, loop):
        self.loop = loop

        try:
            _BaseEventLoop = asyncio.BaseEventLoop
        except AttributeError:
            _BaseEventLoop = asyncio.AbstractEventLoop

        self.is_asyncio = isinstance(loop, _BaseEventLoop)

    def new_http_client(self):
        """Create new http client.

        If service is running on Tornado IOLoop, then
        `tornado.httpclient.AsyncHTTPClient`_ is used. When asyncio event
        loop is specified `aiohttp`_ client is used, in that case aiohttp
        library is required to be installed.

        .. _aiohttp: http://aiohttp.readthedocs.org
        .. _tornado.httpclient.AsyncHTTPClient: http://tornado.readthedocs.org/en/latest/httpclient.html

        """
        if self.is_asyncio:
            from ._http.aio import AioHTTPClient
            return AioHTTPClient(loop=self.loop)
        else:
            from ._http.tornado import TornadoHTTPClient
            return TornadoHTTPClient(loop=self.loop)            


class BasePushService(BaseService):
    """Push notifications sender interface class mixin.

    Provides empty methods for push notifications sender, which should
    be implemented in subclasses.

    Usage example::

        from pushka import BasePushService

        class ParsePushService(BasePushService):
            \"\"\"Send push notifications via Parse service.\"\"\"
            @asyncio.coroutine
            def send_push(self, token=None, device_type=None, tags=None,
                          alert=None, badge=None, sound=None, **kwargs):
                do_something()
                # ...

    """
    @asyncio.coroutine
    def add_target(self, token=None, device_type=None, tags=None):
        """Register target device push token. Coroutine."""
        raise NotImplementedError

    @asyncio.coroutine
    def del_target(self, token=None, device_type=None, tags=None):
        """Unregister target device push token. Coroutine."""
        raise NotImplementedError

    @asyncio.coroutine
    def add_tags(self, token=None, tags=None):
        """Add tags for registered device token, it may also be considered as
        subscribing to channel. Returns updated list of tags. Coroutine.

        """
        raise NotImplementedError

    @asyncio.coroutine
    def get_tags(self, token=None, tags=None):
        """Get tags for registered device token. Returns list of tags.
        Coroutine.

        """
        raise NotImplementedError

    @asyncio.coroutine
    def del_tags(self, token=None, tags=None):
        """Remove tags for registered device token, it may also be considered as
        unsubscribing from channel. Returns updated list of tags. Coroutine.

        """
        raise NotImplementedError

    @asyncio.coroutine
    def send_push(self, token=None, device_type=None, tags=None,
                  alert=None, badge=None, sound=None, **kwargs):
        """Send push message to single or multiple devices specified by
        filtering options. Coroutine.

        Args:
            token (str): Device token string
            device_type (str): Device type: 'ios' / 'android'
            tags (list): List of string tags / channels

            alert (str): Notification alert text
            badge (int, optional): Application badge number to set
            sound (str, optional): Sound name to play, use 'default' for system sound

        """
        raise NotImplementedError


class BaseMailService(BaseService):
    """Email sender base class.

    Provides empty method for email sender, which should be implemented
    in subclasses.

    Args:
        loop: asyncio event loop or Tornado IOLoop
        default_sender (str): default sender's email address

    Usage example::

        from pushka import BaseMailService

        class SESMailService(BaseMailService):
            \"\"\"Send email via Amazon SES service.\"\"\"
            @asyncio.coroutine
            def send_mail(self, subject='', body=None, recipients=None, sender=None,
                          html=None, attachments=None, reply_to=None,
                          cc=None, bcc=None, **kwargs):
                do_something()
                # ...

    """
    def __init__(self, *, loop, default_sender=None):
        super().__init__(loop=loop)
        self.default_sender = default_sender

    @asyncio.coroutine
    def send_mail(self, text=None, subject='', recipients=None, sender=None,
                  html=None, attachments=None, reply_to=None,
                  cc=None, bcc=None, return_path=None, **kwargs):
        """Send email message. Coroutine.

        Args:
            text (str): Plain text message in UTF-8 encoding
            subject (str): Subject string, must be single line string
            recipients (list): List of recipients email adresses
            
            sender (str, optional): Sender address or default will be used
            html (str, optional): HTML message in UTF-8 encoding
            reply_to (str, optional): Reply-to address
            cc (str, optional): Cc list
            bcc (str, optional): Bcc list

        """
        raise NotImplementedError


class BaseSMSService(BaseService):
    """SMS sender base class.

    Provides empty method for SMS sender, which should be implemented
    in subclasses.

    Args:
        loop: asyncio event loop or Tornado IOLoop
        default_sender (str): default sender's phone number

    Usage example::

        from pushka import BaseSMSService

        class TwilioSMSService(BaseSMSService):
            \"\"\"Send SMS via Twilio service.\"\"\"
            @asyncio.coroutine
            def send_sms(self, text=None, recipients=None, sender=None):
                ...

    """
    def __init__(self, *, loop, default_sender=None):
        super().__init__(loop=loop)
        self.default_sender = default_sender

    @asyncio.coroutine
    def send_sms(self, *, text, recipients, sender=None):
        """Send SMS. Coroutine.

        Args:
            text (str): Plain text message in UTF-8 encoding
            recipients (list): List of recipients phone numbers in format ['+13334445577', ...]
            sender (str): Sender phone number or default one will be used

        """
        raise NotImplementedError
