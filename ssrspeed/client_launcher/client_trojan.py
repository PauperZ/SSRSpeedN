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

class Trojan(BaseClient):
	def __init__(self):
		super(Trojan,self).__init__()

	def startClient(self,config={}):
		self._config = config
		#logger.info(json.dumps(self._config))
		with open("./config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(self._config))
		try:
			if (self._process == None):
				if (self._checkPlatform() == "Windows"):
					if (logger.level == logging.DEBUG):
						self._process = subprocess.Popen(["./clients/trojan/trojan.exe","--config","{}/config.json".format(os.getcwd())])
					else:
						self._process = subprocess.Popen(["./clients/trojan/trojan.exe","--config","{}/config.json".format(os.getcwd())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
					logger.info("Starting trojan with server %s:%d" % (config["server"],config["server_port"]))
				else:
					logger.critical("Your system does not supported.Please contact developer.")
					sys.exit(1)
		except FileNotFoundError:
			#logger.exception("")
			logger.error("V2Ray Core Not Found !")
			sys.exit(1)


