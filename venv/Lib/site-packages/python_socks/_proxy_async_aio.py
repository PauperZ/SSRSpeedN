import asyncio
import socket
import sys

import async_timeout

from ._errors import ProxyConnectionError, ProxyTimeoutError
from ._proto_http_async import HttpProto
from ._proto_socks4_async import Socks4Proto
from ._proto_socks5_async import Socks5Proto
from ._proxy_async import (
    AsyncProxy
)
from ._stream_async_aio import AsyncioSocketStream
from ._resolver_async_aio import Resolver

DEFAULT_TIMEOUT = 60


class AsyncioProxy(AsyncProxy):
    def __init__(self, proxy_host, proxy_port,
                 loop: asyncio.AbstractEventLoop = None):

        if loop is None:
            loop = asyncio.get_event_loop()

        self._loop = loop

        self._proxy_host = proxy_host
        self._proxy_port = proxy_port

        self._dest_host = None
        self._dest_port = None
        self._timeout = None

        self._stream = AsyncioSocketStream(loop=loop)
        self._resolver = Resolver(loop=loop)

    async def connect(self, dest_host, dest_port, timeout=None,
                      _socket=None) -> socket.socket:
        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        self._dest_host = dest_host
        self._dest_port = dest_port
        self._timeout = timeout

        try:
            await self._connect(_socket=_socket)
        except asyncio.TimeoutError as e:
            raise ProxyTimeoutError(
                'Proxy connection timed out: %s'
                % self._timeout) from e

        return self._stream.socket

    async def _connect(self, _socket=None):
        async with async_timeout.timeout(self._timeout):
            try:
                await self._stream.open_connection(
                    host=self._proxy_host,
                    port=self._proxy_port,
                    _socket=_socket
                )
            except OSError as e:
                await self._stream.close()
                msg = ('Can not connect to proxy %s:%s [%s]' %
                       (self._proxy_host, self._proxy_port, e.strerror))
                raise ProxyConnectionError(e.errno, msg) from e
            except Exception:  # pragma: no cover
                await self._stream.close()
                raise

            try:
                await self._negotiate()
            except asyncio.CancelledError:  # pragma: no cover
                # https://bugs.python.org/issue30064
                # https://bugs.python.org/issue34795
                if self._can_be_closed_safely():
                    await self._stream.close()
                raise
            except Exception:
                await self._stream.close()
                raise

    def _can_be_closed_safely(self):  # pragma: no cover
        def is_proactor_event_loop():
            try:
                from asyncio import ProactorEventLoop  # noqa
            except ImportError:
                return False
            return isinstance(self._loop, ProactorEventLoop)

        def is_uvloop_event_loop():
            try:
                from uvloop import Loop  # noqa
            except ImportError:
                return False
            return isinstance(self._loop, Loop)

        return (sys.version_info[:2] >= (3, 8)
                or is_proactor_event_loop()
                or is_uvloop_event_loop())

    async def _negotiate(self):
        raise NotImplementedError()  # pragma: no cover

    @property
    def proxy_host(self):
        return self._proxy_host

    @property
    def proxy_port(self):
        return self._proxy_port


class Socks5Proxy(AsyncioProxy):
    def __init__(self, proxy_host, proxy_port,
                 username=None, password=None, rdns=None,
                 loop: asyncio.AbstractEventLoop = None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port,
                         loop=loop)
        self._username = username
        self._password = password
        self._rdns = rdns

    async def _negotiate(self):
        proto = Socks5Proto(
            stream=self._stream,
            resolver=self._resolver,
            dest_host=self._dest_host,
            dest_port=self._dest_port,
            username=self._username,
            password=self._password,
            rdns=self._rdns
        )
        await proto.negotiate()


class Socks4Proxy(AsyncioProxy):
    def __init__(self, proxy_host, proxy_port,
                 user_id=None, rdns=None,
                 loop: asyncio.AbstractEventLoop = None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port,
                         loop=loop)
        self._user_id = user_id
        self._rdns = rdns

    async def _negotiate(self):
        proto = Socks4Proto(
            stream=self._stream,
            resolver=self._resolver,
            dest_host=self._dest_host,
            dest_port=self._dest_port,
            user_id=self._user_id,
            rdns=self._rdns
        )
        await proto.negotiate()


class HttpProxy(AsyncioProxy):
    def __init__(self, proxy_host, proxy_port,
                 username=None, password=None,
                 loop: asyncio.AbstractEventLoop = None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port,
                         loop=loop)
        self._username = username
        self._password = password

    async def _negotiate(self):
        proto = HttpProto(
            stream=self._stream,
            dest_host=self._dest_host,
            dest_port=self._dest_port,
            username=self._username,
            password=self._password
        )
        await proto.negotiate()
