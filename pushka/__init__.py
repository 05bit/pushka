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
"""Push notifications, SMS, and emails.

Runs on top of asyncio, so Python 3.3+ is required. Supported services:

- Email: Amazon SES
- SMS: Twilio
- Push notifications: Parse (deprecated)

Quickstart
----------

If you are new to asyncio, please read some intro on it first! And here's a
basic example for sending notification via Parse::

    >>> import asyncio
    >>> import pushka
    >>> parse_app_id = '***' # Paste real APP ID here
    >>> parse_api_key = '***' # Paste real Rest API key here
    >>> token = '***' # Paste device token here
    >>> device_type = 'ios' # Or 'android'
    >>> loop = asyncio.get_event_loop()
    >>> run = loop.run_until_complete # Shortcut
    >>> push = pushka.ParsePushService(parse_app_id, parse_api_key, asyncio_loop=loop)
    >>> run(push.add_target(token=token, device_type=device_type))
    >>> run(push.send(token=token, device_type=device_type, alert="La-la-la!"))

.. _Twilio: https://www.twilio.com
.. _Parse: https://parse.com

"""

__version__  = '0.1.0'

from .base import (
    BaseService,
    BasePushService,
    BaseMailService,
    BaseSMSService,
)

from ._providers.parse import ParsePushService
from ._providers.twilio import TwilioSMSService
from ._providers.ses import AmazonSESService

__all__ = (
    'BaseService',
    'BasePushService',
    'BaseMailService',
    'BaseSMSService',

    'ParsePushService',
    'TwilioSMSService',
    'AmazonSESService',
)
