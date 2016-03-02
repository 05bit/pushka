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
"""Parse async client.
"""
import asyncio
import json
from .. import base


class ParsePushService(base.BasePushService):
    """Push notifications sender, which uses `Parse`_ service.

    Args:
        loop: asyncio event loop or Tornado IOLoop
        app_id: Parse application ID
        api_key: Parse Rest API key for application

    .. _Parse: https://parse.com
    """
    base_url = 'https://api.parse.com/1/'

    def __init__(self, *, loop, app_id, api_key, gcm_sender_id):
        super().__init__(loop=loop)

        self._http = self.new_http_client()
        self._headers = {
            'X-Parse-Application-Id': app_id,
            'X-Parse-REST-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        self._gcm_sender_id = gcm_sender_id and str(gcm_sender_id)

    @asyncio.coroutine
    def add_target(self, *, token, device_type, tags=None):
        """Register device token at `Parse`_ service.

        See :meth:`.BasePushService.add_target` method docs for
        parameters reference.

        .. _Parse: https://parse.com
        """
        url = ''.join((self.base_url, 'installations'))

        data = {
            'deviceType': device_type,
            'deviceToken': token,
            'channels': tags if tags else [],
        }

        if device_type == 'android':
            if self._gcm_sender_id:
                data.update({
                    'pushType': 'gcm',
                    'GCMSenderId': self._gcm_sender_id,
                })
            else:
                raise ValueError("Provide `gcm_sender_id` to enable "
                                 "Android devices support.")

        return (yield from self._http.post(url, data=json.dumps(data),
                                           headers=self._headers))

    @asyncio.coroutine
    def send_push(self, *, alert, device_type, token=None, tags=None,
                  badge=None, sound=None, title=None):
        """Send push notification via `Parse`_ service.

        See :meth:`.BasePushService.send_push` method docs
        for parameters reference.

        .. _Parse: https://parse.com
        """
        url = ''.join((self.base_url, 'push'))
        data = {'data': {'alert': alert}}

        # Message
        msg = data['data']
        if title:
            msg['title'] = title
        if sound:
            msg['sound'] = sound
        if badge:
            msg['badge'] = badge

        # Device query
        if token:
            data['where'] = {'deviceToken': token}
        elif tags:
            data['channels'] = tags
        else:
            data['where'] = {'deviceType': device_type}

        # Request
        return (yield from self._http.post(url, data=json.dumps(data),
                                           headers=self._headers))
