"""
Simple wrapper for Tornado AsyncHTTPClient for using with asyncio event loop.
"""
import asyncio
import urllib.parse
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.ioloop import IOLoop

from . import base
from . import utils


class TornadoHTTPClient(base.BaseHTTPClient):
    def __init__(self, loop=None):
        """Create async HTTP client that runs on specified Tornado IOLoop.

        loop -- Tornado IOLoop that runs on asyncio event loop.
        """
        super().__init__()

        if not loop:
            loop = IOLoop.instance()

        self._asyncio_loop = loop.asyncio_loop
        self._client = AsyncHTTPClient(loop)

    @asyncio.coroutine
    def _request(self, url_, method_, params=None, data=None, **kwargs):
        """Perform request with Tornado's async HTTP client and return result
        wrapped with `asyncio.Future`.
        """
        request = HTTPRequest(utils.merge_url(url_, params),
                              method=method_, body=utils.encode_body(data),
                              **utils.norm_tornado_kwargs(**kwargs))

        # Async fetch request
        future = asyncio.Future(loop=self._asyncio_loop)
        def on_fetch(resp):
            future.set_result(resp)

        try:
            self._client.fetch(request, on_fetch)
        except Exception as e:
            future.set_exception(e)

        # Wrap result
        return self._result((yield from future))

    def _result(self, result):
        """Wrap HTTPResponse to simple dict.

        Result `dict` format::

            {
                'code': int response code,
                'body': str result,
                'error': dict with errors
            }
        """
        return {
            'code': result.code,
            'body': result.body.decode('utf-8') if result.body else '',
            'error': result.error,
        }
