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
"""Twilio async SMS sender.
"""
import logging
import asyncio
import json
from .. import base


class TwilioSMSService(base.BaseSMSService):
    """Twilio powered SMS sender, subclass of :class:`.BaseSMSService`

    Args:
        loop: asyncio event loop or Tornado IOLoop
        account (str): Twilio account identifier
        token (str): Twilio secret token
        default_sender (str): Default sender phone number

    """
    url = 'https://api.twilio.com/2010-04-01/Accounts/{account}/Messages.json'

    def __init__(self, *, loop, account, token, default_sender=None):
        super().__init__(loop=loop, default_sender=default_sender)
        self._account = account
        self._token = token
        self._http = self.new_http_client()

    @asyncio.coroutine
    def send_sms(self, *, text, recipients, sender=None):
        """Send SMS asynchronously.

        See :meth:`.BaseSMSService.send_sms` docs for
        parameters reference.

        """
        answers = []
        url = self.url.format(account=self._account)
        recipients = [recipients] if isinstance(recipients, str) else recipients

        for to_phone in recipients:
            data = {
                'To': to_phone.startswith('+') and to_phone or ('+%s' % to_phone),
                'From': sender or self.default_sender,
                'Body': text,
            }

            result = yield from self._http.post(
                url, data=data, auth=(self._account, self._token))

            answers.append(result)

        return answers
