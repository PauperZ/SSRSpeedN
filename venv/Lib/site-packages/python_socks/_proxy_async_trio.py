import trio

from ._errors import ProxyConnectionError, ProxyTimeoutError
from ._proto_http_async import HttpProto
from ._proto_socks4_async import Socks4Proto
from ._proto_socks5_async import Socks5Proto
from ._proxy_async import (
    AsyncProxy
)
from ._stream_async_trio import TrioSocketStream
from ._resolver_async_trio import Resolver

DEFAULT_TIMEOUT = 60


class TrioProxy(AsyncProxy):
    def __init__(self, proxy_host, proxy_port):
        self._proxy_host = proxy_host
        self._proxy_port = proxy_port

        self._dest_host = None
        self._dest_port = None
        self._timeout = None

        self._stream = TrioSocketStream()
        self._resolver = Resolver()

    async def connect(self, dest_host, dest_port, timeout=None,
                      _socket=None) -> trio.socket.SocketType:
        if timeout is None:
            timeout = DEFAULT_TIMEOUT

        self._dest_host = dest_host
        self._dest_port = dest_port
        self._timeout = timeout

        try:
            await self._connect(_socket=_socket)
        except OSError as e:
            await self._stream.close()
            msg = ('Can not connect to proxy %s:%s [%s]' %
                   (self._proxy_host, self._proxy_port, e.strerror))
            raise ProxyConnectionError(e.errno, msg) from e
        except trio.TooSlowError as e:
            await self._stream.close()
            raise ProxyTimeoutError('Proxy connection timed out: %s'
                                    % self._timeout) from e
        except Exception:
            await self._stream.close()
            raise

        return self._stream.socket

    async def _connect(self, _socket=None):
        with trio.fail_after(self._timeout):
            await self._stream.open_connection(
                host=self._proxy_host,
                port=self._proxy_port,
                _socket=_socket
            )

            await self._negotiate()

    async def _negotiate(self):
        raise NotImplementedError

    @property
    def proxy_host(self):
        return self._proxy_host

    @property
    def proxy_port(self):
        return self._proxy_port


class Socks5Proxy(TrioProxy):
    def __init__(self, proxy_host, proxy_port,
                 username=None, password=None, rdns=None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port)
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


class Socks4Proxy(TrioProxy):
    def __init__(self, proxy_host, proxy_port, user_id=None, rdns=None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port)
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


class HttpProxy(TrioProxy):
    def __init__(self, proxy_host, proxy_port, username=None, password=None):
        super().__init__(proxy_host=proxy_host, proxy_port=proxy_port)
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
