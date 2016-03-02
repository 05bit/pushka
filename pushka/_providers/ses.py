# Copyright 2011 The greplin-tornado-ses Authors
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
"""Amazon SES async client.
"""
import asyncio
import hmac
import hashlib
import base64
import urllib.parse
import logging
from datetime import datetime
from .. import base

logger = logging.getLogger('pushka.mail')


class AmazonSESService(base.BaseMailService):
    """Amazon SES API client.

    The client uses `SendEmail` method, so user's policy must grant
    `ses:SendEmail` permission.
    """
    DEFAULT_BASE_URL = 'https://email.us-east-1.amazonaws.com'

    def __init__(self, access_id, secret_key, base_url=None,
                 loop=None, default_sender=None):
        super().__init__(loop=loop, default_sender=default_sender)
        self._access_id = access_id
        self._secret_key = secret_key
        self._base_url = base_url or self.DEFAULT_BASE_URL
        self._http = self.new_http_client()

    def _sign(self, message):
        """Sign an AWS request"""
        signed_hash = hmac.new(key=self._secret_key.encode('utf-8'),
                               msg=message.encode('utf-8'),
                               digestmod=hashlib.sha256)
        return base64.b64encode(signed_hash.digest()).decode()

    @asyncio.coroutine
    def _ses_call(self, action, data=None):
        """Make a call to SES.
        """
        params = data or {}
        params['Action'] = action
        now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Date': now,
            'X-Amzn-Authorization': 'AWS3-HTTPS AWSAccessKeyId=%s, '
                                    'Algorithm=HMACSHA256, Signature=%s' % (
                                        self._access_id, self._sign(now))}
        return (yield from self._http.post(
            self._base_url,
            data=urllib.parse.urlencode(params),
            headers=headers))

    @asyncio.coroutine
    def send_mail(self, text=None, subject='', recipients=None, sender=None,
                  html=None, attachments=None, reply_to=None,
                  cc=None, bcc=None, return_path=None, **kwargs):
        """Compose and send mail coroutine.
        """
        if not (text or html):
            raise TypeError("Either `text` or `html` argument"
                            "should be provided")

        message = {
            'Source': sender or self.default_sender,
            'Message.Subject.Data': subject
        }
        if text:
            message['Message.Body.Text.Data'] = text
        if html:
            message['Message.Body.Html.Data'] = html
        if return_path:
            message['ReturnPath'] = return_path

        params = ListParameterContainer()
        params['Destination.ToAddresses.member'] = recipients
        if cc:
            params['Destination.CcAddresses.member'] = cc
        if bcc:
            params['Destination.BccAddresses.member'] = bcc
        if reply_to:
            params['ReplyToAddresses.member'] = reply_to

        response = yield from self._ses_call('SendEmail',
                                             dict(message, **params))

        if not (200 <= response['code'] < 300):
            response['error'] = response['body']
            response['body'] = ''
            logging.warning(response['error'])

        return response


class ListParameterContainer(dict):
    """Build a parameters list as required by Amazon SES.
    """
    def __setitem__(self, key, value):
        if isinstance(value, str):
            value = [value]
        for i in range(1, len(value) + 1):
            dict.__setitem__(self, '%s.%d' % (key, i), value[i - 1])
