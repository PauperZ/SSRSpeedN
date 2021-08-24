#coding:utf-8

import logging
import json
import copy

logger = logging.getLogger("Sub")

class ParserShadowsocksD(object):
	def __init__(self,baseConfig):
		self.__configList = []
		self.__baseConfig = baseConfig

	def __getShadowsocksBaseConfig(self):
		return copy.deepcopy(self.__baseConfig)

	def parseSubsConfig(self,config):
		ssdConfig = json.loads(config)
		group = ssdConfig.get("airport","N/A")
		defaultPort = int(ssdConfig["port"])
		defaultMethod = ssdConfig["encryption"]
		defaultPassword = ssdConfig["password"]
		defaultPlugin = ssdConfig.get("plugin","")
		defaultPluginOpts = ssdConfig.get("plugin_options","")
		servers = ssdConfig["servers"]
		for server in servers:
			_config = self.__getShadowsocksBaseConfig()
			_config["server"] = server["server"]
			_config["server_port"] = int(server.get("port",defaultPort))
			_config["method"] = server.get("encryption",defaultMethod)
			_config["password"] = server.get("password",defaultPassword)
			_config["plugin"] = server.get("plugin",defaultPlugin)
			_config["plugin_opts"] = server.get("plugin_options",defaultPluginOpts)
			_config["group"] = group
			_config["remarks"] = server.get("remarks",server["server"])
			if not _config["remarks"]: _config["remarks"] = _config["server"]
			self.__configList.append(_config)
		logger.info("Read {} config(s).".format(len(self.__configList)))
		return self.__configList

	def parseGuiConfig(self,filename):
		# In BasicParser.py
		raise AttributeError("'parseGuiConfig' built-in 'BasicParser.py' with basic shadowsocks parser.")

