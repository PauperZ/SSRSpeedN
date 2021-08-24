import socket


class SyncResolver:
    # noinspection PyMethodMayBeStatic
    def resolve(self, host, port=0, family=socket.AF_UNSPEC):
        infos = socket.getaddrinfo(
            host=host, port=port,
            family=family, type=socket.SOCK_STREAM)

        if not infos:
            raise OSError('Can`t resolve address '  # pragma: no cover
                          '{}:{} [{}]'.format(host, port, family))

        infos = sorted(infos, key=lambda info: info[0])

        family, _, _, _, address = infos[0]
        return family, address[0]
