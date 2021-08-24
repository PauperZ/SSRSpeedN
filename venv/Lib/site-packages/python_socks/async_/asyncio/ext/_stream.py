import asyncio
import socket

from ...._helpers import is_ipv4_address, is_ipv6_address
from ...._resolver_async_aio import Resolver
from ...._stream_async import AsyncSocketStream

DEFAULT_RECEIVE_SIZE = 65536


# noinspection PyUnusedLocal
async def backport_start_tls(
        transport,
        protocol,
        ssl_context,
        *,
        server_side=False,
        server_hostname=None,
        ssl_handshake_timeout=None,
):  # pragma: no cover
    """
    Python 3.6 asyncio doesn't have a start_tls() method on the loop
    so we use this function in place of the loop's start_tls() method.
    Adapted from this comment:
    https://github.com/urllib3/urllib3/issues/1323#issuecomment-362494839
    """
    import asyncio.sslproto

    loop = asyncio.get_event_loop()
    waiter = loop.create_future()
    ssl_protocol = asyncio.sslproto.SSLProtocol(
        loop,
        protocol,
        ssl_context,
        waiter,
        server_side=False,
        server_hostname=server_hostname,
        call_connection_made=False,
    )

    transport.set_protocol(ssl_protocol)
    loop.call_soon(ssl_protocol.connection_made, transport)
    loop.call_soon(transport.resume_reading)  # type: ignore

    await waiter
    return ssl_protocol._app_transport  # noqa


class AsyncioSocketStream(AsyncSocketStream):
    _loop: asyncio.AbstractEventLoop = None
    _reader: asyncio.StreamReader = None
    _writer: asyncio.StreamWriter = None

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._resolver = Resolver(loop=loop)

    async def open_connection(self, host, port):
        family, host = await self._resolve(host=host)

        self._reader, self._writer = await asyncio.open_connection(
            host=host,
            port=port,
            family=family,
        )

    async def close(self):
        if self._writer is not None:
            self._writer.close()
            self._writer.transport.abort()  # noqa

    async def write_all(self, data):
        self._writer.write(data)
        await self._writer.drain()

    async def read(self, max_bytes=DEFAULT_RECEIVE_SIZE):
        return await self._reader.read(max_bytes)

    async def read_exact(self, n):
        return await self._reader.readexactly(n)

    async def start_tls(self, hostname, ssl_context):
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)

        loop_start_tls = getattr(self._loop, 'start_tls', backport_start_tls)

        transport = await loop_start_tls(
            self._writer.transport,
            protocol,
            ssl_context,
            server_side=False,
            server_hostname=hostname
        )

        # reader.set_transport(transport)

        # Initialize the protocol, so it is made aware of being tied to
        # a TLS connection.
        # See: https://github.com/encode/httpx/issues/859
        protocol.connection_made(transport)

        writer = asyncio.StreamWriter(
            transport=transport,
            protocol=protocol,
            reader=reader,
            loop=self._loop
        )

        self._reader = reader
        self._writer = writer

    @property
    def reader(self):
        return self._reader  # pragma: no cover

    @property
    def writer(self):
        return self._writer  # pragma: no cover

    async def _resolve(self, host):
        if is_ipv4_address(host):
            return socket.AF_INET, host
        if is_ipv6_address(host):
            return socket.AF_INET6, host
        return await self._resolver.resolve(host=host)
