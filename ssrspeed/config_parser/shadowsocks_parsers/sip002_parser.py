# -*- coding: utf-8 -*-

import logging
import json
import urllib.parse
import copy

from ...utils import b64plus

logger = logging.getLogger("Sub")

class ParserShadowsocksSIP002:
	def __init__(self, base_config: dict):
		self.__config_list = []
		self.__base_config = base_config

	def __get_shadowsocks_base_config(self):
		return copy.deepcopy(self.__base_config)

	def __parse_link(self, link: str):
		_config = self.__get_shadowsocks_base_config()
		if link[:5] != "ss://":
			logger.error("Unsupport link : %s" % link)
			return None
		
		url_unquoted = urllib.parse.unquote(link)
		url_data = urllib.parse.urlparse(url_unquoted)
		plugin_raw = url_data.query
		remarks = url_data.fragment
		decoded = b64plus.decode(url_data.netloc[:url_data.netloc.find("@")]).decode("utf-8")
		d_pos = decoded.find(":")
		encryption = decoded[:d_pos]
		password = decoded[d_pos + 1:]

		ad_port = url_data.netloc[url_data.netloc.find("@") + 1:].split(":")
		if len(ad_port) != 2:
			logger.error(f"Invalid {str(ad_port)} for link {link}")
			return None
		server = ad_port[0]
		port = int(ad_port[1])
		
		plugin = ""
		plugin_opts = ""
		if ("plugin=" in plugin_raw.lower()):
			index1 = plugin_raw.find("plugin=") + 7
			index2 = plugin_raw.find(";",index1)
			plugin = plugin_raw[index1:index2]
			index3 = plugin_raw.find("&",index2)
			plugin_opts = plugin_raw[index2 + 1:index3 if index3 != -1 else None]

		_config["server"] = server
		_config["server_port"] = port
		_config["method"] = encryption
		_config["password"] = password
		_config["remarks"] = remarks if remarks else server
		if plugin.lower() in ["simple-obfs", "obfs-local"]:
			plugin = "simple-obfs"
		elif not plugin:
			plugin = ""
			plugin_opts = ""
		else:
			logger.warn(f"Unsupport plugin: {plugin}")
			return None

		_config["plugin"] = plugin
		_config["plugin_opts"] = plugin_opts

		return _config

	def parse_single_link(self, link):
		return self.__parse_link(link)

	def parseSubsConfig(self, links):
		for link in links:
			link = link.strip()
			cfg = self.__parse_link(link)
			if cfg:
				self.__config_list.append(cfg)
		logger.info("Read {} config(s).".format(len(self.__config_list)))
		return self.__config_list


