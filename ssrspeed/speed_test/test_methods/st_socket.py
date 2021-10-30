#coding:utf-8

import threading
import socks
import socket
import requests
import json
import time
import re
import copy
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("Sub")

from ...utils.geo_ip import IPLoc
from ...utils.rules import DownloadRuleMatch

from config import config

MAX_THREAD = config["fileDownload"]["maxWorkers"]
DEFAULT_SOCKET = socket.socket
MAX_FILE_SIZE = 100 * 1024 * 1024
BUFFER = config["fileDownload"]["buffer"]
EXIT_FLAG = False
LOCAL_PORT = 1080
LOCK = threading.Lock()
TOTAL_RECEIVED = 0
MAX_TIME = 0
SPEED_TEST = config["speed"]
STSPEED_TEST = config["StSpeed"]

def setProxyPort(port):
	global LOCAL_PORT
	LOCAL_PORT = port

def restoreSocket():
	socket.socket = DEFAULT_SOCKET


def speedTestThread(link):
	global TOTAL_RECEIVED,MAX_TIME
	logger.debug("Thread {} started.".format(threading.current_thread().ident))
	link = link.replace("https://","").replace("http://","")
	host = link[:link.find("/")]
	requestUri = link[link.find("/"):]
	logger.debug("\nLink: %s\nHost: %s\nRequestUri: %s" % (link,host,requestUri))
	#print(link,MAX_FILE_SIZE)
	try:
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.settimeout(12)
		try:
			s.connect((host,80))
			logger.debug("Connected to %s" % host)
		except:
			logger.error("Connect to %s error." % host)
			LOCK.acquire()
			TOTAL_RECEIVED += 0
			LOCK.release()
			return
		s.send(b"GET %b HTTP/1.1\r\nHost: %b\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36\r\n\r\n" % (requestUri.encode("utf-8"),host.encode("utf-8")))
		logger.debug("Request sent.")
		startTime = time.time()
		received = 0
		while True:
			try:
				xx = s.recv(BUFFER)
			except socket.timeout:
				logger.error("Receive data timeout.")
				break
			except ConnectionResetError:
				logger.warn("Remote host closed connection.")
				break
			lxx = len(xx)
		#	received += len(xx)
			received += lxx
		#	TR = 0
			LOCK.acquire()
			TOTAL_RECEIVED += lxx
		#	TR = TOTAL_RECEIVED
			LOCK.release()
		#	logger.debug(TR)
			if (received >= MAX_FILE_SIZE or EXIT_FLAG):
				break
		endTime = time.time()
		deltaTime = endTime - startTime
		if (deltaTime >= 12):
			deltaTime = 11
		s.close()
		logger.debug("Thread {} done,time : {}".format(threading.current_thread().ident,deltaTime))
		LOCK.acquire()
	#	TOTAL_RECEIVED += received
		MAX_TIME = max(MAX_TIME,deltaTime)
		LOCK.release()
	except:
		logger.exception("")
		return 0

