# -*- coding: utf-8 -*-

import socket

def check_port(port: int):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(3)
	s.connect(("127.0.0.1", port))
	s.shutdown(2)

