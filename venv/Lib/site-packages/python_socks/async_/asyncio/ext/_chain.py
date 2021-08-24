from typing import Iterable
from ._proxy import AsyncioProxy


class ProxyChain:
    def __init__(self, proxies: Iterable[AsyncioProxy]):
        self._proxies = proxies

    async def connect(self, dest_host, dest_port,
                      dest_ssl=None, timeout=None):
        stream = None
        proxies = list(self._proxies)

        length = len(proxies) - 1
        for i in range(length):
            proxy = proxies[i]
            if stream is not None:
                proxy._stream = stream
                proxy._in_chain = True

            stream = await proxy.connect(
                dest_host=proxies[i + 1].proxy_host,
                dest_port=proxies[i + 1].proxy_port,
                timeout=timeout,
            )

        stream = await proxies[length].connect(
            dest_host=dest_host,
            dest_port=dest_port,
            dest_ssl=dest_ssl,
            timeout=timeout,
        )

        return stream
