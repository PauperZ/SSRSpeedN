#coding:utf-8

import time
import logging
import json
import threading
import socket
import sys
import os

logger = logging.getLogger("Sub")

from ..client_launcher import ShadowsocksClient as SSClient
from ..client_launcher import ShadowsocksRClient as SSRClient
from ..client_launcher import V2RayClient

from ..config_parser import UniversalParser

from ..result import ExportResult
from ..result import importResult
from ..result import Sorter

from ..speed_test import SpeedTest
from ..utils import check_platform
from ..utils.port_checker import check_port

from config import config

try:
	check_port(config["localPort"])
	print("Port {} already in use,".format(config["localPort"]) + " please change the local port in ssrspeed_config.json or terminate the application.")
	sys.exit(0)
except (ConnectionRefusedError, socket.timeout):
	pass


class SSRSpeedCore(object):
	def __init__(self):
		
		self.testMethod = "SOCKET"
		self.proxyType = "SSR"
		self.webMode = False
		self.colors = "origin"
		self.sortMethod = ""
		self.testMode = "TCP_PING"
		
		self.__timeStampStart = -1
		self.__timeStampStop = -1
		self.__parser = UniversalParser()
		self.__stc = None
		self.__results = []
		self.__status = "stopped"

	def set_group(self, group: str):
		self.__parser.set_group(group)
	
	#Web Methods
	def web_get_colors(self):
		return config["exportResult"]["colors"]
	
	def web_get_status(self):
		return self.__status
	
	def __generate_web_configs(self, nodes: list) -> list:
		result = []
		for node in nodes:
			result.append(
				{
					"type": node.node_type,
					"config": node.config
				}
			)
		return result
	
	def web_read_subscription(self, url: str) -> list:
		parser = UniversalParser()
		urls = url.split(" ")
		if parser:
			parser.read_subscription(urls)
			return self.__generate_web_configs(parser.nodes)
		return []

	def web_read_config_file(self, filename) -> list:
		parser = UniversalParser()
		if parser:
			parser.read_gui_config(filename)
			return self.__generate_web_configs(parser.nodes)
		return []
	
	def web_setup(self,**kwargs):
		self.testMethod = kwargs.get("testMethod","SOCKET")
		self.colors = kwargs.get("colors","origin")
		self.sortMethod = kwargs.get("sortMethod","")
		self.testMode = kwargs.get("testMode","TCP_PING")

	def web_set_configs(self, configs: list):
		if (self.__parser):
			self.__parser.set_nodes(
				UniversalParser.web_config_to_node(configs)
			)
	
	#Console Methods
	def console_setup(self,
		test_mode: str,
		test_method: str,
		color: str = "origin",
		sort_method: str = "",
		url: str = "",
		cfg_filename: str = ""
	):
		self.testMethod = test_method
		self.testMode = test_mode
		self.sortMethod = sort_method
		self.colors = color
		if self.__parser:
			if cfg_filename:
				self.__parser.read_gui_config(cfg_filename)
			elif url:
				self.__parser.read_subscription(url.split(" "))
			else:
				raise ValueError("Subscription URL or configuration file must be set !")

	def start_test(self, use_ssr_csharp=False):
		self.__timeStampStart = time.time()
		self.__stc = SpeedTest(self.__parser, self.testMethod, use_ssr_csharp)
		self.__status = "running"
		if (self.testMode == "TCP_PING"):
			self.__stc.tcpingOnly()
		elif(self.testMode == "ALL"):
			self.__stc.fullTest()
		elif (self.testMode == "WEB_PAGE_SIMULATION"):
			self.__stc.webPageSimulation()
		self.__status = "stopped"
		self.__results = self.__stc.getResult()
		self.__timeStampStop = time.time()
		self.__exportResult()

	def clean_result(self):
		self.__results = []
		if (self.__stc):
			self.__stc.resetStatus()

	def get_results(self):
		return self.__results

	def web_get_results(self):
		if (self.__status == "running"):
			if (self.__stc):
				status = "running"
			else:
				status = "pending"
		else:
			status = self.__status
		r = {
			"status":status,
			"current":self.__stc.getCurrent() if (self.__stc and status == "running") else {},
			"results":self.__stc.getResult() if (self.__stc) else []
		}
		return r

	def filter_nodes(self, fk=[], fgk=[], frk=[], ek=[], egk=[], erk=[]):
	#	self.__parser.excludeNode([],[],config["excludeRemarks"])
		self.__parser.filter_nodes(fk, fgk, frk, ek, egk, erk + config["excludeRemarks"])
		self.__parser.print_nodes()
		logger.info("{} node(s) will be test.".format(len(self.__parser.nodes)))
	

	def import_and_export(self,filename,split=0):
		self.__results = importResult(filename)
		self.__exportResult(split,2)
		self.__results = []

	def __exportResult(self,split = 0,exportType= 0):
		er = ExportResult()
		er.setTimeUsed(self.__timeStampStop - self.__timeStampStart)
		if self.testMode == "WEB_PAGE_SIMULATION":
			er.exportWpsResult(self.__results, exportType)
		else:
			er.setColors(self.colors)
			er.export(self.__results,split,exportType,self.sortMethod)



