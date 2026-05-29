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

class Shadowsocks(BaseClient):
	def __init__(self):
		super(Shadowsocks,self).__init__()

	def startClient(self,config={},testing=False):
		self._config = config
	#	self._config["server_port"] = int(self._config["server_port"])
		with open("./config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(self._config))
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["./clients/shadowsocks-libev/ss-local.exe", "-u", "-c","{}/config.json".format(os.getcwd()),"-v"])
				else:
					self._process = subprocess.Popen(["./clients/shadowsocks-libev/ss-local.exe", "-u","-c","{}/config.json".format(os.getcwd())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting Shadowsocks-libev with server %s:%d" % (config["server"],config["server_port"]))
			elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["ss-local", "-u","-v","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["ss-local", "-u","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting Shadowsocks-libev with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.critical("Your system does not supported.Please contact developer.")
				sys.exit(1)

class Shadowsockss(BaseClient):
	def __init__(self):
		super(Shadowsockss,self).__init__()

	def getCurrrentConfig(self):
		with open("./clients/shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
		curIndex = tmpConf["index"]
		return tmpConf["configs"][curIndex]

	def nextWinConf(self):
		self.stopClient()
		with open("./clients/shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
		tmpConf["configs"] = []
		try:
			curConfig = self._configList.pop(0)
		except IndexError:
			return None
		tmpConf["configs"].append(curConfig)
		with open("./clients/shadowsocks-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))
		logger.info("Wait {} secs to start client.".format(3))
		for i in range(0,6):
			time.sleep(0.5)
		self.startClient({},True)
		return curConfig
	#	return tmpConf["configs"][curIndex]

	def __winConf(self):
		with open("./clients/shadowsocks-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
		tmpConf["localPort"] = self._localPort
		tmpConf["index"] = 0
		tmpConf["global"] = False
		tmpConf["enabled"] = False
		tmpConf["configs"] = []
		for iitem in self._configList:
			tmpConf["configs"].append(iitem)
		with open("./clients/shadowsocks-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))

	def startClient(self,config={},testing=False):
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				if (not testing):
					self.__winConf()
			#	sys.exit(0)
				self._process = subprocess.Popen(["./clients/shadowsocks-win/Shadowsocks.exe"])
			elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
				self._config = config
				self._config["server_port"] = int(self._config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self._config))
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["ss-local","-v","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["ss-local","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting Shadowsocks-libev with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.critical("Your system does not supported.Please contact developer.")
				sys.exit(1)
