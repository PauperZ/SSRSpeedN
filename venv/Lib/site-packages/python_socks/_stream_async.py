DEFAULT_RECEIVE_SIZE = 65536


class AsyncSocketStream:

    async def open_connection(self, host, port):
        raise NotImplementedError()  # pragma: no cover

    async def close(self):
        raise NotImplementedError()  # pragma: no cover

    async def write_all(self, data):
        raise NotImplementedError()  # pragma: no cover

    async def read(self, max_bytes=None):
        raise NotImplementedError()  # pragma: no cover

    async def read_exact(self, n):
        raise NotImplementedError()  # pragma: no cover
