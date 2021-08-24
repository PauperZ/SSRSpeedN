#coding:utf-8

import json
import requests
import platform
import os
import time
import sys
import copy
import urllib.parse
import logging
logger = logging.getLogger("Sub")


from ..utils import b64plus
from .base_configs import shadowsocks_get_config
from config import config

LOCAL_ADDRESS = config["localAddress"]
LOCAL_PORT = config["localPort"]
TIMEOUT = 10

class BaseParser(object):
	def __init__(self):
		self._configList = []
		self.__baseShadowsocksConfig = shadowsocks_get_config()
		self.__baseShadowsocksConfig["timeout"] = TIMEOUT
		self.__baseShadowsocksConfig["local_port"] = LOCAL_PORT
		self.__baseShadowsocksConfig["local_address"] = LOCAL_ADDRESS

	def cleanConfigs(self):
		self._configList = []
	
	def addConfigs(self,newConfigs):
		for item in newConfigs:
			self._configList.append(item)

	def _parseLink(self,link):
		return {}

	def parse_single_link(self, link):
		return self._parseLink(link)

	def _getLocalConfig(self):
		return (LOCAL_ADDRESS,LOCAL_PORT)
	
	def _getShadowsocksBaseConfig(self):
		return copy.deepcopy(self.__baseShadowsocksConfig)

	def __checkInList(self,item,_list):
		for _item in _list:
			server1 = item.get("server", "")
			server2 = _item.get("server", "")
			port1 = item.get("server_port", item.get("port", 0))
			port2 = _item.get("server_port", _item.get("port", 0))
			if server1 and server2 and port1 and port2:
				if server1 == server2 and port1 == port2:
					logger.warn("{} - {} ({}:{}) already in list.".format(
						item.get("group", "N/A"),
						item.get("remarks", "N/A"),
						item.get("server", "Server EMPTY"),
						item.get("server_port", item.get("port", 0))
					))
					return True
			else:
				return True
		return False

	def __filterGroup(self,gkwl):
		_list = []
		if (gkwl == []):return
		for gkw in gkwl:
			for item in self._configList:
				if (self.__checkInList(item,_list)):continue
				if (gkw in item["group"]):
					_list.append(item)
		self._configList = _list

	def __filterRemark(self,rkwl):
		_list = []
		if (rkwl == []):return
		for rkw in rkwl:
			for item in self._configList:
				if (self.__checkInList(item,_list)):continue
			#	print(item["remarks"])
				if (rkw in item["remarks"]):
					_list.append(item)
		self._configList = _list

	def filterNode(self,kwl = [],gkwl = [],rkwl = []):
		_list = []
	#	print(len(self._configList))
	#	print(type(kwl))
		if (kwl != []):
			for kw in kwl:
				for item in self._configList:
					if (self.__checkInList(item,_list)):continue
					if ((kw in item["group"]) or (kw in item["remarks"])):
					#	print(item["remarks"])
						_list.append(item)
			self._configList = _list
		self.__filterGroup(gkwl)
		self.__filterRemark(rkwl)

	def __excludeGroup(self,gkwl):
		if (gkwl == []):return
		for gkw in gkwl:
			_list = []
			for item in self._configList:
				if (self.__checkInList(item,_list)):continue
				if (gkw not in item["group"]):
					_list.append(item)
			self._configList = _list

	def __excludeRemark(self,rkwl):
		if (rkwl == []):return
		for rkw in rkwl:
			_list = []
			for item in self._configList:
				if (self.__checkInList(item,_list)):continue
				if (rkw not in item["remarks"]):
					_list.append(item)
			self._configList = _list

	def excludeNode(self,kwl = [],gkwl = [],rkwl = []):
	#	print((kw,gkw,rkw))
	#	print(len(self._configList))
	#	print(self._configList)
		if (kwl != []):
			for kw in kwl:
				_list = []
				for item in self._configList:
					if (self.__checkInList(item,_list)):continue
					if ((kw not in item["group"]) and (kw not in item["remarks"])):
						_list.append(item)
					else:
						logger.debug("Excluded {} - {}".format(item["group"], item["remarks"]))
				self._configList = _list
		self.__excludeGroup(gkwl)
		self.__excludeRemark(rkwl)
	#	print(self._configList)

	def printNode(self):
		for item in self._configList:
		#	print("%s - %s" % (item["group"],item["remarks"]))
			logger.info("%s - %s" % (item["group"],item["remarks"]))

	def readSubscriptionConfig(self,url):
		header = {
			"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
		}
		rep = requests.get(url,headers = header,timeout=15)
		rep.encoding = "utf-8"
		rep = rep.content.decode("utf-8").strip()
		linksArr = (b64plus.decode(rep).decode("utf-8")).split("\n")
		for link in linksArr:
			link = link.strip()
		#	print(link)
			cfg = self._parseLink(link)
			if (cfg):
			#	print(cfg["remarks"])
				self._configList.append(cfg)
		logger.info("Read %d node(s)" % len(self._configList))
			
	def readGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			for item in json.load(f)["configs"]:
				_dict = {
					"server":item["server"],
					"server_port":int(item["server_port"]),
					"password":item["password"],
					"method":item["method"],
					"protocol":item.get("protocol",""),
					"protocol_param":item.get("protocolparam",""),
					"plugin":item.get("plugin",""),
					"obfs":item.get("obfs",""),
					"obfs_param":item.get("obfsparam",""),
					"plugin_opts":item.get("plugin_opts",""),
					"plugin_args":item.get("plugin_args",""),
					"remarks":item.get("remarks",item["server"]),
					"group":item.get("group","N/A"),
					"local_address":LOCAL_ADDRESS,
					"local_port":LOCAL_PORT,
					"timeout":TIMEOUT,
					"fast_open": False
				}
				if (_dict["remarks"] == ""):
					_dict["remarks"] = _dict["server"]
			#	logger.info(_dict["server"])
				self._configList.append(_dict)

		logger.info("Read %d node(s)" % len(self._configList))

	def getAllConfig(self):
		return self._configList

	def getNextConfig(self):
		if (self._configList != []):
			return self._configList.pop(0)
		else:
			return None


