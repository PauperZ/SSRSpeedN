#coding:utf-8

import json
import subprocess
import platform
import signal
import os
import time
import sys
import logging
logger = logging.getLogger("Sub")

from .base_client import BaseClient

class V2Ray(BaseClient):
	def __init__(self):
		super(V2Ray,self).__init__()

	def startClient(self,config={}):
		self._config = config
		with open("./config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(self._config))
		try:
			if (self._process == None):
				if (self._checkPlatform() == "Windows"):
					if (logger.level == logging.DEBUG):
						self._process = subprocess.Popen(["./clients/v2ray-core/v2ray.exe","--config","{}/config.json".format(os.getcwd())])
					else:
						self._process = subprocess.Popen(["./clients/v2ray-core/v2ray.exe","--config","{}/config.json".format(os.getcwd())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
					logger.info("Starting v2ray-core with server %s:%d" % (config["server"],config["server_port"]))
				elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
					if (logger.level == logging.DEBUG):
						self._process = subprocess.Popen(["./clients/v2ray-core/v2ray","--config","%s/config.json" % os.getcwd()])
					else:
						self._process = subprocess.Popen(["./clients/v2ray-core/v2ray","--config","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
					logger.info("Starting v2ray-core with server %s:%d" % (config["server"],config["server_port"]))
				else:
					logger.critical("Your system does not supported.Please contact developer.")
					sys.exit(1)
		except FileNotFoundError:
			#logger.exception("")
			logger.error("V2Ray Core Not Found !")
			sys.exit(1)


