#coding:utf-8

import logging
import sys
import os
import subprocess

from .platform_check import check_platform

logger = logging.getLogger("Sub")

class RequirementsCheck(object):
	def __init__(self):
		self.__winRequire = {
			"Shadowsocks-libev":[
				"./clients/shadowsocks-libev/obfs-local.exe",
				"./clients/shadowsocks-libev/simple-obfs.exe",
				"./clients/shadowsocks-libev/ss-local.exe",
				"./clients/shadowsocks-libev/ss-tunnel.exe"
			],
			"ShadowsocksR-libev":[
				"./clients/shadowsocksr-libev/libssp-0.dll",
				"./clients/shadowsocksr-libev/libwinpthread-1.dll",
				"./clients/shadowsocksr-libev/libpcre-1.dll",
				"./clients/shadowsocksr-libev/libcrypto-1_1.dll",
				"./clients/shadowsocksr-libev/ssr-local.exe"
			],
			"ShadowsocksR-C#":[
				"./clients/shadowsocksr-win/shadowsocksr.exe"
			],
			"V2Ray-Core":[
				"./clients/v2ray-core/v2ctl.exe",
				"./clients/v2ray-core/v2ray.exe"
			]
		}

		self.__linuxRequire = {
			"Shadowsocks-libev": [
				# "./clients/shadowsocks-libev/obfs-local.exe",
				"./clients/shadowsocks-libev/simple-obfs",
				"./clients/shadowsocks-libev/ss-local",
				# "./clients/shadowsocks-libev/ss-tunnel.exe"
			],
			"ShadowsocksR-libev": [
				# "./clients/shadowsocksr-libev/libssp-0.dll",
				# "./clients/shadowsocksr-libev/libwinpthread-1.dll",
				# "./clients/shadowsocksr-libev/libpcre-1.dll",
				# "./clients/shadowsocksr-libev/libcrypto-1_1.dll",
				"./clients/shadowsocksr-libev/ssr-local"
			],
			# "ShadowsocksR-C#": [
			# 	"./clients/shadowsocksr-win/shadowsocksr.exe"
			# ],
			"V2Ray-Core":[
				"./clients/v2ray-core/v2ctl",
				"./clients/v2ray-core/v2ray"
			]
		}

	def check(self):
		pfInfo = check_platform()
		if (pfInfo == "Windows"):
			self.__checks(self.__winRequire)
		elif (pfInfo == "Linux" or pfInfo == "MacOS"):
			self.__checks(self.__linuxRequire)
			# self.__linuxCheck()
		else:
			logger.critical("Unsupport platform !")
			sys.exit(1)

	def __checks(self,requires = {}):
		for key in requires.keys():
			for require in requires[key]:
				logger.info("Checking {}".format(require))
				if (os.path.exists(require)):
					if (os.path.isdir(require)):
						logger.warn("Requirement {} not found !!!".format(require))
						continue
				else:
					logger.warn("Requirement {} not found !!!".format(require))

	def __linuxCheck(self):
		if (not self.__linuxCheckLibsodium()):
			logger.critical("Requirement libsodium not found !!!")
			sys.exit(1)
		self.__checks(self.__linuxRequire)
		self.__linuxCheckShadowsocks()	

	def __linuxCheckLibsodium(self):
		logger.info("Checking libsodium.")
		if (check_platform() == "MacOS"):
		#	logger.warn("MacOS does not support detection of libsodium, please ensure that libsodium is installed.")
			try:
				process = subprocess.Popen("brew info libsodium", shell=True, stdout=subprocess.PIPE)
				try:
					out = process.communicate(timeout=15)[0]
				except subprocess.TimeoutExpired:
					process.terminate()
					out, errs = process.communicate()
					logger.exception(out.decode("utf-8") + errs.decode("utf-8"))
					return False
				logger.debug("brew info libsodium : {}".format(out))
				if "Not installed\n" in out.decode("utf-8"):
					logger.error("Libsodium not found.")
					return False
				return True
			except:
				logger.exception("")
				return False
		#	return True
		else:
			try:
				process = subprocess.Popen("ldconfig -p | grep libsodium",shell=True,stdout=subprocess.PIPE)
				try:
					out = process.communicate(timeout=15)[0]
				except subprocess.TimeoutExpired:
					process.terminate()
					out, errs = process.communicate()
					logger.exception(out.decode("utf-8") + errs.decode("utf-8"))
					return False
				logger.debug("ldconfig : {}".format(out))
				if ("libsodium" not in out.decode("utf-8")):
					return False
				return True
			except:
				logger.exception("")
				return False

	def __linuxCheckShadowsocks(self):
		sslibev = False
		simpleobfs = False
		for cmdpath in os.environ["PATH"].split(":"):
			if (not os.path.isdir(cmdpath)):
				continue
			for filename in os.listdir(cmdpath):
				if (filename == "obfs-local" or filename == "simple-obfs"):
					logger.info("Obfs-Local found {}".format(os.path.join(cmdpath,"obfs-local")))
					simpleobfs = True
				elif(filename == "ss-local"):
					logger.info("Shadowsocks-libev found {}".format(os.path.join(cmdpath,"ss-local")))
					sslibev = True
				if (simpleobfs and sslibev):
					break
			if (simpleobfs and sslibev):
				break
		if (not simpleobfs):
			logger.warn("Simple Obfs not found !!!")
		if (not sslibev):
			logger.warn("Shadowsocks-libev not found !!!")
		return True if (simpleobfs and sslibev) else False


