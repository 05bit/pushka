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
"""Push notifications, SMS, and emails on top of asyncio.

Supported services:

- Email: Amazon SES
- SMS: Twilio
- Push notifications: Parse (deprecated)

Install
-------

The easiest way is install via pip::

    pip install pushka

Quickstart
----------

If you are new to asyncio, please read some intro on it first! And here's a
basic example for sending email message via Amazon SES::

    import asyncio
    import pushka

    # NOTE: client uses `SendEmail` method, so user's policy must grant
    # `ses:SendEmail` permission.
    access_id='***' # Amazon SES access ID
    secret_key='***' # Amazon SES secret key

    mail_to = ['to@example.com'] # Some email to receive mail
    mail_from = 'from@example.com' # Sender's email address

    loop = asyncio.get_event_loop()
    run = loop.run_until_complete

    mailer = AmazonSESService(
        access_id=access_id,
        secret_key=secret_key,
        loop=loop)

    run(mailer.send_mail(
            text="Some text",
            subject="Some subject",
            recipients=mail_to,
            sender=mail_from))

.. _AmazonSES: https://aws.amazon.com/ses/
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
