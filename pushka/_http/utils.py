from urllib.parse import urlencode


def merge_url(url, params):
    """Merge URL params with query params and return new URL."""
    if params:
        url = url.strip('&?')
        url += '&' if ('?' in url) else '?'
        url += urlencode(params)
    return url


def encode_body(body):
    """If body is ``dict`` object, perform url encoding,
    else do nothing.
    """
    return urlencode(body) if isinstance(body, dict) else body


def norm_tornado_kwargs(**kwargs):
    """Normalize request parameters for Tornado client."""
    if 'auth' in kwargs:
        auth = kwargs.pop('auth')
        kwargs['auth_username'] = auth[0]
        kwargs['auth_password'] = auth[1]
    return kwargs


def norm_aiohttp_kwargs(**kwargs):
    """Normalize request parameters for aiohttp client."""
    if 'auth' in kwargs:
        kwargs['auth'] = _norm_aiohttp_auth(kwargs['auth'])
    return kwargs


def _norm_aiohttp_auth(auth):
    import aiohttp.helpers
    return aiohttp.helpers.BasicAuth(login=auth[0], password=auth[1])
