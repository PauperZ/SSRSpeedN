import socket

from ._stream_sync import SyncSocketStream
from ._resolver_sync import SyncResolver
from ._proto_socks5 import (
    AuthMethod,
    AuthMethodsRequest,
    AuthMethodsResponse,
    AuthRequest,
    AuthResponse,
    ConnectRequest,
    ConnectResponse
)


class Socks5Proto:
    def __init__(self, stream: SyncSocketStream, resolver: SyncResolver,
                 dest_host, dest_port, username=None, password=None,
                 rdns=None):

        if rdns is None:
            rdns = True

        self._dest_port = dest_port
        self._dest_host = dest_host
        self._username = username
        self._password = password
        self._rdns = rdns

        self._stream = stream
        self._resolver = resolver

    def negotiate(self):
        self._socks_auth()
        self._socks_connect()

    def _socks_auth(self):
        auth_method = self._choose_auth_method()

        # authenticate
        if auth_method == AuthMethod.USERNAME_PASSWORD:
            req = AuthRequest(
                username=self._username,
                password=self._password
            )

            self._stream.write_all(bytes(req))

            res = AuthResponse(self._stream.read_exact(2))
            res.validate()

    def _choose_auth_method(self) -> AuthMethod:
        req = AuthMethodsRequest(
            username=self._username,
            password=self._password
        )

        self._stream.write_all(bytes(req))

        res = AuthMethodsResponse(self._stream.read_exact(2))
        res.validate(request=req)
        return res.auth_method

    def _socks_connect(self):
        req = ConnectRequest(
            host=self._dest_host,
            port=self._dest_port,
            rdns=self._rdns
        )

        if req.need_resolve:
            _, addr = self._resolver.resolve(
                req.host,
                family=socket.AF_UNSPEC
            )
            req.set_resolved_host(addr)

        self._stream.write_all(bytes(req))

        res = ConnectResponse(self._stream.read_exact(3))
        res.validate()

        # read remaining data (bind address)
        self._stream.read()
