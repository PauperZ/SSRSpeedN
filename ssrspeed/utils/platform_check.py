#coding:utf-8

import platform
import logging
logger = logging.getLogger("Sub")

def check_platform():
		tmp = platform.platform()
		logger.info("Platform Info : {}".format(str(tmp)))
		if ("Windows" in tmp):
			return "Windows"
		elif("Linux" in tmp):
			return "Linux"
		elif("Darwin" in tmp):
			return "MacOS"
		else:
			return "Unknown"
