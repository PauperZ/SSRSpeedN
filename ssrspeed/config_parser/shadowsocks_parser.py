#coding:utf-8

import urllib.parse
import logging
import requests
import json
logger = logging.getLogger("Sub")

from . import BaseParser
from .shadowsocks_parsers import ParserShadowsocksBasic, ParserShadowsocksClash, ParserShadowsocksD, ParserShadowsocksSIP002
from ..utils import b64plus

class ShadowsocksParser(BaseParser):
	def __init__(self):
		super(ShadowsocksParser,self).__init__()

	def _parseLink(self, link):
		pssb = ParserShadowsocksBasic(self._getShadowsocksBaseConfig())
		return pssb.parseSubsConfig([link])[0]

	def readSubscriptionConfig(self,url):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header,timeout=15)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8")
		if (rep[:6] == "ssd://"):
			logger.info("Try ShadowsocksD Parser.")
			pssd = ParserShadowsocksD(self._getShadowsocksBaseConfig())
			self._configList = pssd.parseSubsConfig(b64plus.decode(rep[6:]).decode("utf-8"))
		else:
			try:
				logger.info("Try Shadowsocks Basic Parser.")
				linksArr = (b64plus.decode(rep).decode("utf-8")).split("\n")
				try:
					pssb = ParserShadowsocksBasic(self._getShadowsocksBaseConfig())
					self._configList = pssb.parseSubsConfig(linksArr)
				except ValueError:
					logger.info("Try Shadowsocks SIP002 Parser.")
					pssip002 = ParserShadowsocksSIP002(self._getShadowsocksBaseConfig())
					self._configList = pssip002.parseSubsConfig(linksArr)
			except ValueError:
				logger.info("Try Shadowsocks Clash Parser.")
				pssc = ParserShadowsocksClash(self._getShadowsocksBaseConfig())
				self._configList = pssc.parseSubsConfig(rep)
		logger.info("Read %d node(s)" % len(self._configList))
	
	def readGuiConfig(self,filename):
		logger.info("Try Shadowsocks Basic or ShadowsocksD Parser.")
		pssb = ParserShadowsocksBasic(self._getShadowsocksBaseConfig())
		cfg = pssb.parseGuiConfig(filename)
		if (cfg == False):
			logger.info("Not ShadowsocksBasic or ShadowsocksD Config.")
			logger.info("Try Shadowsocks Clash Parser.")
			pssc = ParserShadowsocksClash(self._getShadowsocksBaseConfig())
			cfg = pssc.parseGuiConfig(filename)
			if (cfg == False):
				logger.info("Not Clash Configs")
				cfg = []
				logger.critical("Unspport config file.")
		self._configList = cfg
		logger.info("Read %d node(s)" % len(self._configList))




