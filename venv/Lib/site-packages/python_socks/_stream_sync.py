import socket

from ._resolver_sync import SyncResolver
from ._helpers import is_ipv4_address, is_ipv6_address
from ._errors import ProxyError

DEFAULT_RECEIVE_SIZE = 65536


class SyncSocketStream:
    _socket: socket.socket = None

    def __init__(self):
        self._resolver = SyncResolver()

    def open_connection(self, host, port, timeout=None, _socket=None):
        if _socket is None:
            family, host = self._resolve(host)

            self._socket = socket.socket(
                family=family,
                type=socket.SOCK_STREAM
            )

            if timeout is not None:
                self._socket.settimeout(timeout)

            self._socket.connect((host, port))
        else:
            self._socket = _socket

    def close(self):
        if self._socket is not None:
            self._socket.close()

    def write_all(self, data):
        self._socket.sendall(data)

    def read(self, max_bytes=None):
        if max_bytes is None:
            max_bytes = DEFAULT_RECEIVE_SIZE
        return self._socket.recv(max_bytes)

    def read_exact(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self._socket.recv(n - len(data))
            if not packet:
                raise ProxyError('Connection closed '  # pragma: no cover
                                 'unexpectedly')
            data += packet
        return data

    @property
    def socket(self):
        return self._socket

    def _resolve(self, host):
        if is_ipv4_address(host):
            return socket.AF_INET, host
        if is_ipv6_address(host):
            return socket.AF_INET6, host
        return self._resolver.resolve(host=host)