def speedTestSocket(port):

	if not SPEED_TEST:
		return (0, 0, [], 0)

	global EXIT_FLAG,LOCAL_PORT,MAX_TIME,TOTAL_RECEIVED,MAX_FILE_SIZE
	LOCAL_PORT = port

	dlrm = DownloadRuleMatch()
	res = dlrm.get_url(IPLoc())

	MAX_FILE_SIZE = res[1] * 1024 * 1024
	MAX_TIME = 0
	TOTAL_RECEIVED = 0
	EXIT_FLAG = False
	socks.set_default_proxy(socks.SOCKS5,"127.0.0.1", LOCAL_PORT)
	socket.socket = socks.socksocket
     
	if STSPEED_TEST:
		for i in range(0,1):
			nmsl = threading.Thread(target=speedTestThread,args=(res[0],))
			nmsl.start()

		maxSpeedList = []
		maxSpeed = 0
		currentSpeed = 0
		OLD_RECEIVED = 0
		DELTA_RECEIVED = 0
		for i in range(1,11):
			time.sleep(0.5)
			LOCK.acquire()
			DELTA_RECEIVED = TOTAL_RECEIVED - OLD_RECEIVED
			OLD_RECEIVED = TOTAL_RECEIVED
			LOCK.release()
			currentSpeed = DELTA_RECEIVED / 0.5
			maxSpeedList.append(currentSpeed)
			print("\r[" + "="*i + "> [%d%%/100%%] [%.2f MB/s]" % (int(i * 10),currentSpeed / 1024 / 1024),end='')
			if (EXIT_FLAG):
				break
		print("\r[" + "="*i + "] [100%%/100%%] [%.2f MB/s]" % (currentSpeed / 1024 / 1024),end='\n')
		EXIT_FLAG = True
		for i in range(0,10):
			time.sleep(0.1)
			if (MAX_TIME != 0):
				break
		if (MAX_TIME == 0):
			logger.error("Socket Test Error !")
			return (0, 0, [], 0)
		
		rawSpeedList = copy.deepcopy(maxSpeedList)
		maxSpeedList.sort()
		if (len(maxSpeedList) > 12):
			msum = 0
			for i in range(12,len(maxSpeedList) - 2):
				msum += maxSpeedList[i]
			maxSpeed = (msum / (len(maxSpeedList) - 2 - 12))
		else:
			maxSpeed = currentSpeed
		logger.info("SingleThread: Fetched {:.2f} KB in {:.2f} s.".format(TOTAL_RECEIVED / 1024, MAX_TIME))

		AvgStSpeed = TOTAL_RECEIVED / MAX_TIME

		MAX_TIME = 0
		TOTAL_RECEIVED = 0
		EXIT_FLAG = False

	for i in range(0,MAX_THREAD):
		nmsl = threading.Thread(target=speedTestThread,args=(res[0],))
		nmsl.start()
		
	maxSpeedList = []
	maxSpeed = 0
	currentSpeed = 0
	OLD_RECEIVED = 0
	DELTA_RECEIVED = 0
	for i in range(1,11):
		time.sleep(0.5)
		LOCK.acquire()
		DELTA_RECEIVED = TOTAL_RECEIVED - OLD_RECEIVED
		OLD_RECEIVED = TOTAL_RECEIVED
		LOCK.release()
		currentSpeed = DELTA_RECEIVED / 0.5
		maxSpeedList.append(currentSpeed)
		print("\r[" + "="*i + "> [%d%%/100%%] [%.2f MB/s]" % (int(i * 10),currentSpeed / 1024 / 1024),end='')
		if (EXIT_FLAG):
			break
	print("\r[" + "="*i + "] [100%%/100%%] [%.2f MB/s]" % (currentSpeed / 1024 / 1024),end='\n')
	EXIT_FLAG = True
	for i in range(0,10):
		time.sleep(0.1)
		if (MAX_TIME != 0):
			break
	if (MAX_TIME == 0):
		logger.error("Socket Test Error !")
		return (0, 0, [], 0)
        
	restoreSocket()
	rawSpeedList = copy.deepcopy(maxSpeedList)
	maxSpeedList.sort()
	if (len(maxSpeedList) > 7):
		msum = 0
		for i in range(7,len(maxSpeedList) - 2):
			msum += maxSpeedList[i]
		maxSpeed = (msum / (len(maxSpeedList) - 2 - 7))
	else:
		maxSpeed = currentSpeed
	logger.info("MultiThread: Fetched {:.2f} KB in {:.2f} s.".format(TOTAL_RECEIVED / 1024, MAX_TIME))
	AvgSpeed = TOTAL_RECEIVED / MAX_TIME

	if not STSPEED_TEST:
		AvgStSpeed = AvgSpeed
		AvgSpeed = maxSpeed

	return (AvgStSpeed, AvgSpeed, rawSpeedList, TOTAL_RECEIVED)
