import asyncio
import aiohttp
from . import base
from . import utils


class AioHTTPClient(base.BaseHTTPClient):
    """Simple `aiohttp` wrapper for basic compatibility
    with `tornado.httpclient.AsyncHTTPClient`.
    """
    def __init__(self, loop=None):
        super().__init__()
        self._loop = loop

    @asyncio.coroutine
    def _request(self, url_, method_, params=None, data=None, **kwargs):
        """Perform request via `aiohttp.request`_.

        .. _aiohttp.request: http://aiohttp.readthedocs.org/en/v0.9.2/client.html#make-a-request
        """
        response = yield from aiohttp.request(method_.lower(), url_,
                                              params=params, data=data, loop=self._loop,
                                              **utils.norm_aiohttp_kwargs(**kwargs))
        return {
            'code': response.status,
            'body': (yield from response.text()),
            'error': None, # TODO: how errors statues are described in aiohttp?
        }
