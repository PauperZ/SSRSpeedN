#coding:utf-8

import os
import sys
import time
import re
import socket
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger("Sub")

from config import config
LOCAL_PORT = config["localPort"]

def parseLocation():
	try:
		logger.info("Starting parse location.")
		rep = requests.get("https://api.ip.sb/geoip",proxies = {
			"http":"socks5h://127.0.0.1:%d" % LOCAL_PORT,
			"https":"socks5h://127.0.0.1:%d" % LOCAL_PORT
		},timeout=5)
		tmp = rep.json()
		logger.info("Server Country Code : %s,Continent Code : %s,ISP : %s" % (tmp["country_code"],tmp["continent_code"],tmp["organization"]))
		return (True,tmp["country_code"],tmp["continent_code"],tmp["organization"])
	except requests.exceptions.ReadTimeout:
		logger.error("Parse location timeout.")
	except:
		logger.exception("Parse location failed.")
		try:
			logger.error(rep.content)
		except:
			pass
	return(False,"DEFAULT","DEFAULT","DEFAULT")

def checkIPv4(ip):
	r = re.compile(r"\b((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:(?<!\.)\b|\.)){4}")
	rm = r.match(ip)
	if (rm):
		if (rm.group(0) == ip):
			return True
	return False

def domain2ip(domain):
	logger.info("Translating {} to ipv4.".format(domain))
	if (checkIPv4(domain)):
		return domain
	ip = "N/A"
	try:
		ip = socket.gethostbyname(domain)
		return ip
	except:
		logger.exception("Translate {} to ipv4 failed.".format(domain))
		return "N/A"


def IPLoc(ip = ""):
	try:
		if (ip != "" and not checkIPv4(ip)):
			logger.error("Invalid IP : {}".format(ip))
			return {}
		logger.info("Starting Geo IP.")
		if (ip == "N/A"):
			ip = ""
		headers = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		'Accept - Encoding':'gzip, deflate, br',
		'Accept-Language':'en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7',
		'Connection':'Keep-Alive',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'}
		rep = requests.get("https://api.ip.sb/geoip/{}".format(ip),proxies = {
			"http":"socks5h://127.0.0.1:%d" % LOCAL_PORT,
			"https":"socks5h://127.0.0.1:%d" % LOCAL_PORT
		},timeout=5,headers=headers)
		tmp = rep.json()
		return tmp
	except requests.exceptions.ReadTimeout:
		logger.error("Geo IP Timeout.")
		return {}
	except:
		logger.exception("Geo IP Failed.")
		try:
			logger.error(rep.content)
		except:
			pass
	return {}

