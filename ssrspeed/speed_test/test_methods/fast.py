'''
Python CLI-tool (without need for a GUI) to measure Internet speed with fast.com

'''
import socket
import socks
import logging
logger = logging.getLogger("Sub")

import os
import json
import urllib.request, urllib.parse, urllib.error
import sys
import time
from threading import Thread
import traceback

def setProxy(LOCAL_ADDRESS,LOCAL_PORT):
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,LOCAL_ADDRESS,LOCAL_PORT)
	socket.socket = socks.socksocket

'''
proxy = {"http":"http://127.0.0.1:1081"}
proxySupport = urllib.request.ProxyHandler({"http":"http://127.0.0.1:1081"})
opener = urllib.request.build_opener(proxySupport)
urllib.request.install_opener(opener)
'''

def gethtmlresult(url,result,index):
	'''
	get the stuff from url in chuncks of size CHUNK, and keep writing the number of bytes retrieved into result[index]
	'''
	try:
		req = urllib.request.urlopen(url)
	except urllib.error.URLError:
		result[index] = 0
		return

	CHUNK = 100 * 1024
	i=1
	while True:
			chunk = req.read(CHUNK)
			if not chunk: break
			result[index] = i*CHUNK
			i=i+1


def application_bytes_to_networkbits(bytes):
	# convert bytes (at application layer) to bits (at network layer)
	return bytes * 8 * 1.0415
	# 8 for bits versus bytes
	# 1.0416 for application versus network layers


def findipv4(fqdn):
	'''
		find IPv4 address of fqdn
	'''
	import socket
	ipv4 = socket.getaddrinfo(fqdn, 80, socket.AF_INET)[0][4][0]
	return ipv4


def findipv6(fqdn):
	'''
		find IPv6 address of fqdn
	'''
	import socket
	ipv6 = socket.getaddrinfo(fqdn, 80, socket.AF_INET6)[0][4][0]
	return ipv6


def fast_com(verbose=False, maxtime=15, forceipv4=False, forceipv6=False):
	'''
		verbose: print debug output
		maxtime: max time in seconds to monitor speedtest
		forceipv4: force speed test over IPv4
		forceipv6: force speed test over IPv6
	'''
	# go to fast.com to get the javascript file
	url = 'https://fast.com/'
	try:
		urlresult = urllib.request.urlopen(url)
	except:
		logger.exception("No connection at all")
		# no connection at all?
		return 0
	response = urlresult.read().decode().strip()
	for line in response.split('\n'):
		# We're looking for a line like
		#           <script src="/app-40647a.js"></script>
		if line.find('script src') >= 0:
			jsname = line.split('"')[1] # At time of writing: '/app-40647a.js'


	# From that javascript file, get the token:
	url = 'https://fast.com' + jsname
	if verbose: 
		logger.debug("javascript url is" + url)
	try:
		urlresult = urllib.request.urlopen(url)
	except:
		# connection is broken
		return 0
	allJSstuff = urlresult.read().decode().strip() # this is a obfuscated Javascript file
	for line in allJSstuff.split(','):
		if line.find('token:') >= 0:
			if verbose: 
				logger.debug("line is" + line)
			token = line.split('"')[1]
			if verbose: 
				logger.debug("token is" + token)
			if token:
				break

	# With the token, get the (3) speed-test-URLS from api.fast.com (which will be in JSON format):
	baseurl = 'https://api.fast.com/'
	if forceipv4:
		# force IPv4 by connecting to an IPv4 address of api.fast.com (over ... HTTP)
		ipv4 = findipv4('api.fast.com')
		baseurl = 'http://' + ipv4 + '/'  # HTTPS does not work IPv4 addresses, thus use HTTP
	elif forceipv6:
		# force IPv6
		ipv6 = findipv6('api.fast.com')
		baseurl = 'http://[' + ipv6 + ']/'

	url = baseurl + 'netflix/speedtest?https=true&token=' + token + '&urlCount=3' # Not more than 3 possible
	if verbose: 
		logger.debug("API url is" + url)
	try:
		urlresult = urllib.request.urlopen(url, None, 2)  # 2 second time-out
	except:
		# not good
		if verbose:
			logger.exception("No connection possible") # probably IPv6, or just no network
		return 0  # no connection, thus no speed

	jsonresult = urlresult.read().decode().strip()
	parsedjson = json.loads(jsonresult)

	# Prepare for getting those URLs in a threaded way:
	amount = len(parsedjson)
	if verbose: 
		logger.debug("Number of URLs:" + str(amount))
	threads = [None] * amount
	results = [0] * amount
	urls = [None] * amount
	i = 0
	for jsonelement in parsedjson:
		urls[i] = jsonelement['url']  # fill out speed test url from the json format
		if verbose: 
			logger.debug(jsonelement['url'])
		i = i+1

	# Let's check whether it's IPv6:
	for url in urls:
		fqdn = url.split('/')[2]
		try:
			socket.getaddrinfo(fqdn, None, socket.AF_INET6)
			if verbose: 
				logger.info("IPv6")
		except:
			pass

	# Now start the threads
	for i in range(len(threads)):
		#print "Thread: i is", i
		threads[i] = Thread(target=gethtmlresult, args=(urls[i], results, i))
		threads[i].daemon=True
		threads[i].start()

	# Monitor the amount of bytes (and speed) of the threads
	time.sleep(1)
	sleepseconds = 3  # 3 seconds sleep
	lasttotal = 0
	highestspeedkBps = 0
	maxdownload = 60 #MB
	nrloops = int(maxtime / sleepseconds)
	for loop in range(nrloops):
		total = 0
		for i in range(len(threads)):
			#print i, results[i]
			total += results[i]
		delta = total-lasttotal
		speedkBps = (delta/sleepseconds)/(1024)
		if verbose:
			#logger.info("Loop" + loop"Total MB", total/(1024*1024), "Delta MB", delta/(1024*1024), "Speed kB/s:", speedkBps, "aka Mbps %.1f" % (application_bytes_to_networkbits(speedkBps)/1024))
			logger.info("Loop %s Total %s MB,Delta %s MB,Speed %s KB/s aka %.1f Mbps" % (str(loop),str(total/(1024*1024)),str(delta/(1024*1024)),str(speedkBps),application_bytes_to_networkbits(speedkBps)/1024))
		lasttotal = total
		if speedkBps > highestspeedkBps:
			highestspeedkBps = speedkBps
		time.sleep(sleepseconds)


	Mbps = (application_bytes_to_networkbits(highestspeedkBps)/1024)
	Mbps = float("%.1f" % Mbps)
	if verbose: 
		logger.info("Highest Speed (kB/s):" + str(highestspeedkBps) + "aka Mbps "+ str(Mbps))

	return highestspeedkBps*1024


######## MAIN #################

if __name__ == "__main__":
#	print("let's speed test:")
#	print("\nSpeed test, without logger:")
#	print(fast_com())
#	print("\nSpeed test, with logger:")
	print(fast_com(verbose=True))
#	print("\nSpeed test, IPv4, with verbose logger:")
#	print(fast_com(verbose=True, maxtime=18, forceipv4=True))
#	print("\nSpeed test, IPv6:")
#	print(fast_com(maxtime=12, forceipv6=True))
#	fast_com(verbose=True, maxtime=25)

#	print("\ndone")

