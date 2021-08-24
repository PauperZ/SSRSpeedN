from ._proto_http import ConnectRequest, ConnectResponse
from ._stream_sync import SyncSocketStream


class HttpProto:
    def __init__(self, stream: SyncSocketStream, dest_host, dest_port,
                 username=None, password=None):
        self._dest_host = dest_host
        self._dest_port = dest_port
        self._username = username
        self._password = password

        self._stream = stream

    def negotiate(self):
        request = ConnectRequest(
            host=self._dest_host,
            port=self._dest_port,
            login=self._username,
            password=self._password,
        )

        self._stream.write_all(bytes(request))

        response = ConnectResponse(self._stream.read())
        response.validate()
