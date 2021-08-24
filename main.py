#coding:utf-8

import time
import sys
import os
import logging, colorlog

from config import config

from ssrspeed.shell import cli as cli_cfg
from ssrspeed.utils import check_platform, RequirementsCheck
from ssrspeed.core import SSRSpeedCore

if (not os.path.exists("./logs/")):
	os.mkdir("./logs/")
if (not os.path.exists("./results/")):
	os.mkdir("./results/")

loggerList = []
loggerSub = logging.getLogger("Sub")
logger = logging.getLogger(__name__)
loggerList.append(loggerSub)
loggerList.append(logger)

formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(lineno)d]%(message)s")
fileHandler = logging.FileHandler("./logs/" + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".log",encoding="utf-8")
fileHandler.setFormatter(formatter)
consoleHandler = colorlog.ConsoleHandler()
consoleHandler.setFormatter(formatter)

VERSION = config["VERSION"]

if (__name__ == "__main__"):
	pfInfo = check_platform()
	if (pfInfo == "Unknown"):
		logger.critical("Your system does not supported.Please contact developer.")
		sys.exit(1)

	DEBUG = False
	CONFIG_LOAD_MODE = 0 #0 for import result,1 for guiconfig,2 for subscription url
	CONFIG_FILENAME = ""
	CONFIG_URL = ""
	IMPORT_FILENAME = ""
	FILTER_KEYWORD = []
	FILTER_GROUP_KRYWORD = []
	FILTER_REMARK_KEYWORD = []
	EXCLUDE_KEYWORD = []
	EXCLUDE_GROUP_KEYWORD = []
	EXCLUDE_REMARK_KEWORD = []
	TEST_METHOD = ""
	TEST_MODE = ""
	#PROXY_TYPE = "SSR"
	#SPLIT_CNT = 0
	SORT_METHOD = ""
	SKIP_COMFIRMATION = True
	RESULT_IMAGE_COLOR = "origin"
	
	options,args = cli_cfg.init(VERSION)

	if (options.paolu):
		for root, dirs, files in os.walk(".", topdown=False):
			for name in files:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
			for name in dirs:
				try:
					os.remove(os.path.join(root, name))
				except:
					pass
		sys.exit(0)

	print("****** Import Hint 重要提示******")
	print("ChenBilly yyds！")
	print("*********************************")
	input("Press ENTER to conitnue or Crtl+C to exit.")

	if (options.debug):
		DEBUG = options.debug
		for item in loggerList:
			item.setLevel(logging.DEBUG)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)
	else:
		for item in loggerList:
			item.setLevel(logging.INFO)
			item.addHandler(fileHandler)
			item.addHandler(consoleHandler)

	logger.info("SSRSpeed {}, Web Api Version {}".format(config["VERSION"], config["WEB_API_VERSION"]))

	if (logger.level == logging.DEBUG):
		logger.debug("Program running in debug mode")

	if not options.skip_requirements_check:
		rc = RequirementsCheck()
		rc.check()
	else:
		logger.warn("Requirements check skipped.")

	'''
	if (options.proxy_type):
		if (options.proxy_type.lower() == "ss"):
			PROXY_TYPE = "SS"
		elif (options.proxy_type.lower() == "ssr"):
			PROXY_TYPE = "SSR"
		elif (options.proxy_type.lower() == "ssr-cs"):
			PROXY_TYPE = "SSR-C#"
		elif (options.proxy_type.lower() == "v2ray"):
			PROXY_TYPE = "V2RAY"
		else:
			logger.warn("Unknown proxy type {} ,using default ssr.".format(options.proxy_type))
	'''

	#print(options.test_method)
	if options.test_method == "speedtestnet":
		TEST_METHOD = "SPEED_TEST_NET"
	elif options.test_method == "fast":
		TEST_METHOD = "FAST"
	elif options.test_method == "stasync":
		TEST_METHOD = "ST_ASYNC"
	elif options.test_method == "socket":
		TEST_METHOD = "SOCKET"
	else:
		TEST_METHOD = "ST_ASYNC"

	if (options.test_mode == "pingonly"):
		TEST_MODE = "TCP_PING"
	elif(options.test_mode == "all"):
		TEST_MODE = "ALL"
	elif (options.test_mode == "wps"):
		TEST_MODE = "WEB_PAGE_SIMULATION"
	else:
		logger.critical("Invalid test mode : %s" % options.test_mode)
		sys.exit(1)
	

	if (options.confirmation):
		SKIP_COMFIRMATION = options.confirmation
	
	if (options.result_color):
		RESULT_IMAGE_COLOR = options.result_color

	if (options.import_file):
		CONFIG_LOAD_MODE = 0
	elif (options.guiConfig):
		CONFIG_LOAD_MODE = 1
		CONFIG_FILENAME = options.guiConfig
	elif(options.url):
		CONFIG_LOAD_MODE = 2
		CONFIG_URL = options.url
	else:
		logger.error("No config input,exiting...")
		sys.exit(1)


	if (options.filter):
		FILTER_KEYWORD = options.filter
	if (options.group):
		FILTER_GROUP_KRYWORD = options.group
	if (options.remarks):
		FILTER_REMARK_KEYWORD = options.remarks

	if (options.efliter):
		EXCLUDE_KEYWORD = options.efliter
	#	print (EXCLUDE_KEYWORD)
	if (options.egfilter):
		EXCLUDE_GROUP_KEYWORD = options.egfilter
	if (options.erfilter):
		EXCLUDE_REMARK_KEWORD = options.erfilter

	logger.debug(
		"\nFilter keyword : %s\nFilter group : %s\nFilter remark : %s\nExclude keyword : %s\nExclude group : %s\nExclude remark : %s" % (
			str(FILTER_KEYWORD),str(FILTER_GROUP_KRYWORD),str(FILTER_REMARK_KEYWORD),str(EXCLUDE_KEYWORD),str(EXCLUDE_GROUP_KEYWORD),str(EXCLUDE_REMARK_KEWORD)
		)
	)

	'''
	if (int(options.split_count) > 0):
		SPLIT_CNT = int(options.split_count)
	'''
	
	if (options.sort_method):
		sm = options.sort_method
	#	print(sm)
		if (sm == "speed"):
			SORT_METHOD = "SPEED"
		elif(sm == "rspeed"):
			SORT_METHOD = "REVERSE_SPEED"
		elif(sm == "ping"):
			SORT_METHOD = "PING"
		elif(sm == "rping"):
			SORT_METHOD = "REVERSE_PING"
		else:
			logger.error("Sort method %s not support." % sm)

	sc = SSRSpeedCore()

	if (options.import_file and CONFIG_LOAD_MODE == 0):
		IMPORT_FILENAME = options.import_file
		sc.colors = RESULT_IMAGE_COLOR
		sc.sortMethod = SORT_METHOD if SORT_METHOD else ""
		sc.import_and_export(IMPORT_FILENAME)
		sys.exit(0)

	configs = []
	if (CONFIG_LOAD_MODE == 1):
		sc.console_setup(
			TEST_MODE,
			TEST_METHOD,
			RESULT_IMAGE_COLOR,
			SORT_METHOD,
			cfg_filename = CONFIG_FILENAME
		)
	#	sc.consoleReadFileConfigs(CONFIG_FILENAME)
	else:
		sc.console_setup(
			TEST_MODE,
			TEST_METHOD,
			RESULT_IMAGE_COLOR,
			SORT_METHOD,
			url = CONFIG_URL
		)
	#	sc.consoleReadSubscription(CONFIG_URL)

	if options.group_override:
		sc.set_group(options.group_override)

	sc.filter_nodes(
		FILTER_KEYWORD,
		FILTER_GROUP_KRYWORD,
		FILTER_REMARK_KEYWORD,
		EXCLUDE_KEYWORD,
		EXCLUDE_GROUP_KEYWORD,
		EXCLUDE_REMARK_KEWORD
	)
	sc.clean_result()

	if not SKIP_COMFIRMATION:
		ans = input("Before the test please confirm the nodes,Ctrl-C to exit. (Y/N)")
		if ans.upper() == "Y":
			pass
		else:
			sys.exit(0)
	
	sc.start_test(options.use_ssr_cs)



