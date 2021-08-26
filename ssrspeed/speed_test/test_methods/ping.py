#coding:utf-8
#Author:ranwen NyanChan

import time
import socket
import logging
logger = logging.getLogger("Sub")


def tcp_ping(host, port):

	alt=0
	suc=0
	fac=0
	_list = []
	while True:
		if fac >= 3 or (suc != 0 and fac + suc >= 10):
			break
	#	logger.debug("fac: {}, suc: {}".format(fac, suc))
		try:
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			st=time.time()
			s.settimeout(3)
			s.connect((host,port))
			s.close()
			deltaTime = time.time()-st
			alt += deltaTime
			suc += 1
			_list.append(deltaTime)
		except (socket.timeout):
			fac+=1
			_list.append(0)
			logger.warn("TCP Ping (%s,%d) Timeout %d times." % (host,port,fac))
		#	print("TCP Ping Timeout %d times." % fac)
		except Exception:
			logger.exception("TCP Ping Exception:")
			_list.append(0)
			fac+=1
	if suc==0:
		return (0,0,_list)
	return (alt/suc,suc/(suc+fac),_list)

def google_ping(address, port=1080):

	alt=0
	suc=0
	fac=0
	_list = []
	while True:
		if fac >= 3 or (suc != 0 and fac + suc >= 10):
			break
		try:
			s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(3)
			s.connect((address,port))
			st=time.time()
			s.send(b"\x05\x01\x00")
			s.recv(2)
			s.send(b"\x05\x01\x00\x03\x0agoogle.com\x00\x50")
			s.recv(10)
			s.send(b"GET / HTTP/1.1\r\nHost: google.com\r\nUser-Agent: curl/11.45.14\r\n\r\n")
			s.recv(1)
			s.close()
			deltaTime = time.time()-st
			alt += deltaTime
			suc += 1
			_list.append(deltaTime)
		except (socket.timeout):
			fac += 1
			_list.append(0)
			logger.warn("Google Ping Timeout %d times." % (fac))
		except Exception:
			logger.exception("Google Ping Exception:")
			_list.append(0)
			fac += 1
	if (suc == 0):
		return (0,0,_list)
	return (alt/suc,suc/(suc+fac),_list)

