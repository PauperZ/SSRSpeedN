#coding:utf-8

import logging

logger = logging.getLogger("Sub")

from . import BaseParser
from ..utils import b64plus

class ShadowsocksRParser(BaseParser):
	def __init__(self):
		super(ShadowsocksRParser,self).__init__()

	def _parseLink(self,link):
		_config = self._getShadowsocksBaseConfig()
	#	print(self._baseShadowsocksConfig["remarks"])
		if (link[:6] != "ssr://"):
			logger.error("Unsupport link : %s" % link)
			return None

		link = link[6:]
		decoded = b64plus.decode(link).decode("utf-8")
		decoded1 = decoded.split("/?")[0].split(":")[::-1]
		if (len(decoded1) != 6):
			return None
			addr = ""
			for i in range(5,len(decoded1) - 1):
				addr += decoded1[i] + ":"
			addr += decoded1[len(decoded1) - 1]
			decoded1[5] = addr
		decoded2 = decoded.split("/?")[1].split("&")
		_config["server"] = decoded1[5]
		_config["server_port"] = int(decoded1[4])
		_config["method"] = decoded1[2]
		_config["protocol"] = decoded1[3]
		_config["obfs"] = decoded1[1]
		_config["password"] = b64plus.decode(decoded1[0]).decode("utf-8")
		for ii in decoded2:
			if ("obfsparam" in ii):
				_config["obfs_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("protocolparam" in ii or "protoparam" in ii):
				_config["protocol_param"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif ("remarks" in ii):
				_config["remarks"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue
			elif("group" in ii):
				_config["group"] = b64plus.decode(ii.split("=")[1]).decode("utf-8")
				continue

		if (_config["remarks"] == ""):
			_config["remarks"] = _config["server"]
		return _config


