import curio
import curio.io
import curio.socket

from ._stream_async import AsyncSocketStream, DEFAULT_RECEIVE_SIZE
from ._resolver_async_curio import Resolver
from ._helpers import is_ipv4_address, is_ipv6_address
from ._errors import ProxyError


class CurioSocketStream(AsyncSocketStream):
    _socket: curio.io.Socket = None

    def __init__(self):
        self._resolver = Resolver()

    async def open_connection(self, host, port, _socket=None):
        if _socket is None:
            family, host = await self._resolve(host=host)

            self._socket = curio.socket.socket(
                family=family,
                type=curio.socket.SOCK_STREAM
            )

            await self._socket.connect((host, port))
        else:
            self._socket = _socket

    async def close(self):
        if self._socket is not None:
            await self._socket.close()

    async def write_all(self, data):
        await self._socket.sendall(data)

    async def read(self, max_bytes=None):
        if max_bytes is None:
            max_bytes = DEFAULT_RECEIVE_SIZE
        return await self._socket.recv(max_bytes)

    async def read_exact(self, n):
        data = bytearray()
        while len(data) < n:
            packet = await self._socket.recv(n - len(data))
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
            return curio.socket.AF_INET, host
        if is_ipv6_address(host):
            return curio.socket.AF_INET6, host
        return await self._resolver.resolve(host=host)
