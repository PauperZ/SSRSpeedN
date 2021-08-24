#coding:utf-8

import logging
import json
import urllib.parse
import binascii
import copy

from ...utils import b64plus

logger = logging.getLogger("Sub")

class ParserShadowsocksBasic(object):
	def __init__(self,baseConfig):
		self.__configList = []
		self.__baseConfig = baseConfig

	def __getShadowsocksBaseConfig(self):
		return copy.deepcopy(self.__baseConfig)

	def __parseLink(self, link):
		_config = self.__getShadowsocksBaseConfig()

		if (link[:5] != "ss://"):
			logger.error("Unsupport link : %s" % link)
			return None
		
		try:
			decoded = b64plus.decode(link[5:]).decode("utf-8")
			at_pos = decoded.rfind("@")
			if at_pos == -1:
				raise ValueError("Not shadowsocks basic link.")
			mp = decoded[:at_pos]
			ap = decoded[at_pos + 1:]
			mp_pos = mp.find(":")
			ap_pos = ap.find(":")
			if mp_pos == -1 or ap_pos == -1:
				raise ValueError("Not shadowsocks basic link.")
			encryption = mp[:mp_pos]
			password = mp[mp_pos + 1:]
			server = ap[:ap_pos]
			port = int(ap[ap_pos + 1:])
			_config["server"] = server
			_config["server_port"] = port
			_config["method"] = encryption
			_config["password"] = password
			_config["remarks"] = _config["server"]
		except binascii.Error:
			raise ValueError("Not shadowsocks basic link.")
		except:
			logger.exception(f"Exception link {link}\n")
			return None
		return _config

	def parse_single_link(self, link):
		return self.__parseLink(link)

	def parseSubsConfig(self,links):
		for link in links:
			link = link.strip()
			cfg = self.__parseLink(link)
			if (cfg):
				self.__configList.append(cfg)
		logger.info("Read {} config(s).".format(len(self.__configList)))
		return self.__configList

	def __getSsdGroup(self, ssdSubs, subUrl):
		if len(ssdSubs) == 0 or subUrl == "":
			return "N/A"
		for item in ssdSubs:
			if item.get("url", "") == subUrl:
				return item.get("airport", "N/A")
		return "N/A"
	
	def parse_gui_data(self, data: dict):
		shadowsocksdConf = False
		ssdSubs = []
		if data.__contains__("subscriptions"):
			shadowsocksdConf = True
			ssdSubs = data["subscriptions"]
		configs = data["configs"]
		for item in configs:
			_dict = self.__getShadowsocksBaseConfig()
			_dict["server"] = item["server"]
			_dict["server_port"] = int(item["server_port"])
			_dict["password"] = item["password"]
			_dict["method"] = item["method"]
			_dict["plugin"] = item.get("plugin","")
			_dict["plugin_opts"] = item.get("plugin_opts","")
			_dict["plugin_args"] = item.get("plugin_args","")
			_dict["remarks"] = item.get("remarks",item["server"])
			if not _dict["remarks"]: _dict["remarks"] = _dict["server"]
			if not shadowsocksdConf:
				_dict["group"] = item.get("group","N/A")
			else:
				_dict["group"] = self.__getSsdGroup(ssdSubs, item.get("subscription_url", ""))
			_dict["fast_open"] = False
			self.__configList.append(_dict)
		return self.__configList

	def parseGuiConfig(self,filename):
		with open(filename,"r",encoding="utf-8") as f:
			try:
				fullConf = json.load(f)
				self.parse_gui_data(fullConf)
			except json.decoder.JSONDecodeError:
				return False
			except:
				logger.exception("Not Shadowsocks configuration file.")
				return []
			
		logger.info("Read {} node(s).".format(len(self.__configList)))
		return self.__configList

