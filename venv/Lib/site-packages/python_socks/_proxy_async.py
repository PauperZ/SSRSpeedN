class AsyncProxy:
    async def connect(self, dest_host, dest_port,
                      timeout=None, _socket=None):
        raise NotImplementedError()  # pragma: no cover

    @property
    def proxy_host(self):
        raise NotImplementedError()  # pragma: no cover

    @property
    def proxy_port(self):
        raise NotImplementedError()  # pragma: no cover
