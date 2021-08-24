import asyncio
import socket

from ._stream_async import AsyncSocketStream, DEFAULT_RECEIVE_SIZE
from ._resolver_async_aio import Resolver
from ._helpers import is_ipv4_address, is_ipv6_address
from ._errors import ProxyError


class AsyncioSocketStream(AsyncSocketStream):
    _loop: asyncio.AbstractEventLoop = None
    _socket = None

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._resolver = Resolver(loop=loop)

    async def open_connection(self, host, port, _socket=None):
        if _socket is None:
            family, host = await self._resolve(host=host)

            self._socket = socket.socket(
                family=family,
                type=socket.SOCK_STREAM
            )
            self._socket.setblocking(False)

            await self._loop.sock_connect(
                sock=self._socket,
                address=(host, port)
            )
        else:
            self._socket = _socket

    async def close(self):
        if self._socket is not None:
            self._socket.close()

    async def write_all(self, data):
        await self._loop.sock_sendall(self._socket, data)

    async def read(self, max_bytes=None):
        if max_bytes is None:
            max_bytes = DEFAULT_RECEIVE_SIZE
        return await self._loop.sock_recv(self._socket, max_bytes)

    async def read_exact(self, n):
        data = bytearray()
        while len(data) < n:
            packet = await self._loop.sock_recv(self._socket, n - len(data))
            if not packet:
                raise ProxyError('Connection closed '  # pragma: no cover
                                 'unexpectedly')
            data += packet
        return data

    @property
    def socket(self):
        return self._socket

    async def _resolve(self, host):
        if is_ipv4_address(host):
            return socket.AF_INET, host
        if is_ipv6_address(host):
            return socket.AF_INET6, host
        return await self._resolver.resolve(host=host)
