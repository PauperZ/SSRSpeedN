#coding:utf-8

import json
import subprocess
import requests
import socket
import platform
import signal
import os
import time
import sys
import logging
logger = logging.getLogger("Sub")

from .base_client import BaseClient

class ShadowsocksR(BaseClient):
	def __init__(self):
		super(ShadowsocksR,self).__init__()
		self.useSsrCSharp = False

	def _beforeStopClient(self):
		if (self.useSsrCSharp):
			self.__ssrCSharpConf({})
	
	def __ssrCSharpConf(self,config):
		with open("./clients/shadowsocksr-win/gui-config.json","r+",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
		tmpConf["localPort"] = self._localPort
		tmpConf["sysProxyMode"] = 1
		tmpConf["index"] = 0
		tmpConf["proxyRuleMode"] = 0
		tmpConf["configs"] = []
		config["protocolparam"] = config.get("protocol_param","")
		config["obfsparam"] = config.get("obfs_param","")
		tmpConf["configs"].append(config)
		with open("./clients/shadowsocksr-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))

	def startClient(self,config = {}):
		self._config = config
	#	self._config["server_port"] = int(self._config["server_port"])
		with open("./config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(self._config))
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				if (self.useSsrCSharp):
					self.__ssrCSharpConf(config)
					self._process = subprocess.Popen(["./clients/shadowsocksr-win/shadowsocksr.exe"])
					logger.info("ShadowsocksR-C# started.")
					return
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["./clients/shadowsocksr-libev/ssr-local.exe", "-u", "-c","{}/config.json".format(os.getcwd()),"-v"])
					logger.info("Starting ShadowsocksR-libev with server %s:%d" % (config["server"],config["server_port"]))
				else:
					self._process = subprocess.Popen(["./clients/shadowsocksr-libev/ssr-local.exe", "-u","-c","{}/config.json".format(os.getcwd())],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
					logger.info("Starting ShadowsocksR-libev with server %s:%d" % (config["server"],config["server_port"]))
			elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-v","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
		#	print(self.__process.returncode)

class ShadowsocksRR(BaseClient):
	def __init__(self):
		super(ShadowsocksRR,self).__init__()
		self.__ssrAuth = ""

	def __winConf(self):
		with open("./clients/shadowsocksr-win/gui-config.json","r",encoding="utf-8") as f:
			tmpConf = json.loads(f.read())
		self.__ssrAuth = tmpConf["localAuthPassword"]
		tmpConf["token"]["SpeedTest"] = "SpeedTest"
		tmpConf["localPort"] = self._localPort
		tmpConf["sysProxyMode"] = 1
		tmpConf["index"] = 0
		tmpConf["proxyRuleMode"] = 2
		tmpConf["configs"] = []
		for iitem in self._configList:
			try:
				iitem["protocolparam"] = iitem["protocol_param"]
			except KeyError:
				iitem["protocolparam"] = ""
			try:
				iitem["obfsparam"] = iitem["obfs_param"]
			except KeyError:
				iitem["obfsparam"] = ""
			tmpConf["configs"].append(iitem)
		with open("./clients/shadowsocksr-win/gui-config.json","w+",encoding="utf-8") as f:
			f.write(json.dumps(tmpConf))

	def getCurrrentConfig(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"curConfig"
		}
		i = 0
		while (True):
			try:
				rep = requests.post("http://%s:%d/api?auth=%s" % (self._localAddress,self._localPort,self.__ssrAuth),params = param,timeout=5)
				break
			except (requests.exceptions.Timeout,socket.timeout):
				logger.error("Connect to ssr api server timeout.")
				i += 1
				if (i >= 4):
					return False
				continue
			#	self.nextWinConf()
			#	return False
			except:
				logger.exception("Get current config failed.")
				return False
		rep.encoding = "utf-8"
		if (rep.status_code == 200):
		#	logger.debug(rep.content)
			return rep.json()
		else:
			logger.error(rep.status_code)
			return False

	def nextWinConf(self):
		param = {
			"app":"SpeedTest",
			"token":"SpeedTest",
			"action":"nextConfig"
		}
		i = 0
		while(True):
			try:
				rep = requests.post("http://%s:%d/api?auth=%s" % (self._localAddress,self._localPort,self.__ssrAuth),params = param,timeout=5)
				break
			except (requests.exceptions.Timeout,socket.timeout):
				logger.error("Connect to ssr api server timeout.")
				i += 1
				if (i >= 4):
					return False
				continue
			#	return False
			except:
				logger.exception("Request next config failed.")
				return False
		if (rep.status_code == 403):
			return False
		else:
			return True

	def startClient(self,config = {}):
		if (self._process == None):
			if (self._checkPlatform() == "Windows"):
				self.__winConf()
			#	sys.exit(0)
				self._process = subprocess.Popen(["./clients/shadowsocksr-libev/ssr-local.exe"])
			elif(self._checkPlatform() == "Linux" or self._checkPlatform() == "MacOS"):
				self._config = config
				self._config["server_port"] = int(self._config["server_port"])
				with open("./config.json","w+",encoding="utf-8") as f:
					f.write(json.dumps(self._config))
				if (logger.level == logging.DEBUG):
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()])
				else:
					self._process = subprocess.Popen(["python3","./clients/shadowsocksr/shadowsocks/local.py","-c","%s/config.json" % os.getcwd()],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
				logger.info("Starting ShadowsocksR-Python with server %s:%d" % (config["server"],config["server_port"]))
			else:
				logger.error("Your system does not supported.Please contact developer.")
				sys.exit(1)
		#	print(self.__process.returncode)
