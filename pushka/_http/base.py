import asyncio


class BaseHTTPClient:
    """Simple abstract async HTTP client.

    We use this interface to have ability of switching between
    `AsyncHTTPClient` from Tornado and asyncio powered `aiohttp`.

    Provides HTTP methods calls as coroutines:

        get(url, params=None, **kwargs)
        post(url, params=None, **kwargs)
        put(url, params=None, data=None, **kwargs)
        delete(url, params=None, data=None, **kwargs)

    Args:
        url (str): request URL
        params (dict): query parameters added to URL
        data: dict or raw data for request body

    Keyword Args:
        auth: Authentication data, for basic auth (login, password) tuple
        headers: Custom headers

    Other keyword arguments are not normalized for different HTTP clients
    and should not be used! If you need it, you may need to update
    :func:`.utils.norm_tornado_kwargs` and :func:`.utils.norm_aiohttp_kwargs`.

    """
    @asyncio.coroutine
    def get(self, url, params=None, **kwargs):
        return self._request(url, 'GET', params=params, **kwargs)

    @asyncio.coroutine
    def post(self, url, params=None, data=None, **kwargs):
        return self._request(url, 'POST', data=(data if data else {}),
                             params=params, **kwargs)

    @asyncio.coroutine
    def put(self, url, params=None, data=None, **kwargs):
        return self._request(url, 'PUT', data=(data if data else {}),
                             params=params, **kwargs)

    @asyncio.coroutine
    def delete(self, url, params=None, **kwargs):
        return self._request(url, 'DELETE', params=params, **kwargs)

    @asyncio.coroutine
    def _request(self, url, type, params=None, data=None, **kwargs):
        raise NotImplementedError
